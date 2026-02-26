"""Conversor bioinformático: FASTA / FASTQ → CSV / TXT / FASTA."""
import csv
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext in ("fasta", "fa"):
        records = _parse_fasta(input_path)
    elif input_ext in ("fastq", "fq"):
        records = _parse_fastq(input_path)
    else:
        raise ValueError(f"Bio não suporta entrada: {input_ext}")

    if target_format == "csv":
        _save_csv(records, output_path)
    elif target_format == "txt":
        lines = []
        for r in records:
            lines.append(f">{r['id']} {r.get('description','')}")
            lines.append(r["sequence"])
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    elif target_format == "fasta":
        lines = []
        for r in records:
            lines.append(f">{r['id']} {r.get('description','')}")
            # Quebrar sequência em linhas de 60 caracteres
            seq = r["sequence"]
            for i in range(0, len(seq), 60):
                lines.append(seq[i:i+60])
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    else:
        raise ValueError(f"Bio não suporta saída: {target_format}")


def _parse_fasta(input_path: str) -> list[dict]:
    records = []
    current_id = ""
    current_desc = ""
    current_seq: list[str] = []

    with open(input_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip()
            if line.startswith(">"):
                if current_id:
                    records.append({
                        "id": current_id,
                        "description": current_desc,
                        "sequence": "".join(current_seq),
                        "length": len("".join(current_seq)),
                    })
                parts = line[1:].split(None, 1)
                current_id = parts[0] if parts else ""
                current_desc = parts[1] if len(parts) > 1 else ""
                current_seq = []
            elif line and not line.startswith(";"):
                current_seq.append(line.upper())

    if current_id:
        records.append({
            "id": current_id,
            "description": current_desc,
            "sequence": "".join(current_seq),
            "length": len("".join(current_seq)),
        })
    return records


def _parse_fastq(input_path: str) -> list[dict]:
    records = []
    with open(input_path, encoding="utf-8", errors="replace") as f:
        lines = [l.rstrip() for l in f if l.strip()]

    i = 0
    while i + 3 < len(lines):
        header = lines[i]
        seq    = lines[i + 1]
        plus   = lines[i + 2]
        qual   = lines[i + 3]

        if header.startswith("@") and plus.startswith("+"):
            parts = header[1:].split(None, 1)
            records.append({
                "id":          parts[0],
                "description": parts[1] if len(parts) > 1 else "",
                "sequence":    seq.upper(),
                "quality":     qual,
                "length":      len(seq),
                "avg_quality": _mean_quality(qual),
            })
        i += 4
    return records


def _mean_quality(qual: str) -> float:
    if not qual:
        return 0.0
    scores = [ord(c) - 33 for c in qual]
    return round(sum(scores) / len(scores), 2)


def _save_csv(records: list[dict], output_path: str) -> None:
    if not records:
        Path(output_path).write_text("", encoding="utf-8")
        return
    fields = list(records[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
