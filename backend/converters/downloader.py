"""Downloader de mídia via yt-dlp: YouTube, Instagram, TikTok, Twitter/X e +1000 sites."""
from pathlib import Path


def download(url: str, job_dir: str, fmt: str = "mp4", quality: str = "best") -> Path:
    """
    Baixa mídia da URL. Retorna o Path do arquivo baixado.

    fmt:     mp4 | webm | mp3 | m4a
    quality: best | 1080 | 720 | 480 | 360
    """
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("Instale: pip install yt-dlp")

    job_path = Path(job_dir)
    job_path.mkdir(parents=True, exist_ok=True)

    outtmpl = str(job_path / "output.%(ext)s")

    if fmt in ("mp3", "m4a"):
        codec = "mp3" if fmt == "mp3" else "m4a"
        ydl_opts: dict = {
            "format":         "bestaudio/best",
            "outtmpl":        outtmpl,
            "postprocessors": [{
                "key":              "FFmpegExtractAudio",
                "preferredcodec":   codec,
                "preferredquality": "192",
            }],
            "quiet":       True,
            "no_warnings": True,
        }
    else:
        # Mapa de qualidade → formato yt-dlp
        quality_fmt = {
            "best": "bestvideo+bestaudio/best",
            "1080": "bestvideo[height<=1080][ext=mp4]+bestaudio/bestvideo[height<=1080]+bestaudio/best",
            "720":  "bestvideo[height<=720][ext=mp4]+bestaudio/bestvideo[height<=720]+bestaudio/best",
            "480":  "bestvideo[height<=480][ext=mp4]+bestaudio/bestvideo[height<=480]+bestaudio/best",
            "360":  "bestvideo[height<=360][ext=mp4]+bestaudio/bestvideo[height<=360]+bestaudio/best",
        }
        ydl_opts = {
            "format":               quality_fmt.get(quality, quality_fmt["best"]),
            "outtmpl":              outtmpl,
            "merge_output_format":  fmt,
            "quiet":                True,
            "no_warnings":          True,
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Encontrar o arquivo gerado
    files = sorted(job_path.iterdir(), key=lambda p: p.stat().st_size, reverse=True)
    if not files:
        raise RuntimeError("Download falhou — nenhum arquivo gerado")

    return files[0]


def get_info(url: str) -> dict:
    """Retorna metadados sem baixar (título, duração, thumbnail, plataforma)."""
    try:
        import yt_dlp
    except ImportError:
        raise RuntimeError("Instale: pip install yt-dlp")

    ydl_opts = {
        "quiet":        True,
        "no_warnings":  True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {
        "title":     info.get("title", ""),
        "duration":  info.get("duration"),
        "uploader":  info.get("uploader", ""),
        "thumbnail": info.get("thumbnail", ""),
        "extractor": info.get("extractor_key", ""),
        "url":       url,
    }
