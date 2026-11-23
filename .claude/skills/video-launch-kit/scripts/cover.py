"""Render one 16:9 (1280x720) thumbnail or 9:16 (1080x1920) vertical cover from a selected frame."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_font(font_path, size):
    if font_path:
        return ImageFont.truetype(font_path, size)
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def render_16_9(img, lines, side, font_path, focus, parser):
    canvas = Image.new("RGB", (1280, 720), "#202324")
    if lines:
        frame_w = 730
        x = 1280 - frame_w if side == "left" else 0
        panel_x = 36 if side == "left" else frame_w + 36
        art = ImageOps.fit(img, (frame_w, 720), centering=(focus, 0.5))
        canvas.paste(art, (x, 0))
        draw = ImageDraw.Draw(canvas)
        for size in range(98, 15, -2):
            face = load_font(font_path, size)
            bounds = [draw.textbbox((0, 0), line, font=face) for line in lines]
            if max(b[2] - b[0] for b in bounds) <= 478 and len(lines) * size * 1.2 <= 640:
                break
        else:
            parser.error("Shorten the hook")
        y = (720 - len(lines) * size * 1.2) / 2
        for line in lines:
            draw.text((panel_x, y), line, font=face, fill="#fff3df", anchor="lt")
            y += size * 1.2
    else:
        if img.width / img.height < 1.3:
            art = ImageOps.contain(img, (1280, 720))
            canvas.paste(art, ((1280 - art.width) // 2, (720 - art.height) // 2))
        else:
            canvas = ImageOps.fit(img, (1280, 720), centering=(focus, 0.5))
    return canvas


def render_9_16(img, lines, side, font_path, focus, parser):
    canvas = Image.new("RGB", (1080, 1920), "#202324")
    if lines:
        panel_h = 560
        frame_h = 1920 - panel_h
        is_top = side in ("top", "left")
        frame_y = panel_h if is_top else 0
        panel_y = 0 if is_top else frame_h
        art = ImageOps.fit(img, (1080, frame_h), centering=(focus, 0.5))
        canvas.paste(art, (0, frame_y))
        draw = ImageDraw.Draw(canvas)
        max_text_w = 960
        max_text_h = panel_h - 120
        for size in range(120, 20, -2):
            face = load_font(font_path, size)
            bounds = [draw.textbbox((0, 0), line, font=face) for line in lines]
            if max(b[2] - b[0] for b in bounds) <= max_text_w and len(lines) * size * 1.2 <= max_text_h:
                break
        else:
            parser.error("Shorten the hook")
        y = panel_y + (panel_h - len(lines) * size * 1.2) / 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=face)
            line_w = bbox[2] - bbox[0]
            draw.text(((1080 - line_w) / 2, y), line, font=face, fill="#fff3df", anchor="lt")
            y += size * 1.2
    else:
        canvas = ImageOps.fit(img, (1080, 1920), centering=(focus, 0.5))
    return canvas


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--ratio", choices=("16:9", "9:16"), default="16:9", help="Output aspect ratio")
    p.add_argument("--text", default="", help="Short hook; use | for a manual line break")
    p.add_argument("--side", choices=("left", "right", "top", "bottom"), default=None,
                   help="Text panel side (left/right for 16:9, top/bottom for 9:16)")
    p.add_argument("--font", help="Path to a bold TrueType font")
    p.add_argument("--focus", type=float, default=0.5, help="Crop center 0 to 1")
    a = p.parse_args()
    if not 0 <= a.focus <= 1:
        p.error("focus must be 0 to 1")
    if a.output.exists():
        p.error("Choose a new output filename")
    img = ImageOps.exif_transpose(Image.open(a.image)).convert("RGB")
    lines = a.text.split("|") if a.text else []
    if a.ratio == "9:16":
        side = a.side if a.side else "top"
        canvas = render_9_16(img, lines, side, a.font, a.focus, p)
    else:
        side = a.side if a.side in ("left", "right") else "left"
        canvas = render_16_9(img, lines, side, a.font, a.focus, p)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(a.output, format="JPEG", quality=91, optimize=True)


if __name__ == "__main__":
    main()
