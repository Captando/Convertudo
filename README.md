# Convertudo

Conversor universal de arquivos — Web App que converte qualquer formato para outro, diretamente no navegador.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## Formatos suportados

| Categoria | Entrada | Saída |
|-----------|---------|-------|
| **Imagem** | PNG, JPG, WebP, BMP, GIF, TIFF, ICO, HEIC, HEIF, AVIF | PNG, JPG, WebP, BMP, GIF, TIFF, ICO, PDF |
| **Câmera RAW** | CR2, NEF, ARW, DNG, RAF, ORF, RW2 | PNG, JPG, TIFF |
| **HDR / EXR** | EXR, HDR | PNG, JPG, TIFF, EXR |
| **Adobe** | PSD, AI, EPS | PNG, JPG, PDF, SVG |
| **Vetor / CNC / Plotter** | SVG, DXF, G-code | SVG, DXF, PNG, PDF, EPS, TXT |
| **3D** | STL, OBJ, PLY, GLTF, GLB, 3MF, FBX, OFF | STL, OBJ, PLY, GLTF, GLB, 3MF |
| **CAD** | STEP, STP, IGES, IGS | STL, OBJ |
| **Áudio** | MP3, WAV, FLAC, OGG, AAC, M4A, WMA | MP3, WAV, FLAC, OGG, AAC, M4A |
| **Vídeo** | MP4, AVI, MKV, MOV, WebM, FLV | MP4, AVI, MKV, MOV, WebM, MP3, GIF |
| **Apresentação** | PPTX, PPT | PDF, PNG |
| **Documento** | PDF, DOCX, TXT, HTML, MD | PDF, DOCX, TXT, HTML, MD, PNG |
| **eBook** | EPUB | PDF, TXT, HTML |
| **Dados** | CSV, JSON, XLSX, XLS | CSV, JSON, XLSX |
| **Config / Dev** | YAML, YML, TOML, XML, INI | JSON, YAML, TOML, XML, CSV |
| **Banco de dados** | SQLite, DB, SQL | CSV, JSON, XLSX, SQL, SQLite |
| **Notebook** | IPYNB | HTML, PDF, MD |
| **Fontes** | TTF, OTF, WOFF, WOFF2 | TTF, OTF, WOFF, WOFF2 |
| **Legendas** | SRT, VTT, ASS, SSA, SBV | SRT, VTT, ASS, SBV |
| **Médico** | DCM (DICOM) | PNG, JPG, TIFF |
| **Geoespacial** | GeoJSON, KML, GPX | GeoJSON, KML, GPX, CSV |
| **Arquivos** | ZIP, TAR, GZ, 7Z | ZIP, TAR, 7Z |
| **Email** | EML | PDF, TXT, HTML |
| **Agenda / Contatos** | ICS, VCF | CSV, JSON |
| **QR Code** | TXT (qualquer texto/URL) | PNG (QR Code) |

---

## Funcionalidades

- Interface drag & drop — sem instalação no cliente
- Download automático após conversão
- Arquivos temporários deletados logo após o download
- Dropdown de formatos filtrado automaticamente pela extensão do arquivo enviado
- Suporte a múltiplas categorias na mesma instância

---

## Requisitos

### Sistema

| Dependência | Instalação (macOS) | Instalação (Ubuntu/Debian) |
|-------------|--------------------|-----------------------------|
| Python 3.10+ | `brew install python` | `apt install python3` |
| FFmpeg | `brew install ffmpeg` | `apt install ffmpeg` |
| Ghostscript | `brew install ghostscript` | `apt install ghostscript` |
| LibreOffice *(opcional, PPTX→PDF)* | `brew install --cask libreoffice` | `apt install libreoffice` |
| gmsh *(opcional, STEP/IGES)* | `brew install gmsh` | `apt install gmsh` |

### Python

```
pip install -r requirements.txt
```

Principais dependências:

