"""Conversor de código-fonte → PDF / HTML / TXT / MD via Pygments."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import pygments
        from pygments.lexers import get_lexer_for_filename, TextLexer
        from pygments.formatters import HtmlFormatter
    except ImportError:
        raise RuntimeError("Instale: pip install Pygments")

    target_format = target_format.lower()
    code = Path(input_path).read_text(encoding="utf-8", errors="replace")
    ext = Path(input_path).suffix.lstrip(".")

    try:
        lexer = get_lexer_for_filename(input_path, stripall=True)
    except Exception:
        lexer = TextLexer()

    if target_format == "txt":
        Path(output_path).write_text(code, encoding="utf-8")

    elif target_format == "md":
        md = f"```{ext}\n{code}\n```"
        Path(output_path).write_text(md, encoding="utf-8")

    elif target_format == "html":
        formatter = HtmlFormatter(
            full=True,
            style="monokai",
            linenos=True,
            lineanchors="line",
            title=Path(input_path).name,
        )
        html = pygments.highlight(code, lexer, formatter)
        Path(output_path).write_text(html, encoding="utf-8")

    elif target_format == "pdf":
        import weasyprint
        formatter = HtmlFormatter(
            full=True,
            style="monokai",
            linenos=True,
            title=Path(input_path).name,
        )
        html = pygments.highlight(code, lexer, formatter)
        # Adicionar estilo de impressão
        html = html.replace(
            "</style>",
            "body{font-size:11px;} pre{white-space:pre-wrap;word-break:break-all;}</style>"
        )
        weasyprint.HTML(string=html).write_pdf(output_path)

    else:
        raise ValueError(f"Código não suporta saída: {target_format}")
