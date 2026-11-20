#!/usr/bin/env python3
"""Render the GTA WANTED-poster meme for make.fun bounty gta6-meme-x-01.

Variant 1 of 3 (WANTED poster). Everything is drawn programmatically with PIL:
all text is drawn by this script so every word is spelled exactly. The only
bitmap asset is the official make.fun press-kit ghost (assets/ghost.png),
which is the poster's fugitive mugshot — the subject, not a sticker.

Output: meme-wanted.png, 1024x1024, readable at a 480x480 downscale.
"""

import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "meme-wanted.png"
GHOST = "assets/ghost.png"

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_BOLD = FONT_DIR + "DejaVuSans-Bold.ttf"
F_REG = FONT_DIR + "DejaVuSans.ttf"

NAVY_TOP = (13, 18, 38)
NAVY_BOT = (24, 30, 58)
PANEL = (35, 43, 72)
PANEL_LINE = (58, 68, 104)
CREAM = (242, 232, 201)
GOLD = (245, 197, 66)
GOLD_DARK = (176, 132, 24)
WHITE = (255, 255, 255)
MAGENTA = (214, 51, 132)
SUNSET_TOP = (214, 51, 132)
SUNSET_MID = (255, 110, 71)
SUNSET_BOT = (255, 183, 77)
SILHOUETTE = (10, 14, 30)
SUN = (255, 214, 102)


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(size, top, bottom):
    """Vertical gradient image of the given size."""
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))


def hgrad(size, left, right):
    """Horizontal gradient image of the given size."""
    w, h = size
    base = Image.new("RGB", (w, 1))
    px = base.load()
    for x in range(w):
        t = x / max(w - 1, 1)
        px[x, 0] = tuple(round(left[i] + (right[i] - left[i]) * t) for i in range(3))
    return base.resize((w, h))


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def centered(draw, cx, y, text, fnt, fill, stroke_w=0, stroke_fill=None):
    x = cx - text_w(draw, text, fnt) / 2
    draw.text((x, y), text, font=fnt, fill=fill,
              stroke_width=stroke_w, stroke_fill=stroke_fill)
    return x


def spaced_centered(draw, cx, y, text, fnt, fill, spacing, stroke_w=0,
                    stroke_fill=None):
    """Draw text with extra letter spacing, centered on cx."""
    widths = [draw.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill,
                  stroke_width=stroke_w, stroke_fill=stroke_fill)
        x += wch + spacing


def star_points(cx, cy, r_out, r_in, rot=-90):
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_star(draw, cx, cy, r_out, fill, outline, width=3):
    pts = star_points(cx, cy, r_out, r_out * 0.45)
    draw.polygon(pts, fill=fill, outline=outline, width=width)


def draw_palm(draw, base_x, base_y, height, lean, flip=False):
    """Simple palm silhouette: curved trunk + drooping fronds."""
    s = -1 if flip else 1
    # Trunk: quadratic curve from base to crown.
    top_x = base_x + s * lean
    top_y = base_y - height
    pts = []
    for i in range(21):
        t = i / 20
        x = (1 - t) ** 2 * base_x + 2 * (1 - t) * t * (base_x + s * lean * 0.2) \
            + t * t * top_x
        y = (1 - t) ** 2 * base_y + 2 * (1 - t) * t * (base_y - height * 0.4) \
            + t * t * top_y
        pts.append((x, y))
    draw.line(pts, fill=SILHOUETTE, width=11, joint="curve")
    # Fronds: arcs fanning from the crown.
    for ang, length in ((-160, 78), (-130, 92), (-100, 98), (-70, 92),
                        (-40, 78), (-15, 60)):
        a = math.radians(ang if not flip else 180 - ang)
        ex = top_x + s * math.cos(a) * length
        ey = top_y + math.sin(a) * length * 0.55 + length * 0.45
        mx = top_x + s * math.cos(a) * length * 0.55
        my = top_y + math.sin(a) * length * 0.55 - length * 0.12
        fpts = []
        for i in range(16):
            t = i / 15
            x = (1 - t) ** 2 * top_x + 2 * (1 - t) * t * mx + t * t * ex
            y = (1 - t) ** 2 * top_y + 2 * (1 - t) * t * my + t * t * ey
            fpts.append((x, y))
        draw.line(fpts, fill=SILHOUETTE, width=7, joint="curve")
    # Coconuts.
    draw.ellipse([top_x - 9, top_y - 2, top_x + 3, top_y + 10],
                 fill=SILHOUETTE)
    draw.ellipse([top_x - 1, top_y + 2, top_x + 11, top_y + 14],
                 fill=SILHOUETTE)


