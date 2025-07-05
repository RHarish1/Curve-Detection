// === DOM Element References ===
const fileInput = document.querySelector(".file-input"),
      previewImg = document.querySelector(".preview-img img"),
      filterButtons = document.querySelectorAll(".filter button"),
      filterName = document.querySelector(".filter-info .name"),
      filterValue = document.querySelector(".filter-info .value"),
      filterSlider = document.querySelector(".slider input"),
      rotateButtons = document.querySelectorAll(".rotate button"),
      chooseImgBtn = document.querySelector(".choose-img"),
      processBtn = document.querySelector(".save-img"),
      resetBtn = document.querySelector(".reset-filter"),
      deleteBtn = document.querySelector(".delete-img"),
      container = document.querySelector(".container");

let brightness = 100, saturation = 100, inversion = 0, grayscale = 0;
let rotate = 0, flipH = 1, flipV = 1;
let processedImage = null;
let hasProcessed = false;

const placeholderSrc = "static/image-placeholder.svg";

// === Utility Functions ===
function updatePreview() {
    previewImg.style.transform = `rotate(${rotate}deg) scale(${flipH}, ${flipV})`;
    previewImg.style.filter = `brightness(${brightness}%) saturate(${saturation}%) invert(${inversion}%) grayscale(${grayscale}%)`;
}

function resetAllFilters() {
    brightness = 100;
    saturation = 100;
    inversion = 0;
    grayscale = 0;
    rotate = 0;
    flipH = 1;
    flipV = 1;
    processedImage = null;
    hasProcessed = false;
    if (filterButtons.length > 0) filterButtons[0].click();
    updatePreview();
    setProcessState("Process Image", true);
}

function setProcessState(text, enabled) {
    processBtn.innerText = text;
    processBtn.disabled = !enabled;
    processBtn.style.opacity = enabled ? 1 : 0.5;
    processBtn.style.cursor = enabled ? "pointer" : "not-allowed";
}

// === Filter Controls ===
filterButtons.forEach(button => {
    button.addEventListener("click", () => {
        document.querySelector(".filter .active")?.classList.remove("active");
        button.classList.add("active");

        filterName.innerText = button.innerText;
        const id = button.id;
        const value = { brightness, saturation, inversion, grayscale }[id];
        filterSlider.max = (id === "brightness" || id === "saturation") ? 200 : 100;
        filterSlider.value = value;
        filterValue.innerText = `${value}%`;
    });
});

filterSlider.addEventListener("input", () => {
    const value = filterSlider.value;
    filterValue.innerText = `${value}%`;

    const id = document.querySelector(".filter .active")?.id;
    if (!id) return;

    if (id === "brightness") brightness = value;
    else if (id === "saturation") saturation = value;
    else if (id === "inversion") inversion = value;
    else if (id === "grayscale") grayscale = value;

    updatePreview();
});

// === Rotate / Flip Controls ===
rotateButtons.forEach(button => {
    button.addEventListener("click", () => {
        if (button.id === "left") rotate -= 90;
        else if (button.id === "right") rotate += 90;
        else if (button.id === "horizontal") flipH *= -1;
        else if (button.id === "vertical") flipV *= -1;

        updatePreview();
    });
});

// === File Upload ===
chooseImgBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (!file) return;
    hasProcessed = false;
    const reader = new FileReader();
    reader.onload = () => {
        previewImg.src = reader.result;
        resetAllFilters();
        container.classList.remove("disable");
    };
    reader.readAsDataURL(file);
});

// === Process & Download Button ===
processBtn.addEventListener("click", async () => {
    if (!previewImg.src || previewImg.src.includes("image-placeholder")) {
        alert("Please upload an image first.");
        return;
    }

    // 🔁 If already processed, just download the same image
    if (hasProcessed && processedImage) {
        const a = document.createElement("a");
        a.href = `data:image/png;base64,${processedImage}`;
        a.download = "processed_output.png";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        return;
    }

    // ⚙️ Otherwise, process the image
    setProcessState("Processing...", false);
    const canvas = renderCanvas();

    try {
        processedImage = await sendImageToBackend(canvas);

        // Update preview image and mark as processed
        previewImg.src = `data:image/png;base64,${processedImage}`;
        hasProcessed = true;
        setProcessState("Download Output", true);
    } catch (err) {
        console.error("Processing failed:", err);
        alert("Image processing failed.");
        setProcessState("Process Image", true);
    }
});


// === Render Canvas from Preview ===
function renderCanvas() {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");

    const w = previewImg.naturalWidth;
    const h = previewImg.naturalHeight;
    const rotated = rotate % 180 !== 0;

    canvas.width = rotated ? h : w;
    canvas.height = rotated ? w : h;

    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate((rotate * Math.PI) / 180);
    ctx.scale(flipH, flipV);
    ctx.filter = `brightness(${brightness}%) saturate(${saturation}%) invert(${inversion}%) grayscale(${grayscale}%)`;

    ctx.drawImage(previewImg, -w / 2, -h / 2);
    return canvas;
}

// === Upload to Backend ===
function sendImageToBackend(canvas) {
    return new Promise((resolve, reject) => {
        canvas.toBlob(blob => {
            if (!blob) return reject("Canvas toBlob failed");

            const formData = new FormData();
            formData.append("image", blob, "edited_image.png");

            fetch("https://curve-detection.onrender.com/analyze", {
                method: "POST",
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                console.log("Response from backend:", data);
                if (data.image) {
                    return resolve(data.image);
                }
                reject("No base64 image in response");
            })
            .catch(err => reject(err));
        }, "image/png");
    });
}

// === Delete Button ===
deleteBtn.addEventListener("click", () => {
    previewImg.src = placeholderSrc;
    fileInput.value = "";
    resetAllFilters();
    container.classList.remove("disable");
    hasProcessed = false;
});

// === Reset Button ===
resetBtn.addEventListener("click", resetAllFilters);
