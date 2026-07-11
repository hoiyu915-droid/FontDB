import hashlib
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).parent
TOOLS = ROOT.parent / "tools" if (ROOT.parent / "tools").is_dir() else ROOT
sys.path.insert(0, str(TOOLS))

from font_integrity import normalized, verify
from glyph_preflight import resolve
from resolve_typography import locale_matches, rank_profile
from fontdb_entry import disabled_payload, load_mode


def make_font(path: Path, family: str, chars: str, weight: int = 400):
    units = 1000
    fb = FontBuilder(units, isTTF=True)
    glyph_order = [".notdef"] + [f"uni{ord(ch):04X}" for ch in chars]
    fb.setupGlyphOrder(glyph_order)
    cmap = {ord(ch): f"uni{ord(ch):04X}" for ch in chars}
    fb.setupCharacterMap(cmap)
    glyphs = {}
    metrics = {}
    for name in glyph_order:
        pen = TTGlyphPen(None)
        if name != ".notdef":
            pen.moveTo((100, 100)); pen.lineTo((500, 100)); pen.lineTo((500, 700)); pen.lineTo((100, 700)); pen.closePath()
        glyphs[name] = pen.glyph()
        metrics[name] = (600, 0)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": family, "styleName": "Regular", "uniqueFontIdentifier": family + " Regular", "fullName": family + " Regular", "psName": family.replace(" ", "") + "-Regular"})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200, usWeightClass=weight)
    fb.setupPost()
    fb.setupMaxp()
    fb.save(path)


class FontDBTests(unittest.TestCase):
    def test_normalized_aliases(self):
        self.assertEqual(normalized("jf open 粉圓 2.1"), normalized("jf-open 粉圓"))

    def test_integrity_pass_and_impostor_fail(self):
        with tempfile.TemporaryDirectory() as raw:
            exact = Path(raw) / "exact.ttf"
            make_font(exact, "Exact Family", "AB", 700)
            digest = hashlib.sha256(exact.read_bytes()).hexdigest()
            ok = verify(exact, "Exact Family", [], digest, 700)
            self.assertTrue(ok["integrity_pass"])
            bad = verify(exact, "Different Family", [], None, 700)
            self.assertFalse(bad["integrity_pass"])
            self.assertIn("family_name_mismatch", bad["errors"])

    def test_ordered_fallback_and_missing(self):
        with tempfile.TemporaryDirectory() as raw:
            primary = Path(raw) / "primary.ttf"
            fallback = Path(raw) / "fallback.ttf"
            make_font(primary, "Primary", "AB")
            make_font(fallback, "Fallback", "₂")
            ok = resolve("AB₂", [("Primary", primary), ("Fallback", fallback)])
            self.assertTrue(ok["render_allowed"])
            self.assertTrue(ok["fallback_used"])
            self.assertEqual([r["font"] for r in ok["runs"]], ["Primary", "Fallback"])
            bad = resolve("AB🫠", [("Primary", primary), ("Fallback", fallback)])
            self.assertFalse(bad["render_allowed"])
            self.assertEqual(bad["missing_codepoints"][0]["codepoint"], "U+1FAE0")

    def test_locale_and_semantic_rejection(self):
        self.assertTrue(locale_matches("zh-Hant-TW", ["zh-Hant"]))
        profile = {"roles": ["title"], "locales": ["zh-Hant"], "voices": ["friendly"], "status": "verified", "constraints": {"max_title_chars": 4}, "font_stack": [{"family": "X"}]}
        args = type("Args", (), {"role": "title", "locale": "zh-Hant", "voice": "friendly", "text": "12345", "renderer": "deterministic", "seed": None})()
        score, reasons = rank_profile(profile, args)
        self.assertEqual(score, -1)
        self.assertIn("title_too_long:5>4", reasons)

    def test_feature_flag_off_and_environment_override(self):
        with tempfile.TemporaryDirectory() as raw:
            config = Path(raw) / "fontdb.config.yaml"
            config.write_text('mode: "off"\n', encoding="utf-8")
            with patch.dict("os.environ", {}, clear=True):
                mode, _ = load_mode(config)
                self.assertEqual(mode, "off")
                self.assertTrue(disabled_payload("test")["bypass"])
            with patch.dict("os.environ", {"FONTDB_MODE": "advisory"}, clear=True):
                mode, source = load_mode(config)
                self.assertEqual((mode, source), ("advisory", "environment"))


if __name__ == "__main__":
    unittest.main()
