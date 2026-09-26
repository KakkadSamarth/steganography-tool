// static/js/main.js - StegoVault UI & Interactivity

function switchTab(tabName) {
    const encodeSection = document.getElementById("encode-section");
    const decodeSection = document.getElementById("decode-section");
    const tabButtons = document.querySelectorAll(".tab-pill");

    tabButtons.forEach(btn => btn.classList.remove("active"));

    if (tabName === "encode") {
        if (encodeSection) encodeSection.classList.remove("hidden");
        if (decodeSection) decodeSection.classList.add("hidden");
        if (tabButtons[0]) tabButtons[0].classList.add("active");
    } else {
        if (encodeSection) encodeSection.classList.add("hidden");
        if (decodeSection) decodeSection.classList.remove("hidden");
        if (tabButtons[1]) tabButtons[1].classList.add("active");
    }
}

// Format file size nicely
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Copy to Clipboard
function copyResultText() {
    const preElem = document.getElementById("decoded-result-text");
    const labelElem = document.getElementById("copy-btn-label");
    if (!preElem) return;

    const text = preElem.textContent || preElem.innerText;
    navigator.clipboard.writeText(text).then(() => {
        if (labelElem) {
            const original = labelElem.textContent;
            labelElem.textContent = "Copied!";
            setTimeout(() => {
                labelElem.textContent = original;
            }, 2000);
        }
    }).ca
    tch(err => {
        console.error("Clipboard copy failed: ", err);
    });
}

// Setup Drag & Drop and Preview Handlers
function setupFileHandler(inputId, dropZoneId, dropContentId, previewContainerId, mediaType) {
    const fileInput = document.getElementById(inputId);
    const dropZone = document.getElementById(dropZoneId);
    const dropContent = document.getElementById(dropContentId);
    const previewContainer = document.getElementById(previewContainerId);

    if (!fileInput || !dropZone) return;

    // Drag-over styling
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('dragover');
        });
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            fileInput.files = files;
            handleFileChange(files[0]);
        }
    });

    // Handle standard file selection
    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
            handleFileChange(fileInput.files[0]);
        }
    });

    function handleFileChange(file) {
        if (!file) return;

        if (previewContainer) {
            previewContainer.classList.remove('hidden');
        }
        if (dropContent) {
            dropContent.classList.add('hidden');
        }

        const objectUrl = URL.createObjectURL(file);

        if (mediaType === 'image') {
            const imgElem = previewContainer.querySelector('img');
            const nameBadge = previewContainer.querySelector('.meta-name');
            const sizeBadge = previewContainer.querySelector('.meta-size');
            if (imgElem) imgElem.src = objectUrl;
            if (nameBadge) nameBadge.textContent = file.name;
            if (sizeBadge) sizeBadge.textContent = formatFileSize(file.size);
        } else if (mediaType === 'audio') {
            const audioElem = previewContainer.querySelector('audio');
            const nameBadge = previewContainer.querySelector('.meta-name');
            const sizeBadge = previewContainer.querySelector('.meta-size');
            if (audioElem) {
                audioElem.src = objectUrl;
                audioElem.load();
            }
            if (nameBadge) nameBadge.textContent = file.name;
            if (sizeBadge) sizeBadge.textContent = formatFileSize(file.size);
        } else if (mediaType === 'video') {
            const videoElem = previewContainer.querySelector('video');
            const nameBadge = previewContainer.querySelector('.meta-name');
            const sizeBadge = previewContainer.querySelector('.meta-size');
            if (videoElem) {
                videoElem.src = objectUrl;
                videoElem.load();
            }
            if (nameBadge) nameBadge.textContent = file.name;
            if (sizeBadge) sizeBadge.textContent = formatFileSize(file.size);
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    // Setup file handlers for Image tool
    setupFileHandler("cover_image", "encode-drop-zone", "encode-drop-content", "image-encode-preview", "image");
    setupFileHandler("encoded_image", "decode-drop-zone", "decode-drop-content", "image-decode-preview", "image");

    // Setup file handlers for Audio tool
    setupFileHandler("cover_audio", "encode-drop-zone", "encode-drop-content", "audio-encode-preview", "audio");
    setupFileHandler("encoded_audio", "decode-drop-zone", "decode-drop-content", "audio-decode-preview", "audio");

    // Setup file handlers for Video tool
    setupFileHandler("cover_video", "encode-drop-zone", "encode-drop-content", "video-encode-preview", "video");
    setupFileHandler("encoded_video", "decode-drop-zone", "decode-drop-content", "video-decode-preview", "video");

    // Setup file handlers for Converter tool
    setupFileHandler("audio_file", "conv-audio-drop-zone", "conv-audio-drop-content", "conv-audio-preview", "audio");
    setupFileHandler("video_file", "conv-video-drop-zone", "conv-video-drop-content", "conv-video-preview", "video");

    // Secret text character counter
    const secretTextarea = document.getElementById("secret_text");
    const charCounter = document.getElementById("char-counter");
    if (secretTextarea && charCounter) {
        secretTextarea.addEventListener("input", () => {
            const count = secretTextarea.value.length;
            charCounter.textContent = `${count.toLocaleString()} character${count === 1 ? '' : 's'}`;
        });
    }

    // Loading overlay trigger on form submissions
    const overlay = document.getElementById("loading-overlay");
    const loadingText = document.getElementById("loading-text");

    const encodeForm = document.getElementById("encode-form");
    if (encodeForm && overlay) {
        encodeForm.addEventListener("submit", (e) => {
            if (loadingText) loadingText.textContent = "Encoding hidden message & generating payload...";
            overlay.classList.remove("hidden");
            // Auto hide overlay after download prompt starts (fallback after 4 seconds)
            setTimeout(() => {
                overlay.classList.add("hidden");
            }, 4000);
        });
    }

    const decodeForm = document.getElementById("decode-form");
    if (decodeForm && overlay) {
        decodeForm.addEventListener("submit", () => {
            if (loadingText) loadingText.textContent = "Scanning bits & discovering hidden text...";
            overlay.classList.remove("hidden");
        });
    }
});
