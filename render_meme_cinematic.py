#!/usr/bin/env python3
"""Render the cinematic GTA VI key-art meme variant for gta6-meme-x-01.

Composites the generated Vice City scene with the official make.fun ghost
(cut out of its press-kit magenta disc, coin kept) and draws all caption
text with PIL so every word is spelled exactly.

Input : assets/scene-cinematic.png (generated scene, no text in it)
        assets/ghost.png (official press-kit mark: ghost on magenta disc)
Output: meme-cinematic.png (1024x1024)
"""

from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
SCENE = "assets/scene-cinematic.png"
GHOST = "assets/ghost.png"
OUT = "meme-cinematic.png"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (16, 8, 32, 255)
PINK = (255, 46, 136, 255)
WHITE = (255, 255, 255, 255)
INK = (12, 6, 24, 255)


def flood_fill(mask, seed):
    """Boolean array of the 4-connected True region containing seed."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    sy, sx = seed
    if not (0 <= sy < h and 0 <= sx < w) or not mask[sy, sx]:
        return seen
    queue = deque([(sy, sx)])
    seen[sy, sx] = True
    while queue:
        y, x = queue.popleft()
        if y > 0 and mask[y - 1, x] and not seen[y - 1, x]:
            seen[y - 1, x] = True
            queue.append((y - 1, x))
        if y < h - 1 and mask[y + 1, x] and not seen[y + 1, x]:
            seen[y + 1, x] = True
            queue.append((y + 1, x))
        if x > 0 and mask[y, x - 1] and not seen[y, x - 1]:
            seen[y, x - 1] = True
            queue.append((y, x - 1))
        if x < w - 1 and mask[y, x + 1] and not seen[y, x + 1]:
            seen[y, x + 1] = True
            queue.append((y, x + 1))
    return seen


def extract_ghost(path, size=512):
    """Cut the ghost (with its star coin) out of the press-kit disc.

    The disc magenta is the image's most common opaque colour. A flood fill
    from the disc's edge removes the disc only: the coin's magenta survives
    because its black ring seals it off from the disc. A second flood fill
    from the centre keeps just the ghost's connected component, which drops
    the disc's outer black ring.
    """
    g = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    arr = np.array(g).astype(np.int16)
    rgb = arr[..., :3]
    alpha = arr[..., 3] > 0

    opaque = rgb[alpha]
    colors, counts = np.unique(opaque.reshape(-1, 3), axis=0, return_counts=True)
    disc = colors[counts.argmax()].astype(np.int16)
    dist = np.abs(rgb - disc).max(axis=2)

    magenta = alpha & (dist <= 25)
    mid = size // 2
    seed = None
    for x in range(size):
        if magenta[mid, x]:
            seed = (mid, x)
            break
    disc_region = flood_fill(magenta, seed)
    arr[disc_region, 3] = 0

    # Defringe: drop near-magenta stragglers touching the removed disc.
    removed = disc_region
    adjacent = np.zeros_like(removed)
    adjacent[1:, :] |= removed[:-1, :]
    adjacent[:-1, :] |= removed[1:, :]
    adjacent[:, 1:] |= removed[:, :-1]
    adjacent[:, :-1] |= removed[:, 1:]
    near = alpha & (dist <= 70) & ~disc_region
    arr[near & adjacent, 3] = 0

    # Keep only the component holding the centre (the ghost itself).
    alpha2 = arr[..., 3] > 0
    ghost_comp = flood_fill(alpha2, (mid, mid))
    arr[alpha2 & ~ghost_comp, 3] = 0

    out = Image.fromarray(arr.astype(np.uint8), "RGBA")
    return out.crop(out.getbbox())


def centered(draw, text, cx, y, font, fill=WHITE, stroke=0):
    draw.text(
        (cx, y),
        text,
        font=font,
        anchor="ma",
        fill=fill,
        stroke_width=stroke,
        stroke_fill=INK,
    )


def main():
    scene = Image.open(SCENE).convert("RGB").resize((W, H), Image.LANCZOS)
    img = scene.convert("RGBA")

    # Soft top scrim so the caption reads over the busy sky.
    scrim = Image.new("L", (W, H), 0)
    sc = ImageDraw.Draw(scrim)
    for y in range(250):
        sc.line([(0, y), (W, y)], fill=int(80 * (1 - y / 250)))
    img.paste(Image.new("RGBA", (W, H), (10, 5, 25, 255)), (0, 0), scrim)

    # Ghost sitting on the car roof between the two characters.
    ghost = extract_ghost(GHOST)
    gh = 190
    gw = int(ghost.width * gh / ghost.height)
    ghost = ghost.resize((gw, gh), Image.LANCZOS)
    ghost_cx, ghost_base = 605, 606  # clear of the woman's hair on the right
    gx = ghost_cx - gw // 2
    gy = ghost_base - gh
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = ImageDraw.Draw(shadow)
    sh.ellipse(
        [ghost_cx - gw // 2, ghost_base - 12, ghost_cx + gw // 2, ghost_base + 12],
        fill=(0, 0, 0, 110),
    )
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(6)))
    img.paste(ghost, (gx, gy), ghost)

    draw = ImageDraw.Draw(img)

    # Bottom band.
    draw.rectangle([0, 896, W, H], fill=NAVY)
    draw.rectangle([0, 896, W, 900], fill=PINK)

    f_big = ImageFont.truetype(FONT_BOLD, 66)
    f_band = ImageFont.truetype(FONT_BOLD, 44)

    # Top caption, two lines.
    centered(draw, "WAITED 13 YEARS", W // 2, 44, f_big, stroke=3)
    centered(draw, "FOR THIS.", W // 2, 122, f_big, stroke=3)

    # Bottom band text.
    centered(draw, "MY AI AGENT PAID FOR THE RIDE", W // 2, 912, f_band)
    centered(draw, "— MAKE.FUN", W // 2, 962, f_band, fill=PINK)

    img.convert("RGB").save(OUT, optimize=True)
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
