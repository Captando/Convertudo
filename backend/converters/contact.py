"""Conversor de agenda e contatos: ICS → CSV/JSON; VCF → CSV/JSON."""
import json
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext == "ics":
        data = _parse_ics(input_path)
    elif input_ext == "vcf":
        data = _parse_vcf(input_path)
    else:
        raise ValueError(f"Contato não suporta entrada: {input_ext}")

    if target_format == "json":
        Path(output_path).write_text(
            json.dumps(data, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
    elif target_format == "csv":
        _save_csv(data, output_path)
    else:
        raise ValueError(f"Contato não suporta saída: {target_format}")


# --- ICS ---

def _parse_ics(input_path: str) -> list[dict]:
    try:
        from icalendar import Calendar
    except ImportError:
        raise RuntimeError("Instale: pip install icalendar")

    raw = Path(input_path).read_bytes()
    cal = Calendar.from_ical(raw)
    events = []
    for component in cal.walk():
        if component.name == "VEVENT":
            events.append({
                "summary":     str(component.get("SUMMARY", "")),
                "description": str(component.get("DESCRIPTION", "")),
                "location":    str(component.get("LOCATION", "")),
                "start":       str(component.get("DTSTART", {}).dt if component.get("DTSTART") else ""),
                "end":         str(component.get("DTEND", {}).dt if component.get("DTEND") else ""),
                "status":      str(component.get("STATUS", "")),
                "uid":         str(component.get("UID", "")),
            })
    return events


# --- VCF ---

def _parse_vcf(input_path: str) -> list[dict]:
    try:
        import vobject
    except ImportError:
        raise RuntimeError("Instale: pip install vobject")

    text = Path(input_path).read_text(encoding="utf-8", errors="replace")
    contacts = []
    for vcard in vobject.readComponents(text):
        contact: dict = {}

        if hasattr(vcard, "fn"):
            contact["name"] = str(vcard.fn.value)
        if hasattr(vcard, "email"):
            contact["email"] = str(vcard.email.value)
        if hasattr(vcard, "tel"):
            contact["phone"] = str(vcard.tel.value)
        if hasattr(vcard, "org"):
            org = vcard.org.value
            contact["organization"] = " ".join(org) if isinstance(org, list) else str(org)
        if hasattr(vcard, "adr"):
            adr = vcard.adr.value
            contact["address"] = (
                f"{adr.street}, {adr.city}, {adr.region}, {adr.code}, {adr.country}"
            ).strip(", ")
        if hasattr(vcard, "url"):
            contact["url"] = str(vcard.url.value)

        contacts.append(contact)
    return contacts


# --- CSV helper ---

def _save_csv(data: list[dict], output_path: str) -> None:
    import csv
    if not data:
        Path(output_path).write_text("", encoding="utf-8")
        return
    all_keys = list(dict.fromkeys(k for row in data for k in row))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(data)
