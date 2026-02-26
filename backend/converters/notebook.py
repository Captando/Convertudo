"""Conversor de Jupyter Notebooks: IPYNB → HTML / PDF / MD via nbconvert."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import nbformat
        from nbconvert import HTMLExporter, MarkdownExporter
    except ImportError:
        raise RuntimeError("Instale: pip install nbconvert nbformat")

    target_format = target_format.lower()

    with open(input_path, encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    if target_format == "html":
        exporter = HTMLExporter()
        html_body, _ = exporter.from_notebook_node(nb)
        Path(output_path).write_text(html_body, encoding="utf-8")

    elif target_format == "md":
        exporter = MarkdownExporter()
        md_body, _ = exporter.from_notebook_node(nb)
        Path(output_path).write_text(md_body, encoding="utf-8")

    elif target_format == "pdf":
        # Converter para HTML primeiro, depois HTML → PDF via weasyprint
        import weasyprint
        exporter = HTMLExporter()
        html_body, _ = exporter.from_notebook_node(nb)
        weasyprint.HTML(string=html_body).write_pdf(output_path)

    else:
        raise ValueError(f"Notebook não suporta saída: {target_format}")
