# ------------------------------------------------------------------------------
# File: modules/labels_handler.py
# Description: Handles loading and saving YOLO label files.
# ------------------------------------------------------------------------------

import os
from .shapes import PointData


class LabelHandler:
    """
    Label handler for YOLO segmentation format:
    class x1 y1 x2 y2 ... xN yN
    """

    def __init__(self):
        self.current_image_path = None

    def save_labels(self, polygons, img_width, img_height):
        """
        Saves each polygon in YOLO segmentation format:
            class x1 y1 x2 y2 ... xN yN
        All coords normalized to [0..1].
        """
        if not self.current_image_path:
            return

        folder = os.path.dirname(self.current_image_path)
        base_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
        txt_path = os.path.join(folder, base_name + ".txt")

        lines = []
        for poly_key, poly in polygons.items():
            pts = poly["points"]
            if len(pts) < 3:
                # Segmentation normally expects >= 3 points for a valid polygon.
                continue

            cls_id = poly.get("class_id", "0")
            # Normalize points to [0..1] range
            coords_norm = [f"{p.x / img_width:.6f} {p.y / img_height:.6f}" for p in pts]

            # Write "class" followed by all normalized (x, y) pairs
            line = f"{cls_id} " + " ".join(coords_norm)
            lines.append(line)

        # Write labels to file
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def load_labels(self, txt_path, workspace_frame):
        if not workspace_frame.image:
            return

        workspace_frame.poly_manager.clear_all()
        img_w = workspace_frame.image.width
        img_h = workspace_frame.image.height

        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()

                # YOLO bounding box format: class center_x center_y width height
                if len(parts) == 5:
                    try:
                        cls_id, center_x_norm, center_y_norm, width_norm, height_norm = map(float, parts)
                    except ValueError:
                        print(f"Skipping invalid line: {line}")
                        continue

                    # Convert normalized coordinates to absolute
                    center_x = center_x_norm * img_w
                    center_y = center_y_norm * img_h
                    width = width_norm * img_w
                    height = height_norm * img_h

                    # Calculate coordinates of the four corners
                    x1 = center_x - width / 2
                    y1 = center_y - height / 2
                    x2 = center_x + width / 2
                    y2 = center_y - height / 2
                    x3 = center_x + width / 2
                    y3 = center_y + height / 2
                    x4 = center_x - width / 2
                    y4 = center_y + height / 2

                    # Create polygon points
                    poly_points = [
                        PointData(x1, y1),
                        PointData(x2, y2),
                        PointData(x3, y3),
                        PointData(x4, y4),
                    ]

                    # Create polygon and add it to workspace
                    color = workspace_frame.line_color
                    polygon_dict = {
                        "points": poly_points,
                        "color": color,
                        "class_id": str(int(cls_id)),
                        "is_closed": True,
                    }
                    workspace_frame.polygons[color] = polygon_dict

                # YOLO segmentation format: class x1 y1 x2 y2 ... xN yN
                elif len(parts) >= 5 and len(parts) % 2 != 1:
                    try:
                        cls_id = parts[0]
                        coords = list(map(float, parts[1:]))

                        poly_points = []
                        for i in range(0, len(coords), 2):
                            xn = coords[i]
                            yn = coords[i + 1]
                            x_abs = xn * img_w
                            y_abs = yn * img_h
                            poly_points.append(PointData(x_abs, y_abs))

                        if len(poly_points) > 2:
                            # Create polygon and add it to workspace
                            color = workspace_frame.line_color
                            polygon_dict = {
                                "points": poly_points,
                                "color": color,
                                "class_id": cls_id,
                                "is_closed": True,
                            }
                            workspace_frame.polygons[color] = polygon_dict

                    except ValueError:
                        print(f"Skipping invalid line: {line}")
                        continue
