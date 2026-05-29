

const API_URL = 'http://127.0.0.1:5000/predict';

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewWrap = document.getElementById('previewWrap');
const previewImg = document.getElementById('previewImg');
const btnRemove = document.getElementById('btnRemove');
const btnAnalyze = document.getElementById('btnAnalyze');

const resultIdle = document.getElementById('resultIdle');
const resultLoading = document.getElementById('resultLoading');
const resultOutput = document.getElementById('resultOutput');
const resultStatusBar = document.getElementById('resultStatusBar');
const statusIcon = document.getElementById('statusIcon');
const statusLabel = document.getElementById('statusLabel');
const resultBody = document.getElementById('resultBody');

let selectedFile = null;

// ── FILE SELECTION ───────────────────────────────────────────────

dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

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

function handleFile(file) {
  const allowed = ['image/jpeg', 'image/png'];
  if (!allowed.includes(file.type)) {
    alert('Format tidak didukung. Gunakan file JPG atau PNG.');
    return;
  }

  selectedFile = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewWrap.classList.add('visible');
    dropZone.style.display = 'none';
  };
  reader.readAsDataURL(file);

  btnAnalyze.disabled = false;
  resetResult();
}

btnRemove.addEventListener('click', () => {
  selectedFile = null;
  previewImg.src = '';
  previewWrap.classList.remove('visible');
  dropZone.style.display = '';
  fileInput.value = '';
  btnAnalyze.disabled = true;
  resetResult();
});

// ── ANALYZE ──────────────────────────────────────────────────────

btnAnalyze.addEventListener('click', async () => {
  if (!selectedFile) return;

  setLoading(true);

  const formData = new FormData();
  formData.append('image', selectedFile);

  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      body: formData,
    });

    const contentType = res.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error(`Server mengembalikan respons non-JSON (Status: ${res.status}). Kemungkinan terjadi error internal server.`);
    }

    const data = await res.json();
    renderResult(data);

  } catch (err) {
    console.error("Error pada saat fetch:", err);
    renderError('Terjadi kesalahan komunikasi dengan server. Periksa apakah backend berjalan dengan normal.');
  } finally {
    setLoading(false);
  }
});

// ── RENDER ────────────────────────────────────────────────────────

function renderResult(data) {
  resultOutput.style.display = 'flex';

  // ── SUCCESS ──
  if (data.status === 'success') {
    setStatusBar('success', '✓', 'Analisis Berhasil');

    const freshnessClass = data.freshness === 'Fresh' ? 'fresh' : 'non-fresh';
    const freshnessFill = parseFloat(data.freshness_confidence) || 0;
    const speciesFill = parseFloat(data.species_confidence) || 0;

    resultBody.innerHTML = `
      <div class="result-metric">
        <div>
          <div class="metric-label">Kesegaran</div>
          <div class="confidence-bar-wrap">
            <div class="metric-value ${freshnessClass}">${data.freshness}</div>
            <div class="confidence-bar">
              <div class="confidence-fill ${freshnessClass}" id="fillFreshness" style="width:0%"></div>
            </div>
            <div style="font-size:12px;color:var(--gray-400);margin-top:4px;">Kepercayaan: ${data.freshness_confidence}</div>
          </div>
        </div>
      </div>
      <div class="result-metric">
        <div style="width:100%">
          <div class="metric-label">Spesies</div>
          <div class="confidence-bar-wrap">
            <div class="metric-value">${data.species}</div>
            <div class="confidence-bar">
              <div class="confidence-fill" id="fillSpecies" style="width:0%"></div>
            </div>
            <div style="font-size:12px;color:var(--gray-400);margin-top:4px;">Kepercayaan: ${data.species_confidence}</div>
          </div>
        </div>
      </div>
    `;

    // Animate bars with a short delay so transition fires
    requestAnimationFrame(() => {
      setTimeout(() => {
        const ff = document.getElementById('fillFreshness');
        const fs = document.getElementById('fillSpecies');
        if (ff) ff.style.width = freshnessFill + '%';
        if (fs) fs.style.width = speciesFill + '%';
      }, 60);
    });

    return;
  }

  // ── REJECTED ──
  if (data.status === 'rejected') {
    setStatusBar('rejected', '✕', 'Gambar Ditolak');
    resultBody.innerHTML = `
      <div class="result-reason">${data.reason}</div>
      ${data.species_confidence ? `
        <div class="result-metric">
          <span class="metric-label">Kepercayaan Spesies</span>
          <span class="metric-value">${data.species_confidence}</span>
        </div>` : ''}
    `;
    return;
  }

  // ── UNCERTAIN ──
  if (data.status === 'uncertain') {
    setStatusBar('uncertain', '⚠', 'Tidak Dapat Dipastikan');
    resultBody.innerHTML = `
      <div class="result-reason">${data.reason}</div>
      <div class="result-metric">
        <span class="metric-label">Spesies</span>
        <span class="metric-value">${data.species || '—'}</span>
      </div>
      <div class="result-metric">
        <span class="metric-label">Kepercayaan Spesies</span>
        <span class="metric-value">${data.species_confidence || '—'}</span>
      </div>
      <div class="result-metric">
        <span class="metric-label">Kepercayaan Kesegaran</span>
        <span class="metric-value">${data.freshness_confidence || '—'}</span>
      </div>
    `;
    return;
  }

  // ── ERROR (dari server) ──
  if (data.error) {
    renderError(data.error);
  }
}

function renderError(msg) {
  resultOutput.style.display = 'flex';
  setStatusBar('rejected', '✕', 'Terjadi Kesalahan');
  resultBody.innerHTML = `<div class=\"result-reason\">${msg}</div>`;
}

// ── HELPERS ───────────────────────────────────────────────────────

function setStatusBar(type, icon, label) {
  resultStatusBar.className = 'result-status-bar ' + type;
  statusIcon.textContent = icon;
  statusLabel.textContent = label;
}

// PERBAIKAN LOGIKA LOADING & KLIK NAVBAR
function setLoading(isLoading) {
  btnAnalyze.disabled = isLoading;
  if (isLoading) {
    resultIdle.style.display = 'none';
    resultLoading.style.display = 'flex';
    resultOutput.style.display = 'none';
  } else {
    resultLoading.style.display = 'none';
  }
}

function resetResult() {
  resultIdle.style.display = 'flex';
  resultLoading.style.display = 'none';
  resultOutput.style.display = 'none';
  resultBody.innerHTML = '';
}

// ── HAMBURGER MENU ────────────────────────────────────────────────
const menuToggle = document.getElementById('menuToggle');
const navMenu = document.querySelector('.nav-menu');

if (menuToggle && navMenu) {
  menuToggle.addEventListener('click', function (e) {
    e.stopPropagation();
    const isOpen = navMenu.classList.toggle('open');
    menuToggle.classList.toggle('open', isOpen);
    menuToggle.setAttribute('aria-expanded', String(isOpen));
  });

  // Tutup menu saat klik di luar
  document.addEventListener('click', function (e) {
    if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
      navMenu.classList.remove('open');
      menuToggle.classList.remove('open');
      menuToggle.setAttribute('aria-expanded', 'false');
    }
  });

  // Tutup menu saat salah satu link diklik
  navMenu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      navMenu.classList.remove('open');
      menuToggle.classList.remove('open');
      menuToggle.setAttribute('aria-expanded', 'false');
    });
  });
}
