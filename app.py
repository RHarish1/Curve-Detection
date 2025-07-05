from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import numpy as np
import cv2
from PIL import Image
import io
import base64
import os
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or list specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

import numpy as np

def convert_numpy_bools(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy_bools(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_bools(i) for i in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    return obj


# ===================== Image Processing Functions =====================

def preprocess_image(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (13, 13), 0)
    edges = cv2.Canny(blurred_img, 50, 150)
    kernel = np.ones((5, 5), np.uint8)
    dilated_img = cv2.dilate(edges, kernel, iterations=2)
    eroded_img = cv2.erode(dilated_img, kernel, iterations=1)
    contours, _ = cv2.findContours(eroded_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, eroded_img

def is_star(approx):
    return len(approx) == 10

def classify_shape(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    num_vertices = len(approx)

    if num_vertices == 3:
        shape = "triangle"
    elif num_vertices == 4:
        x, y, w, h = cv2.boundingRect(approx)
        ar = w / float(h)
        shape = "square" if 0.95 <= ar <= 1.05 else "rectangle"
    elif num_vertices == 5:
        shape = "pentagon"
    elif num_vertices == 6:
        shape = "hexagon"
    elif num_vertices == 7:
        shape = "heptagon"
    elif num_vertices == 10 and is_star(approx):
        shape = "star"
    else:
        area = cv2.contourArea(contour)
        circularity = 4 * np.pi * area / (peri * peri)
        (x, y), (MA, ma), angle = cv2.fitEllipse(contour)
        aspect_ratio = MA / ma
        if 0.80 <= aspect_ratio <= 1.20 and circularity >= 0.80:
            shape = "circle"
        else:
            shape = "ellipse"
        if num_vertices > 7 and shape not in ["ellipse", "circle"]:
            shape = "polygon"
    return shape, approx

def rotate_and_smooth(img):
    smoothed_img = cv2.GaussianBlur(img, (3, 3), 0)
    moments = cv2.moments(smoothed_img)
    if moments['mu20'] == moments['mu02']:
        return smoothed_img
    angle = 0.5 * np.arctan2(2 * moments['mu11'], moments['mu20'] - moments['mu02'])
    angle = np.degrees(angle)
    rows, cols = smoothed_img.shape
    center = (cols // 2, rows // 2)
    rot_mat = cv2.getRotationMatrix2D(center, -angle, 1.0)
    rotated_img = cv2.warpAffine(smoothed_img, rot_mat, (cols, rows), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    return rotated_img

def calculate_symmetry(img):
    rows, cols = img.shape
    h_flip = cv2.flip(img, 1)
    v_flip = cv2.flip(img, 0)
    d_rot = rotate_and_smooth(img)
    d_flip = cv2.flip(d_rot, 0)

    h_diff = np.sum(np.abs(img - h_flip) > 0) / (np.sum(img == 0) + 1e-6)
    v_diff = np.sum(np.abs(img - v_flip) > 0) / (np.sum(img == 0) + 1e-6)
    d_diff = np.sum(np.abs(d_rot - d_flip) > 0) / (np.sum(d_rot == 0) + 1e-6)

    c_diffs = []
    center = (cols // 2, rows // 2)
    for angle in range(0, 360, 2):
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, rot_mat, (cols, rows), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
        c_diff = np.sum(np.abs(img - rotated) > 0) / (np.sum(img == 0) + 1e-6)
        c_diffs.append(c_diff)
    c_mean_diff = np.mean(c_diffs)
    return h_diff, v_diff, d_diff, c_mean_diff

# ===================== Routes =====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    contents = await image.read()
    img_pil = Image.open(io.BytesIO(contents))
    img_np = np.array(img_pil.convert("RGB")).astype(np.uint8)

    contours, processed_img = preprocess_image(img_np)
    if not contours:
        return JSONResponse(content={"message": "No contours detected in the image."})

    results = []
    for contour in contours:
        shape, approx = classify_shape(contour)
        x, y, w, h = cv2.boundingRect(contour)
        cropped = processed_img[y:y+h, x:x+w]
        max_side = max(w, h)
        centered = np.full((max_side, max_side), 255, dtype=np.uint8)
        centered[(max_side - h)//2:(max_side - h)//2 + h, (max_side - w)//2:(max_side - w)//2 + w] = cropped

        pre_img = rotate_and_smooth(centered)
        h_diff, v_diff, d_diff, c_diff = calculate_symmetry(pre_img)

        results.append({
            "shape": shape,
            "symmetry": {
                "horizontal": h_diff < 0.2,
                "vertical": v_diff < 0.2,
                "diagonal": d_diff < 0.2,
                "rotational": c_diff < 0.5
            }
        })

        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            
            # Draw shape name
            cv2.putText(img_np, shape, (cX - 20, cY + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw symmetry labels
            cv2.putText(img_np, f"Horizontal Symmetry: {h_diff < 0.2}", (cX - 20, cY + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            cv2.putText(img_np, f"Vertical Symmetry: {v_diff < 0.2}",   (cX - 20, cY + 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            cv2.putText(img_np, f"Diagonal Symmetry: {d_diff < 0.2}",   (cX - 20, cY + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            cv2.putText(img_np, f"Rotational Symmetry: {c_diff < 0.5}", (cX - 20, cY + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    # Convert processed image to BGR for OpenCV
    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    # Draw contours on image
    cv2.drawContours(img_np, contours, -1, (0, 255, 0), 2)

    # Convert final image to base64
    img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
    buffer = io.BytesIO()
    img_pil.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    results = convert_numpy_bools(results)

    return JSONResponse(content={"image": img_str, "results": results})

# ===================== Run =====================

# Run with: uvicorn filename:app --reload
