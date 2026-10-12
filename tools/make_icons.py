#!/usr/bin/env python3
"""Draw the fallback date-tile icons into public/ (needs Pillow; not run by the build).

The app redraws its icons with the real date on the device (dateIcon in src/slate.html and
the service worker), so these files are only the fallback. They are square and fully opaque
white on purpose: iOS rounds the corners itself and paints any transparent pixel black.
"""
import sys, datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PUBLIC = Path(__file__).resolve().parent.parent / "public"
BLUE = (0, 122, 255, 255)
EN = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]  # date.weekday(): Monday = 0
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-%s.ttc"


def font(weight, px):
    for path in (CJK % weight, "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if weight == "Bold" else "-ExtraLight")):
        try:
            return ImageFont.truetype(path, int(px))
        except OSError:
            continue
    return ImageFont.load_default()


def tile(size, d, round_corners=False, scale=4):
    S = size * scale
    im = Image.new("RGBA", (S, S), (255, 255, 255, 255) if not round_corners else (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    if round_corners:
        dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * .2237), fill=(255, 255, 255, 255))

    def centred(text, px, weight, baseline, spacing=0.0):
        f = font(weight, px)
        widths = [dr.textlength(ch, font=f) for ch in text]
        total = sum(widths) + spacing * px * (len(text) - 1)
        if total > S * (.7 if weight == "Bold" else .74):  # shrink long words to fit
            return centred(text, px * S * (.7 if weight == "Bold" else .74) / total, weight, baseline, spacing)
        x = (S - total) / 2
        for ch, w in zip(text, widths):
            dr.text((x, baseline), ch, font=f, fill=BLUE, anchor="ls")
            x += w + spacing * px
        return None

    centred(EN[d.weekday()], S * .165, "Bold", S * .285, .06)
    centred(str(d.day), S * .6, "Light", S * .805)
    return im.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.date.today()
    for name, size, rnd in [("apple-touch-icon.png", 180, False), ("icon-192.png", 192, False), ("icon-512.png", 512, False), ("favicon.png", 64, True)]:
        tile(size, d, rnd).save(PUBLIC / name)
    print("wrote icons for", d)
