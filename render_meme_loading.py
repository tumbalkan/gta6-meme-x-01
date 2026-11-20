#!/usr/bin/env python3
"""Render meme-loading.png: a GTA-style loading screen parody for the
make.fun gta6-meme-x-01 bounty (variant 3 of 3).

Pure PIL: sunset artwork strip with palm silhouettes and the official
make.fun ghost composited onto the beach, a TIP box in the classic GTA
loading-screen style, and a download bar stuck at 99%.

Output: meme-loading.png (1024x1024), readable when shrunk to 480x480.
"""

import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

NAVY = (11, 11, 22)
PANEL = (20, 20, 42)
MAGENTA = (233, 30, 99)
PINK = (255, 64, 129)
ORANGE = (255, 123, 46)
GOLD = (255, 205, 80)
WHITE = (255, 255, 255)
LIGHT = (235, 235, 245)
DIM = (170, 170, 190)
TRACK = (48, 48, 70)
SAND = (232, 197, 140)
SILHOUETTE = (26, 10, 38)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, box, top, bottom):
    x0, y0, x1, y1 = box
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        draw.line([(x0, y), (x1, y)], fill=lerp(top, bottom, (y - y0) / span))


def hgrad(draw, box, left, right):
    x0, y0, x1, y1 = box
    span = max(1, x1 - x0)
    for x in range(x0, x1):
        draw.line([(x, y0), (x, y1)], fill=lerp(left, right, (x - x0) / span))


def center(draw, cx, y, text, fnt, fill):
    box = draw.textbbox((0, 0), text, font=fnt)
    w = box[2] - box[0]
    draw.text((cx - w / 2 - box[0], y), text, font=fnt, fill=fill)


def palm(draw, x, y, s, color):
    """A palm silhouette rooted at (x, y); s scales it. Trunk curves
    gently; fronds are thick arcs fanning from the crown."""
    # Trunk: quadratic curve, drawn as thick segments.
    pts = []
    for i in range(13):
        t = i / 12
        px = x + (26 * s) * t * t
        py = y - (150 * s) * t
        pts.append((px, py))
    draw.line(pts, fill=color, width=max(3, int(13 * s)), joint="curve")
    cx, cy = pts[-1]
    # Fronds: arcs drooping from the crown.
    for ang in (-165, -125, -90, -55, -15, 20):
        r = 78 * s
        rad = math.radians(ang)
        ex = cx + r * math.cos(rad)
        ey = cy + r * math.sin(rad) * 0.55 + 34 * s
        mx = cx + (r * 0.55) * math.cos(rad)
        my = cy + (r * 0.55) * math.sin(rad) * 0.55 - 14 * s
        seg = []
        for i in range(9):
            t = i / 8
            qx = (1 - t) ** 2 * cx + 2 * (1 - t) * t * mx + t * t * ex
            qy = (1 - t) ** 2 * cy + 2 * (1 - t) * t * my + t * t * ey
            seg.append((qx, qy))
        draw.line(seg, fill=color, width=max(2, int(7 * s)), joint="curve")
    # Coconuts.
    draw.ellipse([cx - 7 * s, cy - 2 * s, cx + 3 * s, cy + 8 * s], fill=color)
    draw.ellipse([cx + 1 * s, cy + 1 * s, cx + 11 * s, cy + 11 * s], fill=color)


