# Convertudo

Conversor universal de arquivos + downloader de mídia — Web App que converte qualquer formato para outro e baixa vídeos do YouTube, Instagram, TikTok e mais de 1000 sites.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## Funcionalidades

- **Conversor de arquivos** — drag & drop ou clique para selecionar, escolha o formato e baixe
- **Downloader de mídia** — cole um link do YouTube, Instagram, TikTok, Twitter/X, Facebook e +1000 sites
- Mais de **200 formatos** em **33 categorias**
- Seleção automática de conversor por extensão
- Arquivos temporários deletados logo após o download
- Sem envio de dados para terceiros — tudo processado no servidor local

---

## Formatos suportados

| Categoria | Entrada | Saída |
|-----------|---------|-------|
| **Imagem** | PNG, JPG, WebP, BMP, GIF, TIFF, ICO, HEIC, HEIF, AVIF, TGA, DDS, PCX, PPM, PGM | PNG, JPG, WebP, BMP, TIFF, PDF |
| **Câmera RAW** | CR2, NEF, ARW, DNG, RAF, ORF, RW2 | PNG, JPG, TIFF |
| **HDR / EXR** | EXR, HDR | PNG, JPG, TIFF, EXR |
| **Adobe** | PSD, AI, EPS | PNG, JPG, PDF, SVG |
| **Vetor / CNC / Plotter** | SVG, DXF, G-code | SVG, DXF, PNG, PDF, EPS, TXT |
| **3D** | STL, OBJ, PLY, GLTF, GLB, 3MF, FBX, OFF | STL, OBJ, PLY, GLTF, GLB, 3MF |
| **CAD** | STEP, STP, IGES, IGS | STL, OBJ |
| **Áudio** | MP3, WAV, FLAC, OGG, AAC, M4A, WMA, OPUS, AIFF, AIF, AMR, APE | MP3, WAV, FLAC, OGG, AAC, OPUS |
| **Vídeo** | MP4, AVI, MKV, MOV, WebM, FLV, TS, M2TS, 3GP, MPG, MPEG, WMV, ASF, MXF | MP4, AVI, MKV, MOV, WebM, MP3, GIF |
| **Apresentação** | PPTX, PPT | PDF, PNG |
| **Documento** | PDF, DOCX, TXT, HTML, MD | PDF, DOCX, TXT, HTML, MD, PNG |
| **Office aberto** | RTF, ODT, TEX | PDF, TXT, HTML |
| **OpenDocument** | ODS, ODP | CSV, JSON, XLSX / PDF, PNG |
| **eBook** | EPUB | PDF, TXT, HTML |
| **Dados** | CSV, JSON, XLSX, XLS | CSV, JSON, XLSX |
| **Big Data** | Parquet, JSONL, NDJSON, Feather, HDF5, H5 | CSV, JSON, Parquet |
| **Config / Dev** | YAML, YML, TOML, XML, INI, ENV, Properties, HCL | JSON, YAML, TOML, XML, CSV |
| **Banco de dados** | SQLite, DB, SQL | CSV, JSON, XLSX, SQL, SQLite |
| **Notebook** | IPYNB | HTML, PDF, MD |
| **Código-fonte** | PY, JS, JSX, TSX, JAVA, C, CPP, H, HPP, GO, RS, RB, PHP, CS, Swift, KT, SH, Lua, Dart, Scala, R | HTML, PDF, TXT, MD |
| **Fontes** | TTF, OTF, WOFF, WOFF2 | TTF, OTF, WOFF, WOFF2 |
| **Legendas** | SRT, VTT, ASS, SSA, SBV | SRT, VTT, ASS, SBV |
| **Médico** | DCM (DICOM) | PNG, JPG, TIFF |
| **Geoespacial** | GeoJSON, KML, GPX | GeoJSON, KML, GPX, CSV |
| **Arquivos** | ZIP, TAR, GZ, 7Z | ZIP, TAR, 7Z |
| **Email** | EML, MSG, MBOX | PDF, TXT, HTML |
| **Agenda / Contatos** | ICS, VCF | CSV, JSON |
| **Certificados SSL/TLS** | PEM, CRT, CER, DER, PFX, P12, KEY | PEM, DER, PFX |
| **Financeiro** | OFX, QFX, QIF | CSV, JSON |
| **Científico** | FITS, FIT, FTS, NetCDF (NC) | PNG, CSV, JSON |
| **Bioinformática** | FASTA, FA, FASTQ, FQ | CSV, TXT, FASTA |
| **Playlist** | M3U, M3U8 | JSON, TXT, CSV |
| **HAR** | HAR (HTTP Archive) | JSON, CSV |
| **QR Code** | TXT (qualquer texto/URL) | PNG (QR Code) |

