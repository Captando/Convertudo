"""Conversor de fontes: TTF ↔ OTF ↔ WOFF ↔ WOFF2 via fonttools."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        from fontTools.ttLib import TTFont
    except ImportError:
        raise RuntimeError("Instale: pip install fonttools")

    target_format = target_format.lower()

    font = TTFont(input_path)

    if target_format == "woff":
        font.flavor = "woff"
        font.save(output_path)

    elif target_format == "woff2":
        try:
            font.flavor = "woff2"
            font.save(output_path)
        except Exception:
            # Requer brotli para WOFF2
            try:
                import brotli  # noqa: F401
            except ImportError:
                raise RuntimeError("WOFF2 requer: pip install brotli")
            font.flavor = "woff2"
            font.save(output_path)

    elif target_format in ("ttf", "otf"):
        font.flavor = None  # remove WOFF wrapper se houver
        font.save(output_path)

    else:
        raise ValueError(f"Fonte não suporta saída: {target_format}")
