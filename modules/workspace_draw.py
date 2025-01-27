# --------------------------------------------------------------------------
# File: modules/workspace_draw.py
# Description: Handles all drawing operations on the canvas.
# --------------------------------------------------------------------------

import math
from PIL import Image, ImageTk


class WorkspaceDrawer:
    """Manages image and polygon rendering on the workspace canvas."""

    def __init__(self, workspace):
        self.workspace = workspace
        self.photo_image = None

    def draw_all(self):
        """Clears canvas and draws the image, polygons, and any temp segments."""
        ws = self.workspace
        ws.canvas.delete("all")
        self._draw_image()
        self._draw_polygons()
        self._draw_temp_segment()

        # Trigger refresh in main app
        ws.event_generate("<<RefreshPolygonList>>", when="tail")

    def _draw_image(self):
        """Draws the main image onto the canvas with current offset and scale."""
        ws = self.workspace
        if not ws.image:
            return
        w = int(ws.base_width * ws.scale)
        h = int(ws.base_height * ws.scale)
        if w < 1:
            w = 1
        if h < 1:
            h = 1

        resized_img = ws.image.resize((w, h), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(resized_img)
        ws.canvas.create_image(ws.offset_x, ws.offset_y, image=self.photo_image, anchor="nw")

    def _draw_polygons(self):
        """Draws all polygons from the polygon manager."""
        ws = self.workspace
        for _, poly in ws.poly_manager.polygons.items():
            pts = poly["points"]
            color = poly["color"]
            is_closed = poly["is_closed"]

            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    p1, p2 = pts[i], pts[i + 1]
                    x1, y1 = ws._to_canvas_coords(p1.x, p1.y)
                    x2, y2 = ws._to_canvas_coords(p2.x, p2.y)
                    ws.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
                
                # Desenha a linha de fechamento se o polígono estiver fechado e tiver pelo menos 2 pontos
                if is_closed and len(pts) >= 2:
                    p1, p2 = pts[-1], pts[0] # Último e primeiro ponto
                    x1, y1 = ws._to_canvas_coords(p1.x, p1.y)
                    x2, y2 = ws._to_canvas_coords(p2.x, p2.y)
                    ws.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

            # Points (small circles)
            for pt in pts:
                cx, cy = ws._to_canvas_coords(pt.x, pt.y)
                ws.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=color, outline="")

    def _draw_temp_segment(self):
        """Draws the temporary segment while creating a bounding box in box mode."""
        ws = self.workspace
        if ws.is_drawing_segment and ws.temp_point:
            x1, y1 = ws._to_canvas_coords(ws.temp_point.x, ws.temp_point.y)
            ws.canvas.create_oval(x1 - 3, y1 - 3, x1 + 3, y1 + 3, fill=ws.line_color, outline="")
