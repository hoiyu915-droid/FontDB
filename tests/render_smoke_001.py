from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Minimal reproducible renderer. Font binaries are intentionally not vendored.
# Expected local files:
# NotoSansTC-700.ttf, NotoSansTC-900.ttf, NotoSerifTC-600.ttf,
# Iansui-Regular.ttf, jf-openhuninn-2.1.ttf

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "font_test_assets"
OUT = ROOT / "test-output" / "fontdb_smoke_zh_hant.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

rows = [
    ("knowledge_sans", "NotoSansTC-700.ttf", "研究證據不是裝飾，結論必須能被核查"),
    ("editorial_ming", "NotoSerifTC-600.ttf", "研究證據不是裝飾，結論必須能被核查"),
    ("handwritten_note", "Iansui-Regular.ttf", "今天先記下：缺字比難看更危險"),
    ("rounded_education", "jf-openhuninn-2.1.ttf", "知識要清楚，也可以保持親切"),
]

im = Image.new("RGB", (1600, 1700), "#F5F0E6")
d = ImageDraw.Draw(im)
y = 80
for profile, filename, sample in rows:
    font = ImageFont.truetype(str(FONTS / filename), 66)
    d.text((90, y), profile, font=font, fill="#B65D45")
    d.text((90, y + 90), sample, font=font, fill="#182126")
    y += 330

heavy = ImageFont.truetype(str(FONTS / "NotoSansTC-900.ttf"), 86)
text = "高負荷作業警示"
box = heavy.getbbox(text)
layer = Image.new("RGBA", (box[2] - box[0] + 30, box[3] - box[1] + 30))
ImageDraw.Draw(layer).text((15 - box[0], 15 - box[1]), text, font=heavy, fill="#182126")
compressed = layer.resize((round(layer.width * 0.85), layer.height), Image.Resampling.LANCZOS)
im.paste(compressed, (90, y), compressed)
im.save(OUT, optimize=True)
print(OUT)
