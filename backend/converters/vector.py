"""Conversor de vetores e arquivos CNC/Plotter: DXF, SVG, EPS, AI, G-code."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext == "svg":
        _svg_convert(input_path, output_path, target_format)
    elif input_ext == "dxf":
        _dxf_convert(input_path, output_path, target_format)
    elif input_ext == "eps":
        _eps_convert(input_path, output_path, target_format)
    elif input_ext == "ai":
        _ai_convert(input_path, output_path, target_format)
    elif input_ext == "gcode":
        _gcode_convert(input_path, output_path, target_format)
    else:
        raise ValueError(f"Conversor vetorial não suporta entrada: {input_ext}")


def _svg_convert(input_path, output_path, target_format):
    if target_format == "png":
        import cairosvg
        cairosvg.svg2png(url=input_path, write_to=output_path)

    elif target_format == "pdf":
        import cairosvg
        cairosvg.svg2pdf(url=input_path, write_to=output_path)

    elif target_format == "eps":
        import cairosvg
        cairosvg.svg2ps(url=input_path, write_to=output_path)

    elif target_format == "dxf":
        _svg_to_dxf(input_path, output_path)

    else:
        raise ValueError(f"SVG não suporta saída: {target_format}")


def _svg_to_dxf(svg_path, dxf_path):
    """Converte caminhos SVG para entidades LINE em DXF."""
    import ezdxf
    from xml.etree import ElementTree as ET
    import re

    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}

    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for rect in root.findall(".//svg:rect", ns):
        try:
            x = float(rect.get("x", 0))
            y = float(rect.get("y", 0))
            w = float(rect.get("width", 0))
            h = float(rect.get("height", 0))
            msp.add_lwpolyline(
                [(x, -y), (x + w, -y), (x + w, -(y + h)), (x, -(y + h))],
                close=True,
            )
        except (ValueError, TypeError):
            pass

    for circle in root.findall(".//svg:circle", ns):
        try:
            cx = float(circle.get("cx", 0))
            cy = float(circle.get("cy", 0))
            r = float(circle.get("r", 0))
            msp.add_circle((cx, -cy), r)
        except (ValueError, TypeError):
            pass

    doc.saveas(dxf_path)


def _dxf_convert(input_path, output_path, target_format):
    import ezdxf

    doc = ezdxf.readfile(input_path)
    msp = doc.modelspace()

    if target_format == "svg":
        _dxf_to_svg(msp, output_path)
    elif target_format in ("png", "pdf"):
        # DXF → SVG temporário → PNG/PDF
        svg_tmp = output_path + ".tmp.svg"
        _dxf_to_svg(msp, svg_tmp)
        import cairosvg
        if target_format == "png":
            cairosvg.svg2png(url=svg_tmp, write_to=output_path)
        else:
            cairosvg.svg2pdf(url=svg_tmp, write_to=output_path)
        Path(svg_tmp).unlink(missing_ok=True)
    else:
        raise ValueError(f"DXF não suporta saída: {target_format}")


def _dxf_to_svg(msp, svg_path):
    """Converte entidades DXF básicas para SVG."""
    lines = []
    circles = []
    polylines = []

    for entity in msp:
        if entity.dxftype() == "LINE":
            lines.append(entity)
        elif entity.dxftype() == "CIRCLE":
            circles.append(entity)
        elif entity.dxftype() in ("LWPOLYLINE", "POLYLINE"):
            polylines.append(entity)

    # Calcular bounding box
    all_x, all_y = [], []
    for line in lines:
        all_x += [line.dxf.start.x, line.dxf.end.x]
        all_y += [line.dxf.start.y, line.dxf.end.y]
    for circle in circles:
        all_x += [circle.dxf.center.x - circle.dxf.radius, circle.dxf.center.x + circle.dxf.radius]
        all_y += [circle.dxf.center.y - circle.dxf.radius, circle.dxf.center.y + circle.dxf.radius]

    if not all_x:
        all_x, all_y = [0, 100], [0, 100]

    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    width = max(max_x - min_x, 1)
    height = max(max_y - min_y, 1)
    margin = max(width, height) * 0.05

    vb_x = min_x - margin
    vb_y = -(max_y + margin)
    vb_w = width + 2 * margin
    vb_h = height + 2 * margin

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_x:.2f} {vb_y:.2f} {vb_w:.2f} {vb_h:.2f}">',
        '<g stroke="black" stroke-width="0.5" fill="none">',
    ]

    for line in lines:
        x1, y1 = line.dxf.start.x, -line.dxf.start.y
        x2, y2 = line.dxf.end.x, -line.dxf.end.y
        svg_lines.append(f'  <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')

    for circle in circles:
        cx, cy = circle.dxf.center.x, -circle.dxf.center.y
        r = circle.dxf.radius
        svg_lines.append(f'  <circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/>')

    svg_lines += ["</g>", "</svg>"]
    Path(svg_path).write_text("\n".join(svg_lines), encoding="utf-8")


def _eps_convert(input_path, output_path, target_format):
    """Converte EPS usando Pillow (requer Ghostscript instalado)."""
    from PIL import Image

    img = Image.open(input_path)

    if target_format == "png":
        if img.mode == "CMYK":
            img = img.convert("RGB")
        img.save(output_path, format="PNG")
    elif target_format == "jpg":
        img = img.convert("RGB")
        img.save(output_path, format="JPEG", quality=95)
    elif target_format == "pdf":
        img = img.convert("RGB")
        img.save(output_path, format="PDF")
    elif target_format == "svg":
        # EPS → PNG → avisar que SVG raster não é ideal
        from PIL import Image as PILImage
        import cairosvg
        png_tmp = output_path + ".tmp.png"
        img.convert("RGB").save(png_tmp, format="PNG")
        # Embute PNG em SVG
        import base64
        data = Path(png_tmp).read_bytes()
        b64 = base64.b64encode(data).decode()
        w, h = img.size
        svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><image href="data:image/png;base64,{b64}" width="{w}" height="{h}"/></svg>'
        Path(output_path).write_text(svg_content)
        Path(png_tmp).unlink(missing_ok=True)
    else:
        raise ValueError(f"EPS não suporta saída: {target_format}")


def _ai_convert(input_path, output_path, target_format):
    """Adobe Illustrator (.ai) é baseado em PDF — usa PyMuPDF."""
    import fitz

    doc = fitz.open(input_path)
    if target_format == "pdf":
        doc.save(output_path)
    elif target_format == "png":
        from PIL import Image
        import io
        page = doc[0]
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        img.save(output_path, format="PNG")
    else:
        raise ValueError(f"AI não suporta saída: {target_format}")
    doc.close()


def _gcode_convert(input_path, output_path, target_format):
    """G-code → TXT (reformatado com comentários)."""
    if target_format != "txt":
        raise ValueError("G-code só pode ser convertido para TXT")
    text = Path(input_path).read_text(encoding="utf-8", errors="replace")
    Path(output_path).write_text(text, encoding="utf-8")
