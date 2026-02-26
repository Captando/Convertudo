from typing import Callable

SUPPORTED_CONVERSIONS: dict[str, list[str]] = {
    # Imagens raster
    "png":     ["jpg", "webp", "bmp", "gif", "tiff", "ico", "pdf"],
    "jpg":     ["png", "webp", "bmp", "tiff", "pdf"],
    "jpeg":    ["png", "webp", "bmp", "tiff", "pdf"],
    "webp":    ["png", "jpg", "bmp", "pdf"],
    "gif":     ["png", "jpg", "webp", "mp4"],
    "bmp":     ["png", "jpg", "webp"],
    "tiff":    ["png", "jpg", "pdf"],
    "ico":     ["png", "jpg"],
    "heic":    ["jpg", "png", "webp", "tiff"],
    "heif":    ["jpg", "png", "webp", "tiff"],
    "avif":    ["jpg", "png", "webp"],
    # Câmera RAW
    "cr2":     ["png", "jpg", "tiff"],
    "nef":     ["png", "jpg", "tiff"],
    "arw":     ["png", "jpg", "tiff"],
    "dng":     ["png", "jpg", "tiff"],
    "raf":     ["png", "jpg", "tiff"],
    "orf":     ["png", "jpg", "tiff"],
    "rw2":     ["png", "jpg", "tiff"],
    # HDR / EXR
    "exr":     ["png", "jpg", "tiff"],
    "hdr":     ["png", "jpg", "tiff", "exr"],
    # Adobe
    "psd":     ["png", "jpg", "pdf"],
    "ai":      ["png", "pdf"],
    "eps":     ["png", "jpg", "pdf", "svg"],
    "svg":     ["png", "pdf", "dxf", "eps"],
    # Vetores / CNC / Plotter
    "dxf":     ["svg", "png", "pdf"],
    "gcode":   ["txt"],
    # 3D
    "stl":     ["obj", "ply", "gltf", "glb", "3mf"],
    "obj":     ["stl", "ply", "gltf", "glb", "3mf"],
    "ply":     ["stl", "obj", "gltf", "glb"],
    "gltf":    ["glb", "stl", "obj", "ply"],
    "glb":     ["gltf", "stl", "obj", "ply"],
    "3mf":     ["stl", "obj"],
    "fbx":     ["stl", "obj", "gltf"],
    "off":     ["stl", "obj", "ply"],
    # CAD
    "step":    ["stl", "obj"],
    "stp":     ["stl", "obj"],
    "iges":    ["stl", "obj"],
    "igs":     ["stl", "obj"],
    # Áudio
    "mp3":     ["wav", "flac", "ogg", "aac", "m4a"],
    "wav":     ["mp3", "flac", "ogg", "aac"],
    "flac":    ["mp3", "wav", "ogg"],
    "ogg":     ["mp3", "wav", "flac"],
    "m4a":     ["mp3", "wav"],
    "aac":     ["mp3", "wav", "flac"],
    "wma":     ["mp3", "wav"],
    # Vídeo
    "mp4":     ["avi", "mkv", "mov", "webm", "mp3", "gif"],
    "avi":     ["mp4", "mkv", "mov", "webm"],
    "mkv":     ["mp4", "avi", "mov", "webm"],
    "mov":     ["mp4", "avi", "mkv", "webm"],
    "webm":    ["mp4", "avi"],
    "flv":     ["mp4", "avi"],
    # Apresentação
    "pptx":    ["pdf", "png"],
    "ppt":     ["pdf", "png"],
    # Documentos
    "pdf":     ["txt", "html", "png"],
    "docx":    ["pdf", "txt", "html"],
    "txt":     ["pdf", "html", "md", "docx", "qr"],
    "html":    ["pdf", "txt", "md"],
    "md":      ["html", "txt", "pdf"],
    # eBook
    "epub":    ["pdf", "txt", "html"],
    # Dados
    "csv":     ["json", "xlsx"],
    "json":    ["csv", "xlsx"],
    "xlsx":    ["csv", "json"],
    "xls":     ["csv", "json", "xlsx"],
    # Config / Dev
    "yaml":    ["json", "toml", "xml"],
    "yml":     ["json", "yaml", "toml", "xml"],
    "toml":    ["json", "yaml", "xml"],
    "xml":     ["json", "yaml", "csv"],
    "ini":     ["json", "yaml"],
    # Banco de dados
    "sqlite":  ["csv", "json", "xlsx", "sql"],
    "db":      ["csv", "json", "xlsx", "sql"],
    "sql":     ["sqlite", "csv", "json"],
    # Notebook
    "ipynb":   ["html", "pdf", "md"],
    # Fontes
    "ttf":     ["otf", "woff", "woff2"],
    "otf":     ["ttf", "woff", "woff2"],
    "woff":    ["ttf", "otf", "woff2"],
    "woff2":   ["ttf", "otf", "woff"],
    # Legendas
    "srt":     ["vtt", "ass", "sbv"],
    "vtt":     ["srt", "ass", "sbv"],
    "ass":     ["srt", "vtt", "sbv"],
    "ssa":     ["srt", "vtt", "ass"],
    "sbv":     ["srt", "vtt", "ass"],
    # Médico
    "dcm":     ["png", "jpg", "tiff"],
    # Geoespacial
    "geojson": ["kml", "gpx", "csv"],
    "kml":     ["geojson", "gpx", "csv"],
    "gpx":     ["geojson", "kml", "csv"],
    # Arquivos comprimidos
    "zip":     ["tar", "7z"],
    "tar":     ["zip", "7z"],
    "gz":      ["zip", "7z"],
    "7z":      ["zip", "tar"],
    # Email
    "eml":     ["pdf", "txt", "html"],
    # Agenda / Contatos
    "ics":     ["csv", "json"],
    "vcf":     ["csv", "json"],
}

