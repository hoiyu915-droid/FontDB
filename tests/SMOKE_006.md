# Smoke test 006 — Integrity-gated semantic resolver

Date: 2026-07-11

## Pipeline

1. semantic profile filtering and scoring
2. source-record lookup
3. runtime primary-font integrity verification
4. runtime fallback integrity verification
5. glyph preflight
6. render-run compilation

## Exact-stack case

Request selected `rounded_education`.

- primary: jf open 粉圓 2.1
- primary name and SHA-256: pass
- fallback: Noto Sans TC verified runtime file
- fallback name and SHA-256: pass
- U+29D5A resolved by fallback
- `render_allowed: true`

## Impostor case

The runtime bound `NotoSansTC.ttf` under the claim `Source Han Sans TC`.

Result:

- source record found for Source Han Sans TC
- internal family name did not match
- rejected reason: `font_integrity_failed:Source Han Sans TC`
- no profile selected
- `render_allowed: false`
- exit code: 2

The file never reached glyph preflight.

## Network note

The first local test attempt timed out fetching the public raw source registry. The same committed registry was then fetched through the GitHub connector and the test completed. This was transport failure, not resolver failure.
