# YOLO Bounding Box Labeling Application

[![Project Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/sangoi-exe/EZLabel)
[![Python Version](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)

## Overview

This application is a user-friendly Python-based tool designed for labeling images with bounding boxes and polygons in the YOLO (You Only Look Once) format. It provides an intuitive graphical interface built with Tkinter, making image annotation efficient and accessible for computer vision and machine learning projects, particularly for object detection tasks.

This tool is ideal for preparing datasets for training YOLO models and similar object detection architectures. It emphasizes ease of use, robust functionality, and adherence to Python best practices.

## Key Features

- **Image Loading:** Supports loading various image formats (JPEG, PNG, BMP, GIF) for annotation.
- **Bounding Box and Freehand Polygon Drawing:**
  - **Box Mode:** Quickly draw rectangular bounding boxes by defining two corner points.
  - **Free Mode (Polygon):** Create complex polygon shapes for precise object segmentation.
  - Continuous and non-continuous drawing options in Free Mode.
- **Zoom & Pan Functionality:**
  - Mouse wheel zoom with focus point under the cursor for detailed annotation.
  - Manual zoom percentage input via combobox and direct value setting.
  - Right-click and drag panning for easy navigation in zoomed images.
- **Polygon Editing:**
  - **Selection:** Easily select polygons for modification via a dropdown list.
  - **Point Dragging:** Modify polygon shapes by dragging individual points.
  - **Point Insertion:** Double-click near a polygon segment to insert a new point on that segment, refining polygon boundaries.
  - **Segment Snap:** "Magnetic snap" feature for closed polygons. When the cursor approaches a segment, it snaps to the line, allowing for precise point addition directly on the segment with a single click.
  - **Point Deletion:** Right-click on a point and choose to delete it.
- **YOLO Label Format Support:** Generates and loads labels in the YOLO segmentation format (`class x1 y1 x2 y2 ... xN yN`), with normalized coordinates.
- **Label File Management:**
  - **Open Label Files:** Load existing YOLO label files to continue or modify annotations.
  - **Generate Label Files:** Save annotations to `.txt` files in the YOLO format, ready for model training.
- **Customizable Line Color:** Choose different line colors for bounding boxes/polygons via a color palette dialog.
- **Class ID Assignment:** Prompt for class IDs for each bounding box or polygon created, ensuring accurate labeling.
- **User-Friendly Interface:** Clean and intuitive Tkinter GUI, designed for efficient annotation workflows.
- **Zoom Balloon (Magnifier):** A small zoomed-in window appears when dragging points, providing pixel-level precision for fine adjustments.

## Getting Started

### Prerequisites

- **Python 3.7 or later:** Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).
- **pip:** Python package installer (usually included with Python installations).

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/sangoi-exe/EZLabel.git
    cd EZLabel
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv ezlabel-venv  # Or your preferred environment name
    ```

    Activate the virtual environment:

    - **On Windows:**
      ```bash
      ezlabel-venv\Scripts\activate
      ```
    - **On macOS and Linux:**
      ```bash
      source ezlabel-venv/bin/activate
      ```

3.  **Install dependencies:**

    ```bash
    pip install pillow tkinter
    ```

    This command installs the necessary Python libraries:

    - **Pillow (PIL):** For image processing.
    - **tkinter:** Python's standard GUI toolkit (usually included with Python, but ensure it's available).

    _(Optional)_: For more robust dependency management, consider creating a `requirements.txt` file in your project directory with the following content:

    ```txt
    Pillow
    ```

    Then install using:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To start the YOLO Bounding Box Labeling Application, execute the main script from your terminal within the project directory:

```bash
python main_app.py
```

This will launch the application window, and you can start annotating your images.

## Usage

1.  **Open Image:** Click the "Open Image" button in the toolbar to select and load an image file.
2.  **Select Drawing Mode:** Choose between "box" (bounding box) and "free" (freehand polygon) modes using the "Mode" dropdown in the toolbar.
3.  **Zoom & Pan:**
    - Use the mouse wheel to zoom in and out. The zoom will be centered around the mouse cursor.
    - Adjust the zoom level directly using the "Zoom" combobox.
    - Right-click and drag to pan the image when zoomed in.
4.  **Drawing Annotations:**
    - **Box Mode:** Click and drag to define a rectangular bounding box. Release the mouse button to complete the box and you will be prompted to enter a class ID.
    - **Free Mode:**
      - Click to add points to create a polygon.
      - To close a polygon, click near the starting point. You will be prompted for a class ID once the polygon is closed.
      - Enable "Continuous" mode in the toolbar for continuous polygon drawing. Disable for point-by-point polygon creation.
5.  **Polygon Editing:**
    - **Select Polygon:** Choose a polygon to edit from the "Polygon" dropdown list in the toolbar.
    - **Drag Points:** Click and drag existing points of the selected polygon to reshape it.
    - **Insert Points on Segments:** Double-click near a segment of a **closed** polygon to insert a new point on that segment.
    - **Segment Snap:** For closed polygons, when your cursor is close to a segment, it will "snap" to the line. A single left-click in this state will add a point directly on the segment.
    - **Delete Points:** Right-click on a point and confirm to delete it.
6.  **Line Color:** Change the annotation line color by clicking the "Line Color" button and selecting a color from the palette.
7.  **Save Labels:** Click "Generate Label" to save the annotations for the currently loaded image in a YOLO format `.txt` file (with the same base name as the image).
8.  **Load Labels:** Click "Open Label File" to load existing YOLO label files and display the annotations on the image.

## Contributing

Contributions to improve this application are welcome! If you have suggestions, bug reports, or would like to contribute code, please:

1.  **Fork the repository.**
2.  **Create a branch** for your feature or bug fix.
3.  **Make your changes** and commit them with clear and descriptive commit messages.
4.  **Submit a pull request** to the main repository.

Please adhere to Python best practices and coding style (PEP 8) when contributing code.

## License

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
