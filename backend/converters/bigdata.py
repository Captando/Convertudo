"""Conversor de dados grandes: Parquet, JSONL/NDJSON, Feather, HDF5."""
import json
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext == "parquet":
        _parquet_convert(input_path, output_path, target_format)
    elif input_ext in ("jsonl", "ndjson"):
        _jsonl_convert(input_path, output_path, target_format)
    elif input_ext == "feather":
        _feather_convert(input_path, output_path, target_format)
    elif input_ext in ("hdf5", "h5"):
        _hdf5_convert(input_path, output_path, target_format)
    else:
        raise ValueError(f"BigData não suporta entrada: {input_ext}")


def _parquet_convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError("Instale: pip install pandas pyarrow")
    try:
        import pyarrow  # noqa: F401
    except ImportError:
        raise RuntimeError("Instale: pip install pyarrow")

    df = pd.read_parquet(input_path)
    _df_save(df, output_path, target_format)


def _jsonl_convert(input_path: str, output_path: str, target_format: str) -> None:
    import pandas as pd

    rows = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    if target_format == "json":
        Path(output_path).write_text(
            json.dumps(rows, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
        return

    df = pd.DataFrame(rows)
    _df_save(df, output_path, target_format)


def _feather_convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import pandas as pd
        import pyarrow.feather as feather  # noqa: F401
    except ImportError:
        raise RuntimeError("Instale: pip install pandas pyarrow")

    df = pd.read_feather(input_path)
    _df_save(df, output_path, target_format)


def _hdf5_convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import h5py
    except ImportError:
        raise RuntimeError("Instale: pip install h5py")
    import pandas as pd

    result: dict = {}
    with h5py.File(input_path, "r") as f:
        def _visit(name, obj):
            if isinstance(obj, h5py.Dataset):
                try:
                    data = obj[()]
                    if hasattr(data, "tolist"):
                        result[name] = data.tolist()
                    else:
                        result[name] = str(data)
                except Exception:
                    pass
        f.visititems(_visit)

    if target_format == "json":
        Path(output_path).write_text(
            json.dumps(result, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8"
        )
    elif target_format == "csv":
        # Tentar converter datasets 1D/2D para DataFrame
        dfs = []
        for k, v in result.items():
            try:
                df = pd.DataFrame(v if isinstance(v, list) else [v])
                df.insert(0, "_dataset", k)
                dfs.append(df)
            except Exception:
                pass
        if dfs:
            pd.concat(dfs, ignore_index=True).to_csv(output_path, index=False)
        else:
            Path(output_path).write_text(
                json.dumps(result, default=str), encoding="utf-8"
            )
    elif target_format == "xlsx":
        import openpyxl
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        for k, v in result.items():
            ws = wb.create_sheet(title=k[:31].replace("/", "_"))
            if isinstance(v, list):
                if v and isinstance(v[0], list):
                    for row in v:
                        ws.append(row)
                else:
                    for item in v:
                        ws.append([item])
            else:
                ws.append([str(v)])
        wb.save(output_path)
    else:
        raise ValueError(f"HDF5 não suporta saída: {target_format}")


def _df_save(df, output_path: str, target_format: str) -> None:
    import pandas as pd

    if target_format == "csv":
        df.to_csv(output_path, index=False)
    elif target_format == "json":
        df.to_json(output_path, orient="records", indent=2, force_ascii=False)
    elif target_format == "xlsx":
        df.to_excel(output_path, index=False)
    else:
        raise ValueError(f"BigData não suporta saída: {target_format}")
