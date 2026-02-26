"""Conversor científico: FITS (astronomia) → PNG/CSV; NetCDF → CSV/JSON."""
import json
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()

    if input_ext in ("fits", "fit", "fts"):
        _fits_convert(input_path, output_path, target_format)
    elif input_ext == "nc":
        _netcdf_convert(input_path, output_path, target_format)
    else:
        raise ValueError(f"Científico não suporta entrada: {input_ext}")


# --- FITS ---

def _fits_convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        from astropy.io import fits
    except ImportError:
        raise RuntimeError("Instale: pip install astropy")

    with fits.open(input_path) as hdul:
        if target_format == "png":
            _fits_to_png(hdul, output_path)
        elif target_format == "csv":
            _fits_to_csv(hdul, output_path)
        else:
            raise ValueError(f"FITS não suporta saída: {target_format}")


def _fits_to_png(hdul, output_path: str) -> None:
    import numpy as np
    from PIL import Image

    # Procurar o primeiro HDU com dados de imagem 2D
    img_data = None
    for hdu in hdul:
        if hasattr(hdu, "data") and hdu.data is not None:
            if hdu.data.ndim >= 2:
                img_data = hdu.data
                break

    if img_data is None:
        raise ValueError("FITS sem dados de imagem")

    # Usar apenas os dois últimos eixos se for cubo (3D+)
    while img_data.ndim > 2:
        img_data = img_data[0]

    img_data = img_data.astype(np.float64)

    # Remover NaN e aplicar escala
    img_data = np.nan_to_num(img_data, nan=0.0)
    vmin, vmax = np.percentile(img_data, [1, 99])
    if vmax > vmin:
        img_data = np.clip((img_data - vmin) / (vmax - vmin) * 255, 0, 255)
    else:
        img_data = np.zeros_like(img_data)

    img = Image.fromarray(img_data.astype(np.uint8), mode="L")
    img.save(output_path, format="PNG")


def _fits_to_csv(hdul, output_path: str) -> None:
    import csv

    # Procurar tabela binária ou ASCII
    for hdu in hdul:
        if hasattr(hdu, "columns") and hdu.columns is not None:
            cols = hdu.columns.names
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(cols)
                for row in hdu.data:
                    writer.writerow([str(v) for v in row])
            return

    # Fallback: exportar dados numéricos brutos
    for hdu in hdul:
        if hasattr(hdu, "data") and hdu.data is not None and hdu.data.ndim == 2:
            import numpy as np
            import csv
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                for row in hdu.data:
                    writer.writerow(row.tolist())
            return

    raise ValueError("FITS sem tabela ou dados matriciais exportáveis")


# --- NetCDF ---

def _netcdf_convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import netCDF4 as nc
    except ImportError:
        raise RuntimeError("Instale: pip install netCDF4")

    ds = nc.Dataset(input_path, "r")
    try:
        result: dict = {}
        for var_name in ds.variables:
            var = ds.variables[var_name]
            try:
                data = var[:].tolist() if hasattr(var[:], "tolist") else list(var[:])
                result[var_name] = data
            except Exception:
                result[var_name] = str(var[:])

        if target_format == "json":
            Path(output_path).write_text(
                json.dumps(result, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8"
            )
        elif target_format == "csv":
            import csv
            import pandas as pd
            dfs = []
            for k, v in result.items():
                try:
                    if isinstance(v, list) and v and not isinstance(v[0], list):
                        dfs.append(pd.DataFrame({k: v}))
                except Exception:
                    pass
            if dfs:
                import functools
                combined = functools.reduce(
                    lambda a, b: a.join(b, how="outer"), dfs
                )
                combined.to_csv(output_path, index=False)
            else:
                Path(output_path).write_text(
                    json.dumps(result, default=str), encoding="utf-8"
                )
        else:
            raise ValueError(f"NetCDF não suporta saída: {target_format}")
    finally:
        ds.close()
