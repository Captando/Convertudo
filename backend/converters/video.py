"""Conversor de vídeo via FFmpeg."""
import subprocess
import shutil
from pathlib import Path


def _check_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg não encontrado. Instale com: brew install ffmpeg")


def convert(input_path: str, output_path: str, target_format: str) -> None:
    _check_ffmpeg()
    target_format = target_format.lower()

    if target_format == "gif":
        # GIF de alta qualidade com palette
        palette_path = output_path + ".palette.png"
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path,
                "-vf", "fps=10,scale=480:-1:flags=lanczos,palettegen",
                palette_path
            ], capture_output=True, check=True)
            subprocess.run([
                "ffmpeg", "-y", "-i", input_path, "-i", palette_path,
                "-lavfi", "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse",
                output_path
            ], capture_output=True, check=True)
        finally:
            if Path(palette_path).exists():
                Path(palette_path).unlink()
    elif target_format == "mp3":
        # Extrair áudio do vídeo
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vn", "-acodec", "libmp3lame", "-q:a", "2", output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg falhou:\n{result.stderr}")
    else:
        cmd = ["ffmpeg", "-y", "-i", input_path, output_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg falhou:\n{result.stderr}")
