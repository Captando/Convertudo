"""Conversor de imagens: Pillow (raster) + rawpy (câmera RAW)."""
import os
from pathlib import Path

RAW_EXTENSIONS = {"cr2", "nef", "arw", "dng", "raf", "orf", "rw2"}

PILLOW_FORMAT_MAP = {
    "jpg":  "JPEG",
    "jpeg": "JPEG",
    "png":  "PNG",
    "webp": "WEBP",
    "bmp":  "BMP",
    "gif":  "GIF",
    "tiff": "TIFF",
    "ico":  "ICO",
    "pdf":  "PDF",
}


def _raw_to_numpy(input_path: str):
    import rawpy
    with rawpy.imread(input_path) as raw:
        return raw.postprocess()


def convert(input_path: str, output_path: str, target_format: str) -> None:
    from PIL import Image

    target_format = target_format.lower()
    input_ext = Path(input_path).suffix.lstrip(".").lower()

    if input_ext in RAW_EXTENSIONS:
        import numpy as np
        rgb = _raw_to_numpy(input_path)
        img = Image.fromarray(rgb)
    else:
        img = Image.open(input_path)

    # Converter para RGB se necessário (PNG/GIF pode ter transparência)
    pil_format = PILLOW_FORMAT_MAP.get(target_format)
    if pil_format is None:
        raise ValueError(f"Formato de saída não suportado: {target_format}")

    if pil_format in ("JPEG", "BMP") and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    save_kwargs: dict = {}
    if pil_format == "JPEG":
        save_kwargs["quality"] = 95
    if pil_format == "PDF":
        if img.mode != "RGB":
            img = img.convert("RGB")

    img.save(output_path, format=pil_format, **save_kwargs)
