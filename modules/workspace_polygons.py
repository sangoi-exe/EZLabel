# --------------------------------------------------------------------------
# workspace_polygons.py (versão ajustada)
# --------------------------------------------------------------------------

import math
from tkinter import simpledialog
from .shapes import PointData


class WorkspacePolygons:
    """Manages polygon operations (creation, editing, storage), now tied to color."""

    def __init__(self, workspace):
        self.workspace = workspace
        self.polygons = {}
        self.current_free_polygon = None
        self.temp_free_point = None

    def get_polygon_by_color(self, color):
        """
        Returns the polygon dict associated with the given color, or None if it doesn't exist yet.
        """
        return self.polygons.get(color)

    def create_or_append_free_polygon(self, cx, cy, color):
        """
        Creates or appends a point to the polygon of 'color' in free mode.
        If it doesn't exist yet, starts a new polygon.
        """
        if color not in self.polygons:
            p = PointData(cx, cy)
            self.polygons[color] = {  # Modificação 1: Usa a cor como chave do polígono.
                "points": [p],
                "color": color,
                "class_id": "",
                "is_closed": False,
            }
            self.current_free_polygon = self.polygons[color]
        else:
            poly = self.polygons[color]
            if not poly["is_closed"]:
                first_pt = poly["points"][0]
                dist = math.dist((first_pt.x, first_pt.y), (cx, cy))
                if dist < 10:
                    if poly["points"][-1] != first_pt:
                        poly["points"].append(first_pt)
                    poly["is_closed"] = True
                    class_id = self.workspace.prompt_class_selection()
                    poly["class_id"] = class_id if class_id else "0"
                else:
                    poly["points"].append(PointData(cx, cy))

    def create_box_polygon(self, p1, p2, color):
        """
        Creates a rectangular polygon from two diagonal points.
        """
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y

        # Ordena os pontos para obter os cantos corretos
        min_x, max_x = sorted([x1, x2])
        min_y, max_y = sorted([y1, y2])

        # Define os quatro pontos do retângulo
        rect_points = [
            PointData(min_x, min_y),
            PointData(max_x, min_y),
            PointData(max_x, max_y),
            PointData(min_x, max_y),
        ]

        self.polygons[color] = {  # Modificação 2: Usa a cor como chave do polígono.
            "points": rect_points,
            "color": color,
            "class_id": "",
            "is_closed": True,
        }
        class_id = self.workspace.prompt_class_selection()
        self.polygons[color]["class_id"] = class_id if class_id else "0"

    def delete_point(self, color, point_idx):
        """
        Deletes a point from the polygon of the given color.
        If the polygon ends up too small, remove it entirely.
        """
        if color not in self.polygons:
            return
        poly = self.polygons[color]
        poly["points"].pop(point_idx)

        # Se ficou menor que 2 pontos, apagamos o polígono
        if len(poly["points"]) < 2:
            del self.polygons[color]

    def insert_point_on_segment(self, color, seg_index, x_ins, y_ins):
        """Inserts a point at (x_ins, y_ins) in the polygon with that color."""
        if color not in self.polygons:
            return
        poly = self.polygons[color]
        new_pt = PointData(x_ins, y_ins)
        poly["points"].insert(seg_index + 1, new_pt)

    def insert_point_after(self, color, point_index, x_new, y_new):
        """Inserts a new point after 'point_index' in the polygon with that color."""
        if color not in self.polygons:
            return
        poly = self.polygons[color]
        new_pt = PointData(x_new, y_new)
        poly["points"].insert(point_index + 1, new_pt)

    def clear_all(self):
        """Clears all polygons."""
        self.polygons.clear()
        self.current_free_polygon = None
        self.temp_free_point = None
