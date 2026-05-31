const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewWrap = document.getElementById('previewWrap');
const previewImg = document.getElementById('previewImg');
const btnRemove = document.getElementById('btnRemove');
const btnAnalyze = document.getElementById('btnAnalyze');

const resultIdle = document.getElementById('resultIdle');
const resultLoading = document.getElementById('resultLoading');
const resultOutput = document.getElementById('resultOutput');

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

// ── HELPERS ───────────────────────────────────────────────────────

function resetResult() {
  resultIdle.style.display = 'flex';
  resultLoading.style.display = 'none';
  resultOutput.style.display = 'none';
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
