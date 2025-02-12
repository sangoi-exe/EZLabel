# EZLabel: Your Efficient YOLO Labeling Tool

[![Project Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/sangoi-exe/EZLabel)
[![Python Version](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](LICENSE)

## Overview
EZLabel is a sophisticated and user-friendly Python application designed to streamline the image-labeling process for Ultralytics YOLO object detection models. Developed with Tkinter, it provides an intuitive graphical interface for drawing bounding boxes, free-form polygons, and rectangular regions, all while generating YOLO-friendly annotation files. Whether you need bounding boxes or precise segmentation polygons, EZLabel equips you with an efficient, robust solution to prepare your image datasets.

## ✨ Key Features

- ◼ Multiple Drawing Modes:  
  - **Box** for standard bounding boxes.  
  - **Free** for free-form polygonal segmentation.  
  - **Rect** for quickly drawing rectangular (diagonal-based) polygons.
  
- ◼ Intuitive Graphical Interface:  
  Built on Tkinter for a clean, responsive environment.  

- ◼ YOLO Label Generation:  
  Seamlessly saves annotations in standard YOLO text-file format.  

- ◼ Class Definitions & Selection:  
  Includes a default set of classes (e.g., CNH, RG, CPF, Título de Eleitor) and offers an interactive dialog for choosing or modifying the class ID at polygon closure or bounding box creation.

- ◼ Color-Coded Annotations:  
  Assign unique colors per class or per polygon for quick visual distinction.  

- ◼ Advanced Zoom & Pan:  
  Resize and reposition images at will, using mouse wheel or the toolbar.  

- ◼ Balloon Zoom for Pixel Precision:  
  A specialized floating zoom window helps you drag points with pinpoint accuracy.  

- ◼ Overwrite vs. Train-Mode Label Generation:  
  - When "Overwrite Label" is checked, annotations overwrite the existing .txt file in the same directory.  
  - When unchecked, annotated images and label files automatically move to "train/images" and "train/labels".  

- ◼ Keyboard Shortcuts:  
  - Image Navigation: Up/Down or W/S for previous/next.  
  - Drawing Modes:  
    • R → Rect  
    • B → Box  
    • F → Free  
  - Colors (1 to 8): Quickly switch annotation color (#FF0000, #00FF00, #0000FF, #FFFF00, #FF00FF, #00FFFF, #000000, #FFFFFF).  
  - WASD → Also mapped to Up/Down navigation if preferred.

- ◼ Multi-Point Editing & Double-Click Simplification:  
  Double-click near the first point of a polygon to close it and open class-selection. You can also double-click on an existing closed polygon edge to insert a new point.

- ◼ Continuously Annotate Free Polygons:  
  Toggle "Continuous" mode to add multiple points sequentially without reselecting the color or class.

- ◼ Existing Label Loading:  
  Open YOLO ".txt" files to refine or continue existing labels.

- ◼ Configuration via Toolbar & Combobox:  
  Simple toggles for "Overwrite Label," Zoom level, and the drawing mode.

## 🚀 Getting Started

### Prerequisites
• Python 3.x installed on your system.  
• Tkinter (usually included by default with most Python distributions).  
• Pillow (PIL Fork) for image handling.

Install Pillow if needed:
  
  pip install Pillow

### Installation & Running

1. Clone this repository:
   git clone https://github.com/sangoi-exe/EZLabel.git
   cd EZLabel

2. Run the main application:
   python main_app.py

The EZLabel window will launch, ready to load images or folders for labeling.

## ✍️ Usage Guide

1. Opening Images or Folders:
   • Click "Open Image" to select a single image.  
   • Click "Open Folder" to batch-load a directory of images; they appear in the file list on the right.  

2. Selecting a Drawing Mode:
   • "Box": Draw bounding boxes.  
   • "Free": Click-and-place points for polygons; double-click near your first point to close.  
   • "Rect": Diagonal-based rectangle creation (useful for quickly defining polygonal rectangle regions).

3. Color Selection & Keyboard Shortcuts:
   • Pick a color in the toolbar (each color is assigned a distinct button).  
   • Quickly swap with the number keys (1–8).  

4. Creating Annotations:
   • Box Mode: Click-and-drag for a bounding box. Release the mouse to finalize; a class-selection dialog appears.  
   • Rect Mode: Two clicks define opposite corners of a rectangle. You will then be prompted for the class ID.  
   • Free Mode: Click multiple points to sketch any shape. Double-click to close and choose a class ID.

5. Continuous Free Mode:
   • If "Continuous" is checked, you can keep adding points to the same polygon without reselecting anything.  

6. Navigating Images:
   • If a folder is opened, use the file list on the right or press Up/Down (or W/S) to move between images.  

7. Zoom & Pan:
   • Select a percentage from the Zoom combobox or click "Fit" to auto-scale the image.  
   • Right-click + drag to pan around.  
   • Use the mouse wheel (or trackpad scroll) to zoom in/out, pivoting around the mouse cursor.  

8. Generating Labels:
   • Click "Generate Label" once your image annotations are complete.  
   • If "Overwrite Label" is checked, the generated ".txt" file saves (or replaces) in the same location as the image.  
   • If unchecked, the image and its label file move to "train/images" and "train/labels" automatically, helping organize data for training.  

9. Loading Existing Labels:
   • Click "Open Label File" to load a YOLO ".txt" annotation for the current image.  
   • Continue or modify previous annotations in the workspace.

10. Class Definition & Advanced Editing:
   • EZLabel ships with a default dictionary of class IDs (0–14).  
   • You can extend or modify these definitions in the source code (“class_definitions” in main_app.py).  
   • Closing a free-form polygon or creating a bounding box triggers a prompt to assign the class.

11. Tooltips & Balloon Zoom:
   • Hovering over buttons or generating labels can trigger a tooltip.  
   • Dragging points while holding the left mouse button activates a floating balloon zoom window for precise control.

## 📁 Directory Structure

The following outlines the typical structure inside the EZLabel directory:

```
EZLabel/
├── main_app.py             # Main application entry point
├── modules/                # Core modules
│   ├── balloon_zoom.py       # Magnified window for precise point movement
│   ├── class_selection.py    # Dialog for class ID selection
│   ├── color_palette.py      # Color palette selection dialog
│   ├── labels_handler.py     # Logic to load/save YOLO label files
│   ├── shapes.py             # Data classes for points/polygons
│   ├── tooltip.py            # Tooltip implementation
│   ├── workspace.py          # Main workspace frame & image handling
│   ├── workspace_draw.py     # Rendering polygons & images on canvas
│   ├── workspace_events.py   # Mouse/keyboard event handling
│   └── workspace_polygons.py # Polygon creation, insertion, editing
├── train/                  # (Auto-created when Overwrite Label is off)
│   ├── images/               # Moves labeled images here
│   └── labels/               # Stores generated label files
└── README.md               # Project documentation (this file)
```

## ⚙️ Dependencies
• Python 3.x    
• Tkinter (standard with Python)  
• Pillow (install via pip install Pillow)  

## License

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
