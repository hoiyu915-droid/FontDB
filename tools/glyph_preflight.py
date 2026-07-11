#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from fontTools.ttLib import TTFont, TTCollection


def unicode_cmap(path: Path, font_number: int = 0) -> set[int]:
    suffix = path.suffix.lower()
    if suffix in {".ttc", ".otc"}:
        collection = TTCollection(str(path), lazy=True)
        font = collection.fonts[font_number]
    else:
        font = TTFont(str(path), fontNumber=font_number, lazy=True)
    points: set[int] = set()
    for table in font["cmap"].tables:
        if table.isUnicode():
            points.update(table.cmap)
    font.close()
    return points


def parse_font(value: str):
    if "=" not in value:
        raise argparse.ArgumentTypeError("font must be NAME=PATH")
    name, raw_path = value.split("=", 1)
    path = Path(raw_path)
    if not name or not path.is_file():
        raise argparse.ArgumentTypeError(f"invalid font entry: {value}")
    return name, path


def codepoint(ch: str) -> str:
    return f"U+{ord(ch):04X}"


def resolve(text: str, fonts: list[tuple[str, Path]]) -> dict:
    maps = [(name, unicode_cmap(path)) for name, path in fonts]
    chars = []
    missing = []
    runs = []

    for index, ch in enumerate(text):
        owner = None
        if ch.isspace():
            owner = "whitespace"
        else:
            for name, points in maps:
                if ord(ch) in points:
                    owner = name
                    break
        item = {"index": index, "char": ch, "codepoint": codepoint(ch), "font": owner}
        chars.append(item)
        if owner is None:
            missing.append({"char": ch, "codepoint": codepoint(ch)})

        run_owner = owner or "missing"
        if runs and runs[-1]["font"] == run_owner:
            runs[-1]["text"] += ch
            runs[-1]["end"] = index + 1
        else:
            runs.append({"font": run_owner, "text": ch, "start": index, "end": index + 1})

    unique_missing = list({x["codepoint"]: x for x in missing}.values())
    used = []
    for run in runs:
        if run["font"] not in {"whitespace", "missing"} and run["font"] not in used:
            used.append(run["font"])
    return {
        "text": text,
        "font_order": [name for name, _ in fonts],
        "used_fonts": used,
        "fallback_used": len(used) > 1,
        "render_allowed": not unique_missing,
        "missing_codepoints": unique_missing,
        "runs": runs,
        "characters": chars,
    }


def main():
    parser = argparse.ArgumentParser(description="Resolve each Unicode code point against an ordered font stack.")
    parser.add_argument("--text", required=True)
    parser.add_argument("--font", action="append", required=True, type=parse_font, metavar="NAME=PATH")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    result = resolve(args.text, args.font)
    print(json.dumps(result, ensure_ascii=False, indent=None if args.compact else 2))
    raise SystemExit(0 if result["render_allowed"] else 2)


if __name__ == "__main__":
    main()
