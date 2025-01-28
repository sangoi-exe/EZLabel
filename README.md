# EZLabel: Your Efficient YOLO Labeling Tool

## Overview

EZLabel is a user-friendly Python application designed to streamline the process of labeling images for YOLO (You Only Look Once) object detection models. Built with Tkinter, EZLabel provides an intuitive graphical interface for drawing bounding boxes and free-form polygons, making image annotation efficient and accurate. Whether you're working on object detection, image segmentation, or any vision task requiring labeled datasets, EZLabel offers a robust solution to prepare your data in the widely adopted YOLO format.

## ✨ Key Features

- **Intuitive Graphical Interface:**  Leverages Tkinter to offer a clean and responsive user experience for image annotation.
- **Bounding Box & Free Polygon Support:** Draw both rectangular bounding boxes for standard object detection and free-form polygons for more precise segmentation tasks.
- **YOLO Label Format Generation:** Automatically generates label files in the YOLO format (`.txt` files), ready for training your models.
- **Class Definition Customization:** Easily define and manage your object classes directly within the application.
- **Color-Coded Labels:** Assign distinct colors to different object classes for visual clarity during annotation.
- **Zoom & Pan Functionality:** Zoom into images for detailed annotation and pan to navigate large images efficiently.
- **Zoom Fit & Manual Zoom:** Quickly fit the image to the workspace or set a custom zoom level.
- **Continuous Free Mode:** For rapid polygon drawing, enabling continuous point placement in free-form mode.
- **Zoom Balloon for Precision:** A magnified view pops up when dragging points, ensuring pixel-perfect adjustments.
- **File Navigation & Management:** Open individual images or entire folders, with a file list for easy browsing and selection.
- **Keyboard Navigation:** Use up and down arrow keys to quickly switch between images in a folder.
- **Tooltip Hints:** Helpful tooltips guide users through the application's functionalities.
- **Label Loading & Saving:** Load existing YOLO label files to continue or edit annotations, and save new labels seamlessly.
- **Customizable Zoom Levels:** Choose from predefined zoom percentages or set a specific zoom value.

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have Python installed on your system. EZLabel is built using standard Python libraries, so no extensive external dependencies are required. However, it's recommended to have `Pillow` (PIL Fork) installed for image handling. You can install it using pip:

```bash
pip install Pillow
```

### Installation & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sangoi-exe/EZLabel.git
   cd EZLabel
   ```

2. **Run the application:**
   ```bash
   python main_app.py
   ```

   This command will launch the EZLabel application.

## ✍️ Usage Guide

1. **Open Image or Folder:**
   - Click "Open Image" to load a single image for labeling.
   - Click "Open Folder" to load a directory containing images. The file list on the right side will populate with image files from the selected folder.

2. **Select Drawing Mode:**
   - Choose between "box" for bounding boxes and "free" for free-form polygons using the "Mode" dropdown in the toolbar.

3. **Choose a Color:**
   - Select a color from the color palette in the toolbar. Each color can represent a different object class, enhancing visual organization. Click on a color square to activate it.

4. **Drawing Annotations:**
   - **Box Mode:**
     - Click and drag on the image to draw a bounding box. Release the mouse button to complete the box.
   - **Free Mode:**
     - Click on the image to start drawing a polygon.
     - Continue clicking to add points to the polygon.
     - **Double-click near the starting point to close the polygon and assign a class ID.** A dialog will prompt you to select a class for the polygon.
     - In "Continuous" free mode (checkbox in the toolbar), you can keep adding points to the current polygon of the selected color without needing to re-select the color.

5. **Navigating Images:**
   - If you opened a folder, use the file list on the right to select images.
   - Use the **up and down arrow keys** to quickly navigate through the images in the file list.

6. **Zoom & Pan:**
   - Use the "Zoom" dropdown to select a predefined zoom level (25% to 300%).
   - Click "Fit" to automatically zoom the image to fit the workspace.
   - Right-click and drag to pan the image within the workspace.
   - Use the mouse wheel to zoom in and out, pivoting around the mouse cursor location.

7. **Generate Label File:**
   - Once you have labeled an image, click "Generate Label" to save the labels in a `.txt` file in the same directory as the image, following the YOLO format. A tooltip will confirm successful label generation.

8. **Loading Existing Labels:**
    - Click "Open Label File" to load existing YOLO `.txt` label files for the currently opened image. This allows you to edit or continue labeling previously annotated images.

9. **Class Selection:**
    - When closing a free-form polygon or creating a bounding box, a class selection dialog will appear, allowing you to assign a predefined class to your annotation.

## 📁 Directory Structure

```
EZLabel/
├── main_app.py         # Main application script - launches EZLabel
├── modules/            # Directory containing application modules
│   ├── balloon_zoom.py   # Module for the zoom balloon functionality
│   ├── class_selection.py# Module for the class selection dialog
│   ├── color_palette.py  # Module for the color palette dialog (if implemented separately)
│   ├── labels_handler.py # Module for loading and saving YOLO label files
│   ├── shapes.py         # Defines data classes for points and polygons
│   ├── tooltip.py        # Module for creating tooltips
│   ├── workspace.py      # Module for the main image workspace frame
│   ├── workspace_draw.py # Module handling canvas drawing operations
│   ├── workspace_events.py# Module managing event handling (mouse, keyboard)
│   └── workspace_polygons.py# Module for managing polygon data and operations
└── README.md           # This README file
```

## ⚙️ Dependencies

- Python (3.x recommended)
- Tkinter (standard Python GUI library)
- Pillow (PIL Fork) - for image processing (`pip install Pillow`)
- ttk (Tk themed widgets, usually included with Tkinter)

## 🤝 Contributing

Contributions to EZLabel are welcome! If you have suggestions for improvements, bug fixes, or new features, please feel free to fork the repository and submit a pull request. For major changes, it's recommended to open an issue first to discuss your ideas.

## 📜 License

[Specify License here, e.g., MIT License, Apache 2.0, etc. If none, consider adding one.]

---