---

## Downloader de mídia

Cole o link de qualquer vídeo na aba **🔗 URL** e escolha o formato e a qualidade.

| Plataforma | Observação |
|------------|-----------|
| YouTube | Vídeo + áudio até 1080p; playlists; shorts |
| Instagram | Reels, posts, stories |
| TikTok | Vídeos públicos |
| Twitter / X | Tweets com vídeo |
| Facebook | Vídeos públicos |
| Twitch | Clipes e VODs |
| Reddit | Vídeos do feed |
| Vimeo, Dailymotion | Vídeos públicos |
| +1000 sites | Via yt-dlp |

**Formatos de saída:** MP4, WebM, MP3, M4A
**Qualidades:** Melhor disponível, 1080p, 720p, 480p, 360p

> **Atenção:** Use apenas para conteúdo próprio ou com permissão. Respeite os direitos autorais e os Termos de Uso de cada plataforma.

---

## Requisitos do sistema

| Dependência | macOS | Ubuntu/Debian |
|-------------|-------|---------------|
| Python 3.10+ | `brew install python` | `apt install python3` |
| FFmpeg | `brew install ffmpeg` | `apt install ffmpeg` |
| Ghostscript | `brew install ghostscript` | `apt install ghostscript` |
| LibreOffice *(opcional — PPTX, ODT, TEX)* | `brew install --cask libreoffice` | `apt install libreoffice` |
| gmsh *(opcional — STEP/IGES)* | `brew install gmsh` | `apt install gmsh` |
| pdflatex *(opcional — TEX→PDF direto)* | MacTeX | `apt install texlive` |

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

O servidor serve o frontend automaticamente — não é necessário abrir o HTML separadamente.

---

## Principais dependências Python

| Biblioteca | Uso |
|---|---|
| `Pillow`, `pillow-heif` | Imagens raster + HEIC/HEIF/AVIF + TGA/DDS/PCX |
| `rawpy` | Câmera RAW (CR2, NEF, ARW…) |
| `opencv-python`, `imageio` | HDR e EXR |
| `psd-tools` | Adobe PSD |
| `cairosvg`, `ezdxf` | SVG ↔ DXF, EPS, AI |
| `trimesh` | 3D (STL, OBJ, GLTF, GLB…) |
| `gmsh` *(opcional)* | CAD (STEP, IGES) |
| `PyMuPDF`, `python-docx`, `weasyprint` | Documentos PDF/DOCX/HTML |
| `pandas`, `openpyxl` | CSV, JSON, XLSX |
| `pyarrow` | Parquet e Feather |
| `h5py` | HDF5 |
| `pyyaml`, `tomli`, `tomli-w` | YAML, TOML |
| `striprtf` | RTF |
| `python-pptx` | Apresentações PPTX |
| `Pygments` | Syntax highlight de código-fonte |
| `fonttools`, `brotli` | Fontes TTF/OTF/WOFF/WOFF2 |
| `pysubs2` | Legendas SRT/VTT/ASS |
| `ebooklib` | eBooks EPUB |
| `qrcode[pil]` | Geração de QR Code |
| `pydicom` | Imagens médicas DICOM |
| `nbconvert` | Jupyter Notebooks |
| `gpxpy` | Arquivos GPX |
| `py7zr` | Arquivos 7Z |
| `icalendar`, `vobject` | Calendário ICS e contatos VCF |
| `cryptography` | Certificados SSL/TLS (PEM, DER, PFX) |
| `ofxparse` | Arquivos financeiros OFX/QFX |
| `extract-msg` | E-mails Outlook .MSG |
| `astropy` | Imagens FITS (astronomia) |
| `netCDF4` | Arquivos NetCDF (clima, oceanografia) |
| `yt-dlp` | Downloader YouTube, Instagram, TikTok, +1000 sites |

