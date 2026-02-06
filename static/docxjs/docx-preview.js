(function () {

    function getQueryParam(name) {
        const params = new URLSearchParams(window.location.search);
        return params.get(name);
    }

    const fileUrl = getQueryParam('file');

    const container = document.getElementById("docx_container");
    const errorEl = document.getElementById("error");
    const zoomControl = document.getElementById("zoomControl");
    const downloadBtn = document.getElementById("downloadBtn");
    const openBtn = document.getElementById("openBtn");
    const closeBtn = document.getElementById("closeBtn");

    if (!fileUrl) {
        errorEl.style.display = "block";
        errorEl.innerText = "No file specified. Use ?file=<your.docx>";
        return;
    }

    // Set buttons links
    downloadBtn.href = fileUrl;
    openBtn.href = fileUrl;

    // Close window or go back
    closeBtn.addEventListener("click", () => {
        if (window.opener) window.close();
        else history.back();
    });

    // Zoom
    zoomControl.addEventListener('change', function () {
        const scale = parseFloat(this.value);
        container.style.transform = `scale(${scale})`;
    });

    // Load DOCX file
    fetch(fileUrl)
        .then(response => {
            if (!response.ok) throw new Error("Failed to load file");
            return response.arrayBuffer();
        })
        .then(arrayBuffer => {
            container.innerHTML = "";

            docx.renderAsync(arrayBuffer, container, null, {
                className: "docxPage",
                inWrapper: true,
                ignoreFonts: false,
                ignoreStyles: false,
                breakPages: true,
                experimental: true
            });
        })
        .catch(err => {
            console.error(err);
            errorEl.style.display = "block";
            errorEl.innerText = "Error loading document: " + err.message;
        });

})();
