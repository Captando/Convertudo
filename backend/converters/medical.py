"""Conversor de imagens médicas DICOM → PNG/JPG/TIFF via pydicom + Pillow."""
from pathlib import Path
import numpy as np


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import pydicom
    except ImportError:
        raise RuntimeError("Instale: pip install pydicom")

    from PIL import Image

    target_format = target_format.lower()

    ds = pydicom.dcmread(input_path)
    pixel_array = ds.pixel_array

    # Normalizar para 8-bit
    pmin, pmax = pixel_array.min(), pixel_array.max()
    if pmax > pmin:
        normalized = ((pixel_array - pmin) / (pmax - pmin) * 255).astype(np.uint8)
    else:
        normalized = np.zeros_like(pixel_array, dtype=np.uint8)

    # Lidar com imagens RGB vs grayscale
    if normalized.ndim == 2:
        img = Image.fromarray(normalized, mode="L")
    elif normalized.ndim == 3 and normalized.shape[2] == 3:
        img = Image.fromarray(normalized, mode="RGB")
    elif normalized.ndim == 3 and normalized.shape[2] == 4:
        img = Image.fromarray(normalized, mode="RGBA")
    else:
        img = Image.fromarray(normalized)

    fmt_map = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "tiff": "TIFF"}
    pil_format = fmt_map.get(target_format)
    if pil_format is None:
        raise ValueError(f"DICOM não suporta saída: {target_format}")

    if pil_format == "JPEG" and img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    save_kwargs: dict = {}
    if pil_format == "JPEG":
        save_kwargs["quality"] = 95

    img.save(output_path, format=pil_format, **save_kwargs)