def main():
    img = vgrad((W, H), NAVY_TOP, NAVY_BOT).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # --- Sunset strip at the bottom -------------------------------------
    strip_top = 884
    strip_h = H - strip_top
    # Smooth three-stop vertical gradient (magenta -> orange -> yellow),
    # built row by row so there are no visible band edges.
    strip = Image.new("RGB", (1, strip_h))
    spx = strip.load()
    for y in range(strip_h):
        t = y / max(strip_h - 1, 1)
        if t < 0.5:
            u = t / 0.5
            c = tuple(round(SUNSET_TOP[i] + (SUNSET_MID[i] - SUNSET_TOP[i]) * u)
                      for i in range(3))
        else:
            u = (t - 0.5) / 0.5
            c = tuple(round(SUNSET_MID[i] + (SUNSET_BOT[i] - SUNSET_MID[i]) * u)
                      for i in range(3))
        spx[0, y] = c
    strip = strip.resize((W, strip_h))
    img.paste(strip, (0, strip_top))
    draw = ImageDraw.Draw(img)

    # Sun, small and off to the right so it never sits behind the
    # centered bottom text.
    sun_cx, sun_cy, sun_r = 836, strip_top + 62, 44
    draw.ellipse([sun_cx - sun_r, sun_cy - sun_r,
                  sun_cx + sun_r, sun_cy + sun_r], fill=SUN)
    # Palms at both edges only — no third palm crowding the left.
    draw_palm(draw, 66, H - 6, 120, 26, flip=False)
    draw_palm(draw, 958, H - 6, 122, 30, flip=True)

    # --- Gold double-rule border -----------------------------------------
    draw.rectangle([14, 14, W - 15, H - 15], outline=GOLD, width=3)
    draw.rectangle([24, 24, W - 25, H - 25], outline=GOLD_DARK, width=1)

    # --- WANTED headline --------------------------------------------------
    f_wanted = font(F_BOLD, 148)
    spaced_centered(draw, W // 2, 30, "WANTED", f_wanted, CREAM, spacing=14,
                    stroke_w=2, stroke_fill=(0, 0, 0))
    f_sub = font(F_BOLD, 25)
    centered(draw, W // 2, 196, "LEONIDA POLICE DEPARTMENT  ·  VICE CITY",
             f_sub, GOLD)

    # --- Six gold stars ---------------------------------------------------
    star_y = 262
    star_r = 30
    gap = 78
    total_w = 6 * star_r * 2 + 5 * (gap - star_r * 2)
    x0 = W // 2 - total_w / 2 + star_r
    for i in range(6):
        draw_star(draw, x0 + i * gap, star_y, star_r, GOLD, GOLD_DARK, width=3)

    # --- Mugshot panel: height-chart backdrop ------------------------------
    px0, py0, px1, py1 = 172, 312, W - 172, 626
    draw.rounded_rectangle([px0, py0, px1, py1], radius=18, fill=PANEL,
                           outline=GOLD, width=3)
    # Height-chart lines + labels.
    f_mark = font(F_REG, 17)
    marks = [("6'6\"", 0.12), ("6'0\"", 0.36), ("5'6\"", 0.60),
             ("5'0\"", 0.84)]
    for label, frac in marks:
        ly = py0 + (py1 - py0) * frac
        draw.line([px0 + 14, ly, px1 - 14, ly], fill=PANEL_LINE, width=2)
        draw.text((px0 + 22, ly - 22), label, font=f_mark,
                  fill=(148, 158, 192))
    # Vertical center line, faint.
    draw.line([W // 2, py0 + 10, W // 2, py1 - 10], fill=PANEL_LINE, width=1)

    # Ghost mugshot, large and central.
    ghost = Image.open(GHOST).convert("RGBA")
    bbox = ghost.getbbox()
    ghost = ghost.crop(bbox)
    target_h = 288
    scale = target_h / ghost.height
    ghost = ghost.resize((round(ghost.width * scale), target_h),
                         Image.LANCZOS)
    gx = W // 2 - ghost.width // 2
    gy = py0 + (py1 - py0 - ghost.height) // 2 + 4
    img.paste(ghost, (gx, gy), ghost)
    draw = ImageDraw.Draw(img)
    # "MUGSHOT" tag under the panel's top edge.
    f_tag = font(F_BOLD, 20)
    centered(draw, W // 2, py1 + 10, "MUGSHOT No. VI-2013", f_tag,
             (148, 158, 192))

    # --- Charges block ------------------------------------------------------
    f_charge = font(F_BOLD, 33)
    f_detail = font(F_BOLD, 30)
    f_reward = font(F_BOLD, 36)
    cy = 668
    centered(draw, W // 2, cy, "CHARGES: MAKING AGENTS RICH", f_charge, CREAM)
    centered(draw, W // 2, cy + 42, "WHILE YOU WAITED 13 YEARS", f_charge,
             CREAM)
    centered(draw, W // 2, cy + 96, "LAST SEEN: VICE CITY, 2026", f_detail,
             WHITE)
    centered(draw, W // 2, cy + 138, "REWARD: $250 — PAID BY MAKE.FUN",
             f_reward, GOLD)

    # --- Bottom line, over the sunset strip --------------------------------
    f_bottom = font(F_BOLD, 27)
    centered(draw, W // 2, 918, "IF SEEN, DO NOT APPROACH.", f_bottom,
             WHITE, stroke_w=2, stroke_fill=SILHOUETTE)
    centered(draw, W // 2, 952, "JOIN HIM AT MAKE.FUN", f_bottom,
             WHITE, stroke_w=2, stroke_fill=SILHOUETTE)

    img.convert("RGB").save(OUT, quality=95)
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
