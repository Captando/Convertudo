"""Conversor de HEIC, HEIF e AVIF via pillow-heif + Pillow."""
from pathlib import Path

PILLOW_FORMAT_MAP = {
    "jpg": "JPEG", "jpeg": "JPEG",
    "png": "PNG", "webp": "WEBP", "tiff": "TIFF",
}


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        raise RuntimeError("Instale: pip install pillow-heif")

    from PIL import Image

    target_format = target_format.lower()
    pil_format = PILLOW_FORMAT_MAP.get(target_format)
    if pil_format is None:
        raise ValueError(f"Formato de saída não suportado: {target_format}")

    img = Image.open(input_path)

    if pil_format in ("JPEG",) and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    save_kwargs: dict = {}
    if pil_format == "JPEG":
        save_kwargs["quality"] = 95

    img.save(output_path, format=pil_format, **save_kwargs)
