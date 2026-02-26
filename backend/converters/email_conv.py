"""Conversor de e-mails: EML / MSG / MBOX → PDF / TXT / HTML."""
import email
import email.policy
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext == "msg":
        _convert_msg(input_path, output_path, target_format)
        return
    if input_ext == "mbox":
        _convert_mbox(input_path, output_path, target_format)
        return

    # EML (padrão)
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


# --- MSG (Outlook) ---

def _convert_msg(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import extract_msg
    except ImportError:
        raise RuntimeError("Instale: pip install extract-msg")

    m = extract_msg.Message(input_path)
    subject  = m.subject or "(sem assunto)"
    from_    = m.sender or ""
    to_      = m.to or ""
    date_    = str(m.date or "")
    body_txt = m.body or ""
    body_html = m.htmlBody.decode("utf-8", errors="replace") if m.htmlBody else ""

    _render_email(subject, from_, to_, date_, body_txt, body_html, output_path, target_format)


# --- MBOX ---

def _convert_mbox(input_path: str, output_path: str, target_format: str) -> None:
    import mailbox
    mbox = mailbox.mbox(input_path)
    messages = list(mbox)
    if not messages:
        Path(output_path).write_text("(MBOX vazio)", encoding="utf-8")
        return

    parts = []
    for msg in messages:
        subject = str(msg.get("Subject", "(sem assunto)"))
        from_   = str(msg.get("From", ""))
        to_     = str(msg.get("To", ""))
        date_   = str(msg.get("Date", ""))
        body_txt, body_html = _extract_body(msg)
        parts.append((subject, from_, to_, date_, body_txt, body_html))

    if target_format == "txt":
        lines = []
        for i, (subj, fr, to, dt, bt, bh) in enumerate(parts, 1):
            lines += [f"=== Mensagem {i} ===", f"De: {fr}", f"Para: {to}",
                      f"Data: {dt}", f"Assunto: {subj}", "", bt or _html_to_text(bh or ""), ""]
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")

    elif target_format == "html":
        blocks = []
        for i, (subj, fr, to, dt, bt, bh) in enumerate(parts, 1):
            body = bh if bh else f"<pre>{_esc(bt)}</pre>"
            blocks.append(
                f"<h2>Mensagem {i}: {_esc(subj)}</h2>"
                f"<p><b>De:</b> {_esc(fr)} | <b>Para:</b> {_esc(to)} | <b>Data:</b> {_esc(dt)}</p>"
                f"<div>{body}</div><hr>"
            )
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>body{font-family:sans-serif;max-width:900px;margin:auto;padding:20px}</style>"
            f"</head><body>{''.join(blocks)}</body></html>"
        )
        Path(output_path).write_text(html, encoding="utf-8")

    elif target_format == "pdf":
        import weasyprint
        blocks = []
        for i, (subj, fr, to, dt, bt, bh) in enumerate(parts, 1):
            body = bh if bh else f"<pre>{_esc(bt)}</pre>"
            blocks.append(
                f"<h2>Mensagem {i}: {_esc(subj)}</h2>"
                f"<p><b>De:</b> {_esc(fr)} | <b>Para:</b> {_esc(to)} | <b>Data:</b> {_esc(dt)}</p>"
                f"<div>{body}</div><hr>"
            )
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<style>body{font-family:sans-serif;max-width:900px;margin:auto;padding:20px}</style>"
            f"</head><body>{''.join(blocks)}</body></html>"
        )
        weasyprint.HTML(string=html).write_pdf(output_path)

    else:
        raise ValueError(f"MBOX/MSG não suporta saída: {target_format}")


def _render_email(subject, from_, to_, date_, body_txt, body_html, output_path, target_format):
    """Helper compartilhado para renderizar um e-mail em TXT/HTML/PDF."""
    if target_format == "txt":
        lines = [f"De: {from_}", f"Para: {to_}", f"Data: {date_}",
                 f"Assunto: {subject}", "", body_txt or _html_to_text(body_html or "")]
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")

    elif target_format == "html":
        body = body_html if body_html else f"<pre>{_esc(body_txt)}</pre>"
        header = (
            f"<table style='border-collapse:collapse;margin-bottom:20px'>"
            f"<tr><td><b>De:</b></td><td>{_esc(from_)}</td></tr>"
            f"<tr><td><b>Para:</b></td><td>{_esc(to_)}</td></tr>"
            f"<tr><td><b>Data:</b></td><td>{_esc(date_)}</td></tr>"
            f"<tr><td><b>Assunto:</b></td><td>{_esc(subject)}</td></tr>"
            f"</table><hr>"
        )
        full = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>body{{font-family:sans-serif;max-width:800px;margin:auto;padding:20px}}</style>"
            f"</head><body>{header}{body}</body></html>"
        )
        Path(output_path).write_text(full, encoding="utf-8")

    elif target_format == "pdf":
        import weasyprint
        body = body_html if body_html else f"<pre style='white-space:pre-wrap'>{_esc(body_txt)}</pre>"
        header = (
            f"<table style='border-collapse:collapse;margin-bottom:20px;font-size:13px'>"
            f"<tr><td><b>De:</b></td><td>{_esc(from_)}</td></tr>"
            f"<tr><td><b>Para:</b></td><td>{_esc(to_)}</td></tr>"
            f"<tr><td><b>Data:</b></td><td>{_esc(date_)}</td></tr>"
            f"<tr><td><b>Assunto:</b></td><td>{_esc(subject)}</td></tr>"
            f"</table><hr>"
        )
        full = (
            f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<style>body{{font-family:sans-serif;max-width:800px;margin:auto;padding:20px}}</style>"
            f"</head><body>{header}{body}</body></html>"
        )
        weasyprint.HTML(string=full).write_pdf(output_path)

    else:
        raise ValueError(f"Email não suporta saída: {target_format}")
