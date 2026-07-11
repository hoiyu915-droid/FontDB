#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


VALID_MODES = {"off", "advisory", "enforce"}


def load_mode(config: Path | None) -> tuple[str, str]:
    env = os.getenv("FONTDB_MODE")
    if env:
        mode = env.strip().lower()
        source = "environment"
    elif config and config.is_file():
        data = yaml.safe_load(config.read_text(encoding="utf-8")) or {}
        raw_mode = data.get("mode", "off")
        mode = "off" if raw_mode is False else str(raw_mode).lower()
        source = str(config)
    else:
        mode, source = "off", "default"
    if mode not in VALID_MODES:
        raise ValueError(f"invalid FONTDB mode: {mode}")
    return mode, source


def disabled_payload(source: str) -> dict:
    return {
        "fontdb": {"enabled": False, "mode": "off", "mode_source": source},
        "render_allowed": True,
        "bypass": True,
        "selected": None,
        "warnings": ["fontdb_disabled_existing_renderer_unchanged"],
    }


def main():
    root = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(description="Stable feature-flagged FontDB entrypoint.")
    p.add_argument("--config", type=Path, default=root / "fontdb.config.yaml")
    p.add_argument("resolver_args", nargs=argparse.REMAINDER, help="Arguments passed to resolve_typography.py after --")
    args = p.parse_args()
    try:
        mode, source = load_mode(args.config)
    except ValueError as exc:
        print(json.dumps({"fontdb": {"enabled": False, "mode": "invalid"}, "render_allowed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        raise SystemExit(64)

    if mode == "off":
        print(json.dumps(disabled_payload(source), ensure_ascii=False, indent=2))
        return

    forwarded = args.resolver_args
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]
    resolver = Path(__file__).with_name("resolve_typography.py")
    proc = subprocess.run([sys.executable, str(resolver), *forwarded], text=True, capture_output=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"render_allowed": False, "error": "resolver_non_json_output", "stdout": proc.stdout, "stderr": proc.stderr}

    payload["fontdb"] = {"enabled": True, "mode": mode, "mode_source": source}
    if mode == "advisory":
        payload["advisory_would_block"] = not bool(payload.get("render_allowed"))
        payload["render_allowed"] = True
        payload.setdefault("warnings", []).append("fontdb_advisory_does_not_block_renderer")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(proc.returncode)


if __name__ == "__main__":
    main()
