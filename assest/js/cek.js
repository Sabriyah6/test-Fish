const API_SPECIES = 'https://backend-fish-freshness.onrender.com/predict-species';
const API_FRESHNESS = 'https://backend-fish-freshness.onrender.com/predict-freshness';

// ── SPECIES SECTION ───────────────────────────────────────────────
const dropZoneSpecies = document.getElementById('dropZoneSpecies');
const fileInputSpecies = document.getElementById('fileInputSpecies');
const previewWrapSpecies = document.getElementById('previewWrapSpecies');
const previewImgSpecies = document.getElementById('previewImgSpecies');
const btnRemoveSpecies = document.getElementById('btnRemoveSpecies');
const btnAnalyzeSpecies = document.getElementById('btnAnalyzeSpecies');
const resultIdleSpecies = document.getElementById('resultIdleSpecies');
const resultLoadingSpecies = document.getElementById('resultLoadingSpecies');
const resultOutputSpecies = document.getElementById('resultOutputSpecies');
const resultStatusBarSpecies = document.getElementById('resultStatusBarSpecies');
const statusIconSpecies = document.getElementById('statusIconSpecies');
const statusLabelSpecies = document.getElementById('statusLabelSpecies');
const resultBodySpecies = document.getElementById('resultBodySpecies');

// ── FRESHNESS SECTION ─────────────────────────────────────────────
const dropZoneFreshness = document.getElementById('dropZoneFreshness');
const fileInputFreshness = document.getElementById('fileInputFreshness');
const previewWrapFreshness = document.getElementById('previewWrapFreshness');
const previewImgFreshness = document.getElementById('previewImgFreshness');
const btnRemoveFreshness = document.getElementById('btnRemoveFreshness');
const btnAnalyzeFreshness = document.getElementById('btnAnalyzeFreshness');
const resultIdleFreshness = document.getElementById('resultIdleFreshness');
const resultLoadingFreshness = document.getElementById('resultLoadingFreshness');
const resultOutputFreshness = document.getElementById('resultOutputFreshness');
const resultStatusBarFreshness = document.getElementById('resultStatusBarFreshness');
const statusIconFreshness = document.getElementById('statusIconFreshness');
const statusLabelFreshness = document.getElementById('statusLabelFreshness');
const resultBodyFreshness = document.getElementById('resultBodyFreshness');

let selectedFileSpecies = null;
let selectedFileFreshness = null;

// ── GENERIC FILE HANDLER ──────────────────────────────────────────
function setupDropZone(dropZone, fileInput, previewWrap, previewImg, btnRemove, btnAnalyze, onFile) {
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => { if (fileInput.files[0]) onFile(fileInput.files[0]); });
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files[0]) onFile(e.dataTransfer.files[0]);
    });
    btnRemove.addEventListener('click', () => {
        previewImg.src = '';
        previewWrap.classList.remove('visible');
        dropZone.style.display = '';
        fileInput.value = '';
        btnAnalyze.disabled = true;
        if (dropZone === dropZoneSpecies) { selectedFileSpecies = null; resetResult('species'); }
        else { selectedFileFreshness = null; resetResult('freshness'); }
    });
}

function handleFileSpecies(file) {
    if (!validateFile(file)) return;
    selectedFileSpecies = file;
    loadPreview(file, previewImgSpecies, previewWrapSpecies, dropZoneSpecies);
    btnAnalyzeSpecies.disabled = false;
    resetResult('species');
}

function handleFileFreshness(file) {
    if (!validateFile(file)) return;
    selectedFileFreshness = file;
    loadPreview(file, previewImgFreshness, previewWrapFreshness, dropZoneFreshness);
    btnAnalyzeFreshness.disabled = false;
    resetResult('freshness');
}

function validateFile(file) {
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
        alert('Format tidak didukung. Gunakan JPG atau PNG.');
        return false;
    }
    return true;
}

