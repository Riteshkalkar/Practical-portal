// viewer.js
function openFilePreview(fileUrl) {
    const viewer = document.getElementById("viewerContainer");
    const previewBox = document.getElementById("filePreview");

    previewBox.innerHTML = "";
    viewer.style.display = "block";
    viewer.scrollIntoView({ behavior: "smooth" });

    const lower = fileUrl.toLowerCase();

    if (lower.endsWith(".pdf")) {
        renderPDF(fileUrl, previewBox);
    } else if (lower.endsWith(".docx")) {
        renderDOCX(fileUrl, previewBox);
    } else if (lower.match(/\.(jpg|jpeg|png|gif)$/)) {
        previewBox.innerHTML = `<img src="${fileUrl}" class="img-fluid rounded shadow">`;
    } else if (lower.endsWith(".txt")) {
        fetch(fileUrl)
            .then(res => res.text())
            .then(text => {
                previewBox.innerHTML = `<pre class="text-viewer">${text}</pre>`;
            })
            .catch(err => {
                previewBox.innerHTML = `<p class="text-danger">⚠ Failed to load TXT file. <a href="${fileUrl}" download>Download</a></p>`;
                console.error(err);
            });
    } else {
        previewBox.innerHTML = `
            <p class="text-danger">⚠ Unsupported file type</p>
            <a href="${fileUrl}" class="btn btn-primary" download>Download File</a>
        `;
    }
}

function renderPDF(url, container) {
    container.innerHTML = "<p>Loading PDF...</p>";

    pdfjsLib.getDocument(url).promise
        .then(pdf => {
            container.innerHTML = "";
            pdf.getPage(1).then(page => {
                const canvas = document.createElement("canvas");
                const ctx = canvas.getContext("2d");
                container.appendChild(canvas);

                const viewport = page.getViewport({ scale: 1.3 });
                canvas.height = viewport.height;
                canvas.width = viewport.width;

                page.render({ canvasContext: ctx, viewport: viewport });
            });
        })
        .catch(err => {
            container.innerHTML = `<p class="text-danger">⚠ Failed to load PDF. <a href="${url}" download>Download</a></p>`;
            console.error(err);
        });
}

function renderDOCX(url, container) {
    container.innerHTML = "<p>Loading DOCX...</p>";

    fetch(url)
        .then(res => res.arrayBuffer())
        .then(buffer => {
            container.innerHTML = ""; // clear loading text
            const docxContainer = document.createElement("div");
            container.appendChild(docxContainer);

            // Proper docx-preview usage
            docx.renderAsync(buffer, docxContainer, {
                className: "docx-preview"
            }).catch(err => {
                container.innerHTML = `<p class="text-danger">⚠ Failed to load DOCX. <a href="${url}" download>Download</a></p>`;
                console.error(err);
            });
        })
        .catch(err => {
            container.innerHTML = `<p class="text-danger">⚠ Failed to fetch DOCX. <a href="${url}" download>Download</a></p>`;
            console.error(err);
        });
}
