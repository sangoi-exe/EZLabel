import os
import cv2
import numpy as np
from tkinter import Tk, filedialog
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm  # progress bar import


MODEL_PATH = r"C:\Users\lucas\OneDrive\Documentos\EZClassify\Detect-Document\Model-v3\weights\best.pt"

# Global operation mode: "prediction" for detection (bounding boxes) or "segmentation" for mask segmentation.
OPERATION_MODE = "prediction"  # Change to "segmentation" if needed.
# Confidence threshold for detections.
CONFIDENCE_THRESHOLD = 0.7
# Global toggle to create output images only when at least one detection is found above the threshold.
CREATE_ONLY_IF_DETECTED = True  # Set to True to only create output images if a detection is found.
# Define folder names for output copies.
CONTOUR_IMAGES_FOLDER = "detected_images"  # Folder for copies with drawn contours.
INPUT_COPY_FOLDER = "clean_copy"  # Folder for the 640px input copy.
# Global toggles for output folders.
ENABLE_CONTOUR_FOLDER = True  # Set to False to disable saving the contour images folder.
ENABLE_INPUT_FOLDER = True  # Set to False to disable saving the input copy folder.
# Global variable to define how many contours (detections in segmentation mode) to draw.
NUM_CONTOURS_TO_DRAW = 1


def get_color(index):
    """
    Returns a unique color from a predefined palette based on index.
    """
    COLORS = ["red", "green", "blue", "orange", "purple", "cyan", "magenta", "yellow"]
    return COLORS[index % len(COLORS)]


