"""Conversor de legendas: SRT ↔ VTT ↔ ASS/SSA ↔ SBV via pysubs2."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import pysubs2
    except ImportError:
        raise RuntimeError("Instale: pip install pysubs2")

    target_format = target_format.lower()

    FORMAT_MAP = {
        "srt":  "srt",
        "vtt":  "webvtt",
        "ass":  "ass",
        "ssa":  "ass",
        "sbv":  "sbv",
    }

    out_fmt = FORMAT_MAP.get(target_format)
    if out_fmt is None:
        raise ValueError(f"Legenda não suporta saída: {target_format}")

    subs = pysubs2.load(input_path)
    subs.save(output_path, format_=out_fmt)
