"""Conversor de documentos Office abertos e LaTeX:
RTF, ODT, ODS, ODP → PDF/DOCX/TXT/HTML/CSV/PNG
TEX → PDF/HTML
"""
import shutil
import subprocess
import tempfile
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext == "rtf":
        _rtf_convert(input_path, output_path, target_format)
    elif input_ext == "tex":
        _tex_convert(input_path, output_path, target_format)
    elif input_ext in ("odt", "ods", "odp"):
        _libreoffice_convert(input_path, output_path, input_ext, target_format)
    else:
        raise ValueError(f"Office não suporta entrada: {input_ext}")


# --- RTF ---

def _rtf_convert(input_path: str, output_path: str, target_format: str) -> None:
    if target_format == "txt":
        try:
            from striprtf.striprtf import rtf_to_text
            rtf = Path(input_path).read_text(encoding="utf-8", errors="replace")
            text = rtf_to_text(rtf)
            Path(output_path).write_text(text, encoding="utf-8")
            return
        except ImportError:
            pass
        # Fallback via LibreOffice
        _libreoffice_convert(input_path, output_path, "rtf", target_format)

    elif target_format in ("pdf", "docx", "html"):
        lo = shutil.which("libreoffice") or shutil.which("soffice")
        if lo:
            _lo_convert(lo, input_path, output_path, target_format)
        else:
            # Fallback: strip RTF e gerar PDF de texto
            try:
                from striprtf.striprtf import rtf_to_text
                rtf = Path(input_path).read_text(encoding="utf-8", errors="replace")
                text = rtf_to_text(rtf)
            except ImportError:
                text = Path(input_path).read_text(encoding="utf-8", errors="replace")
            _text_to_target(text, output_path, target_format)
    else:
        raise ValueError(f"RTF não suporta saída: {target_format}")


# --- TEX / LaTeX ---

def _tex_convert(input_path: str, output_path: str, target_format: str) -> None:
    if target_format == "pdf":
        pdflatex = shutil.which("pdflatex") or shutil.which("xelatex")
        if pdflatex:
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    [pdflatex, "-interaction=nonstopmode",
                     "-output-directory", tmpdir, input_path],
                    capture_output=True, text=True
                )
                stem = Path(input_path).stem
                generated = Path(tmpdir) / f"{stem}.pdf"
                if generated.exists():
                    generated.rename(output_path)
                    return
                raise RuntimeError(f"pdflatex falhou:\n{result.stdout[-500:]}")
        else:
            raise RuntimeError(
                "pdflatex não encontrado. Instale: brew install --cask mactex\n"
                "ou: apt install texlive-latex-base"
            )

    elif target_format == "html":
        # Converter TEX para HTML básico preservando o conteúdo
        tex = Path(input_path).read_text(encoding="utf-8", errors="replace")
        import re
        # Extrair conteúdo entre \begin{document} e \end{document}
        m = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", tex, re.DOTALL)
        body = m.group(1) if m else tex

        # Substituições LaTeX → HTML básico
        body = re.sub(r"\\section\*?\{(.*?)\}", r"<h2>\1</h2>", body)
        body = re.sub(r"\\subsection\*?\{(.*?)\}", r"<h3>\1</h3>", body)
        body = re.sub(r"\\textbf\{(.*?)\}", r"<b>\1</b>", body)
        body = re.sub(r"\\textit\{(.*?)\}", r"<i>\1</i>", body)
        body = re.sub(r"\\emph\{(.*?)\}", r"<em>\1</em>", body)
        body = re.sub(r"\\\\", r"<br>", body)
        body = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", body)
        body = re.sub(r"\\[a-zA-Z]+", "", body)

        html = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>body{{font-family:serif;max-width:800px;margin:auto;padding:20px}}</style>"
            f"</head><body>{body}</body></html>"
        )
        Path(output_path).write_text(html, encoding="utf-8")

    else:
        raise ValueError(f"TEX não suporta saída: {target_format}")


# --- LibreOffice ---

def _libreoffice_convert(
    input_path: str, output_path: str, input_ext: str, target_format: str
) -> None:
    lo = shutil.which("libreoffice") or shutil.which("soffice")
    if not lo:
        raise RuntimeError(
            "LibreOffice não encontrado.\n"
            "Instale: brew install --cask libreoffice\n"
            "ou: apt install libreoffice"
        )
    _lo_convert(lo, input_path, output_path, target_format)


def _lo_convert(lo: str, input_path: str, output_path: str, target_format: str) -> None:
    LO_FORMAT_MAP = {
        "pdf":  "pdf",
        "docx": "docx",
        "txt":  "txt",
        "html": "html",
        "csv":  "csv",
        "xlsx": "xlsx",
        "png":  "png",
    }
    lo_fmt = LO_FORMAT_MAP.get(target_format)
    if lo_fmt is None:
        raise ValueError(f"LibreOffice não suporta saída: {target_format}")

    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            [lo, "--headless", "--convert-to", lo_fmt,
             "--outdir", tmpdir, input_path],
            capture_output=True, text=True
        )
        stem = Path(input_path).stem
        generated = Path(tmpdir) / f"{stem}.{lo_fmt}"
        if generated.exists():
            generated.rename(output_path)
            return

    raise RuntimeError(
        f"LibreOffice não gerou o arquivo de saída.\n"
        f"stderr: {result.stderr[-300:]}"
    )


# --- Helpers ---

def _text_to_target(text: str, output_path: str, target_format: str) -> None:
    if target_format == "pdf":
        import weasyprint
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html = f"<html><body><pre style='font-family:serif;white-space:pre-wrap'>{escaped}</pre></body></html>"
        weasyprint.HTML(string=html).write_pdf(output_path)
    elif target_format == "html":
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html = f"<html><body><pre>{escaped}</pre></body></html>"
        Path(output_path).write_text(html, encoding="utf-8")
    elif target_format == "docx":
        from docx import Document
        doc = Document()
        for line in text.splitlines():
            doc.add_paragraph(line)
        doc.save(output_path)
