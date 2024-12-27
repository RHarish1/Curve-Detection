# Curvetopia

## Overview

**Curvetopia** is a tool designed to analyze 2D images or polylines, classify shapes, and evaluate their symmetry. The code processes input images or manually defined polylines, identifies geometric shapes such as triangles, squares, rectangles, circles, etc., and computes various symmetry measures (horizontal, vertical, diagonal, and rotational). The output is an image with the detected shapes labeled and a report on the symmetry of each shape.

## Features

- **Shape Detection**: Identifies and classifies shapes including triangles, squares, rectangles, pentagons, hexagons, heptagons, stars, circles, ellipses, and generic polygons.
- **Symmetry Calculation**: Calculates and reports on the horizontal, vertical, diagonal, and rotational symmetry of each shape.
- **Custom Polyline Support**: Allows custom polylines to be analyzed as shapes, providing flexibility beyond standard image inputs.
- **Visualization**: Outputs an annotated image showing the detected shapes and their symmetry.

## Dependencies

The code requires the following Python libraries:
- OpenCV
- NumPy
- Matplotlib
- Pandas

You can install these dependencies using pip:

```bash
pip install opencv-python-headless numpy matplotlib
```

## Code Explanation

### 1. **Preprocess Image**
```python
def preprocess_image(img):
    # Converts image to grayscale and applies Gaussian blur
    # Detects edges using the Canny method
    # Uses morphological operations (dilation, erosion) to clean up the edges
    # Returns contours found in the processed image
```

### 2. **Shape Classification**
```python
def classify_shape(contour):
    # Calculates the perimeter and approximates the contour to a polygon
    # Determines the shape based on the number of vertices or special properties like circularity
```

### 3. **Crop and Center Contour**
```python
def crop_and_center(contour, binary_img, padding=10):
    # Crops the image around the detected contour and centers it on a square canvas
```

### 4. **Rotate and Smooth Image**
```python
def rotate_and_smooth(img):
    # Smooths the image and aligns it by calculating the angle of rotation needed for symmetry
    # Returns the rotated image
```

### 5. **Symmetry Calculation**
```python
def calculate_symmetry(img):
    # Calculates horizontal, vertical, diagonal, and rotational symmetry
    # Returns normalized differences indicating the presence or absence of each type of symmetry
```

### 6. **Analyze Image or Polyline**
```python
def analyze_image(input_data, input_type='image'):
    # Main function to load an image or polyline, preprocess it, classify the shape, calculate symmetry, and output results
    # Saves and displays the final image with annotated shapes
```

### 7. **Generate Regular Polygon**
```python
def generate_polygon(center, radius, num_sides):
    # Generates vertices for a regular polygon with the specified number of sides
```

## Usage

### Analyzing an Image

You can analyze an image by providing its file path to the `analyze_image` function:

```python
analyze_image('path_to_your_image.png', input_type='image')
```

### Analyzing a Custom Polyline, You can use the csv code (uploaded in the Problem Description) to convert csv to polylines.

You can also analyze a custom-defined polyline. For example, to analyze a pentagon:

```python
# Define center and radius
center = (250, 250)
radius = 100

# Generate pentagon vertices
pentagon_polyline = generate_polygon(center, radius, num_sides=5)

# Analyze the polyline
analyze_image(pentagon_polyline, input_type='polyline')
```

## Example Output

The code will produce an output image with the shapes detected and labeled. Symmetry information for each shape is printed in the console.


