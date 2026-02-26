'use strict';

const API_BASE = '';

// Icons por categoria
const CATEGORY_ICONS = {
  'Imagem':    '🖼️',
  'RAW':       '📷',
  'Adobe':     '🎨',
  'Vetor/CNC': '📐',
  '3D':        '🧊',
  'Áudio':     '🎵',
  'Vídeo':     '🎬',
  'Documento': '📄',
  'Dados':     '📊',
};

const EXT_ICONS = {
  png: '🖼️', jpg: '🖼️', jpeg: '🖼️', webp: '🖼️', gif: '🎞️', bmp: '🖼️',
  tiff: '🖼️', ico: '🖼️', svg: '📐', dxf: '📐', gcode: '⚙️',
  psd: '🎨', ai: '🎨', eps: '🎨',
  cr2: '📷', nef: '📷', arw: '📷', dng: '📷', raf: '📷', orf: '📷', rw2: '📷',
  stl: '🧊', obj: '🧊', ply: '🧊', gltf: '🧊', glb: '🧊', '3mf': '🧊', fbx: '🧊', off: '🧊',
  mp3: '🎵', wav: '🎵', flac: '🎵', ogg: '🎵', aac: '🎵', m4a: '🎵', wma: '🎵',
  mp4: '🎬', avi: '🎬', mkv: '🎬', mov: '🎬', webm: '🎬', flv: '🎬',
  pdf: '📕', docx: '📝', txt: '📄', html: '🌐', md: '📝',
  csv: '📊', json: '📊', xlsx: '📊', xls: '📊',
};

// State
let selectedFile = null;
let formatsData = null;

// Elements
const dropZone     = document.getElementById('dropZone');
const fileInput    = document.getElementById('fileInput');
const stepUpload   = document.getElementById('step-upload');
const stepConfigure = document.getElementById('step-configure');
const stepResult   = document.getElementById('step-result');
const fileName     = document.getElementById('fileName');
const fileSize     = document.getElementById('fileSize');
const fileIcon     = document.getElementById('fileIcon');
const formatSelect = document.getElementById('formatSelect');
const btnConvert   = document.getElementById('btnConvert');
const btnChangeFile = document.getElementById('btnChangeFile');
const btnDownload  = document.getElementById('btnDownload');
const btnReset     = document.getElementById('btnReset');
const resultInfo   = document.getElementById('resultInfo');
const errorToast   = document.getElementById('errorToast');
const errorMessage = document.getElementById('errorMessage');
const toastClose   = document.getElementById('toastClose');

// Load formats on startup
(async () => {
  try {
    const resp = await fetch(`${API_BASE}/api/formats`);
    formatsData = await resp.json();
  } catch (e) {
    // Will show formats error when user tries to convert
  }
})();

// --- Drag & Drop ---

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

// --- File Handling ---

function handleFile(file) {
  selectedFile = file;
  const ext = getExt(file.name);

  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  fileIcon.textContent = EXT_ICONS[ext] || '📄';

  populateFormats(ext);
  showStep(stepConfigure);
}