---

## Estrutura do projeto

```
Convertudo/
├── backend/
│   ├── main.py                  # FastAPI — API e serving do frontend
│   ├── requirements.txt
│   └── converters/
│       ├── registry.py          # 33 categorias, 200+ formatos, roteador central
│       ├── image.py             # Pillow + rawpy (RAW)
│       ├── heic.py              # pillow-heif (HEIC, AVIF)
│       ├── hdr.py               # opencv/imageio (EXR, HDR)
│       ├── audio.py             # FFmpeg (MP3, FLAC, OPUS, APE…)
│       ├── video.py             # FFmpeg (MP4→GIF, extração de áudio…)
│       ├── document.py          # PyMuPDF, python-docx, weasyprint, pandas
│       ├── office.py            # LibreOffice CLI (RTF, ODT, ODS, ODP, TEX)
│       ├── threed.py            # trimesh (STL, OBJ, GLTF, GLB…)
│       ├── cad.py               # gmsh (STEP, IGES)
│       ├── vector.py            # ezdxf + cairosvg (DXF, SVG, EPS, AI, G-code)
│       ├── adobe.py             # psd-tools (PSD)
│       ├── presentation.py      # python-pptx + LibreOffice (PPTX)
│       ├── config.py            # YAML, TOML, XML, INI, ENV, HCL
│       ├── database.py          # sqlite3 (SQLite, SQL)
│       ├── bigdata.py           # pandas + pyarrow (Parquet, Feather, JSONL, HDF5)
│       ├── code.py              # Pygments (PY, JS, GO, RS, C, Java…)
│       ├── font.py              # fonttools (TTF, OTF, WOFF, WOFF2)
│       ├── subtitle.py          # pysubs2 (SRT, VTT, ASS, SBV)
│       ├── ebook.py             # ebooklib (EPUB)
│       ├── qrcode_conv.py       # qrcode (TXT → QR PNG)
│       ├── medical.py           # pydicom (DICOM)
│       ├── notebook.py          # nbconvert (IPYNB)
│       ├── geo.py               # gpxpy (GeoJSON, KML, GPX)
│       ├── archive.py           # zipfile, tarfile, py7zr (ZIP, TAR, 7Z)
│       ├── email_conv.py        # email stdlib + extract-msg (EML, MSG, MBOX)
│       ├── contact.py           # icalendar, vobject (ICS, VCF)
│       ├── cert.py              # cryptography (PEM, DER, PFX)
│       ├── financial.py         # ofxparse (OFX, QIF)
│       ├── scientific.py        # astropy + netCDF4 (FITS, NC)
│       ├── bio.py               # parser manual (FASTA, FASTQ)
│       ├── misc.py              # M3U/M3U8, HAR
│       └── downloader.py        # yt-dlp (YouTube, Instagram, TikTok…)
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
  "Imagem": { "png": ["jpg", "webp", "bmp", "pdf"], "jpg": ["png", "webp"] },
  "3D":     { "stl": ["obj", "ply", "gltf", "glb"] }
}
```

### `GET /api/outputs/{extension}`

Retorna os formatos de saída disponíveis para uma extensão.

```json
{ "extension": "mp4", "outputs": ["avi", "mkv", "mov", "webm", "mp3", "gif"] }
```

### `POST /api/convert`

Converte um arquivo.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `file` | `multipart/form-data` | Arquivo de entrada |
| `target_format` | `string` | Extensão de saída (ex: `"png"`, `"mp3"`) |

Retorna o arquivo convertido como download.

### `GET /api/info?url={url}`

Retorna metadados de uma URL de mídia (sem baixar).

```json
{ "title": "Nome do vídeo", "duration": 183, "uploader": "Canal", "extractor": "Youtube" }
```

### `POST /api/download`

Baixa mídia de uma URL.

| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `url` | `string` | — | URL do vídeo |
| `format` | `string` | `mp4` | `mp4` \| `webm` \| `mp3` \| `m4a` |
| `quality` | `string` | `best` | `best` \| `1080` \| `720` \| `480` \| `360` |

Retorna o arquivo de mídia como download.

---

## Licença

MIT
