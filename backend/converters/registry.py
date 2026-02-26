from typing import Callable

SUPPORTED_CONVERSIONS: dict[str, list[str]] = {
    # --- Imagens raster ---
    "png":        ["jpg", "webp", "bmp", "gif", "tiff", "ico", "pdf"],
    "jpg":        ["png", "webp", "bmp", "tiff", "pdf"],
    "jpeg":       ["png", "webp", "bmp", "tiff", "pdf"],
    "webp":       ["png", "jpg", "bmp", "pdf"],
    "gif":        ["png", "jpg", "webp", "mp4"],
    "bmp":        ["png", "jpg", "webp"],
    "tiff":       ["png", "jpg", "pdf"],
    "ico":        ["png", "jpg"],
    "heic":       ["jpg", "png", "webp", "tiff"],
    "heif":       ["jpg", "png", "webp", "tiff"],
    "avif":       ["jpg", "png", "webp"],
    "tga":        ["png", "jpg", "webp", "bmp"],
    "dds":        ["png", "jpg", "bmp"],
    "pcx":        ["png", "jpg", "bmp"],
    "ppm":        ["png", "jpg", "bmp"],
    "pgm":        ["png", "jpg", "bmp"],
    # --- Câmera RAW ---
    "cr2":        ["png", "jpg", "tiff"],
    "nef":        ["png", "jpg", "tiff"],
    "arw":        ["png", "jpg", "tiff"],
    "dng":        ["png", "jpg", "tiff"],
    "raf":        ["png", "jpg", "tiff"],
    "orf":        ["png", "jpg", "tiff"],
    "rw2":        ["png", "jpg", "tiff"],
    # --- HDR / EXR ---
    "exr":        ["png", "jpg", "tiff"],
    "hdr":        ["png", "jpg", "tiff", "exr"],
    # --- Adobe ---
    "psd":        ["png", "jpg", "pdf"],
    "ai":         ["png", "pdf"],
    "eps":        ["png", "jpg", "pdf", "svg"],
    "svg":        ["png", "pdf", "dxf", "eps"],
    # --- Vetores / CNC / Plotter ---
    "dxf":        ["svg", "png", "pdf"],
    "gcode":      ["txt"],
    # --- 3D ---
    "stl":        ["obj", "ply", "gltf", "glb", "3mf"],
    "obj":        ["stl", "ply", "gltf", "glb", "3mf"],
    "ply":        ["stl", "obj", "gltf", "glb"],
    "gltf":       ["glb", "stl", "obj", "ply"],
    "glb":        ["gltf", "stl", "obj", "ply"],
    "3mf":        ["stl", "obj"],
    "fbx":        ["stl", "obj", "gltf"],
    "off":        ["stl", "obj", "ply"],
    # --- CAD ---
    "step":       ["stl", "obj"],
    "stp":        ["stl", "obj"],
    "iges":       ["stl", "obj"],
    "igs":        ["stl", "obj"],
    # --- Áudio ---
    "mp3":        ["wav", "flac", "ogg", "aac", "m4a", "opus"],
    "wav":        ["mp3", "flac", "ogg", "aac", "opus"],
    "flac":       ["mp3", "wav", "ogg", "opus"],
    "ogg":        ["mp3", "wav", "flac"],
    "m4a":        ["mp3", "wav", "flac"],
    "aac":        ["mp3", "wav", "flac"],
    "wma":        ["mp3", "wav", "flac"],
    "opus":       ["mp3", "wav", "flac", "ogg"],
    "aiff":       ["mp3", "wav", "flac", "ogg"],
    "aif":        ["mp3", "wav", "flac"],
    "amr":        ["mp3", "wav"],
    "ape":        ["mp3", "wav", "flac"],
    # --- Vídeo ---
    "mp4":        ["avi", "mkv", "mov", "webm", "mp3", "gif"],
    "avi":        ["mp4", "mkv", "mov", "webm"],
    "mkv":        ["mp4", "avi", "mov", "webm"],
    "mov":        ["mp4", "avi", "mkv", "webm"],
    "webm":       ["mp4", "avi"],
    "flv":        ["mp4", "avi"],
    "ts":         ["mp4", "mkv", "avi"],
    "m2ts":       ["mp4", "mkv", "avi"],
    "3gp":        ["mp4", "avi"],
    "mpg":        ["mp4", "avi", "mkv"],
    "mpeg":       ["mp4", "avi", "mkv"],
    "wmv":        ["mp4", "avi", "mkv"],
    "asf":        ["mp4", "avi"],
    "mxf":        ["mp4", "mov"],
    # --- Apresentação ---
    "pptx":       ["pdf", "png"],
    "ppt":        ["pdf", "png"],
    # --- Documentos ---
    "pdf":        ["txt", "html", "png"],
    "docx":       ["pdf", "txt", "html"],
    "txt":        ["pdf", "html", "md", "docx", "qr"],
    "html":       ["pdf", "txt", "md"],
    "md":         ["html", "txt", "pdf"],
    # --- Office aberto ---
    "rtf":        ["pdf", "txt", "html"],
    "odt":        ["pdf", "txt", "html"],
    "tex":        ["pdf"],
    "ods":        ["csv", "json", "xlsx"],
    "odp":        ["pdf", "png"],
    # --- eBook ---
    "epub":       ["pdf", "txt", "html"],
    # --- Dados tabulares ---
    "csv":        ["json", "xlsx"],
    "json":       ["csv", "xlsx"],
    "xlsx":       ["csv", "json"],
    "xls":        ["csv", "json", "xlsx"],
    # --- Big Data ---
    "parquet":    ["csv", "json"],
    "jsonl":      ["csv", "json", "parquet"],
    "ndjson":     ["csv", "json", "parquet"],
    "feather":    ["csv", "json", "parquet"],
    "hdf5":       ["csv", "json"],
    "h5":         ["csv", "json"],
    # --- Config / Dev ---
    "yaml":       ["json", "toml", "xml"],
    "yml":        ["json", "yaml", "toml", "xml"],
    "toml":       ["json", "yaml", "xml"],
    "xml":        ["json", "yaml", "csv"],
    "ini":        ["json", "yaml"],
    "env":        ["json", "yaml", "toml"],
    "properties": ["json", "yaml"],
    "hcl":        ["json"],
    # --- Banco de dados ---
    "sqlite":     ["csv", "json", "xlsx", "sql"],
    "db":         ["csv", "json", "xlsx", "sql"],
    "sql":        ["sqlite", "csv", "json"],
    # --- Notebook ---
    "ipynb":      ["html", "pdf", "md"],
    # --- Fontes ---
    "ttf":        ["otf", "woff", "woff2"],
    "otf":        ["ttf", "woff", "woff2"],
    "woff":       ["ttf", "otf", "woff2"],
    "woff2":      ["ttf", "otf", "woff"],
    # --- Legendas ---
    "srt":        ["vtt", "ass", "sbv"],
    "vtt":        ["srt", "ass", "sbv"],
    "ass":        ["srt", "vtt", "sbv"],
    "ssa":        ["srt", "vtt", "ass"],
    "sbv":        ["srt", "vtt", "ass"],
    # --- Médico ---
    "dcm":        ["png", "jpg", "tiff"],
    # --- Geoespacial ---
    "geojson":    ["kml", "gpx", "csv"],
    "kml":        ["geojson", "gpx", "csv"],
    "gpx":        ["geojson", "kml", "csv"],
    # --- Arquivos comprimidos ---
    "zip":        ["tar", "7z"],
    "tar":        ["zip", "7z"],
    "gz":         ["zip", "7z"],
    "7z":         ["zip", "tar"],
    # --- Email ---
    "eml":        ["pdf", "txt", "html"],
    "msg":        ["pdf", "txt", "html"],
    "mbox":       ["pdf", "txt", "html"],
    # --- Agenda / Contatos ---
    "ics":        ["csv", "json"],
    "vcf":        ["csv", "json"],
    # --- Certificados SSL/TLS ---
    "pem":        ["der", "pfx"],
    "crt":        ["der", "pfx", "pem"],
    "cer":        ["der", "pfx", "pem"],
    "der":        ["pem", "pfx"],
    "pfx":        ["pem"],
    "p12":        ["pem"],
    "key":        ["pem"],
    # --- Financeiro ---
    "ofx":        ["csv", "json"],
    "qfx":        ["csv", "json"],
    "qif":        ["csv", "json"],
    # --- Código-fonte ---
    "py":         ["html", "pdf", "txt", "md"],
    "js":         ["html", "pdf", "txt", "md"],
    "jsx":        ["html", "pdf", "txt", "md"],
    "tsx":        ["html", "pdf", "txt", "md"],
    "java":       ["html", "pdf", "txt", "md"],
    "c":          ["html", "pdf", "txt", "md"],
    "cpp":        ["html", "pdf", "txt", "md"],
    "h":          ["html", "pdf", "txt", "md"],
    "hpp":        ["html", "pdf", "txt", "md"],
    "go":         ["html", "pdf", "txt", "md"],
    "rs":         ["html", "pdf", "txt", "md"],
    "rb":         ["html", "pdf", "txt", "md"],
    "php":        ["html", "pdf", "txt", "md"],
    "cs":         ["html", "pdf", "txt", "md"],
    "swift":      ["html", "pdf", "txt", "md"],
    "kt":         ["html", "pdf", "txt", "md"],
    "sh":         ["html", "pdf", "txt", "md"],
    "lua":        ["html", "pdf", "txt", "md"],
    "dart":       ["html", "pdf", "txt", "md"],
    "scala":      ["html", "pdf", "txt", "md"],
    "r":          ["html", "pdf", "txt", "md"],
    # --- Científico ---
    "fits":       ["png", "csv"],
    "fit":        ["png", "csv"],
    "fts":        ["png", "csv"],
    "nc":         ["json", "csv"],
    # --- Bioinformática ---
    "fasta":      ["csv", "txt", "fasta"],
    "fa":         ["csv", "txt", "fasta"],
    "fastq":      ["csv", "txt", "fasta"],
    "fq":         ["csv", "txt", "fasta"],
    # --- Playlist ---
    "m3u":        ["json", "txt", "csv"],
    "m3u8":       ["json", "txt", "csv"],
    # --- HAR (HTTP Archive) ---
    "har":        ["json", "csv"],
}