def load_font(image_width):
    """
    Returns a PIL font scaled to the image width.
    """
    font_size = max(12, image_width // 50)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    return font


def draw_detections_on_pil(image, detections, op_mode, class_names, scale_factor=1.0):
    """
    Draws detections on a PIL image. For detection mode, draws bounding boxes.
    For segmentation mode, extracts and draws the mask contours.
    Coordinates are scaled by 'scale_factor'.
    """
    draw = ImageDraw.Draw(image)
    font = load_font(image.width)
    for idx, detection in enumerate(detections):
        color = get_color(idx)
        if op_mode == "prediction":
            # Unpack detection tuple (box, cls_id, conf_score)
            box, cls_id, conf_score = detection
            # Convert box coordinates to a list if needed and scale them.
            box_vals = box.tolist() if not isinstance(box, list) else box
            scaled_box = [int(coord * scale_factor) for coord in box_vals]
            # Draw rectangle outline.
            draw.rectangle(scaled_box, outline=color, width=2)
            class_id_int = int(cls_id)
            label_text = class_names.get(class_id_int, f"class_{class_id_int}")
            draw.text((scaled_box[0], scaled_box[1]), label_text, fill=color, font=font)
        elif op_mode == "segmentation":
            # Unpack detection tuple (box, cls_id, conf_score, mask)
            box, cls_id, conf_score, mask = detection
            box_vals = box.tolist() if not isinstance(box, list) else box
            scaled_box = [int(coord * scale_factor) for coord in box_vals]
            # Convert mask to a NumPy array.
            mask_np = np.array(mask.cpu()) if hasattr(mask, "cpu") else np.array(mask)
            # If scaling is needed, resize the mask to match the current image size.
            if scale_factor != 1.0:
                new_size = (image.width, image.height)  # (width, height)
                mask_np = cv2.resize(mask_np, new_size, interpolation=cv2.INTER_NEAREST)
            # Threshold the mask; expected mask values are [0, 1] or 0-255.
            if mask_np.max() <= 1.0:
                _, binary_mask = cv2.threshold(mask_np, 0.5, 255, cv2.THRESH_BINARY)
            else:
                _, binary_mask = cv2.threshold(mask_np, 127, 255, cv2.THRESH_BINARY)
            # Find contours from the binary mask.
            contours_data, _ = cv2.findContours(binary_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours_data:
                if len(contour) >= 3:
                    # Convert contour points to a list of tuples.
                    points = [tuple(pt[0]) for pt in contour]
                    # Draw the contour outline (closed polygon).
                    draw.line(points + [points[0]], fill=color, width=2)
            class_id_int = int(cls_id)
            label_text = class_names.get(class_id_int, f"class_{class_id_int}")
            draw.text((scaled_box[0], scaled_box[1]), label_text, fill=color, font=font)
    return image


def process_images(input_folder):
    """
    Processes each image in the input folder with a dynamically updating progress bar.
    Inference is run on a copy of the original image.
    Output copies are conditionally saved based on global flags.
    """
    # Create output directories if enabled.
    contour_folder = os.path.join(input_folder, CONTOUR_IMAGES_FOLDER) if ENABLE_CONTOUR_FOLDER else None
    if contour_folder:
        os.makedirs(contour_folder, exist_ok=True)
    input_copy_folder = os.path.join(input_folder, INPUT_COPY_FOLDER) if ENABLE_INPUT_FOLDER else None
    if input_copy_folder:
        os.makedirs(input_copy_folder, exist_ok=True)

    # Load the YOLO model for the appropriate task.
    model = YOLO(MODEL_PATH, task="segment" if OPERATION_MODE == "segmentation" else "detect")
    class_names = model.names if hasattr(model, "names") else {}

    # Get list of image files.
    image_files = [f for f in os.listdir(input_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

    # Initialize counters.
    detect_count = 0  # Count of images with detections.
    skip_count = 0  # Count of images skipped (no detections or error)

    # Process images with a dynamically updating tqdm progress bar.
    with tqdm(image_files, desc="Processing images", ncols=80, dynamic_ncols=True) as pbar:
        for file_name in pbar:
            file_path = os.path.join(input_folder, file_name)
            image_base_name, ext = os.path.splitext(file_name)
            try:
                # Run inference on the image.
                results = model(file_path, conf=CONFIDENCE_THRESHOLD, verbose=False)
                img_pil = Image.open(file_path).convert("RGB")

                # Prepare the detections list.
                detections = []
                if OPERATION_MODE == "prediction":
                    if results and results[0].boxes and len(results[0].boxes) > 0:
                        for i in range(len(results[0].boxes)):
                            box = results[0].boxes.xyxy[i]
                            cls_id = results[0].boxes.cls[i]
                            conf_score = results[0].boxes.conf[i]
                            detections.append((box, cls_id, conf_score))

                elif OPERATION_MODE == "segmentation":
                    if results and hasattr(results[0], "masks") and results[0].masks is not None and len(results[0].masks.data) > 0:
                        masks_data = results[0].masks.data
                        for i in range(len(results[0].boxes)):
                            box = results[0].boxes.xyxy[i]
                            cls_id = results[0].boxes.cls[i]
                            conf_score = results[0].boxes.conf[i]
                            detections.append((box, cls_id, conf_score, masks_data[i]))
                        if detections:
                            # Sort detections by confidence and limit number drawn.
                            detections = sorted(detections, key=lambda d: d[2], reverse=True)
                            if NUM_CONTOURS_TO_DRAW < len(detections):
                                detections = detections[:NUM_CONTOURS_TO_DRAW]
                    else:
                        print(f"No segmentations found in image: {file_name}")

                # Determine whether to process the image based on detections.
                if CREATE_ONLY_IF_DETECTED and not detections:
                    skip_count += 1
                else:
                    detect_count += 1
                    # Save contour image copy if enabled.
                    if ENABLE_CONTOUR_FOLDER:
                        contour_img = img_pil.copy()
                        contour_img = draw_detections_on_pil(
                            contour_img,
                            detections,
                            OPERATION_MODE,
                            class_names,
                            scale_factor=1.0,
                        )
                        contour_save_name = f"{image_base_name}_contours{ext}"
                        contour_save_path = os.path.join(contour_folder, contour_save_name)
                        contour_img.save(contour_save_path)
                    # Save a copy of the original image if enabled.
                    if ENABLE_INPUT_FOLDER:
                        input_img = img_pil.copy()
                        input_save_name = f"{image_base_name}_input_copy{ext}"
                        input_save_path = os.path.join(input_copy_folder, input_save_name)
                        input_img.save(input_save_path)
            except FileNotFoundError as e:
                print(f"Error opening image {file_name}: {e}")
                skip_count += 1
            except Exception as e:
                print(f"Error processing image {file_name}: {e}")
                skip_count += 1

            # Update progress bar postfix only once per iteration.
            pbar.set_postfix(detect=detect_count, skip=skip_count, total=detect_count + skip_count)
            pbar.refresh()


def select_folder():
    """
    Opens a dialog to select a folder.
    """
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder_selected = filedialog.askdirectory()
    root.destroy()
    return folder_selected


if __name__ == "__main__":
    selected_folder = select_folder()
    if selected_folder:
        process_images(selected_folder)
    else:
        print("No folder selected.")