| Biblioteca | Uso |
|---|---|
| `Pillow`, `pillow-heif` | Imagens raster + HEIC/HEIF/AVIF |
| `rawpy` | Câmera RAW (CR2, NEF, ARW…) |
| `opencv-python`, `imageio` | HDR e EXR |
| `psd-tools` | Adobe PSD |
| `cairosvg`, `ezdxf` | SVG ↔ DXF, EPS, AI |
| `trimesh` | 3D (STL, OBJ, GLTF, GLB…) |
| `gmsh` *(opcional)* | CAD (STEP, IGES) |
| `PyMuPDF`, `python-docx`, `weasyprint` | Documentos PDF/DOCX |
| `pandas`, `openpyxl` | CSV, JSON, XLSX |
| `pyyaml`, `tomli`, `tomli-w` | YAML, TOML |
| `python-pptx` | Apresentações PPTX |
| `fonttools`, `brotli` | Fontes TTF/OTF/WOFF/WOFF2 |
| `pysubs2` | Legendas SRT/VTT/ASS |
| `ebooklib` | eBooks EPUB |
| `qrcode[pil]` | Geração de QR Code |
| `pydicom` | Imagens médicas DICOM |
| `nbconvert` | Jupyter Notebooks |
| `gpxpy` | Arquivos GPX |
| `py7zr` | Arquivos 7Z |
| `icalendar`, `vobject` | Calendário ICS e contatos VCF |

---

## Instalação e uso

```bash
# 1. Clonar
git clone git@github.com:Captando/Convertudo.git
cd Convertudo

# 2. Instalar dependências do sistema (macOS)
brew install ffmpeg ghostscript

# 3. Instalar dependências Python
cd backend
pip install -r requirements.txt

# 4. Iniciar o servidor
uvicorn main:app --reload

# 5. Abrir no navegador
open http://localhost:8000
```

O servidor serve o frontend automaticamente — **não é necessário** abrir o HTML separadamente.

---

## Estrutura do projeto

```
Convertudo/
├── backend/
│   ├── main.py                  # FastAPI — rotas da API e serving do frontend
│   ├── requirements.txt
│   └── converters/
│       ├── registry.py          # Mapa de conversões e roteador central
│       ├── image.py             # Pillow + rawpy (RAW de câmera)
│       ├── heic.py              # pillow-heif (HEIC, HEIF, AVIF)
│       ├── hdr.py               # opencv/imageio (EXR, HDR)
│       ├── audio.py             # FFmpeg
│       ├── video.py             # FFmpeg (MP4→GIF, extração de áudio)
│       ├── document.py          # PyMuPDF, python-docx, weasyprint, pandas
│       ├── threed.py            # trimesh (STL, OBJ, GLTF, GLB…)
│       ├── cad.py               # gmsh (STEP, IGES)
│       ├── vector.py            # ezdxf + cairosvg (DXF, SVG, EPS, AI, G-code)
│       ├── adobe.py             # psd-tools (PSD)
│       ├── presentation.py      # python-pptx + LibreOffice (PPTX)
│       ├── config.py            # pyyaml, tomli (YAML, TOML, XML, INI)
│       ├── database.py          # sqlite3 (SQLite, SQL)
│       ├── font.py              # fonttools (TTF, OTF, WOFF, WOFF2)
│       ├── subtitle.py          # pysubs2 (SRT, VTT, ASS, SBV)
│       ├── ebook.py             # ebooklib (EPUB)
│       ├── qrcode_conv.py       # qrcode (TXT → QR PNG)
│       ├── medical.py           # pydicom (DICOM)
│       ├── notebook.py          # nbconvert (IPYNB)
│       ├── geo.py               # gpxpy (GeoJSON, KML, GPX)
│       ├── archive.py           # zipfile, tarfile, py7zr (ZIP, TAR, 7Z)
│       ├── email_conv.py        # email stdlib (EML)
│       └── contact.py           # icalendar, vobject (ICS, VCF)
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

---

## API

### `GET /api/formats`

Retorna todos os formatos suportados agrupados por categoria.

```json
{
  "Imagem": {
    "png": ["jpg", "webp", "bmp", "gif", "tiff", "ico", "pdf"],
    "jpg": ["png", "webp", "bmp", "tiff", "pdf"]
  },
  "3D": {
    "stl": ["obj", "ply", "gltf", "glb", "3mf"]
  }
}
```

### `GET /api/outputs/{extension}`

Retorna os formatos de saída disponíveis para uma extensão específica.

```json
{
  "extension": "mp4",
  "outputs": ["avi", "mkv", "mov", "webm", "mp3", "gif"]
}
```

### `POST /api/convert`

Converte um arquivo.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `file` | `multipart/form-data` | Arquivo de entrada |
| `target_format` | `string` | Extensão de saída (ex: `"png"`, `"mp3"`) |

Retorna o arquivo convertido como download (`Content-Disposition: attachment`).

---

## Licença

MIT
