# See local smoke-test implementation pattern in tests/render_smoke_001.py.
# Matrix 002 adds:
# - cmap union across all Unicode cmap tables
# - per-codepoint missing-glyph reporting
# - character-based title wrapping
# - 100/88/85/82 percent horizontal compression comparison
#
# Canonical corpus additions that exposed failures:
MIXED = "VO₂max 52.4｜ΔLa 3.8 mmol/L｜95% CI［1.2, 4.6］"
TAIWAN_EXTENDED = "尪仔標楷注音ㄅㄆㄇㄈ臺語𪜶𨑨迌𩵚鰡"
