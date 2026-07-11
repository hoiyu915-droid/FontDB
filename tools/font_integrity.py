#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path
from fontTools.ttLib import TTFont, TTCollection


NAME_IDS = {1: "family", 2: "subfamily", 4: "full_name", 6: "postscript", 16: "typographic_family", 17: "typographic_subfamily"}


def normalized(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"\b(?:version|ver)?\s*\d+(?:\.\d+)*\b", "", value)
    return re.sub(r"[^0-9a-z\u3400-\u9fff]+", "", value)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def open_font(path: Path, font_number: int):
    if path.suffix.lower() in {".ttc", ".otc"}:
        return TTCollection(str(path), lazy=True).fonts[font_number]
    return TTFont(str(path), fontNumber=font_number, lazy=True)


def inspect(path: Path, font_number: int = 0) -> dict:
    font = open_font(path, font_number)
    names = {label: set() for label in NAME_IDS.values()}
    for record in font["name"].names:
        label = NAME_IDS.get(record.nameID)
        if label:
            try:
                names[label].add(record.toUnicode())
            except Exception:
                pass
    weight = font["OS/2"].usWeightClass if "OS/2" in font else None
    font.close()
    return {"sha256": sha256(path), "weight_class": weight, "names": {k: sorted(v) for k, v in names.items() if v}}


def verify(path: Path, expected: str, aliases: list[str], expected_sha: str | None, expected_weight: int | None, font_number: int = 0) -> dict:
    meta = inspect(path, font_number)
    actual_names = {normalized(x) for values in meta["names"].values() for x in values}
    accepted = [expected, *aliases]
    accepted_names = {normalized(x) for x in accepted}
    name_match = bool(actual_names & accepted_names)
    sha_match = expected_sha is None or meta["sha256"].lower() == expected_sha.lower()
    weight_match = expected_weight is None or meta["weight_class"] == expected_weight
    errors = []
    if not name_match:
        errors.append("family_name_mismatch")
    if not sha_match:
        errors.append("sha256_mismatch")
    if not weight_match:
        errors.append("weight_class_mismatch")
    return {
        "file": str(path),
        "expected_family": expected,
        "accepted_aliases": aliases,
        "integrity_pass": not errors,
        "errors": errors,
        "checks": {"name_match": name_match, "sha256_match": sha_match, "weight_match": weight_match},
        "metadata": meta,
    }


def main():
    p = argparse.ArgumentParser(description="Verify that a runtime font file matches its claimed FontDB identity.")
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--expect", required=True)
    p.add_argument("--alias", action="append", default=[])
    p.add_argument("--sha256")
    p.add_argument("--weight", type=int)
    p.add_argument("--font-number", type=int, default=0)
    args = p.parse_args()
    result = verify(args.file, args.expect, args.alias, args.sha256, args.weight, args.font_number)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["integrity_pass"] else 3)


if __name__ == "__main__":
    main()