function loadPreview(file, imgEl, wrapEl, dropZone) {
    const reader = new FileReader();
    reader.onload = (e) => {
        imgEl.src = e.target.result;
        wrapEl.classList.add('visible');
        dropZone.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

setupDropZone(dropZoneSpecies, fileInputSpecies, previewWrapSpecies, previewImgSpecies, btnRemoveSpecies, btnAnalyzeSpecies, handleFileSpecies);
setupDropZone(dropZoneFreshness, fileInputFreshness, previewWrapFreshness, previewImgFreshness, btnRemoveFreshness, btnAnalyzeFreshness, handleFileFreshness);

// ── ANALYZE SPECIES ───────────────────────────────────────────────
btnAnalyzeSpecies.addEventListener('click', async () => {
    if (!selectedFileSpecies) return;
    setLoading('species', true);
    const formData = new FormData();
    formData.append('image', selectedFileSpecies);
    try {
        const res = await fetch(API_SPECIES, { method: 'POST', body: formData });
        const data = await res.json();
        renderSpeciesResult(data);
    } catch (err) {
        renderError('species', 'Terjadi kesalahan komunikasi dengan server.');
    } finally {
        setLoading('species', false);
    }
});

// ── ANALYZE FRESHNESS ─────────────────────────────────────────────
btnAnalyzeFreshness.addEventListener('click', async () => {
    if (!selectedFileFreshness) return;
    setLoading('freshness', true);
    const formData = new FormData();
    formData.append('image', selectedFileFreshness);
    try {
        const res = await fetch(API_FRESHNESS, { method: 'POST', body: formData });
        const data = await res.json();
        renderFreshnessResult(data);
    } catch (err) {
        renderError('freshness', 'Terjadi kesalahan komunikasi dengan server.');
    } finally {
        setLoading('freshness', false);
    }
});

// ── RENDER SPECIES ────────────────────────────────────────────────
function renderSpeciesResult(data) {
    resultOutputSpecies.style.display = 'flex';
    if (data.status === 'success') {
        setStatusBar(resultStatusBarSpecies, statusIconSpecies, statusLabelSpecies, 'success', '✓', 'Spesies Terdeteksi');
        const fill = parseFloat(data.confidence) || 0;
        resultBodySpecies.innerHTML = `
            <div class="result-metric">
                <div style="width:100%">
                    <div class="metric-label">Spesies</div>
                    <div class="confidence-bar-wrap">
                        <div class="metric-value">${data.species}</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill" id="fillSpecies" style="width:0%"></div>
                        </div>
                        <div style="font-size:12px;color:var(--gray-400);margin-top:4px;">Kepercayaan: ${data.confidence}</div>
                    </div>
                </div>
            </div>`;
        requestAnimationFrame(() => setTimeout(() => {
            const el = document.getElementById('fillSpecies');
            if (el) el.style.width = fill + '%';
        }, 60));
        return;
    }
    if (data.status === 'rejected') {
        setStatusBar(resultStatusBarSpecies, statusIconSpecies, statusLabelSpecies, 'rejected', '✕', 'Spesies Tidak Dikenali');
        resultBodySpecies.innerHTML = `<div class="result-reason">${data.reason}</div>`;
        return;
    }
    if (data.error) renderError('species', data.error);
}

// ── RENDER FRESHNESS ──────────────────────────────────────────────
function renderFreshnessResult(data) {
    resultOutputFreshness.style.display = 'flex';
    if (data.status === 'success') {
        setStatusBar(resultStatusBarFreshness, statusIconFreshness, statusLabelFreshness, 'success', '✓', 'Analisis Berhasil');
        const freshnessClass = data.freshness === 'Fresh' ? 'fresh' : 'non-fresh';
        const fill = parseFloat(data.confidence) || 0;
        resultBodyFreshness.innerHTML = `
            <div class="result-metric">
                <div>
                    <div class="metric-label">Kesegaran</div>
                    <div class="confidence-bar-wrap">
                        <div class="metric-value ${freshnessClass}">${data.freshness}</div>
                        <div class="confidence-bar">
                            <div class="confidence-fill ${freshnessClass}" id="fillFreshness" style="width:0%"></div>
                        </div>
                        <div style="font-size:12px;color:var(--gray-400);margin-top:4px;">Kepercayaan: ${data.confidence}</div>
                    </div>
                </div>
            </div>
            <div class="result-metric">
                <div style="width:100%">
                    <div class="metric-label">Terdeteksi dari</div>
                    <div class="metric-value">${data.part || '—'}</div>
                </div>
            </div>`;
        requestAnimationFrame(() => setTimeout(() => {
            const el = document.getElementById('fillFreshness');
            if (el) el.style.width = fill + '%';
        }, 60));
        return;
    }
    if (data.status === 'uncertain') {
        setStatusBar(resultStatusBarFreshness, statusIconFreshness, statusLabelFreshness, 'uncertain', '⚠', 'Tidak Dapat Dipastikan');
        resultBodyFreshness.innerHTML = `<div class="result-reason">${data.reason}</div>`;
        return;
    }
    if (data.error) renderError('freshness', data.error);
}

// ── HELPERS ───────────────────────────────────────────────────────
function setStatusBar(bar, iconEl, labelEl, type, icon, label) {
    bar.className = 'result-status-bar ' + type;
    iconEl.textContent = icon;
    labelEl.textContent = label;
}

function setLoading(section, isLoading) {
    const idle = section === 'species' ? resultIdleSpecies : resultIdleFreshness;
    const loading = section === 'species' ? resultLoadingSpecies : resultLoadingFreshness;
    const output = section === 'species' ? resultOutputSpecies : resultOutputFreshness;
    const btn = section === 'species' ? btnAnalyzeSpecies : btnAnalyzeFreshness;
    btn.disabled = isLoading;
    if (isLoading) { idle.style.display = 'none'; loading.style.display = 'flex'; output.style.display = 'none'; }
    else { loading.style.display = 'none'; }
}

function resetResult(section) {
    const idle = section === 'species' ? resultIdleSpecies : resultIdleFreshness;
    const loading = section === 'species' ? resultLoadingSpecies : resultLoadingFreshness;
    const output = section === 'species' ? resultOutputSpecies : resultOutputFreshness;
    const body = section === 'species' ? resultBodySpecies : resultBodyFreshness;
    idle.style.display = 'flex';
    loading.style.display = 'none';
    output.style.display = 'none';
    body.innerHTML = '';
}

function renderError(section, msg) {
    const output = section === 'species' ? resultOutputSpecies : resultOutputFreshness;
    const bar = section === 'species' ? resultStatusBarSpecies : resultStatusBarFreshness;
    const icon = section === 'species' ? statusIconSpecies : statusIconFreshness;
    const label = section === 'species' ? statusLabelSpecies : statusLabelFreshness;
    const body = section === 'species' ? resultBodySpecies : resultBodyFreshness;
    output.style.display = 'flex';
    setStatusBar(bar, icon, label, 'rejected', '✕', 'Terjadi Kesalahan');
    body.innerHTML = `<div class="result-reason">${msg}</div>`;
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
    document.addEventListener('click', function (e) {
        if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
            navMenu.classList.remove('open');
            menuToggle.classList.remove('open');
            menuToggle.setAttribute('aria-expanded', 'false');
        }
    });
    navMenu.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () {
            navMenu.classList.remove('open');
            menuToggle.classList.remove('open');
            menuToggle.setAttribute('aria-expanded', 'false');
        });
    });
}