def extract_ghost(path):
    """Cut the make.fun ghost out of its magenta disc: flood-fill the
    connected disc magenta to transparent (the star coin survives — it
    is disconnected from the disc by the ghost's hand), defringe the
    edge, then crop to the ghost's own content box, which also drops
    the disc's dark outer ring."""
    from collections import deque

    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    disc = (196, 28, 131)

    def is_disc(x, y):
        r, g, b, a = px[x, y]
        return (a > 200
                and abs(r - disc[0]) + abs(g - disc[1]) + abs(b - disc[2]) <= 60)

    seen = set()
    queue = deque([(512, 120)])
    while queue:
        x, y = queue.popleft()
        if (x, y) in seen or not (0 <= x < w and 0 <= y < h):
            continue
        if not is_disc(x, y):
            continue
        seen.add((x, y))
        queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for x, y in seen:
        px[x, y] = (0, 0, 0, 0)

    # Defringe: one pass over pixels touching transparency that are
    # still dark-magenta edge blends. The coin is enclosed by the hand
    # and never touches transparency, so it is untouched.
    px = im.load()
    fringe = []
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 200:
                continue
            if not (80 <= r <= 210 and g < 70 and 60 <= b <= 170):
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] < 200:
                    fringe.append((x, y))
                    break
    for x, y in fringe:
        px[x, y] = (0, 0, 0, 0)

    # Drop the disc's dark outer ring: it sits at radius ~440-455 from
    # the centre while no ghost pixel reaches past ~310, so anything
    # beyond radius 380 is ring, never ghost.
    cx, cy = w // 2, h // 2
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 > 380 ** 2:
                px[x, y] = (0, 0, 0, 0)

    bbox = im.getbbox()
    return im.crop((bbox[0] - 6, bbox[1] - 6, bbox[2] + 6, bbox[3] + 6))


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # ---- Title zone ----
    center(d, W // 2, 42, "GRAND THEFT AUTO VI", font(62), WHITE)
    # Thin gold rule under the title.
    d.rectangle([W // 2 - 260, 128, W // 2 + 260, 132], fill=GOLD)
    center(d, W // 2, 146, "L O A D I N G . . .", font(26), MAGENTA)

    # ---- Sunset artwork strip ----
    ax0, ay0, ax1, ay1 = 48, 200, 976, 596
    horizon = 445
    sand_top = 505
    # Sky: magenta -> orange -> gold.
    vgrad(d, (ax0, ay0, ax1, horizon), (196, 26, 110), (255, 150, 60))
    vgrad(d, (ax0, horizon - 60, ax1, horizon), (255, 150, 60), (255, 214, 110))
    # Stars in the upper sky.
    stars = [(120, 235), (220, 260), (330, 228), (700, 240), (820, 262),
             (900, 232), (560, 252), (470, 232), (90, 300), (940, 305)]
    for sx, sy in stars:
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 240, 220))
    # Sun with synthwave slats.
    sun_cx, sun_cy, sun_r = 512, 405, 100
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
              fill=(255, 236, 170))
    for i, sy in enumerate(range(sun_cy + 6, sun_cy + sun_r, 15)):
        d.rectangle([sun_cx - sun_r, sy, sun_cx + sun_r, sy + 5 + i],
                    fill=(255, 150, 60))
    # Ocean.
    vgrad(d, (ax0, horizon, ax1, sand_top), (16, 120, 140), (10, 60, 90))
    for i in range(5):
        yy = horizon + 10 + i * 13
        wdt = 300 - i * 40
        d.line([(sun_cx - wdt // 2, yy), (sun_cx + wdt // 2, yy)],
               fill=(255, 200, 130), width=3)
    # Beach.
    vgrad(d, (ax0, sand_top, ax1, ay1), SAND, (206, 164, 105))
    # Palms: a tall one left, a shorter one right.
    palm(d, 150, sand_top + 42, 1.05, SILHOUETTE)
    palm(d, 852, sand_top + 48, 0.85, SILHOUETTE)
    # Frame the artwork.
    d.rectangle([ax0, ay0, ax1, ay1], outline=(255, 255, 255), width=3)

    # Ghost on the beach, standing on the sand next to the right palm —
    # the disc cut away, so it reads as a character in the scene.
    ghost = extract_ghost("assets/ghost.png")
    gh = 175
    gw = int(ghost.width * gh / ghost.height)
    ghost = ghost.resize((gw, gh), Image.LANCZOS)
    gx, gy = 668, ay1 - 8 - gh
    d.ellipse([gx + 18, ay1 - 14, gx + gw - 18, ay1 - 4], fill=(0, 0, 0))
    img.paste(ghost, (gx, gy), ghost)
    d = ImageDraw.Draw(img)

    # ---- TIP box (GTA loading-screen style) ----
    bx0, by0, bx1, by1 = 48, 624, 976, 762
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=PANEL,
                        outline=MAGENTA, width=3)
    d.text((bx0 + 26, by0 + 18), "TIP:", font=font(34), fill=MAGENTA)
    tip_lines = [
        "WHILE THIS DOWNLOADS, YOUR AI AGENT COULD BE",
        "WINNING REAL MONEY ON MAKE.FUN.",
    ]
    for i, line in enumerate(tip_lines):
        d.text((bx0 + 26, by0 + 62 + i * 34), line, font=font(26), fill=LIGHT)

    # ---- Loading bar ----
    bar_y = 842
    d.text((48, bar_y - 42), "DOWNLOADING GTA VI \u2014 214 GB",
           font=font(26), fill=WHITE)
    pct = "99%"
    pw = d.textbbox((0, 0), pct, font=font(30))[2]
    d.text((976 - pw, bar_y - 46), pct, font=font(30), fill=GOLD)
    d.rounded_rectangle([48, bar_y, 976, bar_y + 34], radius=17, fill=TRACK)
    fill_w = int((976 - 48) * 0.99)
    # Gradient fill, clipped to the rounded track via a mask.
    bar = Image.new("RGB", (W, H), (0, 0, 0))
    bd = ImageDraw.Draw(bar)
    hgrad(bd, (48, bar_y, 48 + fill_w, bar_y + 34), MAGENTA, PINK)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([48, bar_y, 48 + fill_w, bar_y + 34], radius=17,
                         fill=255)
    img.paste(Image.composite(bar, img, mask), (0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([48, bar_y, 976, bar_y + 34], radius=17,
                        outline=(255, 255, 255), width=2)

    # ---- Estimated time ----
    center(d, W // 2, 904, "ESTIMATED TIME REMAINING: 13 YEARS",
           font(26), GOLD)
    center(d, W // 2, 950, "VICE CITY AWAITS. YOUR AGENT IS ALREADY EARNING.",
           font(20), DIM)

    img.save("meme-loading.png", optimize=True)
    print("wrote meme-loading.png", img.size)


if __name__ == "__main__":
    main()
