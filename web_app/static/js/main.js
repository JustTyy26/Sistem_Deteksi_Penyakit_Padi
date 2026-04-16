// ========================================
// DOM Elements
// ========================================
const elements = {
    // Tabs
    tabBtns: document.querySelectorAll('.tab-btn'),
    cameraTab: document.getElementById('camera-tab'),
    uploadTab: document.getElementById('upload-tab'),

    // Camera
    video: document.getElementById('camera-video'),
    canvas: document.getElementById('camera-canvas'),
    cameraPlaceholder: document.getElementById('camera-placeholder'),
    startCameraBtn: document.getElementById('start-camera-btn'),
    captureBtn: document.getElementById('capture-btn'),
    switchCameraBtn: document.getElementById('switch-camera-btn'),

    // Upload
    dropZone: document.getElementById('drop-zone'),
    fileInput: document.getElementById('file-input'),
    uploadPlaceholder: document.getElementById('upload-placeholder'),
    previewImage: document.getElementById('preview-image'),
    uploadBtn: document.getElementById('upload-btn'),

    // Captured Preview
    capturedPreview: document.getElementById('captured-preview'),
    capturedImage: document.getElementById('captured-image'),
    retakeBtn: document.getElementById('retake-btn'),
    diagnoseBtn: document.getElementById('diagnose-btn'),

    // Result
    loading: document.getElementById('loading'),
    resultCard: document.getElementById('result-card'),
    resultOriginal: document.getElementById('result-original'),
    resultMask: document.getElementById('result-mask'),
    diseaseName: document.getElementById('disease-name'),
    diseaseNameId: document.getElementById('disease-name-id'),
    severity: document.getElementById('severity'),
    confidence: document.getElementById('confidence'),
    damageRatio: document.getElementById('damage-ratio'),
    diseaseDesc: document.getElementById('disease-desc'),
    diseaseTreatment: document.getElementById('disease-treatment'),
    alertMessage: document.getElementById('alert-message'),
    newScanBtn: document.getElementById('new-scan-btn'),

    // Model
    modelSelect: document.getElementById('model-select')
};

// ========================================
// State
// ========================================
let state = {
    stream: null,
    facingMode: 'environment', // 'user' untuk kamera depan
    capturedImageData: null,
    uploadedFile: null
};

