"""Conversor geoespacial: GeoJSON ↔ KML ↔ GPX ↔ CSV via gpxpy / xml."""
import json
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    data = _load(input_path, input_ext)
    _save(data, output_path, target_format)


# --- Estrutura interna: lista de features GeoJSON ---

def _load(input_path: str, ext: str) -> list[dict]:
    if ext == "geojson":
        raw = json.loads(Path(input_path).read_text(encoding="utf-8"))
        if raw.get("type") == "FeatureCollection":
            return raw.get("features", [])
        if raw.get("type") == "Feature":
            return [raw]
        return []

    if ext == "kml":
        return _kml_to_features(Path(input_path).read_text(encoding="utf-8"))

    if ext == "gpx":
        return _gpx_to_features(input_path)

    raise ValueError(f"Geoespacial não suporta entrada: {ext}")


def _save(features: list[dict], output_path: str, fmt: str) -> None:
    if fmt == "geojson":
        doc = {"type": "FeatureCollection", "features": features}
        Path(output_path).write_text(
            json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    elif fmt == "kml":
        Path(output_path).write_text(_features_to_kml(features), encoding="utf-8")

    elif fmt == "gpx":
        Path(output_path).write_text(_features_to_gpx(features), encoding="utf-8")

    elif fmt == "csv":
        _features_to_csv(features, output_path)

    else:
        raise ValueError(f"Geoespacial não suporta saída: {fmt}")


# --- KML ---

def _kml_to_features(kml_text: str) -> list[dict]:
    from xml.etree import ElementTree as ET
    ns = "http://www.opengis.net/kml/2.2"
    root = ET.fromstring(kml_text)

    features = []
    for pm in root.iter(f"{{{ns}}}Placemark"):
        name_el = pm.find(f"{{{ns}}}name")
        name = name_el.text if name_el is not None else ""
        desc_el = pm.find(f"{{{ns}}}description")
        desc = desc_el.text if desc_el is not None else ""

        geometry = None
        for point in pm.iter(f"{{{ns}}}Point"):
            coords_el = point.find(f"{{{ns}}}coordinates")
            if coords_el is not None and coords_el.text:
                parts = coords_el.text.strip().split(",")
                if len(parts) >= 2:
                    lon, lat = float(parts[0]), float(parts[1])
                    geometry = {"type": "Point", "coordinates": [lon, lat]}

        for ls in pm.iter(f"{{{ns}}}LineString"):
            coords_el = ls.find(f"{{{ns}}}coordinates")
            if coords_el is not None and coords_el.text:
                coords = []
                for pair in coords_el.text.strip().split():
                    p = pair.split(",")
                    if len(p) >= 2:
                        coords.append([float(p[0]), float(p[1])])
                geometry = {"type": "LineString", "coordinates": coords}

        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {"name": name, "description": desc},
        })
    return features


def _features_to_kml(features: list[dict]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
    ]
    for f in features:
        name = (f.get("properties") or {}).get("name", "")
        desc = (f.get("properties") or {}).get("description", "")
        geom = f.get("geometry") or {}

        lines.append(f"  <Placemark>")
        lines.append(f"    <name>{_esc(name)}</name>")
        if desc:
            lines.append(f"    <description>{_esc(desc)}</description>")

        if geom.get("type") == "Point":
            lon, lat = geom["coordinates"][:2]
            lines.append(f"    <Point><coordinates>{lon},{lat}</coordinates></Point>")
        elif geom.get("type") == "LineString":
            coords_str = " ".join(f"{c[0]},{c[1]}" for c in geom["coordinates"])
            lines.append(f"    <LineString><coordinates>{coords_str}</coordinates></LineString>")

        lines.append("  </Placemark>")
    lines += ["</Document></kml>"]
    return "\n".join(lines)


# --- GPX ---

def _gpx_to_features(input_path: str) -> list[dict]:
    try:
        import gpxpy
        import gpxpy.gpx
    except ImportError:
        raise RuntimeError("Instale: pip install gpxpy")

    with open(input_path, encoding="utf-8") as f:
        gpx = gpxpy.parse(f)

    features = []
    for track in gpx.tracks:
        for segment in track.segments:
            coords = [[p.longitude, p.latitude] for p in segment.points]
            features.append({
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords},
                "properties": {"name": track.name or "track"},
            })
    for wpt in gpx.waypoints:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [wpt.longitude, wpt.latitude]},
            "properties": {"name": wpt.name or "waypoint"},
        })
    return features


def _features_to_gpx(features: list[dict]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<gpx version="1.1" creator="Convertudo" xmlns="http://www.topografix.com/GPX/1/1">',
    ]
    for f in features:
        name = (f.get("properties") or {}).get("name", "")
        geom = f.get("geometry") or {}

        if geom.get("type") == "Point":
            lon, lat = geom["coordinates"][:2]
            lines.append(f'  <wpt lat="{lat}" lon="{lon}"><name>{_esc(name)}</name></wpt>')
        elif geom.get("type") == "LineString":
            lines.append(f'  <trk><name>{_esc(name)}</name><trkseg>')
            for c in geom["coordinates"]:
                lines.append(f'    <trkpt lat="{c[1]}" lon="{c[0]}"/>')
            lines.append("  </trkseg></trk>")

    lines.append("</gpx>")
    return "\n".join(lines)


# --- CSV ---

def _features_to_csv(features: list[dict], output_path: str) -> None:
    import csv
    rows = []
    for f in features:
        props = f.get("properties") or {}
        geom = f.get("geometry") or {}
        row = dict(props)
        if geom.get("type") == "Point":
            row["longitude"] = geom["coordinates"][0]
            row["latitude"] = geom["coordinates"][1]
        row["geometry_type"] = geom.get("type", "")
        rows.append(row)

    if not rows:
        Path(output_path).write_text("", encoding="utf-8")
        return

    all_keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        writer.writerows(rows)


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