function getExt(filename) {
  return filename.split('.').pop().toLowerCase();
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function populateFormats(ext) {
  formatSelect.innerHTML = '<option value="">Selecione o formato...</option>';
  btnConvert.disabled = true;

  if (!formatsData) {
    showError('Não foi possível carregar os formatos. Verifique se o servidor está rodando.');
    return;
  }

  // Encontrar os outputs para essa extensão
  let outputs = null;
  let inputCategory = null;

  for (const [category, exts] of Object.entries(formatsData)) {
    if (exts[ext]) {
      outputs = exts[ext];
      inputCategory = category;
      break;
    }
  }

  if (!outputs || outputs.length === 0) {
    const opt = document.createElement('option');
    opt.textContent = `Formato ".${ext}" não suportado`;
    opt.disabled = true;
    formatSelect.appendChild(opt);
    return;
  }

  // Agrupar outputs por categoria
  const grouped = {};
  for (const outExt of outputs) {
    let cat = 'Outros';
    for (const [c, exts] of Object.entries(formatsData)) {
      if (exts[outExt] !== undefined || Object.keys(exts).includes(outExt)) {
        cat = c;
        break;
      }
    }
    // Fallback: procurar em CATEGORY_ICONS
    if (cat === 'Outros') {
      for (const [c, icon] of Object.entries(CATEGORY_ICONS)) {
        // match by icon prefix rough check
      }
    }
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(outExt);
  }

  // Se só há uma categoria de saída, não usar optgroup
  const cats = Object.keys(grouped);
  if (cats.length === 1) {
    for (const outExt of grouped[cats[0]]) {
      const opt = document.createElement('option');
      opt.value = outExt;
      opt.textContent = `.${outExt.toUpperCase()}`;
      formatSelect.appendChild(opt);
    }
  } else {
    for (const [cat, exts] of Object.entries(grouped)) {
      const group = document.createElement('optgroup');
      group.label = (CATEGORY_ICONS[cat] || '') + ' ' + cat;
      for (const outExt of exts) {
        const opt = document.createElement('option');
        opt.value = outExt;
        opt.textContent = `.${outExt.toUpperCase()}`;
        group.appendChild(opt);
      }
      formatSelect.appendChild(group);
    }
  }
}

// --- Format Selection ---

formatSelect.addEventListener('change', () => {
  btnConvert.disabled = !formatSelect.value;
});

// --- Change File ---

btnChangeFile.addEventListener('click', () => {
  resetToUpload();
});

// --- Convert ---

btnConvert.addEventListener('click', async () => {
  if (!selectedFile || !formatSelect.value) return;

  const targetFormat = formatSelect.value;
  const btnText = btnConvert.querySelector('.btn-text');
  const btnSpinner = btnConvert.querySelector('.btn-spinner');

  btnConvert.disabled = true;
  btnText.textContent = 'Convertendo...';
  btnSpinner.classList.remove('hidden');

  try {
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('target_format', targetFormat);

    const resp = await fetch(`${API_BASE}/api/convert`, {
      method: 'POST',
      body: formData,
    });

    if (!resp.ok) {
      let detail = `Erro ${resp.status}`;
      try {
        const err = await resp.json();
        detail = err.detail || detail;
      } catch {}
      throw new Error(detail);
    }

    const blob = await resp.blob();
    const ext = getExt(selectedFile.name);
    const baseName = selectedFile.name.slice(0, -(ext.length + 1));
    const outName = `${baseName}.${targetFormat}`;

    const url = URL.createObjectURL(blob);
    btnDownload.href = url;
    btnDownload.download = outName;

    const inSize = formatBytes(selectedFile.size);
    const outSize = formatBytes(blob.size);
    resultInfo.textContent = `${selectedFile.name} → ${outName} · ${inSize} → ${outSize}`;

    showStep(stepResult);

  } catch (err) {
    showError(err.message || 'Erro inesperado na conversão');
    btnConvert.disabled = false;
    btnText.textContent = 'Converter';
    btnSpinner.classList.add('hidden');
  }
});

// --- Reset ---

btnReset.addEventListener('click', () => {
  resetToUpload();
});

function resetToUpload() {
  selectedFile = null;
  fileInput.value = '';
  formatSelect.innerHTML = '';
  btnConvert.querySelector('.btn-text').textContent = 'Converter';
  btnConvert.querySelector('.btn-spinner').classList.add('hidden');

  // Revogar URL do objeto anterior
  if (btnDownload.href && btnDownload.href.startsWith('blob:')) {
    URL.revokeObjectURL(btnDownload.href);
    btnDownload.href = '#';
  }

  showStep(stepUpload);
}

// --- Error Toast ---

function showError(msg) {
  errorMessage.textContent = msg;
  errorToast.classList.remove('hidden');
  clearTimeout(window._errorTimer);
  window._errorTimer = setTimeout(() => hideError(), 6000);
}

function hideError() {
  errorToast.classList.add('hidden');
}

toastClose.addEventListener('click', hideError);

// --- Step Navigation ---

function showStep(step) {
  [stepUpload, stepConfigure, stepResult].forEach(s => s.classList.remove('active'));
  step.classList.add('active');
}
