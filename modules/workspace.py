# ------------------------------------------------------------------------------
# File: modules/workspace.py
# Description: Contains the WorkspaceFrame class with references to the new
#              managers (events, polygons, drawing).
# ------------------------------------------------------------------------------

import tkinter as tk
from PIL import Image
import math

from .balloon_zoom import BalloonZoom
from .shapes import PointData
from .workspace_events import WorkspaceEvents
from .workspace_polygons import WorkspacePolygons
from .workspace_draw import WorkspaceDrawer


class WorkspaceFrame(tk.Frame):
    """
    This frame contains the main drawing canvas, plus references to event,
    polygon, and drawing managers.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.image = None
        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Basic properties
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.base_width = 1
        self.base_height = 1
        self.line_color = "#FF0000"

        # States and references
        self.draw_mode = "free"  # "box" or "free"
        self.is_continuous_free_mode = True
        self.is_drawing_segment = False
        self.temp_point = None

        # PointData constructor reference (para evitar import redundante em event handler)
        self.PointDataClass = PointData

        # Managers
        self.balloon_zoom = BalloonZoom(self.canvas)
        self.poly_manager = WorkspacePolygons(self)
        self.drawer = WorkspaceDrawer(self)
        self.events = WorkspaceEvents(self)
        self.events.bind_all()

    def load_image(self, path):
        """Loads image, resets zoom/pan, clears polygons, and redraws."""
        self.image = Image.open(path)
        self.base_width = self.image.width
        self.base_height = self.image.height
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.poly_manager.clear_all()
        self.drawer.draw_all()

    def set_continuous_mode(self, val):
        """Activates/deactivates continuous mode in free drawing."""
        self.is_continuous_free_mode = val
        self.poly_manager.current_free_polygon = None
        self.drawer.draw_all()

    def set_draw_mode(self, mode):
        """Sets draw mode to 'box' or 'free' and resets related states."""
        self.draw_mode = mode
        self.temp_point = None
        self.is_drawing_segment = False
        self.poly_manager.current_free_polygon = None
        self.poly_manager.temp_free_point = None
        self.drawer.draw_all()

    def set_line_color(self, color):
        """Updates the color used for new polygons."""
        if color:
            self.line_color = color

    def set_selected_polygon(self, poly_key):
        """Delegates to polygon manager."""
        self.poly_manager.set_selected_polygon(poly_key)

    @property
    def polygons(self):
        """
        Maintains compatibility: returns the internal polygons dict
        so main_app can still access them directly if needed.
        """
        return self.poly_manager.polygons

    # ----------------------------
    # Utility methods:
    # ----------------------------

    def _to_image_coords(self, cx, cy):
        """Canvas -> image coordinates."""
        x = (cx - self.offset_x) / self.scale
        y = (cy - self.offset_y) / self.scale
        return x, y

    def _to_canvas_coords(self, x, y):
        """Image -> canvas coordinates."""
        cx = x * self.scale + self.offset_x
        cy = y * self.scale + self.offset_y
        return cx, cy

    def _find_point_near(self, x, y, radius=10):
        """
        Returns (closest_point, polygon_key, index_in_polygon)
        if found within 'radius' distance on canvas.
        """
        nearest_point = None
        nearest_poly_key = None
        nearest_pt_idx = None
        min_dist = float("inf")

        for key, poly in self.poly_manager.polygons.items():
            for i, pt in enumerate(poly["points"]):
                dist = math.dist((pt.x, pt.y), (x, y))
                if dist < min_dist and dist <= radius / self.scale:
                    min_dist = dist
                    nearest_point = pt
                    nearest_poly_key = key
                    nearest_pt_idx = i

        return (nearest_point, nearest_poly_key, nearest_pt_idx) if nearest_point else (None, None, None)

    def _check_near_point(self, x, y, radius=10):
        """
        Returns the nearest point if inside 'radius', or None.
        """
        found_point, _, _ = self._find_point_near(x, y, radius)
        return found_point

    def _find_segment_near(self, x, y, radius=20):
        """
        Searches all polygons for a line segment near (x, y).
        Returns (polygon_key, segment_index, x_proj, y_proj) if found.
        """
        best_dist = float("inf")
        best_result = None

        for key, poly in self.poly_manager.polygons.items():
            pts = poly["points"]
            num_points = len(pts)
            if num_points < 2:  # Polígono precisa de pelo menos 2 pontos para ter segmentos
                continue
            for i in range(num_points):  # Itera por todos os pontos
                p1 = pts[i]
                p2 = pts[(i + 1) % num_points]  # Próximo ponto, usando módulo para fechar o loop
                dist_info = self._point_to_segment_distance(x, y, p1.x, p1.y, p2.x, p2.y)
                dist, x_proj, y_proj, _ = dist_info

                # Converte projeção para canvas coords para comparar com radius
                cx_proj, cy_proj = self._to_canvas_coords(x_proj, y_proj)
                cx_click, cy_click = self._to_canvas_coords(x, y)
                canvas_dist = math.dist((cx_proj, cy_proj), (cx_click, cy_click))

                if canvas_dist < best_dist and canvas_dist <= radius:
                    best_dist = canvas_dist
                    best_result = (key, i, x_proj, y_proj)  # 'i' é o índice do ponto inicial do segmento
        return best_result

    def _point_to_segment_distance(self, px, py, x1, y1, x2, y2):
        """
        Returns (dist, x_proj, y_proj, t) for distance from (px, py) to segment (x1,y1)-(x2,y2).
        """
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            dist = math.dist((px, py), (x1, y1))
            return dist, x1, y1, 0

        t = ((px - x1) * dx + (py - y1) * dy) / float(dx * dx + dy * dy)
        if t < 0:
            t = 0
        elif t > 1:
            t = 1

        x_proj = x1 + t * dx
        y_proj = y1 + t * dy
        dist = math.dist((px, py), (x_proj, y_proj))
        return dist, x_proj, y_proj, t
