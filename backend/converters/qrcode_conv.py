"""Gerador de QR Code: TXT → PNG (via qrcode)."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import qrcode
    except ImportError:
        raise RuntimeError("Instale: pip install qrcode[pil]")

    # Ler conteúdo do arquivo de texto
    text = Path(input_path).read_text(encoding="utf-8", errors="replace").strip()

    if not text:
        raise ValueError("Arquivo de texto está vazio — nada para codificar no QR")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
