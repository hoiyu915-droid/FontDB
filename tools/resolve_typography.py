#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import yaml

from glyph_preflight import resolve as resolve_glyphs
from font_integrity import verify as verify_font


def parse_binding(value: str):
    if "=" not in value:
        raise argparse.ArgumentTypeError("binding must be FAMILY=PATH")
    family, raw_path = value.split("=", 1)
    path = Path(raw_path)
    if not family or not path.is_file():
        raise argparse.ArgumentTypeError(f"invalid font binding: {value}")
    return family, path


def locale_matches(requested: str, supported: list[str]) -> bool:
    return requested in supported or any(requested.startswith(x + "-") for x in supported)


def rank_profile(profile: dict, args) -> tuple[int, list[str]]:
    rejected = []
    if args.role not in profile.get("roles", []):
        rejected.append("role_mismatch")
    if not locale_matches(args.locale, profile.get("locales", [])):
        rejected.append("locale_mismatch")
    limit = profile.get("constraints", {}).get("max_title_chars")
    if limit is not None and args.role in {"title", "cover_title", "section_title", "warning"} and len(args.text) > limit:
        rejected.append(f"title_too_long:{len(args.text)}>{limit}")
    if args.renderer == "deterministic" and not profile.get("font_stack"):
        rejected.append("no_verified_font_stack")
    if rejected:
        return -1, rejected

    score = 0
    voices = profile.get("voices", [])
    score += 30 if args.voice in voices else 0
    score += 20 if profile.get("status") in {"verified", "tested"} else 0
    score += 5 if args.role == profile.get("roles", [None])[0] else 0
    seed = profile.get("seed_compatibility", {})
    score += 8 if args.seed and args.seed in seed.get("preferred", []) else 0
    score -= 20 if args.seed and args.seed in seed.get("avoid", []) else 0
    return score, []


def main():
    p = argparse.ArgumentParser(description="Resolve a FontDB semantic profile and deterministic font runs.")
    p.add_argument("--catalog", required=True, type=Path)
    p.add_argument("--sources", type=Path)
    p.add_argument("--text", required=True)
    p.add_argument("--locale", default="zh-Hant")
    p.add_argument("--role", required=True)
    p.add_argument("--voice", required=True)
    p.add_argument("--renderer", choices=["deterministic", "image_generation"], default="deterministic")
    p.add_argument("--seed")
    p.add_argument("--bind", action="append", default=[], type=parse_binding, metavar="FAMILY=PATH")
    p.add_argument("--fallback", action="append", default=[], type=parse_binding, metavar="FAMILY=PATH")
    args = p.parse_args()

    catalog = yaml.safe_load(args.catalog.read_text(encoding="utf-8"))
    sources = yaml.safe_load(args.sources.read_text(encoding="utf-8")) if args.sources else {"sources": []}
    bindings = dict(args.bind)
    ranked, rejected = [], []

    source_index = {}
    for source in sources.get("sources", []):
        keys = set(source.get("profile_families", []))
        keys.add(source.get("family", ""))
        keys.add(source.get("english_family", ""))
        for key in keys:
            if key:
                source_index[key] = source

    for profile in catalog.get("profiles", []):
        score, reasons = rank_profile(profile, args)
        if reasons:
            rejected.append({"profile_id": profile["id"], "reasons": reasons})
            continue

        coverage = None
        missing_binding = []
        if args.renderer == "deterministic":
            ordered = []
            for entry in profile.get("font_stack", []):
                family = entry["family"]
                if family in bindings:
                    path = bindings[family]
                    source = source_index.get(family)
                    if args.sources and not source:
                        rejected.append({"profile_id": profile["id"], "reasons": ["source_record_missing:" + family]})
                        missing_binding.append("__integrity_rejected__")
                        continue
                    if source:
                        digests = source.get("verified_file_sha256", {})
                        expected_sha = digests.get(path.name)
                        aliases = source.get("family_aliases", [])
                        check = verify_font(path, family, aliases, expected_sha, None)
                        if not check["integrity_pass"]:
                            rejected.append({"profile_id": profile["id"], "reasons": ["font_integrity_failed:" + family], "integrity": check})
                            missing_binding.append("__integrity_rejected__")
                            continue
                    ordered.append((family, path))
                else:
                    missing_binding.append(family)
            fallback_failed = False
            for family, path in args.fallback:
                source = source_index.get(family)
                if args.sources and not source:
                    rejected.append({"profile_id": profile["id"], "reasons": ["fallback_source_record_missing:" + family]})
                    fallback_failed = True
                    break
                if source:
                    expected_sha = source.get("verified_file_sha256", {}).get(path.name)
                    check = verify_font(path, family, source.get("family_aliases", []), expected_sha, None)
                    if not check["integrity_pass"]:
                        rejected.append({"profile_id": profile["id"], "reasons": ["fallback_integrity_failed:" + family], "integrity": check})
                        fallback_failed = True
                        break
                ordered.append((family, path))
            if fallback_failed:
                continue
            if missing_binding or not ordered:
                if "__integrity_rejected__" in missing_binding:
                    continue
                rejected.append({"profile_id": profile["id"], "reasons": ["unbound_font:" + x for x in missing_binding] or ["no_bound_font"]})
                continue
            coverage = resolve_glyphs(args.text, ordered)
            if not coverage["render_allowed"]:
                rejected.append({"profile_id": profile["id"], "reasons": ["missing_codepoints"], "missing_codepoints": coverage["missing_codepoints"]})
                continue
            score += 10
            score -= max(0, len(coverage["used_fonts"]) - 1)

        ranked.append({
            "profile_id": profile["id"],
            "score": score,
            "status": profile.get("status"),
            "archetype": profile.get("archetype"),
            "treatment": profile.get("treatment", {}),
            "prompt_constraints": profile.get("prompt_constraints", []),
            "coverage": coverage,
        })

    ranked.sort(key=lambda x: (-x["score"], x["profile_id"]))
    result = {
        "request": {"text": args.text, "locale": args.locale, "role": args.role, "voice": args.voice, "renderer": args.renderer, "seed": args.seed},
        "selected": ranked[0] if ranked else None,
        "candidates": ranked,
        "rejected": rejected,
        "render_allowed": bool(ranked),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if ranked else 2)


if __name__ == "__main__":
    main()
