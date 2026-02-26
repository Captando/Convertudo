"""Conversor financeiro: OFX, QIF → CSV / JSON."""
import json
import re
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext == "ofx":
        transactions = _parse_ofx(input_path)
    elif input_ext == "qif":
        transactions = _parse_qif(input_path)
    else:
        raise ValueError(f"Financeiro não suporta entrada: {input_ext}")

    if target_format == "csv":
        _save_csv(transactions, output_path)
    elif target_format == "json":
        Path(output_path).write_text(
            json.dumps(transactions, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
    else:
        raise ValueError(f"Financeiro não suporta saída: {target_format}")


# --- OFX Parser ---

def _parse_ofx(input_path: str) -> list[dict]:
    """Parseia OFX/QFX (baseado em XML ou SGML legado)."""
    text = Path(input_path).read_text(encoding="utf-8", errors="replace")

    # Tentar ofxparse primeiro
    try:
        from ofxparse import OfxParser
        import io
        ofx = OfxParser.parse(io.BytesIO(Path(input_path).read_bytes()))
        txns = []
        for account in (ofx.accounts if hasattr(ofx, "accounts") else [ofx.account]):
            if hasattr(account, "statement") and account.statement:
                for t in account.statement.transactions:
                    txns.append({
                        "date":   str(getattr(t, "date", "")),
                        "amount": str(getattr(t, "amount", "")),
                        "memo":   str(getattr(t, "memo", "")),
                        "type":   str(getattr(t, "type", "")),
                        "id":     str(getattr(t, "id", "")),
                    })
        return txns
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: parsing manual via regex (OFX SGML legado)
    transactions = []
    for block in re.finditer(r"<STMTTRN>(.*?)</STMTTRN>", text, re.DOTALL | re.IGNORECASE):
        chunk = block.group(1)
        txn = {}
        for tag, field in [
            ("DTPOSTED", "date"),
            ("TRNAMT",   "amount"),
            ("MEMO",     "memo"),
            ("NAME",     "name"),
            ("TRNTYPE",  "type"),
            ("FITID",    "id"),
        ]:
            m = re.search(rf"<{tag}>(.*?)(?:<|$)", chunk, re.IGNORECASE)
            if m:
                txn[field] = m.group(1).strip()
        if txn:
            transactions.append(txn)
    return transactions


# --- QIF Parser ---

def _parse_qif(input_path: str) -> list[dict]:
    """Parseia QIF (Quicken Interchange Format)."""
    text = Path(input_path).read_text(encoding="utf-8", errors="replace")

    transactions = []
    current: dict = {}

    QIF_FIELDS = {
        "D": "date",
        "T": "amount",
        "M": "memo",
        "P": "payee",
        "N": "number",
        "C": "cleared",
        "L": "category",
    }

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line == "^":
            if current:
                transactions.append(current)
                current = {}
        elif line.startswith("!"):
            continue  # tipo de conta
        elif line[0] in QIF_FIELDS:
            key = QIF_FIELDS[line[0]]
            current[key] = line[1:].strip()

    if current:
        transactions.append(current)

    return transactions


# --- Save helpers ---

def _save_csv(rows: list[dict], output_path: str) -> None:
    import csv
    if not rows:
        Path(output_path).write_text("", encoding="utf-8")
        return
    all_keys = list(dict.fromkeys(k for row in rows for k in row))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(rows)
