"""Conversor de e-mails: EML → PDF / TXT / HTML."""
import email
import email.policy
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    target_format = target_format.lower()

    raw = Path(input_path).read_bytes()
    msg = email.message_from_bytes(raw, policy=email.policy.default)

    subject  = str(msg.get("Subject", "(sem assunto)"))
    from_    = str(msg.get("From", ""))
    to_      = str(msg.get("To", ""))
    date_    = str(msg.get("Date", ""))
    body_txt, body_html = _extract_body(msg)

    if target_format == "txt":
        lines = [
            f"De: {from_}",
            f"Para: {to_}",
            f"Data: {date_}",
            f"Assunto: {subject}",
            "",
            body_txt or _html_to_text(body_html or ""),
        ]
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")

    elif target_format == "html":
        if body_html:
            html = body_html
        else:
            escaped = (body_txt or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html = f"<pre>{escaped}</pre>"

        header_html = (
            f"<table style='border-collapse:collapse;margin-bottom:20px'>"
            f"<tr><td><b>De:</b></td><td>{_esc(from_)}</td></tr>"
            f"<tr><td><b>Para:</b></td><td>{_esc(to_)}</td></tr>"
            f"<tr><td><b>Data:</b></td><td>{_esc(date_)}</td></tr>"
            f"<tr><td><b>Assunto:</b></td><td>{_esc(subject)}</td></tr>"
            f"</table><hr>"
        )
        full = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>body{{font-family:sans-serif;max-width:800px;margin:auto;padding:20px}}"
            f"</style></head><body>{header_html}{html}</body></html>"
        )
        Path(output_path).write_text(full, encoding="utf-8")

    elif target_format == "pdf":
        import weasyprint

        if body_html:
            body = body_html
        else:
            escaped = (body_txt or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            body = f"<pre style='white-space:pre-wrap'>{escaped}</pre>"

        header_html = (
            f"<table style='border-collapse:collapse;margin-bottom:20px;font-size:13px'>"
            f"<tr><td><b>De:</b></td><td>{_esc(from_)}</td></tr>"
            f"<tr><td><b>Para:</b></td><td>{_esc(to_)}</td></tr>"
            f"<tr><td><b>Data:</b></td><td>{_esc(date_)}</td></tr>"
            f"<tr><td><b>Assunto:</b></td><td>{_esc(subject)}</td></tr>"
            f"</table><hr>"
        )
        full = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>body{{font-family:sans-serif;max-width:800px;margin:auto;padding:20px}}"
            f"</style></head><body>{header_html}{body}</body></html>"
        )
        weasyprint.HTML(string=full).write_pdf(output_path)

    else:
        raise ValueError(f"EML não suporta saída: {target_format}")


def _extract_body(msg) -> tuple[str, str]:
    txt, html = "", ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            disp = str(part.get("Content-Disposition", ""))
            if "attachment" in disp:
                continue
            if ct == "text/plain" and not txt:
                txt = part.get_content() or ""
            elif ct == "text/html" and not html:
                html = part.get_content() or ""
    else:
        ct = msg.get_content_type()
        if ct == "text/plain":
            txt = msg.get_content() or ""
        elif ct == "text/html":
            html = msg.get_content() or ""
    return txt, html


def _html_to_text(html: str) -> str:
    import re
    return re.sub(r"<[^>]+>", " ", html)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
