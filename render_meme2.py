#!/usr/bin/env python3
"""Render the round-2 GTA 6 meme for make.fun bounty gta6-meme-x-01.

Two-panel illustrated comic, 1024x1024:
  panel 1 (2013, excited gamer) / "13 YEARS LATER..." band /
  panel 2 (2026, bearded gamer + make.fun ghost) / punchline band.
All text is drawn here with PIL so every word is spelled exactly.
Panel art: assets/panel1.png, assets/panel2.png (generated illustration, no text).
Ghost: assets/ghost.png (official make.fun press-kit mark).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE / "meme.png"

W, H = 1024, 1024
PANEL_H = 400
BAND_H = 80
CAPTION_H = H - 2 * PANEL_H - BAND_H  # 144

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (16, 24, 40)
MAGENTA = (200, 20, 90)
PINK = (233, 30, 99)
WHITE = (255, 255, 255)
DARK = (20, 20, 28)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD, size)


def crop_to_fill(img: Image.Image, target_w: int, target_h: int, focus: float) -> Image.Image:
    """Center-crop img to the target aspect ratio. focus 0.0 keeps the top,
    0.5 the vertical middle, 1.0 the bottom; then resize to the target size."""
    iw, ih = img.size
    target_ratio = target_w / target_h
    if iw / ih > target_ratio:
        new_w = int(ih * target_ratio)
        x0 = int((iw - new_w) * 0.5)
        box = (x0, 0, x0 + new_w, ih)
    else:
        new_h = int(iw / target_ratio)
        y0 = int((ih - new_h) * focus)
        box = (0, y0, iw, y0 + new_h)
    return img.crop(box).resize((target_w, target_h), Image.LANCZOS)


def draw_tag(draw: ImageDraw.ImageDraw, x: int, y: int, text: str) -> None:
    """Small dark year tag with white bold text."""
    f = font(30)
    tw = draw.textlength(text, font=f)
    pad_x, pad_y = 16, 8
    draw.rounded_rectangle(
        [x, y, x + tw + 2 * pad_x, y + 30 + 2 * pad_y],
        radius=10, fill=NAVY,
    )
    draw.text((x + pad_x, y + pad_y - 2), text, font=f, fill=WHITE)


def draw_banner(draw: ImageDraw.ImageDraw, cx: int, y: int, text: str) -> None:
    """White rounded banner with dark bold text, centred on cx."""
    f = font(40)
    tw = draw.textlength(text, font=f)
    pad_x, pad_y = 26, 12
    box = [cx - tw / 2 - pad_x, y, cx + tw / 2 + pad_x, y + 40 + 2 * pad_y]
    draw.rounded_rectangle(box, radius=14, fill=WHITE, outline=MAGENTA, width=4)
    draw.text((cx - tw / 2, y + pad_y - 2), text, font=f, fill=NAVY)


def main() -> None:
    canvas = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(canvas)

    # --- Panel 1: 2013, excited gamer (keep the top: raised fists + face). ---
    p1 = Image.open(ASSETS / "panel1.png").convert("RGB")
    p1 = crop_to_fill(p1, W, PANEL_H, focus=0.12)
    canvas.paste(p1, (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw_tag(draw, 18, 18, "2013")
    draw_banner(draw, W // 2, PANEL_H - 78, "GTA 6 IS COMING!")

    # --- Middle band: the intertitle. ---
    band_y = PANEL_H
    draw.rectangle([0, band_y, W, band_y + BAND_H], fill=NAVY)
    draw.rectangle([0, band_y, W, band_y + 4], fill=MAGENTA)
    draw.rectangle([0, band_y + BAND_H - 4, W, band_y + BAND_H], fill=MAGENTA)
    f_band = font(56)
    text = "13 YEARS LATER..."
    tw = draw.textlength(text, font=f_band)
    draw.text(((W - tw) / 2, band_y + (BAND_H - 56) / 2 - 4),
              text, font=f_band, fill=WHITE)

    # --- Panel 2: 2026, bearded gamer (mid-low focus: beard + desk). ---
    p2_top = PANEL_H + BAND_H
    p2 = Image.open(ASSETS / "panel2.png").convert("RGB")
    p2 = crop_to_fill(p2, W, PANEL_H, focus=0.35)
    canvas.paste(p2, (0, p2_top))
    draw = ImageDraw.Draw(canvas)
    draw_tag(draw, 18, p2_top + 18, "2026")

    # Ghost: official mark, floating beside the gamer at the desk, right side.
    # Sized generously so it stays recognisable at the 480px judge view.
    ghost = Image.open(ASSETS / "ghost.png").convert("RGBA")
    gh = 182
    gw = int(ghost.width * gh / ghost.height)
    ghost = ghost.resize((gw, gh), Image.LANCZOS)
    gx = W - gw - 26
    gy = p2_top + PANEL_H - gh + 2
    canvas.paste(ghost, (gx, gy), ghost)
    draw = ImageDraw.Draw(canvas)

    # --- Bottom punchline band. ---
    cap_y = 2 * PANEL_H + BAND_H
    draw.rectangle([0, cap_y, W, H], fill=MAGENTA)
    lines = ["MY AI AGENT MADE $250", "ON MAKE.FUN WHILE I WAITED"]
    f_cap = font(44)
    line_h = 56
    total = line_h * len(lines)
    y = cap_y + (CAPTION_H - total) / 2
    for line in lines:
        tw = draw.textlength(line, font=f_cap)
        draw.text(((W - tw) / 2, y), line, font=f_cap, fill=WHITE)
        y += line_h

    canvas.save(OUT, "PNG")
    print(f"wrote {OUT} {canvas.size}")


if __name__ == "__main__":
    main()
