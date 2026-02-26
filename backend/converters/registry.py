from typing import Callable

SUPPORTED_CONVERSIONS: dict[str, list[str]] = {
    # Imagens raster
    "png":   ["jpg", "webp", "bmp", "gif", "tiff", "ico", "pdf"],
    "jpg":   ["png", "webp", "bmp", "tiff", "pdf"],
    "jpeg":  ["png", "webp", "bmp", "tiff", "pdf"],
    "webp":  ["png", "jpg", "bmp", "pdf"],
    "gif":   ["png", "jpg", "webp", "mp4"],
    "bmp":   ["png", "jpg", "webp"],
    "tiff":  ["png", "jpg", "pdf"],
    "ico":   ["png", "jpg"],
    # Câmera RAW
    "cr2":   ["png", "jpg", "tiff"],
    "nef":   ["png", "jpg", "tiff"],
    "arw":   ["png", "jpg", "tiff"],
    "dng":   ["png", "jpg", "tiff"],
    "raf":   ["png", "jpg", "tiff"],
    "orf":   ["png", "jpg", "tiff"],
    "rw2":   ["png", "jpg", "tiff"],
    # Adobe
    "psd":   ["png", "jpg", "pdf"],
    "ai":    ["png", "pdf"],
    "eps":   ["png", "jpg", "pdf", "svg"],
    "svg":   ["png", "pdf", "dxf", "eps"],
    # Vetores / CNC / Plotter
    "dxf":   ["svg", "png", "pdf"],
    "gcode": ["txt"],
    # 3D
    "stl":   ["obj", "ply", "gltf", "glb", "3mf"],
    "obj":   ["stl", "ply", "gltf", "glb", "3mf"],
    "ply":   ["stl", "obj", "gltf", "glb"],
    "gltf":  ["glb", "stl", "obj", "ply"],
    "glb":   ["gltf", "stl", "obj", "ply"],
    "3mf":   ["stl", "obj"],
    "fbx":   ["stl", "obj", "gltf"],
    "off":   ["stl", "obj", "ply"],
    # Áudio
    "mp3":   ["wav", "flac", "ogg", "aac", "m4a"],
    "wav":   ["mp3", "flac", "ogg", "aac"],
    "flac":  ["mp3", "wav", "ogg"],
    "ogg":   ["mp3", "wav", "flac"],
    "m4a":   ["mp3", "wav"],
    "aac":   ["mp3", "wav", "flac"],
    "wma":   ["mp3", "wav"],
    # Vídeo
    "mp4":   ["avi", "mkv", "mov", "webm", "mp3", "gif"],
    "avi":   ["mp4", "mkv", "mov", "webm"],
    "mkv":   ["mp4", "avi", "mov", "webm"],
    "mov":   ["mp4", "avi", "mkv", "webm"],
    "webm":  ["mp4", "avi"],
    "flv":   ["mp4", "avi"],
    # Documentos
    "pdf":   ["txt", "html", "png"],
    "docx":  ["pdf", "txt", "html"],
    "txt":   ["pdf", "html", "md", "docx"],
    "html":  ["pdf", "txt", "md"],
    "md":    ["html", "txt", "pdf"],
    # Dados
    "csv":   ["json", "xlsx"],
    "json":  ["csv", "xlsx"],
    "xlsx":  ["csv", "json"],
    "xls":   ["csv", "json", "xlsx"],
}

CATEGORIES: dict[str, list[str]] = {
    "Imagem":     ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "ico"],
    "RAW":        ["cr2", "nef", "arw", "dng", "raf", "orf", "rw2"],
    "Adobe":      ["psd", "ai", "eps"],
    "Vetor/CNC":  ["svg", "dxf", "gcode"],
    "3D":         ["stl", "obj", "ply", "gltf", "glb", "3mf", "fbx", "off"],
    "Áudio":      ["mp3", "wav", "flac", "ogg", "aac", "m4a", "wma"],
    "Vídeo":      ["mp4", "avi", "mkv", "mov", "webm", "flv"],
    "Documento":  ["pdf", "docx", "txt", "html", "md"],
    "Dados":      ["csv", "json", "xlsx", "xls"],
}

# Reverse map: ext → category
EXT_CATEGORY: dict[str, str] = {}
for cat, exts in CATEGORIES.items():
    for ext in exts:
        EXT_CATEGORY[ext] = cat


def get_supported_outputs(ext: str) -> list[str]:
    return SUPPORTED_CONVERSIONS.get(ext.lower(), [])


def route_conversion(input_ext: str, output_ext: str) -> Callable:
    """Return the correct converter function for the given (input, output) pair."""
    input_ext = input_ext.lower()
    output_ext = output_ext.lower()

    in_cat = EXT_CATEGORY.get(input_ext, "")

    if in_cat == "Imagem" or in_cat == "RAW":
        from converters.image import convert
        return convert

    if in_cat == "Adobe":
        if input_ext == "psd":
            from converters.adobe import convert
            return convert
        from converters.vector import convert
        return convert

    if in_cat == "Vetor/CNC":
        from converters.vector import convert
        return convert

    if in_cat == "3D":
        from converters.threed import convert
        return convert

    if in_cat == "Áudio":
        from converters.audio import convert
        return convert

    if in_cat == "Vídeo":
        from converters.video import convert
        return convert

    if in_cat in ("Documento", "Dados"):
        from converters.document import convert
        return convert

    raise ValueError(f"Nenhum conversor encontrado para {input_ext} → {output_ext}")
