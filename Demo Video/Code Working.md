# Demo Video / Code Working

## Overview
This file provides a detailed description of the functionality and demonstration of the code. For visual representation, please refer to the demo video or screenshots provided in the repository.

## Image Details

### 1. Hand-drawn Rectangle
This image demonstrates our code's ability to accurately predict the shape of a hand-drawn imperfect rectangle. The code:
- **Shape Identification:** Detects and classifies the rectangle, even if drawn with imperfections.
- **Curve Smoothening:** Refines the edges to approximate a perfect rectangle.
- **Symmetry Detection:** Identifies both horizontal and vertical symmetries of the rectangle. Users can adjust the thresholds for symmetry detection, including horizontal (`h_diff`), vertical (`v_diff`), diagonal (`d_diff`), and radial (`c_diff`).

### 2. Three Figures in One
This image showcases the code’s capability to process multiple figures within a single image:
- **Outline Shape Prediction:** Accurately identifies and classifies each figure in the image.
- **Symmetry Analysis:** Evaluates and displays the symmetry of each figure.
- **Curve Completion:** Completes curves to approximate their perfect form, demonstrating the code's ability to handle multiple shapes and their symmetries simultaneously.

### 3. All features in One Run (Multiple Shapes and Symmetry)
This image highlights our code's prowess in identifying symmetry in multiple images, classifying figure shapes, and completing curves with high accuracy:
- **Symmetry Detection:** Accurately identifies the symmetry of multiple figures in the image.
- **Shape Identification:** Detects and classifies various shapes within the image.
- **Curve Completion and Regularization:** Completes and regularizes curves to approximate their perfect shapes.
  
  Note: The ellipse is shown as a circle due to the lax parameters set for circle detection. You can adjust these parameters for more accurate shape classification.

## How the Code Works

### 1. Image Preprocessing
- **Conversion to Grayscale:** We first convert the image to grayscale to simplify processing.
- **Blurring:** Gaussian blur is applied to reduce noise and smooth the image.
- **Edge Detection:** The Canny edge detection algorithm is used to identify edges within the image.
- **Morphological Operations:** Dilation and erosion refine the edges and help find contours.

### 2. Shape Classification
- **Contour Approximation:** Contours are approximated to polygons to classify shapes based on the number of vertices.
- **Shape Identification:** Shapes are classified into categories like triangle, square, rectangle, pentagon, hexagon, heptagon, star, circle, ellipse, and polygon.

### 3. Curve Beautification
- **Circle Approximation:** For circular shapes, we find the minimum enclosing circle and approximate the contour to a circular shape.
- **Smoothing and Alignment:** Shapes are smoothed and aligned as needed.

### 4. Symmetry Detection
- **Horizontal and Vertical Symmetry:** We flip the image horizontally and vertically, then calculate the difference between the original and flipped images. Normalized differences are used to determine symmetry.
- **Diagonal Symmetry:** The image is rotated and compared to the original to check for diagonal symmetry.
- **Radial Symmetry:** The image is rotated in small increments, and differences are calculated to assess radial symmetry.

## How to Use
1. Place your image files or polyline data in the appropriate folder.
2. Update the `input_data` variable in the code with the path to your file or polyline data.
3. Run the script to process the image and analyze shapes and symmetries.

## Adjustments
You can modify the symmetry thresholds to suit your needs:
- **Horizontal Symmetry Threshold:** `h_diff`
- **Vertical Symmetry Threshold:** `v_diff`
- **Diagonal Symmetry Threshold:** `d_diff`
- **Radial Symmetry Threshold:** `c_diff`

## Additional Information
For a detailed explanation of each function and its purpose, please refer to the code comments and documentation provided.

## Demo Video
Watch the demo video to see the code in action: [Demo Video](https://drive.google.com/file/d/1eRScXt_NPfY_5DEr8KryrpJg0cAKz_yc/view)

