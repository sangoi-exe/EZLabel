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
        # Agora cada polígono é mapeado pela COR em vez de key. Ex: {"#FF0000": {...}, "#00FF00": {...}}
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
            # Create a new polygon for that color
            p = PointData(cx, cy)
            self.polygons[color] = {
                "points": [p],
                "color": color,
                "class_id": "",
                "is_closed": False,
            }
            self.current_free_polygon = self.polygons[color]
        else:
            poly = self.polygons[color]
            # Se já estiver fechado, não vamos adicionar (depende da lógica que desejar).
            # Mas assumindo que se "is_closed" está False, continuamos a desenhar.
            if not poly["is_closed"]:
                first_pt = poly["points"][0]
                dist = math.dist((first_pt.x, first_pt.y), (cx, cy))
                if dist < 10:
                    # Fecha polígono
                    if poly["points"][-1] != first_pt:
                        poly["points"].append(first_pt)
                    poly["is_closed"] = True
                    class_id = simpledialog.askstring("Class ID", "Enter class number:")
                    poly["class_id"] = class_id if class_id else "0"
                else:
                    poly["points"].append(PointData(cx, cy))

    def create_box_polygon(self, p1, p2, color):
        """
        Creates a 2-point polygon in 'box' mode for the specified color.
        If a polygon with that color already exists and is open, it might
        be overwritten or extended, but aqui assumimos que criamos do zero.
        """
        self.polygons[color] = {
            "points": [p1, p2],
            "color": color,
            "class_id": "",
            "is_closed": False,
        }
        class_id = simpledialog.askstring("Class ID", "Enter class number:")
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
