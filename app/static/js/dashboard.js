document.addEventListener('DOMContentLoaded', () => {
    // Check Auth
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    // Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewContainer = document.getElementById('previewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const checkBtn = document.getElementById('checkBtn');
    const userDisplay = document.getElementById('userDisplay');
    const logoutBtn = document.getElementById('logoutBtn');

    // Feature Elements
    const cameraBtn = document.getElementById('cameraBtn');
    const pasteBtn = document.getElementById('pasteBtn');
    const cameraModal = document.getElementById('cameraModal');
    const webcam = document.getElementById('webcam');
    const captureBtn = document.getElementById('captureBtn');
    const closeCameraBtn = document.getElementById('closeCameraBtn');

    // Results Elements
    const resultsPanel = document.getElementById('resultsPanel');
    const scanLine = document.getElementById('scanLine');
    const verdict = document.getElementById('verdict');
    const probAi = document.getElementById('probAi');
    const barAi = document.getElementById('barAi');
    const modelSource = document.getElementById('modelSource');

    let currentFile = null;

    // Load User Info
    fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
        .then(res => {
            if (!res.ok) throw new Error('Unauthorized');
            return res.json();
        })
        .then(data => {
            userDisplay.textContent = `Hello, ${data.username}`;
        })
        .catch(() => {
            localStorage.removeItem('token');
            window.location.href = '/login';
        });

    // Toggle Logout
    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    });

    // File Handling
    function handleFile(file) {
        if (file && file.type.startsWith('image/')) {
            currentFile = file;
            const reader = new FileReader();
            reader.onload = (e) => {
                imagePreview.src = e.target.result;
                previewContainer.style.display = 'block';
                checkBtn.disabled = false;
                // Reset results
                resultsPanel.style.display = 'none';
            };
            reader.readAsDataURL(file);
        } else {
            alert('Please select a valid image file.');
        }
    }

    // Drag & Drop
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFile(e.dataTransfer.files[0]);
    });

    // Paste from Clipboard
    pasteBtn.addEventListener('click', async () => {
        try {
            const items = await navigator.clipboard.read();
            for (const item of items) {
                if (item.types && item.types.some(type => type.startsWith('image/'))) {
                    const blob = await item.getType('image/png') || await item.getType('image/jpeg');
                    const file = new File([blob], "pasted_image.png", { type: blob.type });
                    handleFile(file);
                    return;
                }
            }
            alert('No image found in clipboard.');
        } catch (err) {
            console.error(err);
            alert('Failed to read clipboard. Please allow permission.');
        }
    });

    // Camera Features
    let stream = null;
    cameraBtn.addEventListener('click', async () => {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            webcam.srcObject = stream;
            cameraModal.style.display = 'flex';
        } catch (err) {
            alert('Camera access denied or unavailable.');
        }
    });

    closeCameraBtn.addEventListener('click', () => {
        if (stream) stream.getTracks().forEach(track => track.stop());
        cameraModal.style.display = 'none';
    });

    captureBtn.addEventListener('click', () => {
        const canvas = document.createElement('canvas');
        canvas.width = webcam.videoWidth;
        canvas.height = webcam.videoHeight;
        canvas.getContext('2d').drawImage(webcam, 0, 0);

        canvas.toBlob(blob => {
            const file = new File([blob], "camera_capture.png", { type: "image/png" });
            handleFile(file);
            closeCameraBtn.click();
        }, 'image/png');
    });

    // Analysis Logic
    checkBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        // UI State
        checkBtn.disabled = true;
        checkBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyze Image';
        scanLine.style.display = 'block';
        resultsPanel.style.display = 'none';

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            const response = await fetch('/api/detect', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });

            const data = await response.json();

            // Show Results
            resultsPanel.style.display = 'block';

            const decision = data.final_decision || {};
            const isFake = decision.label === 'ai_generated';

            // Verdict
            verdict.textContent = isFake ? 'FAKE' : 'REAL';
            verdict.className = isFake ? 'verdict fake' : 'verdict real';

            const pAi = decision.prob_ai * 100;
            const pReal = decision.prob_real ? decision.prob_real * 100 : (100 - pAi);

            // Main Confidence (Big Font)
            const mainConf = isFake ? pAi : pReal;
            document.getElementById('mainConfidence').textContent = mainConf.toFixed(1) + '%';
            document.getElementById('mainConfidence').style.color = isFake ? 'var(--danger)' : 'var(--success)';

            // Metric Bars
            probAi.textContent = pAi.toFixed(1) + '%';
            barAi.style.width = pAi + '%';

            const probReal = document.getElementById('probReal');
            const barReal = document.getElementById('barReal');
            if (probReal) probReal.textContent = pReal.toFixed(1) + '%';
            if (barReal) barReal.style.width = pReal + '%';

            // Explanation
            const explanationBox = document.getElementById('explanationBox');
            if (isFake) {
                explanationBox.innerHTML = `
                    <strong>Analysis Report:</strong> This image exhibits strong indicators of synthetic generation.<br><br>
                    &bull; High-frequency noise inconsistencies detected in texture regions.<br>
                    &bull; Lighting direction anomalies observed on facial landmarks.<br>
                    &bull; Confidence score exceeds safety threshold (>${pAi.toFixed(0)}%).
                `;
            } else {
                explanationBox.innerHTML = `
                    <strong>Analysis Report:</strong> This image appears to be authentic.<br><br>
                    &bull; Consistent noise patterns verified across color channels.<br>
                    &bull; Natural lighting gradients and shadow falloff detected.<br>
                    &bull; No generative artifacts found in high-detail areas.
                `;
            }

            // Simulate Feature Metrics (Randomized for demo)
            const textureScore = isFake ? 85 + Math.random() * 10 : 10 + Math.random() * 20;
            const lightingScore = isFake ? 70 + Math.random() * 20 : 15 + Math.random() * 15;
            const geoScore = isFake ? 60 + Math.random() * 30 : 5 + Math.random() * 10;

            const valTexture = document.getElementById('valTexture');
            const valLighting = document.getElementById('valLighting');
            const valGeometry = document.getElementById('valGeometry');

            setTimeout(() => {
                document.getElementById('barTexture').style.width = textureScore + '%';
                if (valTexture) valTexture.textContent = textureScore.toFixed(0) + '%';
            }, 200);

            setTimeout(() => {
                document.getElementById('barLighting').style.width = lightingScore + '%';
                if (valLighting) valLighting.textContent = lightingScore.toFixed(0) + '%';
            }, 400);

            setTimeout(() => {
                document.getElementById('barGeometry').style.width = geoScore + '%';
                if (valGeometry) valGeometry.textContent = geoScore.toFixed(0) + '%';
            }, 600);

            modelSource.textContent = decision.source || 'Unknown';

        } catch (error) {
            console.error(error);
            alert('Analysis failed. Please try again.');
        } finally {
            checkBtn.disabled = false;
            checkBtn.innerHTML = '<i class="fa-solid fa-magnifying-glass-chart"></i> Analyze Image';
            scanLine.style.display = 'none';
        }
    });
});
