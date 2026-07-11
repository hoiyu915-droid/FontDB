# Smoke test 003 — Executable glyph preflight

Date: 2026-07-11

## Positive case

Input:

```text
VO₂max｜臺語𪜶𨑨迌𩵚鰡
```

Ordered stack:

1. Noto Sans TC
2. Iansui

Result:

- `render_allowed: true`
- `fallback_used: true`
- no missing code points
- Noto Sans TC resolved the common CJK, Latin, 𨑨, 迌, 𩵚, and 鰡
- Iansui resolved U+2082 (₂) and U+2A736 (𪜶)

## Negative case

Input: `繁體🫠`

Result:

- `render_allowed: false`
- exit code: 2
- missing: U+1FAE0

## Unexpected coverage finding

U+30EDE (𰻞, the complex biang character) was present in Iansui, so it could not serve as a negative test. This is direct evidence that coverage must be inspected rather than inferred from the apparent scope of a font.

## Contract

- exit 0: all non-whitespace code points resolve
- exit 2: unresolved code points remain
- JSON output contains ordered runs suitable for a renderer
- first matching font wins
- whitespace is preserved as a neutral run