CATEGORIES: dict[str, list[str]] = {
    "Imagem":          ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tiff", "ico",
                        "heic", "heif", "avif", "tga", "dds", "pcx", "ppm", "pgm"],
    "RAW":             ["cr2", "nef", "arw", "dng", "raf", "orf", "rw2"],
    "HDR":             ["exr", "hdr"],
    "Adobe":           ["psd", "ai", "eps"],
    "Vetor/CNC":       ["svg", "dxf", "gcode"],
    "3D":              ["stl", "obj", "ply", "gltf", "glb", "3mf", "fbx", "off"],
    "CAD":             ["step", "stp", "iges", "igs"],
    "Áudio":           ["mp3", "wav", "flac", "ogg", "aac", "m4a", "wma",
                        "opus", "aiff", "aif", "amr", "ape"],
    "Vídeo":           ["mp4", "avi", "mkv", "mov", "webm", "flv",
                        "ts", "m2ts", "3gp", "mpg", "mpeg", "wmv", "asf", "mxf"],
    "Apresentação":    ["pptx", "ppt"],
    "Documento":       ["pdf", "docx", "txt", "html", "md"],
    "Office":          ["rtf", "odt", "tex"],
    "OpenDocument":    ["ods", "odp"],
    "eBook":           ["epub"],
    "Dados":           ["csv", "json", "xlsx", "xls"],
    "BigData":         ["parquet", "jsonl", "ndjson", "feather", "hdf5", "h5"],
    "Config":          ["yaml", "yml", "toml", "xml", "ini", "env", "properties", "hcl"],
    "Banco de dados":  ["sqlite", "db", "sql"],
    "Notebook":        ["ipynb"],
    "Fonte":           ["ttf", "otf", "woff", "woff2"],
    "Legenda":         ["srt", "vtt", "ass", "ssa", "sbv"],
    "Médico":          ["dcm"],
    "Geoespacial":     ["geojson", "kml", "gpx"],
    "Arquivo":         ["zip", "tar", "gz", "7z"],
    "Email":           ["eml", "msg", "mbox"],
    "Agenda":          ["ics", "vcf"],
    "Certificado":     ["pem", "crt", "cer", "der", "pfx", "p12", "key"],
    "Financeiro":      ["ofx", "qfx", "qif"],
    "Código":          ["py", "js", "jsx", "tsx", "java", "c", "cpp", "h", "hpp",
                        "go", "rs", "rb", "php", "cs", "swift", "kt", "sh", "lua",
                        "dart", "scala", "r"],
    "Científico":      ["fits", "fit", "fts", "nc"],
    "Bioinformática":  ["fasta", "fa", "fastq", "fq"],
    "Playlist":        ["m3u", "m3u8"],
    "HAR":             ["har"],
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

