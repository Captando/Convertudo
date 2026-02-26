"""Conversor de banco de dados: SQLite/DB ↔ CSV/JSON/XLSX/SQL; SQL → SQLite."""
import json
import sqlite3
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext in ("sqlite", "db"):
        _sqlite_export(input_path, output_path, target_format)
    elif input_ext == "sql":
        _sql_import(input_path, output_path, target_format)
    else:
        raise ValueError(f"Banco de dados não suporta entrada: {input_ext}")


# --- SQLite → CSV / JSON / XLSX / SQL ---

def _sqlite_export(input_path: str, output_path: str, target_format: str) -> None:
    conn = sqlite3.connect(input_path)
    conn.row_factory = sqlite3.Row

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            raise ValueError("Banco de dados sem tabelas")

        if target_format == "sql":
            _dump_sql(conn, output_path)

        elif target_format == "json":
            result: dict = {}
            for table in tables:
                rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
                result[table] = [dict(row) for row in rows]
            Path(output_path).write_text(
                json.dumps(result, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8"
            )

        elif target_format == "csv":
            import csv, io
            if len(tables) == 1:
                _table_to_csv(conn, tables[0], output_path)
            else:
                # Múltiplas tabelas → ZIP com um CSV por tabela
                import zipfile
                zip_path = output_path  # output já termina em .csv, mas vamos sobrescrever
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for table in tables:
                        buf = io.StringIO()
                        rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
                        if rows:
                            writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
                            writer.writeheader()
                            for row in rows:
                                writer.writerow(dict(row))
                        zf.writestr(f"{table}.csv", buf.getvalue())

        elif target_format == "xlsx":
            import openpyxl
            wb = openpyxl.Workbook()
            wb.remove(wb.active)  # remove a aba padrão
            for table in tables:
                rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
                ws = wb.create_sheet(title=table[:31])  # Excel: max 31 chars no nome da aba
                if rows:
                    ws.append(list(rows[0].keys()))
                    for row in rows:
                        ws.append(list(dict(row).values()))
            wb.save(output_path)

        else:
            raise ValueError(f"SQLite não suporta saída: {target_format}")

    finally:
        conn.close()


def _table_to_csv(conn: sqlite3.Connection, table: str, output_path: str) -> None:
    import csv
    rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row))


def _dump_sql(conn: sqlite3.Connection, output_path: str) -> None:
    lines = []
    for line in conn.iterdump():
        lines.append(line)
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


# --- SQL → SQLite / CSV / JSON ---

def _sql_import(input_path: str, output_path: str, target_format: str) -> None:
    sql_text = Path(input_path).read_text(encoding="utf-8", errors="replace")

    if target_format == "sqlite":
        # Executar SQL em um novo banco SQLite
        conn = sqlite3.connect(output_path)
        try:
            conn.executescript(sql_text)
            conn.commit()
        finally:
            conn.close()

    elif target_format in ("csv", "json"):
        # Criar banco em memória, executar SQL, exportar
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            conn = sqlite3.connect(tmp_path)
            conn.row_factory = sqlite3.Row
            try:
                conn.executescript(sql_text)
                conn.commit()
                _sqlite_export(tmp_path, output_path, target_format)
            finally:
                conn.close()
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    else:
        raise ValueError(f"SQL não suporta saída: {target_format}")
