"""Conversor de eBooks: EPUB → PDF, TXT, HTML via ebooklib."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import ebooklib
        from ebooklib import epub
    except ImportError:
        raise RuntimeError("Instale: pip install ebooklib")

    target_format = target_format.lower()

    book = epub.read_epub(input_path)

    # Extrair todo o conteúdo HTML dos capítulos
    chapters_html: list[str] = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="replace")
            chapters_html.append(content)

    if target_format == "html":
        combined = "\n\n".join(chapters_html)
        # Adicionar header se não tiver
        if not combined.strip().startswith("<!DOCTYPE"):
            title = book.title or "eBook"
            combined = (
                f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
                f"<title>{title}</title></head><body>\n{combined}\n</body></html>"
            )
        Path(output_path).write_text(combined, encoding="utf-8")

    elif target_format == "txt":
        import re
        texts = []
        for html in chapters_html:
            text = re.sub(r"<[^>]+>", " ", html)
            text = re.sub(r"\s+", " ", text).strip()
            texts.append(text)
        Path(output_path).write_text("\n\n".join(texts), encoding="utf-8")

    elif target_format == "pdf":
        import weasyprint
        combined_html = "\n\n".join(chapters_html)
        title = book.title or "eBook"
        full_html = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>{title}</title>"
            f"<style>body{{font-family:serif;max-width:700px;margin:auto;padding:20px}}"
            f"</style></head><body>\n{combined_html}\n</body></html>"
        )
        weasyprint.HTML(string=full_html).write_pdf(output_path)

    else:
        raise ValueError(f"EPUB não suporta saída: {target_format}")
