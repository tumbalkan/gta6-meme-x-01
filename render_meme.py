#!/usr/bin/env python3
"""Render the LEONIDA AIRLINES boarding-pass meme for make.fun's
gta6-meme-x-01 bounty (Post a GTA 6 meme on X).

Draws the whole meme programmatically with PIL: a fake boarding pass for a
flight that was delayed 13 years, with make.fun's ghost as the gate agent.
Output: meme.png, 1024x1024, readable when shrunk to 480x480.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024

LIB_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
LIB_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
LIB_MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (26, 26, 46)
GRAY = (107, 114, 128)
LIGHT_GRAY = (213, 216, 222)
MAGENTA = (194, 24, 123)
MAGENTA_DARK = (155, 18, 98)
PURPLE = (106, 27, 154)
RED = (211, 47, 47)
WHITE = (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(size, stops):
    """stops: list of (position 0..1, rgb). Returns an RGB image."""
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(size[1]):
        t = y / (size[1] - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                c = lerp(c0, c1, (t - p0) / (p1 - p0) if p1 > p0 else 0)
                break
        else:
            c = stops[-1][1]
        for x in range(size[0]):
            px[x, y] = c
    return img


def tracked(draw, xy, text, fnt, fill, tracking=2, anchor="la"):
    """Draw text with extra space between letters."""
    x, y = xy
    if anchor == "ra":
        total = sum(draw.textlength(ch, font=fnt) + tracking for ch in text) - tracking
        x -= total
    elif anchor == "ma":
        total = sum(draw.textlength(ch, font=fnt) + tracking for ch in text) - tracking
        x -= total / 2
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="la")
        x += draw.textlength(ch, font=fnt) + tracking


def dashed_hline(draw, x0, x1, y, fill, dash=14, gap=10, width=3):
    x = x0
    while x < x1:
        draw.line([(x, y), (min(x + dash, x1), y)], fill=fill, width=width)
        x += dash + gap


def draw_barcode(draw, x0, y0, x1, y1, seed=2013):
    rng = random.Random(seed)
    x = x0
    while x < x1 - 2:
        w = rng.choice([2, 3, 4, 6])
        if rng.random() < 0.62:
            draw.rectangle([x, y0, x + w - 1, y1], fill=(20, 20, 20))
        x += w + rng.choice([2, 3, 4])


def make_stamp(text, subtext, size=(430, 130)):
    """A rotated rubber stamp: red double border, bold text."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([4, 4, size[0] - 5, size[1] - 5], radius=12,
                        outline=RED + (230,), width=6)
    d.rounded_rectangle([14, 14, size[0] - 15, size[1] - 15], radius=8,
                        outline=RED + (230,), width=2)
    d.text((size[0] / 2, 22), text, font=font(LIB_BOLD, 46),
           fill=RED + (235,), anchor="ma")
    d.text((size[0] / 2, 78), subtext, font=font(LIB_BOLD, 24),
           fill=RED + (235,), anchor="ma")
    return layer.rotate(-11, expand=True, resample=Image.BICUBIC)


