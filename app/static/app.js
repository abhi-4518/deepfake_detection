document.getElementById('imageInput').addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const preview = document.getElementById('preview');
            preview.src = e.target.result;
            preview.style.display = 'inline-block';
        }
        reader.readAsDataURL(file);
    }
});

document.getElementById('checkBtn').addEventListener('click', async function () {
    const fileInput = document.getElementById('imageInput');
    const resultDiv = document.getElementById('result');

    if (!fileInput.files[0]) {
        alert("Please select an image first.");
        return;
    }

    resultDiv.innerHTML = "<p>Analyzing...</p>";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("/api/detect", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            displayResult(data);
        } else {
            resultDiv.innerHTML = `<p class="error">Error: ${data.detail || "Unknown error"}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
    }
});

function displayResult(data) {
    const resultDiv = document.getElementById('result');
    const final = data.final_decision;

    let badgeClass = final.label === 'ai_generated' ? 'badge-ai' : 'badge-real';
    let labelText = final.label === 'ai_generated' ? 'Likely AI-Generated' : 'Likely Real';

    const html = `
        <h2>Result: <span class="badge ${badgeClass}">${labelText}</span></h2>
        <p><strong>Confidence (AI):</strong> ${(final.prob_ai * 100).toFixed(2)}%</p>
        <p><strong>Source:</strong> ${final.source} model</p>
        <hr>
        <details>
            <summary>Detailed Debug Info</summary>
            <pre>${JSON.stringify(data, null, 2)}</pre>
        </details>
    `;

    resultDiv.innerHTML = html;
}
