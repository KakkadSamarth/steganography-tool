// main.js
// Handles switching between the Encode/Decode tabs, and does a quick
// sanity check on the forms before they submit (the real validation
// still happens on the server in app.py - never trust the browser alone!).

function showTab(tabName) {
    const encodeSection = document.getElementById("encode-section");
    const decodeSection = document.getElementById("decode-section");
    const buttons = document.querySelectorAll(".tab-btn");

    buttons.forEach(function (btn) {
        btn.classList.remove("active");
    });

    if (tabName === "encode") {
        encodeSection.classList.remove("hidden");
        decodeSection.classList.add("hidden");
        buttons[0].classList.add("active");
    } else {
        encodeSection.classList.add("hidden");
        decodeSection.classList.remove("hidden");
        buttons[1].classList.add("active");
    }
}

// Simple client-side check: make sure a file was actually chosen
// before we bother sending the form to the server.
document.addEventListener("DOMContentLoaded", function () {
    const encodeForm = document.getElementById("encode-form");
    const decodeForm = document.getElementById("decode-form");

    encodeForm.addEventListener("submit", function (event) {
        const fileInput = document.getElementById("cover_image");
        const textInput = document.getElementById("secret_text");

        if (fileInput.files.length === 0) {
            alert("Please choose a cover image first.");
            event.preventDefault();
            return;
        }

        if (textInput.value.trim() === "") {
            alert("Please type a secret message.");
            event.preventDefault();
        }
    });

    decodeForm.addEventListener("submit", function (event) {
        const fileInput = document.getElementById("encoded_image");

        if (fileInput.files.length === 0) {
            alert("Please choose an encoded image first.");
            event.preventDefault();
        }
    });
});
