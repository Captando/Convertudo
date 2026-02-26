"""Conversor de arquivos comprimidos: ZIP ↔ TAR.GZ ↔ 7Z."""
import os
import zipfile
import tarfile
import tempfile
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Extrair arquivo de entrada
        _extract(input_path, input_ext, tmpdir)

        # 2. Recomprimir no formato de saída
        _compress(tmpdir, output_path, target_format)


def _extract(input_path: str, ext: str, dest: str) -> None:
    if ext == "zip":
        with zipfile.ZipFile(input_path, "r") as zf:
            zf.extractall(dest)

    elif ext in ("tar", "gz"):
        mode = "r:gz" if ext == "gz" or input_path.endswith(".tar.gz") else "r:*"
        with tarfile.open(input_path, mode) as tf:
            tf.extractall(dest)

    elif ext == "7z":
        try:
            import py7zr
        except ImportError:
            raise RuntimeError("Instale: pip install py7zr")
        with py7zr.SevenZipFile(input_path, mode="r") as sz:
            sz.extractall(dest)

    else:
        raise ValueError(f"Arquivo não suporta entrada: {ext}")


def _compress(src_dir: str, output_path: str, fmt: str) -> None:
    entries = _list_entries(src_dir)

    if fmt == "zip":
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for abs_path, arc_name in entries:
                zf.write(abs_path, arc_name)

    elif fmt == "tar":
        with tarfile.open(output_path, "w:gz") as tf:
            for abs_path, arc_name in entries:
                tf.add(abs_path, arcname=arc_name)

    elif fmt == "7z":
        try:
            import py7zr
        except ImportError:
            raise RuntimeError("Instale: pip install py7zr")
        with py7zr.SevenZipFile(output_path, "w") as sz:
            for abs_path, arc_name in entries:
                sz.write(abs_path, arc_name)

    else:
        raise ValueError(f"Arquivo não suporta saída: {fmt}")


def _list_entries(src_dir: str) -> list[tuple[str, str]]:
    """Retorna lista de (abs_path, arc_name) para todos os arquivos no diretório."""
    entries = []
    base = Path(src_dir)
    for path in sorted(base.rglob("*")):
        if path.is_file():
            arc_name = str(path.relative_to(base))
            entries.append((str(path), arc_name))
    return entries
