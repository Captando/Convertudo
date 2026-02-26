import os
import uuid
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from converters.registry import SUPPORTED_CONVERSIONS, CATEGORIES, get_supported_outputs, route_conversion

app = FastAPI(title="Convertudo", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
TEMP_DIR = Path(tempfile.gettempdir()) / "convertudo"
TEMP_DIR.mkdir(exist_ok=True)


# --- API Routes ---

@app.get("/api/formats")
def get_formats():
    """Retorna o mapa completo de conversões suportadas, agrupado por categoria."""
    result = {}
    for category, exts in CATEGORIES.items():
        category_data = {}
        for ext in exts:
            outputs = SUPPORTED_CONVERSIONS.get(ext, [])
            if outputs:
                category_data[ext] = outputs
        if category_data:
            result[category] = category_data
    return JSONResponse(result)


@app.get("/api/outputs/{extension}")
def get_outputs(extension: str):
    """Retorna os formatos de saída disponíveis para uma extensão."""
    outputs = get_supported_outputs(extension)
    if not outputs:
        raise HTTPException(status_code=404, detail=f"Formato '{extension}' não suportado")
    return {"extension": extension, "outputs": outputs}


@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    target_format: str = Form(...),
):
    """Recebe um arquivo e retorna o arquivo convertido."""
    original_name = Path(file.filename or "arquivo").stem
    input_ext = Path(file.filename or "").suffix.lstrip(".").lower()

    if not input_ext:
        raise HTTPException(status_code=400, detail="Arquivo sem extensão reconhecida")

    target_format = target_format.lower().lstrip(".")

    # Validar conversão
    supported = get_supported_outputs(input_ext)
    if target_format not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Conversão '{input_ext}' → '{target_format}' não suportada",
        )

    # Criar arquivos temporários
    job_id = uuid.uuid4().hex
    input_path = TEMP_DIR / f"{job_id}_input.{input_ext}"
    output_path = TEMP_DIR / f"{job_id}_output.{target_format}"

    try:
        # Salvar upload
        content = await file.read()
        input_path.write_bytes(content)

        # Converter (em thread para não bloquear o event loop)
        converter = route_conversion(input_ext, target_format)
        await asyncio.get_event_loop().run_in_executor(
            None, converter, str(input_path), str(output_path), target_format
        )

        if not output_path.exists():
            raise RuntimeError("Arquivo de saída não foi gerado")

        # Tipos MIME comuns
        MIME_MAP = {
            "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp", "gif": "image/gif", "bmp": "image/bmp",
            "tiff": "image/tiff", "ico": "image/x-icon", "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "mp3": "audio/mpeg", "wav": "audio/wav", "flac": "audio/flac",
            "ogg": "audio/ogg", "aac": "audio/aac", "m4a": "audio/mp4",
            "mp4": "video/mp4", "avi": "video/x-msvideo", "mkv": "video/x-matroska",
            "mov": "video/quicktime", "webm": "video/webm",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "csv": "text/csv", "json": "application/json",
            "txt": "text/plain", "html": "text/html", "md": "text/markdown",
            "stl": "model/stl", "obj": "model/obj", "gltf": "model/gltf+json",
            "glb": "model/gltf-binary", "ply": "application/octet-stream",
            "3mf": "application/vnd.ms-package.3dmanufacturing-3dmodel+xml",
            "dxf": "application/dxf",
        }
        media_type = MIME_MAP.get(target_format, "application/octet-stream")
        download_name = f"{original_name}.{target_format}"

        return FileResponse(
            path=str(output_path),
            media_type=media_type,
            filename=download_name,
            background=_cleanup_task(input_path, output_path),
        )

    except HTTPException:
        _cleanup(input_path, output_path)
        raise
    except Exception as e:
        _cleanup(input_path, output_path)
        raise HTTPException(status_code=500, detail=str(e))


def _cleanup(*paths):
    for p in paths:
        try:
            Path(p).unlink(missing_ok=True)
        except Exception:
            pass


def _cleanup_task(*paths):
    from starlette.background import BackgroundTask
    return BackgroundTask(_cleanup, *paths)


# --- Servir frontend ---

if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
