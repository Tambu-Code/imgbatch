from PIL import Image, ImageDraw, ImageFont

POSITIONS = [
    "In basso a destra",
    "In basso a sinistra",
    "In alto a destra",
    "In alto a sinistra",
    "Centro",
]


def _load_font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _compute_xy(position, base_w, base_h, item_w, item_h):
    """Restituisce (x, y) dell'angolo in alto a sinistra dell'elemento."""
    margin = int(base_w * 0.02)

    if position == "In basso a destra":
        return base_w - item_w - margin, base_h - item_h - margin
    if position == "In basso a sinistra":
        return margin, base_h - item_h - margin
    if position == "In alto a destra":
        return base_w - item_w - margin, margin
    if position == "In alto a sinistra":
        return margin, margin
    return (base_w - item_w) // 2, (base_h - item_h) // 2  # Centro


def _finish(composed, original_mode):
    """Torna in RGB se l'originale non aveva trasparenza."""
    if original_mode in ("RGBA", "LA", "P"):
        return composed
    return composed.convert("RGB")


def add_text_watermark(img, text, position, opacity, size_percent):
    """Scrive un testo semi-trasparente sull'immagine e restituisce il risultato."""
    original_mode = img.mode
    base = img.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = max(10, int(base.height * size_percent / 100))
    font = _load_font(font_size)

    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_w = right - left
    text_h = bottom - top

    x, y = _compute_xy(position, base.width, base.height, text_w, text_h)
    x -= left
    y -= top

    alpha = int(255 * opacity / 100)
    shadow_offset = max(1, font_size // 20)

    draw.text((x + shadow_offset, y + shadow_offset), text,
              font=font, fill=(0, 0, 0, alpha))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))

    composed = Image.alpha_composite(base, overlay)
    return _finish(composed, original_mode)


def add_logo_watermark(img, logo_path, position, opacity, size_percent):
    """Applica un logo semi-trasparente sull'immagine e restituisce il risultato."""
    original_mode = img.mode
    base = img.convert("RGBA")

    with Image.open(logo_path) as logo_file:
        logo = logo_file.convert("RGBA")

    new_w = max(1, int(base.width * size_percent / 100))
    new_h = max(1, int(logo.height * new_w / logo.width))
    logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)

    alpha = logo.getchannel("A").point(lambda a: a * opacity // 100)
    logo.putalpha(alpha)

    x, y = _compute_xy(position, base.width, base.height, new_w, new_h)

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    overlay.paste(logo, (x, y))

    composed = Image.alpha_composite(base, overlay)
    return _finish(composed, original_mode)