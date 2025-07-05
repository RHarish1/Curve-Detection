# 🌀 Curvetopia

# 🌀 Curvetopia

## 🔍 Overview

## 🔍 Overview

**Curvetopia** is an interactive web-based tool for **shape detection** and **symmetry analysis** in images. Users can upload images containing 2D shapes, apply filters and transformations, and generate annotated results that highlight detected shapes and assess their symmetry.

It features a modern **FastAPI backend** for shape analysis and a responsive **JavaScript/HTML frontend** that allows real-time image manipulation before processing.

---

## ⚙️ Features

**Curvetopia** is an interactive web-based tool for **shape detection** and **symmetry analysis** in images. Users can upload images containing 2D shapes, apply filters and transformations, and generate annotated results that highlight detected shapes and assess their symmetry.

It features a modern **FastAPI backend** for shape analysis and a responsive **JavaScript/HTML frontend** that allows real-time image manipulation before processing.

---

## ⚙️ Features

- 🧠 **Shape Detection**  
  Detects common shapes: triangle, square, rectangle, circle, pentagon, hexagon, heptagon, star, and generic polygons.

- 🔁 **Symmetry Analysis**  
  Automatically computes horizontal, vertical, diagonal, and rotational symmetry of each detected shape.

- 🖼️ **Interactive Image Editor**  
  Modify brightness, saturation, invert, grayscale. Supports rotation and flip before analysis.

- 🔄 **Live Preview & Download**  
  View output image with annotated shapes and download it directly.

- ✏️ **Polyline Support (Advanced)**  
  Use predefined or uploaded polylines (e.g. from `.csv`) as input for geometric shape analysis.

---

## 🧱 Tech Stack

| Component    | Stack                         |
| ------------ | ----------------------------- |
| Frontend     | HTML, CSS, JavaScript         |
| Image Editor | Canvas API, DOM manipulation  |
| Backend      | FastAPI (Python)              |
| Image Proc   | OpenCV, NumPy, Pillow         |
| Shape Logic  | Custom geometric algorithms   |
| Output       | Annotated image + JSON result |

---

## 🚀 Setup & Installation

### 🔧 Backend (FastAPI)

**Install Python dependencies:**

```bash
pip install fastapi uvicorn opencv-python-headless numpy pillow
```

**Run the FastAPI server:**

```bash
uvicorn main:app --reload
```

By default, the server runs at `http://localhost:8000`.

---

### 🌐 Frontend

If you are hosting the source code yourself (and not the hosted website).
Place your HTML, CSS, and JS files inside a `static/` directory served by FastAPI.

Ensure `previewImg.src` and fetch requests use:

```js
fetch("http://localhost:8000/analyze", { method: "POST", ... });
```

---

## 🧪 Image Analysis API

### POST `/analyze`

**Description**: Analyze uploaded image for shape detection and symmetry.

**Request**: Multipart FormData with `image` field.

**Response**:

```json
{
  "image": "<base64_output_image>",
  "results": [
    {
      "shape": "circle",
      "symmetry": {
        "horizontal": true,
        "vertical": true,
        "diagonal": true,
        "rotational": true
      }
    },
    ...
  ]
}
```

---

## 🧠 Core Functions (Python)

### `preprocess_image(img: np.ndarray)`

- Converts to grayscale, applies Canny edge detection, dilation, erosion.
- Returns contours + cleaned image.

### `classify_shape(contour)`

- Uses contour approximation and circularity to identify shape type.

### `rotate_and_smooth(img)`

- Aligns shape and reduces noise before symmetry check.

### `calculate_symmetry(img)`

- Compares image flips (H, V, Diag, 180°) to compute symmetry differences.

---
