# Smoke test 002 — Layout, glyph, and compression matrix

Date: 2026-07-11  
Output SHA-256: `f242f9e3ff12990a042768d6d5efe0f142b2e6bd4c50e2e4e18b38f469da8e2b`

## Test scope

- two-line Traditional Chinese title wrapping
- scientific Latin, Greek, subscript, numerals, brackets, and units
- a mixed Taiwan-oriented glyph corpus
- industrial display compression at 100%, 88%, 85%, and 82%

## Glyph results

| Profile/test font | Missing code points | Interpretation |
|---|---|---|
| knowledge_sans / Noto Sans TC | U+2082, U+2A736 | missing subscript two and 𪜶 |
| editorial_ming / Noto Serif TC | U+2082, U+2A736 | same limitation |
| handwritten_note / Iansui | U+29D5A | missing 𩵚 |
| rounded_education / jf open-huninn 2.1 | U+29D5A | missing 𩵚 |

These findings apply to the exact files rendered. Noto TC files are render surrogates, not byte-identical Source Han production files.

## Layout findings

- All four profiles wrapped the long Traditional Chinese title cleanly at the tested width.
- Latin/number spacing in Iansui and Huninn is visibly looser and more informal than the research profiles.
- A locale declaration alone cannot guarantee scientific notation coverage.
- Missing glyphs must be detected before rendering; fallback cannot be inferred from font category.

## Compression findings

- 88%: conservative; close to normal heavy sans.
- 85%: best provisional balance for display titles.
- 82%: still legible at large size but visibly compressed; reject as a general default.
- No compression result authorizes the label “native condensed font.”

## Gate decision

- retain `industrial_condensed.scale_x: 0.85`
- permitted provisional range: 0.85–0.88
- move 0.82 outside the default permitted range
- add mandatory per-string glyph preflight
- require explicit Latin/symbol fallback for scientific notation
- do not promote any profile to `tested` yet
