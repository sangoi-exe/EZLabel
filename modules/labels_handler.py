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
                # Normally segmentation expects >=3 for a valid polygon,
                # but some want to store lines with only 2 points. Adjust as needed.
                continue

            cls_id = poly.get("class_id", "0")
            # Monta lista [x1, y1, x2, y2, ...] normalizada
            coords_norm = []
            for p in pts:
                xn = p.x / img_width
                yn = p.y / img_height
                coords_norm.append(f"{xn:.6f}")
                coords_norm.append(f"{yn:.6f}")

            # "class" + todos os pares x_i y_i
            line = f"{cls_id} " + " ".join(coords_norm)
            lines.append(line)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def load_labels(self, txt_path, workspace_frame):
        """
        Loads YOLO segmentation format:
        class x1 y1 x2 y2 ... xN yN
        Creates polygons in workspace_frame.
        """
        if not workspace_frame.image:
            return

        workspace_frame.polygons.clear()
        img_w = workspace_frame.image.width
        img_h = workspace_frame.image.height

        with open(txt_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    # Must have at least: class + x1 + y1 + x2 + y2
                    continue

                cls_id = parts[0]
                coords = parts[1:]  # x1, y1, x2, y2, ...

                # Precisamos de pares, então len(coords) deve ser múltiplo de 2
                if len(coords) % 2 != 0:
                    continue

                # Monta a lista de PointData
                poly_points = []
                for i in range(0, len(coords), 2):
                    try:
                        xn = float(coords[i])
                        yn = float(coords[i + 1])
                    except ValueError:
                        continue
                    # Converte para coordenadas absolutas
                    x_abs = xn * img_w
                    y_abs = yn * img_h
                    poly_points.append(PointData(x_abs, y_abs))

                if len(poly_points) < 2:
                    continue

                # Define uma chave e monta o dicionário do polígono
                first_x = int(poly_points[0].x)
                first_y = int(poly_points[0].y)
                polygon_key = (first_x, first_y)

                polygon_dict = {
                    "points": poly_points,
                    "color": workspace_frame.line_color,
                    "class_id": cls_id if cls_id else "0",
                    "is_closed": True,  # Normalmente polígono fechado
                }

                workspace_frame.polygons[polygon_key] = polygon_dict

        workspace_frame._redraw()