CATEGORIES: dict[str, list[str]] = {
    "Imagem":         ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "ico", "heic", "heif", "avif"],
    "RAW":            ["cr2", "nef", "arw", "dng", "raf", "orf", "rw2"],
    "HDR":            ["exr", "hdr"],
    "Adobe":          ["psd", "ai", "eps"],
    "Vetor/CNC":      ["svg", "dxf", "gcode"],
    "3D":             ["stl", "obj", "ply", "gltf", "glb", "3mf", "fbx", "off"],
    "CAD":            ["step", "stp", "iges", "igs"],
    "Áudio":          ["mp3", "wav", "flac", "ogg", "aac", "m4a", "wma"],
    "Vídeo":          ["mp4", "avi", "mkv", "mov", "webm", "flv"],
    "Apresentação":   ["pptx", "ppt"],
    "Documento":      ["pdf", "docx", "txt", "html", "md"],
    "eBook":          ["epub"],
    "Dados":          ["csv", "json", "xlsx", "xls"],
    "Config":         ["yaml", "yml", "toml", "xml", "ini"],
    "Banco de dados": ["sqlite", "db", "sql"],
    "Notebook":       ["ipynb"],
    "Fonte":          ["ttf", "otf", "woff", "woff2"],
    "Legenda":        ["srt", "vtt", "ass", "ssa", "sbv"],
    "Médico":         ["dcm"],
    "Geoespacial":    ["geojson", "kml", "gpx"],
    "Arquivo":        ["zip", "tar", "gz", "7z"],
    "Email":          ["eml"],
    "Agenda":         ["ics", "vcf"],
}

# Reverse map: ext → category
EXT_CATEGORY: dict[str, str] = {}
for _cat, _exts in CATEGORIES.items():
    for _ext in _exts:
        EXT_CATEGORY[_ext] = _cat

# Formatos virtuais: o identificador não corresponde à extensão real do arquivo
VIRTUAL_FORMAT_EXT: dict[str, str] = {
    "qr": "png",
}


def get_supported_outputs(ext: str) -> list[str]:
    return SUPPORTED_CONVERSIONS.get(ext.lower(), [])


def route_conversion(input_ext: str, output_ext: str) -> Callable:
    """Return the correct converter function for the given (input, output) pair."""
    input_ext = input_ext.lower()
    output_ext = output_ext.lower()

    # Caso especial: saída QR code
    if output_ext == "qr":
        from converters.qrcode_conv import convert
        return convert

    in_cat = EXT_CATEGORY.get(input_ext, "")

    if in_cat == "Imagem":
        if input_ext in ("heic", "heif", "avif"):
            from converters.heic import convert
            return convert
        from converters.image import convert
        return convert

    if in_cat == "RAW":
        from converters.image import convert
        return convert

    if in_cat == "HDR":
        from converters.hdr import convert
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

    if in_cat == "CAD":
        from converters.cad import convert
        return convert

    if in_cat == "Áudio":
        from converters.audio import convert
        return convert

    if in_cat == "Vídeo":
        from converters.video import convert
        return convert

    if in_cat == "Apresentação":
        from converters.presentation import convert
        return convert

    if in_cat in ("Documento", "Dados"):
        from converters.document import convert
        return convert

    if in_cat == "eBook":
        from converters.ebook import convert
        return convert

    if in_cat == "Config":
        from converters.config import convert
        return convert

    if in_cat == "Banco de dados":
        from converters.database import convert
        return convert

    if in_cat == "Notebook":
        from converters.notebook import convert
        return convert

    if in_cat == "Fonte":
        from converters.font import convert
        return convert

    if in_cat == "Legenda":
        from converters.subtitle import convert
        return convert

    if in_cat == "Médico":
        from converters.medical import convert
        return convert

    if in_cat == "Geoespacial":
        from converters.geo import convert
        return convert

    if in_cat == "Arquivo":
        from converters.archive import convert
        return convert

    if in_cat == "Email":
        from converters.email_conv import convert
        return convert

    if in_cat == "Agenda":
        from converters.contact import convert
        return convert

    raise ValueError(f"Nenhum conversor encontrado para {input_ext} → {output_ext}")
