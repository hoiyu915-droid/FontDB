# Smoke test 001 — Traditional Chinese rendering

Date: 2026-07-11  
Canvas: 1600 × 2000 PNG  
Renderer: Pillow/FreeType, deterministic text rendering  
Result image SHA-256: `fc725efc389743d55e9d14c415df9b625f4a3caaa94abb7a59030710538c3059`

## Fonts actually rendered

| Profile | Test font | Weight/recipe | Result |
|---|---|---:|---|
| knowledge_sans | Noto Sans TC | 700 static instance | pass |
| editorial_ming | Noto Serif TC | 600 static instance | pass |
| handwritten_note | Iansui Regular | native | pass for test string |
| rounded_education | jf open-huninn 2.1 | native | pass for test string |
| industrial_condensed | Noto Sans TC | 900, then scale-x 0.85 | provisional pass |

Noto Sans/Serif TC were used as locally obtainable render surrogates for the Source Han Sans/Serif profiles. This test therefore validates the semantic treatment and layout pipeline, not byte-identical production stacks.

## Test strings

- 研究證據不是裝飾，結論必須能被核查
- 今天先記下：缺字比難看更危險
- 知識要清楚，也可以保持親切
- 高負荷作業警示

## Findings

1. All four uncompressed profiles rendered the selected Traditional Chinese strings without tofu.
2. Iansui passing one string does not remove its documented incomplete-Big5 limitation.
3. Horizontal compression at 85% remains readable at large display size and is visibly distinct from 100%.
4. The 85% recipe is not a native condensed face and must remain labeled as a renderer treatment.
5. Small-size rasterization, long-title wrapping, punctuation stress, and a broader missing-glyph corpus remain untested.

## Renderer bug discovered

Calling Pillow `set_variation_by_axes()` on variable Noto fonts caused later static CJK rows to render blank in this environment. The stable workaround was to instantiate fixed weights with fontTools before passing fonts to Pillow.

## Gate decision

- knowledge_sans: smoke-pass, not yet `tested`
- editorial_ming: smoke-pass, not yet `tested`
- handwritten_note: smoke-pass-with-coverage-warning
- rounded_education: smoke-pass, not yet `tested`
- industrial_condensed: provisional-large-title-pass

Promotion to `tested` requires the full glyph and layout matrix.
