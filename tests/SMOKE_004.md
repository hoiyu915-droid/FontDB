# Smoke test 004 — Semantic profile resolver

Date: 2026-07-11

## Exact-primary test

Request:

```yaml
text: 親子課程：臺語𩵚也要正確顯示
locale: zh-Hant
role: title
voice: friendly
renderer: deterministic
```

Bindings:

- jf open 粉圓 → exact project font file
- 芫荽 Iansui → exact project font file
- Noto Sans TC → global fallback

Result:

- selected profile: `rounded_education`
- selected score: 64
- rejected profiles: 19
- fallback used: true
- U+29D5A (𩵚) resolved by Noto Sans TC
- all other text resolved by jf open 粉圓
- `render_allowed: true`

## Research-profile surrogate test

A second request with `role=title`, `voice=authoritative`, and a 17-character mixed string selected `knowledge_sans` and rejected profiles whose title limit was exceeded.

The local file bound under the Source Han Sans catalog key was Noto Sans TC, used only as a render surrogate because the exact Source Han release archive was not installed locally. This validates selection and run generation, not exact production-font identity.

## Resolver behavior now covered

- role rejection
- locale rejection
- title-length rejection
- deterministic-stack availability rejection
- voice and verification scoring
- ordered fallback coverage
- missing-codepoint rejection
- stable candidate ranking
- structured rejected reasons

## Remaining integrity gap

Runtime font bindings currently trust the caller-provided family key. A later integrity layer should validate the font name table and/or an approved SHA-256 digest so that an unrelated file cannot be mislabeled as a catalog family.
