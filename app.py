from flask import Flask, request, jsonify, render_template
import numpy as np
import cv2
import io
import base64
from PIL import Image
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Function to preprocess the image
def preprocess_image(img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (13, 13), 0)
    edges = cv2.Canny(blurred_img, threshold1=50, threshold2=150)
    kernel = np.ones((5, 5), np.uint8)
    dilated_img = cv2.dilate(edges, kernel, iterations=2)
    eroded_img = cv2.erode(dilated_img, kernel, iterations=1)
    contours, _ = cv2.findContours(eroded_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, eroded_img

def is_star(approx):
    num_vertices = len(approx)
    return num_vertices == 10

# Function to classify shape based on contours
def classify_shape(contour):
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    num_vertices = len(approx)

    if num_vertices == 3:
        shape = "triangle"
    elif num_vertices == 4:
        (x, y, w, h) = cv2.boundingRect(approx)
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

# Function to rotate and smooth the image
def rotate_and_smooth(img):
    smoothed_img = cv2.GaussianBlur(img, (3, 3), 0)
    moments = cv2.moments(smoothed_img)
    if moments['mu20'] == moments['mu02']:
        return smoothed_img
    angle = 0.5 * np.arctan2(2 * moments['mu11'], moments['mu20'] - moments['mu02'])
    angle = np.degrees(angle)
    rows, cols = smoothed_img.shape
    center = (cols // 2, rows // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)
    rotated_img = cv2.warpAffine(smoothed_img, rotation_matrix, (cols, rows), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
    return rotated_img

# Function to calculate symmetry of the image
def calculate_symmetry(img):
    rows, cols = img.shape
    h_flipped_img = cv2.flip(img, 1)
    h_diff = np.abs(img - h_flipped_img)
    h_norm_diff = np.sum(h_diff > 0) / (np.sum(img == 0) + 1e-6)

    v_flipped_img = cv2.flip(img, 0)
    v_diff = np.abs(img - v_flipped_img)
    v_norm_diff = np.sum(v_diff > 0) / (np.sum(img == 0) + 1e-6)

    d_rotated_img = rotate_and_smooth(img)
    d_flipped_img = cv2.flip(d_rotated_img, 0)
    d_diff = np.abs(d_rotated_img - d_flipped_img)
    d_norm_diff = np.sum(d_diff > 0) / (np.sum(d_rotated_img == 0) + 1e-6)

    c_diffs = []
    center = (cols // 2, rows // 2)
    for angle in range(0, 360, 2):
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_img = cv2.warpAffine(img, rotation_matrix, (cols, rows), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
        c_diff = np.sum(np.abs(img - rotated_img) > 0) / (np.sum(img == 0) + 1e-6)
        c_diffs.append(c_diff)
    c_mean_diff = np.mean(c_diffs)

    return h_norm_diff, v_norm_diff, d_norm_diff, c_mean_diff

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    # Load image from the request
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400
    
    file = request.files['image'].read()
    image = Image.open(io.BytesIO(file))
    if image.mode == 'RGBA':
        img = np.array(image)[:, :, :3]  # Drop alpha if present
    else:
        img = np.array(image)  # Use the image as is (RGB)
    img = img.astype(np.uint8)
    
    # Preprocess the image and get contours
    contours, processed_img = preprocess_image(img)

    if not contours:
        return jsonify({"message": "No contours detected in the image."}), 200

    results = []
    for idx, contour in enumerate(contours):
        shape, approx = classify_shape(contour)

        # Crop and center the contour
        x, y, w, h = cv2.boundingRect(contour)
        cropped_img = processed_img[y:y + h, x:x + w]
        max_side = max(w, h)
        centered_img = np.full((max_side, max_side), 255, dtype=np.uint8)
        start_y = (max_side - h) // 2
        start_x = (max_side - w) // 2
        centered_img[start_y:start_y + h, start_x:start_x + w] = cropped_img
        preprocessed_img = rotate_and_smooth(centered_img)

        # Calculate symmetry metrics
        h_diff, v_diff, d_diff, c_diff = calculate_symmetry(preprocessed_img)

        results.append({
            'shape': shape,
            'symmetry': {
                'horizontal': bool(h_diff < 0.2),
                'vertical': bool(v_diff < 0.2),
                'diagonal': bool(d_diff < 0.2),
                'rotational': bool(c_diff < 0.5)
            }
        })
        cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
        # Draw detected shapes and labels on the image
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.putText(img, shape, (cX - 20, cY + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Draw symmetry info on the image
            symmetry_text = f"Horizontal: {'Exists' if h_diff < 0.2 else 'Not Exists'}"
            cv2.putText(img, symmetry_text, (cX - 20, cY + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            symmetry_text = f"Vertical: {'Exists' if v_diff < 0.2 else 'Not Exists'}"
            cv2.putText(img, symmetry_text, (cX - 20, cY + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            symmetry_text = f"Diagonal: {'Exists' if d_diff < 0.2 else 'Not Exists'}"
            cv2.putText(img, symmetry_text, (cX - 20, cY + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            symmetry_text = f"Rotational: {'Exists' if c_diff < 0.5 else 'Not Exists'}"
            cv2.putText(img, symmetry_text, (cX - 20, cY + 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
    # Convert the final image with contours and symmetry text to a byte array
    img_byte_arr = io.BytesIO()
    final_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    final_img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Encode the image as base64 for display
    img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')

    # Return the final image and results as a JSON response
    return jsonify({'image': img_base64, 'results': results})


if __name__ == '__main__':
    app.run(debug=True)
