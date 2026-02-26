"""Conversores miscelâneos: M3U/M3U8 → TXT/JSON; HAR → JSON/CSV."""
import json
import re
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext in ("m3u", "m3u8"):
        _m3u_convert(input_path, output_path, target_format)
    elif input_ext == "har":
        _har_convert(input_path, output_path, target_format)
    else:
        raise ValueError(f"Misc não suporta entrada: {input_ext}")


# --- M3U ---

def _m3u_convert(input_path: str, output_path: str, target_format: str) -> None:
    text = Path(input_path).read_text(encoding="utf-8", errors="replace")
    entries = _parse_m3u(text)

    if target_format == "json":
        Path(output_path).write_text(
            json.dumps(entries, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    elif target_format == "txt":
        lines = []
        for e in entries:
            if e.get("title"):
                lines.append(f"{e['title']}: {e['url']}")
            else:
                lines.append(e["url"])
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    elif target_format == "csv":
        import csv
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "duration", "url"])
            writer.writeheader()
            writer.writerows(entries)
    else:
        raise ValueError(f"M3U não suporta saída: {target_format}")


def _parse_m3u(text: str) -> list[dict]:
    entries = []
    current: dict = {}

    for line in text.splitlines():
        line = line.strip()
        if not line or line == "#EXTM3U":
            continue
        if line.startswith("#EXTINF:"):
            # #EXTINF:duration,Title
            m = re.match(r"#EXTINF:(-?\d+(?:\.\d+)?),(.*)", line)
            if m:
                current = {
                    "duration": m.group(1),
                    "title": m.group(2).strip(),
                }
        elif not line.startswith("#"):
            current["url"] = line
            entries.append({
                "title":    current.get("title", ""),
                "duration": current.get("duration", ""),
                "url":      current.get("url", line),
            })
            current = {}
    return entries


# --- HAR ---

def _har_convert(input_path: str, output_path: str, target_format: str) -> None:
    raw = json.loads(Path(input_path).read_text(encoding="utf-8"))

    entries = raw.get("log", {}).get("entries", [])
    rows = []
    for e in entries:
        req = e.get("request", {})
        resp = e.get("response", {})
        rows.append({
            "url":              req.get("url", ""),
            "method":           req.get("method", ""),
            "status":           resp.get("status", ""),
            "status_text":      resp.get("statusText", ""),
            "time_ms":          round(e.get("time", 0), 2),
            "response_size":    resp.get("bodySize", -1),
            "content_type":     resp.get("content", {}).get("mimeType", ""),
            "started_at":       e.get("startedDateTime", ""),
        })

    if target_format == "json":
        Path(output_path).write_text(
            json.dumps(rows, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
    elif target_format == "csv":
        import csv
        if not rows:
            Path(output_path).write_text("", encoding="utf-8")
            return
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    else:
        raise ValueError(f"HAR não suporta saída: {target_format}")