// ========================================
// Tab Navigation
// ========================================
elements.tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;

        // Update active tab button
        elements.tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Show corresponding tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabId}-tab`).classList.add('active');

        // Reset state
        hideResult();
        hideCapturedPreview();
    });
});

// ========================================
// Camera Functions
// ========================================
async function startCamera() {
    try {
        // Hentikan stream sebelumnya jika ada
        stopCamera();

        const constraints = {
            video: {
                facingMode: state.facingMode,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };

        state.stream = await navigator.mediaDevices.getUserMedia(constraints);
        elements.video.srcObject = state.stream;
        elements.video.classList.add('active');
        elements.cameraPlaceholder.classList.add('hidden');

        elements.startCameraBtn.innerHTML = '<span>⏹️</span> Stop Kamera';
        elements.captureBtn.disabled = false;

        // Tampilkan tombol switch jika ada lebih dari 1 kamera
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(d => d.kind === 'videoinput');
        if (videoDevices.length > 1) {
            elements.switchCameraBtn.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error accessing camera:', error);
        alert('Tidak dapat mengakses kamera. Pastikan Anda memberikan izin akses kamera.');
    }
}

function stopCamera() {
    if (state.stream) {
        state.stream.getTracks().forEach(track => track.stop());
        state.stream = null;
    }
    elements.video.srcObject = null;
    elements.video.classList.remove('active');
    elements.cameraPlaceholder.classList.remove('hidden');
    elements.startCameraBtn.innerHTML = '<span>🎥</span> Mulai Kamera';
    elements.captureBtn.disabled = true;
    elements.switchCameraBtn.style.display = 'none';
}

function capturePhoto() {
    const ctx = elements.canvas.getContext('2d');
    elements.canvas.width = elements.video.videoWidth;
    elements.canvas.height = elements.video.videoHeight;
    ctx.drawImage(elements.video, 0, 0);

    state.capturedImageData = elements.canvas.toDataURL('image/jpeg', 0.9);
    elements.capturedImage.src = state.capturedImageData;

    showCapturedPreview();
    stopCamera();
}

function switchCamera() {
    state.facingMode = state.facingMode === 'environment' ? 'user' : 'environment';
    startCamera();
}

// Camera event listeners
elements.startCameraBtn.addEventListener('click', () => {
    if (state.stream) {
        stopCamera();
    } else {
        startCamera();
    }
});

elements.captureBtn.addEventListener('click', capturePhoto);
elements.switchCameraBtn.addEventListener('click', switchCamera);
elements.retakeBtn.addEventListener('click', () => {
    hideCapturedPreview();
    startCamera();
});

elements.diagnoseBtn.addEventListener('click', () => {
    if (state.capturedImageData) {
        predict(state.capturedImageData, 'base64');
    }
});

// ========================================
// Upload Functions
// ========================================
elements.dropZone.addEventListener('click', () => {
    elements.fileInput.click();
});

elements.dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.dropZone.classList.add('dragover');
});

elements.dropZone.addEventListener('dragleave', () => {
    elements.dropZone.classList.remove('dragover');
});

elements.dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.dropZone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

elements.fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    // Validasi tipe file
    if (!file.type.startsWith('image/')) {
        alert('Silakan pilih file gambar (JPG, PNG)');
        return;
    }

    // Validasi ukuran (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        alert('Ukuran file maksimal 10MB');
        return;
    }

    state.uploadedFile = file;

    // Preview
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.previewImage.src = e.target.result;
        elements.previewImage.style.display = 'block';
        elements.uploadPlaceholder.classList.add('hidden');
        elements.uploadBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

elements.uploadBtn.addEventListener('click', () => {
    if (state.uploadedFile) {
        predict(state.uploadedFile, 'file');
    }
});

// ========================================
// Prediction
// ========================================
async function predict(imageData, type) {
    showLoading();
    hideResult();

    const model = elements.modelSelect.value;

    try {
        let response;

        if (type === 'file') {
            // Upload file
            const formData = new FormData();
            formData.append('image', imageData);
            formData.append('model', model);

            response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });
        } else {
            // Base64 dari kamera
            response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    image: imageData,
                    model: model
                })
            });
        }

        const result = await response.json();

        if (result.error) {
            throw new Error(result.error);
        }

        displayResult(result);
    } catch (error) {
        console.error('Prediction error:', error);
        alert('Terjadi kesalahan: ' + error.message);
        hideLoading();
    }
}

// ========================================
// Display Result
// ========================================
function displayResult(result) {
    hideLoading();

    // Display images
    if (result.images) {
        elements.resultOriginal.src = result.images.original;
        elements.resultMask.src = result.images.mask;
    }

    // Disease name
    elements.diseaseName.textContent = result.disease;
    elements.diseaseNameId.textContent = `(${result.disease_id})`;

    // Severity
    elements.severity.textContent = `${result.severity.label} (Grade ${result.severity.grade})`;
    elements.severity.style.color = result.severity.color;

    // Stats
    elements.confidence.textContent = `${result.confidence}%`;
    elements.damageRatio.textContent = `${result.severity.ratio}%`;

    // Info
    elements.diseaseDesc.textContent = result.deskripsi;
    elements.diseaseTreatment.textContent = result.penanganan;

    // Alert based on validity and severity
    elements.alertMessage.className = 'alert';

    // Cek apakah prediksi valid (gambar adalah daun padi)
    if (result.warning || result.is_valid_prediction === false) {
        elements.alertMessage.classList.add('alert-danger');
        elements.alertMessage.textContent = `⚠️ PERINGATAN: ${result.warning || 'Gambar tidak terdeteksi sebagai daun padi. Gunakan foto daun padi yang jelas.'}`;
    } else if (result.disease === 'Healthy Rice Leaf') {
        elements.alertMessage.classList.add('alert-success');
        elements.alertMessage.textContent = '✅ TANAMAN SEHAT: Lanjutkan perawatan rutin.';
    } else if (result.severity.grade >= 2) {
        elements.alertMessage.classList.add('alert-danger');
        elements.alertMessage.textContent = '⚠️ PERINGATAN: Infeksi meluas! Lakukan pengendalian segera.';
    } else {
        elements.alertMessage.classList.add('alert-warning');
        elements.alertMessage.textContent = 'ℹ️ SARAN: Pantau terus perkembangan bercak.';
    }

    // Add border color based on validity and severity
    elements.resultCard.style.borderLeftWidth = '5px';
    elements.resultCard.style.borderLeftStyle = 'solid';

    // Jika tidak valid, border merah
    if (result.warning || result.is_valid_prediction === false) {
        elements.resultCard.style.borderLeftColor = '#FF1744';
    } else {
        elements.resultCard.style.borderLeftColor = result.severity.color;
    }

    elements.resultCard.style.display = 'block';

    // Scroll to result
    elements.resultCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ========================================
// UI Helpers
// ========================================
function showCapturedPreview() {
    elements.capturedPreview.style.display = 'block';
}

function hideCapturedPreview() {
    elements.capturedPreview.style.display = 'none';
    state.capturedImageData = null;
}

function showLoading() {
    elements.loading.style.display = 'block';
}

function hideLoading() {
    elements.loading.style.display = 'none';
}

function hideResult() {
    elements.resultCard.style.display = 'none';
}

function resetUpload() {
    elements.previewImage.style.display = 'none';
    elements.uploadPlaceholder.classList.remove('hidden');
    elements.uploadBtn.disabled = true;
    elements.fileInput.value = '';
    state.uploadedFile = null;
}

// New scan button
elements.newScanBtn.addEventListener('click', () => {
    hideResult();
    hideCapturedPreview();
    resetUpload();

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ========================================
// Initialize
// ========================================
console.log('🌾 Sistem Deteksi Penyakit Padi - Ready');
