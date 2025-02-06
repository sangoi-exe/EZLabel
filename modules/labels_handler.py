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
        self.color_list = [
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FFFF00",
            "#FF00FF",
            "#00FFFF",
            "#000000",
            "#FFFFFF",
        ]
        self.color_index = 0
        self.polygon_counter = 0

    def save_labels(self, polygons, img_width, img_height, label_dest_path=None):
        """Saves each polygon in YOLO segmentation format: class x1 y1 x2 y2 ... xN yN"""
        if not self.current_image_path:
            return

        if label_dest_path is None:
            folder = os.path.dirname(self.current_image_path)
            base_name = os.path.splitext(os.path.basename(self.current_image_path))[0]
            label_dest_path = os.path.join(folder, base_name + ".txt")

        lines = []
        for poly in polygons.values():
            if len(poly["points"]) < 3:
                continue
            cls_id = poly.get("class_id", "0")
            coords_norm = [
                f"{p.x / img_width:.6f} {p.y / img_height:.6f}" for p in poly["points"]
            ]
            lines.append(f"{cls_id} " + " ".join(coords_norm))

        with open(label_dest_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def load_labels(self, txt_path, workspace_frame):
        """
        Loads labels from a YOLO format file and creates polygons in the workspace.
        Assigns a color from the color palette to each polygon.
        """
        if not workspace_frame.image:
            return

        workspace_frame.poly_manager.clear_all()
        img_w = workspace_frame.image.width
        img_h = workspace_frame.image.height

        self.color_index = 0  # Reset color index when loading new labels
        self.polygon_counter = 0

        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()

                if len(parts) == 5:
                    try:
                        (
                            cls_id,
                            center_x_norm,
                            center_y_norm,
                            width_norm,
                            height_norm,
                        ) = map(float, parts)
                    except ValueError:
                        continue

                    center_x = center_x_norm * img_w
                    center_y = center_y_norm * img_h
                    width = width_norm * img_w
                    height = height_norm * img_h

                    x1 = center_x - width / 2
                    y1 = center_y - height / 2
                    x2 = center_x + width / 2
                    y2 = y1
                    x3 = x2
                    y3 = center_y + height / 2
                    x4 = x1
                    y4 = y3

                    poly_points = [
                        PointData(x1, y1),
                        PointData(x2, y2),
                        PointData(x3, y3),
                        PointData(x4, y4),
                    ]

                    color = self.color_list[self.color_index % len(self.color_list)]
                    self.color_index += 1

                    polygon_dict = {
                        "points": poly_points,
                        "color": color,  # Usa a cor atribuída
                        "class_id": str(int(cls_id)),
                        "is_closed": True,
                    }

                    workspace_frame.poly_manager.polygons[color] = polygon_dict

                elif len(parts) >= 5 and len(parts) % 2 == 1:
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

                        if len(poly_points) >= 3:
                            color = self.color_list[
                                self.color_index % len(self.color_list)
                            ]
                            self.color_index += 1

                            polygon_dict = {
                                "points": poly_points,
                                "color": color,
                                "class_id": cls_id,
                                "is_closed": True,
                            }

                            workspace_frame.poly_manager.polygons[color] = polygon_dict

                    except ValueError:
                        continue

        workspace_frame.drawer.draw_all()
