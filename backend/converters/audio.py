"""Conversor de áudio via FFmpeg."""
import subprocess
import shutil


def _check_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg não encontrado. Instale com: brew install ffmpeg")


def convert(input_path: str, output_path: str, target_format: str) -> None:
    _check_ffmpeg()
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg falhou:\n{result.stderr}")