# Extensões dentro de "Documento" e "Dados" que usam conversor diferente
_OFFICE_EXTS    = {"rtf", "odt", "tex", "ods", "odp"}
_BIGDATA_EXTS   = {"parquet", "jsonl", "ndjson", "feather", "hdf5", "h5"}


def get_supported_outputs(ext: str) -> list[str]:
    return SUPPORTED_CONVERSIONS.get(ext.lower(), [])


def route_conversion(input_ext: str, output_ext: str) -> Callable:
    """Return the correct converter function for the given (input, output) pair."""
    input_ext  = input_ext.lower()
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

    if in_cat == "Documento":
        from converters.document import convert
        return convert

    if in_cat in ("Office", "OpenDocument"):
        from converters.office import convert
        return convert

    if in_cat == "eBook":
        from converters.ebook import convert
        return convert

    if in_cat == "Dados":
        from converters.document import convert
        return convert

    if in_cat == "BigData":
        from converters.bigdata import convert
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

    if in_cat == "Certificado":
        from converters.cert import convert
        return convert

    if in_cat == "Financeiro":
        from converters.financial import convert
        return convert

    if in_cat == "Código":
        from converters.code import convert
        return convert

    if in_cat == "Científico":
        from converters.scientific import convert
        return convert

    if in_cat == "Bioinformática":
        from converters.bio import convert
        return convert

    if in_cat in ("Playlist", "HAR"):
        from converters.misc import convert
        return convert

    raise ValueError(f"Nenhum conversor encontrado para {input_ext} → {output_ext}")
