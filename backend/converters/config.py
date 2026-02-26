"""Conversor de arquivos de configuração: YAML, TOML, XML, INI ↔ JSON/YAML/TOML/XML."""
import json
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    # 1. Carregar como estrutura Python
    data = _load(input_path, input_ext)

    # 2. Salvar no formato de saída
    _save(data, output_path, target_format)


def _load(input_path: str, ext: str) -> object:
    text = Path(input_path).read_text(encoding="utf-8")

    if ext in ("yaml", "yml"):
        import yaml
        return yaml.safe_load(text)

    if ext == "toml":
        try:
            import tomllib
            return tomllib.loads(text)
        except ImportError:
            import tomli
            return tomli.loads(text)

    if ext == "xml":
        return _xml_to_dict(text)

    if ext == "ini":
        import configparser
        parser = configparser.ConfigParser()
        parser.read_string(text)
        result: dict = {}
        for section in parser.sections():
            result[section] = dict(parser[section])
        return result

    raise ValueError(f"Formato de entrada não suportado: {ext}")


def _save(data: object, output_path: str, fmt: str) -> None:
    if fmt == "json":
        text = json.dumps(data, indent=2, ensure_ascii=False)
        Path(output_path).write_text(text, encoding="utf-8")

    elif fmt in ("yaml", "yml"):
        import yaml
        text = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        Path(output_path).write_text(text, encoding="utf-8")

    elif fmt == "toml":
        try:
            import tomllib  # noqa: F401 — apenas para testar disponibilidade
        except ImportError:
            pass
        try:
            import tomli_w
            Path(output_path).write_bytes(tomli_w.dumps(data).encode())
            return
        except ImportError:
            pass
        # Fallback: serialização manual simples para dicts planos
        lines = []
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    lines.append(f"\n[{k}]")
                    for sk, sv in v.items():
                        lines.append(f"{sk} = {json.dumps(sv)}")
                else:
                    lines.append(f"{k} = {json.dumps(v)}")
        Path(output_path).write_text("\n".join(lines), encoding="utf-8")

    elif fmt == "xml":
        text = _dict_to_xml(data)
        Path(output_path).write_text(text, encoding="utf-8")

    elif fmt == "csv":
        import csv, io
        rows = data if isinstance(data, list) else [data]
        if rows and isinstance(rows[0], dict):
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            Path(output_path).write_text(buf.getvalue(), encoding="utf-8")
        else:
            Path(output_path).write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")

    else:
        raise ValueError(f"Formato de saída não suportado: {fmt}")


# --- XML helpers ---

def _xml_to_dict(text: str) -> dict:
    from xml.etree import ElementTree as ET

    def _node(el) -> object:
        children = list(el)
        if not children:
            return el.text or ""
        result: dict = {}
        for child in children:
            val = _node(child)
            if child.tag in result:
                existing = result[child.tag]
                if not isinstance(existing, list):
                    result[child.tag] = [existing]
                result[child.tag].append(val)
            else:
                result[child.tag] = val
        return result

    root = ET.fromstring(text)
    return {root.tag: _node(root)}


def _dict_to_xml(data: object, root_tag: str = "root", indent: int = 0) -> str:
    pad = "  " * indent

    if isinstance(data, dict):
        if indent == 0:
            # Use first key as root tag if data is a single-key dict
            if len(data) == 1:
                key = next(iter(data))
                return f'<?xml version="1.0" encoding="utf-8"?>\n{_dict_to_xml(data[key], key, 0)}'
            lines = [f'<?xml version="1.0" encoding="utf-8"?>\n<{root_tag}>']
        else:
            lines = [f"{pad}<{root_tag}>"]
        for k, v in data.items():
            lines.append(_dict_to_xml(v, k, indent + 1))
        lines.append(f"{pad}</{root_tag}>")
        return "\n".join(lines)

    if isinstance(data, list):
        return "\n".join(_dict_to_xml(item, root_tag, indent) for item in data)

    return f"{pad}<{root_tag}>{_escape_xml(str(data))}</{root_tag}>"


def _escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
