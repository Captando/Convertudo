"""Conversor de arquivos PSD (Adobe Photoshop) via psd-tools."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    from psd_tools import PSDImage

    target_format = target_format.lower()
    psd = PSDImage.open(input_path)

    if target_format == "png":
        img = psd.composite()
        img.save(output_path, format="PNG")

    elif target_format == "jpg":
        img = psd.composite()
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        img.save(output_path, format="JPEG", quality=95)

    elif target_format == "pdf":
        from PIL import Image
        import io
        import weasyprint

        img = psd.composite()
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        import base64
        b64 = base64.b64encode(buf.read()).decode()
        w, h = img.size

        html = f"""
        <html><body style="margin:0;padding:0;">
        <img src="data:image/png;base64,{b64}" style="width:{w}px;height:{h}px;display:block;">
        </body></html>
        """
        weasyprint.HTML(string=html).write_pdf(output_path)

    else:
        raise ValueError(f"PSD não suporta saída: {target_format}")
