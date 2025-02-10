import os
from ultralytics import YOLO
from tkinter import Tk, filedialog
from tqdm import tqdm
from pathlib import Path  # Robust path handling for special characters
import shutil  # For copying files without annotations

DEBUG = True  # Global debug variable: if True, draw bounding boxes on output images; if False, do not draw them

MODEL_PATH = "C:/Users/lucas/OneDrive/Documentos/EZClassify/best.pt"

# Load detection model (replace with correct path)
model = YOLO(MODEL_PATH, task="detect")


def save_detection_labels(norm_boxes, cls_ids, label_dest_path, polygons=None):
    # Save detection labels in either segmentation or bounding box format.
    lines = []

    # Convert tensors to numpy arrays if needed
    norm_boxes = norm_boxes.cpu().numpy() if hasattr(norm_boxes, "cpu") else norm_boxes
    cls_ids = cls_ids.cpu().numpy() if hasattr(cls_ids, "cpu") else cls_ids

    # Case 1: Polygons provided (segmentation)
    if polygons is not None and len(polygons) > 0:
        for i, class_id in enumerate(cls_ids):
            for polygon in polygons[i]:
                line = f"{int(class_id)}"
                for x, y in polygon:
                    line += f" {x:.6f} {y:.6f}"
                lines.append(line.strip())
    # Case 2: Use bounding boxes if no polygons are provided
    else:
        for i in range(len(norm_boxes)):
            x_center, y_center, width, height = norm_boxes[i]
            x1 = x_center - width / 2
            y1 = y_center - height / 2
            x2 = x_center + width / 2
            y2 = y_center - height / 2
            x3 = x_center + width / 2
            y3 = y_center + height / 2
            x4 = x_center - width / 2
            y4 = y_center + height / 2
            lines.append(f"{int(cls_ids[i])} {x1:.6f} {y1:.6f} {x2:.6f} {y2:.6f} {x3:.6f} {y3:.6f} {x4:.6f} {y4:.6f}")

    with open(label_dest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def process_images(input_folder):
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    input_folder = Path(input_folder)  # Convert to Path for Unicode support
    output_dir = Path("output")
    labels_dir = Path("labels")
    output_dir.mkdir(exist_ok=True)
    labels_dir.mkdir(exist_ok=True)

    # List only valid image files
    files = [f for f in input_folder.iterdir() if f.is_file() and f.suffix.lower() in valid_extensions]

    # Iterate over files with a progress bar
    for file_path in tqdm(files, desc="Processando imagens", unit="imagem"):
        try:
            # Perform inference with a confidence threshold of 0.40
            results = model(str(file_path), conf=0.40, verbose=False)
        except Exception as e:
            print(f"\nErro ao processar {file_path.name}: {e}")
            continue

        if results and len(results) > 0:
            for r in results:
                if r.boxes is not None and len(r.boxes) > 0:
                    # Generate output file paths preserving special characters
                    output_filename = output_dir / f"{file_path.stem}.jpg"
                    label_filename = labels_dir / f"{file_path.stem}.txt"
                    # Generate labels using normalized detection data
                    save_detection_labels(r.boxes.xywhn, r.boxes.cls, str(label_filename))
                    if DEBUG:
                        # Save image with bounding boxes drawn
                        r.save(filename=str(output_filename))
                    else:
                        # Copy original image to output directory without annotations
                        shutil.copy(str(file_path), str(output_filename))


def select_folder():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # Ensure the dialog is on top
    folder_selected = filedialog.askdirectory()
    root.destroy()
    return folder_selected


if __name__ == "__main__":
    input_folder = select_folder()
    if input_folder:
        process_images(input_folder)
    else:
        print("Nenhuma pasta selecionada.")
