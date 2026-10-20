from pathlib import Path
from PIL import Image

from core.watermark import add_text_watermark, add_logo_watermark

# nome mostrato nella GUI -> (formato Pillow, estensione). None = mantieni l'originale
FORMATS = {
    "Originale": None,
    "PNG": ("PNG", ".png"),
    "JPG": ("JPEG", ".jpg"),
    "WebP": ("WEBP", ".webp"),
}


def process_image(src, dst_dir, settings):
    """Ridimensiona, applica i watermark, converte e comprime un'immagine.
    Restituisce il percorso salvato."""
    s = settings
    src = Path(src)

    with Image.open(src) as img:
        original_format = img.format

        if s.keep_ratio:
            img.thumbnail((s.width, s.height))
            result = img
        else:
            result = img.resize((s.width, s.height))

        if s.logo_path:
            result = add_logo_watermark(
                result, s.logo_path, s.logo_position, s.wm_opacity, s.logo_size
            )

        if s.wm_text.strip():
            result = add_text_watermark(
                result, s.wm_text, s.wm_position, s.wm_opacity, s.wm_size
            )

        if FORMATS[s.fmt_name] is None:
            pil_format = original_format
            suffix = src.suffix
        else:
            pil_format, suffix = FORMATS[s.fmt_name]

        if pil_format == "JPEG" and result.mode in ("RGBA", "LA", "P"):
            result = result.convert("RGB")

        options = {}
        if pil_format in ("JPEG", "WEBP"):
            options["quality"] = s.quality
        elif pil_format == "PNG":
            options["optimize"] = True

        dst = Path(dst_dir) / (src.stem + suffix)
        result.save(dst, format=pil_format, **options)

    return dst