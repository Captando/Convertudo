# Convertudo

Conversor universal de arquivos — Web App que converte qualquer formato para outro, diretamente no navegador.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## Formatos suportados

| Categoria | Entrada | Saída |
|-----------|---------|-------|
| **Imagem** | PNG, JPG, JPEG, WebP, BMP, GIF, TIFF, ICO | PNG, JPG, WebP, BMP, GIF, TIFF, ICO, PDF |
| **Câmera RAW** | CR2, NEF, ARW, DNG, RAF, ORF, RW2 | PNG, JPG, TIFF |
| **Adobe** | PSD, AI, EPS | PNG, JPG, PDF, SVG |
| **Vetor / CNC / Plotter** | SVG, DXF, G-code | SVG, DXF, PNG, PDF, EPS, TXT |
| **3D** | STL, OBJ, PLY, GLTF, GLB, 3MF, FBX, OFF | STL, OBJ, PLY, GLTF, GLB, 3MF |
| **Áudio** | MP3, WAV, FLAC, OGG, AAC, M4A, WMA | MP3, WAV, FLAC, OGG, AAC, M4A |
| **Vídeo** | MP4, AVI, MKV, MOV, WebM, FLV | MP4, AVI, MKV, MOV, WebM, MP3, GIF |
| **Documento** | PDF, DOCX, TXT, HTML, MD | PDF, DOCX, TXT, HTML, MD, PNG |
| **Dados** | CSV, JSON, XLSX, XLS | CSV, JSON, XLSX |

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

### Python

```
fastapi
uvicorn[standard]
python-multipart
Pillow
PyMuPDF
python-docx
weasyprint
markdown
pandas
openpyxl
rawpy
numpy
psd-tools
cairosvg
ezdxf
trimesh
```

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
│       ├── audio.py             # FFmpeg
│       ├── video.py             # FFmpeg (MP4→GIF, extração de áudio)
│       ├── document.py          # PyMuPDF, python-docx, weasyprint, pandas
│       ├── threed.py            # trimesh (STL, OBJ, GLTF, GLB…)
│       ├── vector.py            # ezdxf + cairosvg (DXF, SVG, EPS, AI, G-code)
│       └── adobe.py             # psd-tools (PSD)
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