def main():
    # --- sunset background: deep purple -> magenta -> orange ---
    bg = vertical_gradient((W, H), [
        (0.00, (36, 16, 64)),
        (0.45, (150, 30, 120)),
        (0.75, (230, 80, 90)),
        (1.00, (245, 124, 58)),
    ])
    img = bg.convert("RGBA")
    draw = ImageDraw.Draw(img)

    # --- card shadow + white card ---
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([40, 52, 984, 992], radius=30, fill=(0, 0, 0, 90))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(16)))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([40, 40, 984, 984], radius=30, fill=WHITE + (255,))

    # --- header band: magenta -> purple gradient, rounded top corners ---
    header = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(header)
    for x in range(40, 985):
        t = (x - 40) / 944
        hd.line([(x, 40), (x, 175)], fill=lerp(MAGENTA, PURPLE, t) + (255,))
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([40, 40, 984, 175], fill=255)
    # Cut only the corner triangles outside the card's rounded arcs:
    # each is the corner square minus the quarter-disc of the arc.
    import math
    for cx, cy, a0, a1 in ((70, 70, 180, 270), (954, 70, 270, 360)):
        corner_pt = (cx - 30, cy - 30) if a0 == 180 else (cx + 30, cy - 30)
        pts = [corner_pt]
        for deg in range(a0, a1 + 1, 2):
            rad = math.radians(deg)
            pts.append((cx + 30 * math.cos(rad), cy + 30 * math.sin(rad)))
        md.polygon(pts, fill=0)
    img = Image.alpha_composite(img, Image.composite(header,
                                                     Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                                                     mask))
    draw = ImageDraw.Draw(img)
    draw.text((80, 58), "LEONIDA AIRLINES", font=font(LIB_BOLD, 52),
              fill=WHITE, anchor="la")
    tracked(draw, (80, 126), "BOARDING PASS  \u00b7  GRAND THEFT AUTO VI",
            font(LIB_REG, 25), (255, 220, 240), tracking=2)
    draw.text((944, 42), "VI", font=font(LIB_BOLD, 110),
              fill=(255, 255, 255, 70), anchor="ra")

    # --- route: LOS SANTOS 2013 -> VICE CITY 2026 ---
    draw.text((80, 215), "LOS SANTOS", font=font(LIB_BOLD, 56), fill=NAVY)
    draw.text((80, 282), "DEPARTED 2013", font=font(LIB_BOLD, 26), fill=MAGENTA)
    draw.text((944, 215), "VICE CITY", font=font(LIB_BOLD, 56), fill=NAVY, anchor="ra")
    draw.text((944, 282), "ARRIVING 2026", font=font(LIB_BOLD, 26), fill=MAGENTA, anchor="ra")
    # dashed flight path with a plane between the cities
    dashed_hline(draw, 470, 560, 252, MAGENTA, dash=10, gap=8, width=4)
    draw.text((512, 222), "\u2708", font=font(DEJAVU, 46), fill=MAGENTA, anchor="ma")
    dashed_hline(draw, 560, 600, 252, MAGENTA, dash=10, gap=8, width=4)

    dashed_hline(draw, 80, 944, 348, LIGHT_GRAY, dash=12, gap=9, width=3)

    # --- fields ---
    def field(x, y, label, value, vsize=36):
        tracked(draw, (x, y), label, font(LIB_REG, 21), GRAY, tracking=3)
        draw.text((x, y + 26), value, font=font(LIB_BOLD, vsize), fill=NAVY)

    field(80, 372, "PASSENGER", "ONE PATIENT GAMER", 38)
    field(80, 462, "FLIGHT", "VI-2013")
    field(360, 462, "GATE", "VI")
    field(520, 462, "SEAT", "13A")
    field(80, 552, "DATE", "19 NOV 2026")
    field(360, 552, "BAGGAGE", "214 GB")

    # --- DELAYED stamp, overlapping the right of the fields ---
    stamp = make_stamp("DELAYED", "13 YEARS")
    img.paste(stamp, (575, 492), stamp)
    draw = ImageDraw.Draw(img)

    # --- fare band ---
    draw.rounded_rectangle([80, 668, 944, 738], radius=16, fill=MAGENTA)
    draw.text((512, 684), "FARE: PAID IN FULL BY MY AI AGENT ON MAKE.FUN",
              font=font(LIB_BOLD, 29), fill=WHITE, anchor="ma")

    # --- gate agent box with the make.fun ghost ---
    draw.rounded_rectangle([80, 762, 500, 868], radius=16,
                           outline=MAGENTA, width=3, fill=(250, 243, 248, 255))
    ghost = Image.open(os.path.join(HERE, "assets", "ghost.png")).convert("RGBA")
    ghost = ghost.resize((92, 92), Image.LANCZOS)
    img.paste(ghost, (98, 774), ghost)
    draw = ImageDraw.Draw(img)
    tracked(draw, (206, 776), "GATE AGENT", font(LIB_REG, 20), GRAY, tracking=3)
    draw.text((206, 800), "make.fun", font=font(LIB_BOLD, 36), fill=NAVY)
    draw.text((206, 838), "ON DUTY SINCE 2013", font=font(LIB_REG, 19), fill=GRAY)

    # --- punchline, right of the gate agent box ---
    draw.text((944, 770), "BOARDING NOW.", font=font(LIB_BOLD, 44),
              fill=MAGENTA, anchor="ra")
    draw.text((944, 822), "FINALLY.", font=font(LIB_BOLD, 44),
              fill=NAVY, anchor="ra")

    # --- perforation + stub ---
    # Sample the real background beside the card (shadow included) so the
    # notches blend invisibly.
    notch_color = img.getpixel((20, 895))
    dashed_hline(draw, 40, 984, 895, (150, 150, 160), dash=12, gap=9, width=3)
    draw.ellipse([24, 879, 56, 911], fill=notch_color)
    draw.ellipse([968, 879, 1000, 911], fill=notch_color)
    draw_barcode(draw, 362, 912, 662, 952)
    draw.text((512, 956), "VI-2013-2026", font=font(LIB_MONO, 17),
              fill=NAVY, anchor="ma")

    out = os.path.join(HERE, "meme.png")
    img.convert("RGB").save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
