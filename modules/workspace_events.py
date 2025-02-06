# modules/workspace_events.py
# --------------------------------------------------------------------------
# File: modules/workspace_events.py
# Description: Contains all event-related logic (mouse, keyboard, etc.).
# --------------------------------------------------------------------------

import math
from tkinter import messagebox, simpledialog


class WorkspaceEvents:
    """Manages the event callbacks and bindings for the workspace."""

    def __init__(self, workspace):
        self.workspace = workspace
        self.dragged_point = None
        self.drag_start_x = None
        self.drag_start_y = None
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

    def bind_all(self):
        """Binds all events to the workspace canvas."""
        ws = self.workspace
        c = ws.canvas

        c.bind("<Configure>", self._on_configure)
        c.bind("<Button-1>", self._on_left_click)
        c.bind("<B1-Motion>", self._on_left_drag)
        c.bind("<ButtonRelease-1>", self._on_left_release)
        c.bind("<Button-3>", self._on_right_click)
        c.bind("<B3-Motion>", self._on_pan_drag)
        c.bind("<ButtonRelease-3>", self._on_pan_release)
        c.bind("<Double-Button-1>", self._on_left_double_click)

        c.bind("<MouseWheel>", self._on_mouse_wheel)
        c.bind("<Button-4>", self._on_mouse_wheel)
        c.bind("<Button-5>", self._on_mouse_wheel)
        c.bind("<Motion>", self._on_mouse_move)

    def _on_configure(self, event):
        """Redraws on canvas resize."""
        self.workspace.drawer.draw_all()

    def _on_left_click(self, event):
        """
        Handles left-click logic: find a point to drag, or create polygon points
        based on 'box' vs 'free' modes, now tied to the active color.
        """
        ws = self.workspace
        pm = ws.poly_manager

        cx, cy = ws._to_image_coords(event.x, event.y)
        found_point, poly_key, pt_idx = ws._find_point_near(cx, cy)
        if found_point:
            # If clicked near an existing point, prepare to drag it
            self.dragged_point = found_point
            self.drag_start_x = cx
            self.drag_start_y = cy
            return

        # Get the polygon associated with the current active color
        color = ws.line_color
        poly = pm.get_polygon_by_color(color)

        # Logic for "free" mode: either append a point or create a new polygon
        if ws.draw_mode == "free":
            if poly:
                # poly_key, poly_data = poly # Removido: Linha original que causava erro
                poly_data = poly  # Adicionado: 'poly' já é o dicionário do polígono
                # Append point to an existing polygon of the current color
                if not poly_data["is_closed"]:
                    poly_data["points"].append(ws.PointDataClass(cx, cy))
                    ws.drawer.draw_all()
                    return
            else:
                # Create a new polygon if no polygon exists for the current color
                pm.create_or_append_free_polygon(cx, cy, color)
                ws.drawer.draw_all()
                return

        # Logic for "box" mode: handle two-click bounding box creation
        if ws.draw_mode == "box":
            self._handle_box_click(cx, cy, color)

        ws.drawer.draw_all()

    def _handle_box_click(self, cx, cy, color):
        """Box mode: two clicks = two points => bounding box polygon."""
        ws = self.workspace
        pm = ws.poly_manager

        snapped = ws._check_near_point(cx, cy)
        if snapped:
            cx, cy = snapped.x, snapped.y

        if self.dragged_point:
            return

        if not ws.is_drawing_segment:
            ws.temp_point = ws.PointDataClass(cx, cy)
            ws.is_drawing_segment = True
        else:
            p1 = ws.temp_point
            p2 = ws.PointDataClass(cx, cy)
            pm.create_box_polygon(p1, p2, color)
            ws.is_drawing_segment = False
            ws.temp_point = None

    def _handle_free_click(self, cx, cy):
        """Free mode: create or append to free polygon. Closes if near first point."""
        ws = self.workspace
        pm = ws.poly_manager

        if ws.is_continuous_free_mode:
            pm.create_or_append_free_polygon(cx, cy)
        else:
            if not pm.temp_free_point:
                pm.temp_free_point = ws.PointDataClass(cx, cy)
            else:
                p1 = pm.temp_free_point
                p2 = ws.PointDataClass(cx, cy)
                first_key = (int(p1.x), int(p1.y))
                pm.polygons[first_key] = {
                    "points": [p1, p2],
                    "color": ws.line_color,
                    "class_id": "",
                    "is_closed": False,
                }
                class_id = simpledialog.askstring("Class ID", "Enter class number:")
                pm.polygons[first_key]["class_id"] = class_id if class_id else "0"
                pm.temp_free_point = None

    def _on_left_drag(self, event):
        """Drags an existing point if any is selected."""
        ws = self.workspace
        if not self.dragged_point or not ws.image:
            return

        cx, cy = ws._to_image_coords(event.x, event.y)
        if cx < 0:
            cx = 0
        if cy < 0:
            cy = 0
        if cx > ws.image.width:
            cx = ws.image.width
        if cy > ws.image.height:
            cy = ws.image.height

        self.dragged_point.x = cx
        self.dragged_point.y = cy

        snap_target = ws._check_near_point(cx, cy)
        if snap_target and snap_target is not self.dragged_point:
            dist = math.dist((snap_target.x, snap_target.y), (cx, cy))
            if dist < 10:
                self.dragged_point.x = snap_target.x
                self.dragged_point.y = snap_target.y

        ws.balloon_zoom.update_zoom_view(
            ws.image,
            self.dragged_point.x,
            self.dragged_point.y,
            ws.scale,
            mouse_x_root=ws.canvas.winfo_pointerx(),
            mouse_y_root=ws.canvas.winfo_pointery(),
        )
        ws.drawer.draw_all()

    def _on_left_release(self, event):
        """Stops dragging a point."""
        if self.dragged_point:
            self.dragged_point = None
            self.workspace.balloon_zoom.hide_zoom_view()
            self.workspace.drawer.draw_all()

    def _on_right_click(self, event):
        """
        Right-click: if on a point, ask to delete. Otherwise, start panning.
        """
        ws = self.workspace
        pm = ws.poly_manager
        cx, cy = ws._to_image_coords(event.x, event.y)
        found_point, polygon_key, pt_idx = ws._find_point_near(cx, cy)

        if found_point:
            ans = messagebox.askyesno(
                "Delete Point", "Do you want to delete this point?"
            )
            if ans:
                pm.delete_point(polygon_key, pt_idx)
                ws.drawer.draw_all()
            return

        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def _on_pan_drag(self, event):
        """Pans the workspace when right-click dragged."""
        if not self.is_panning:
            return
        ws = self.workspace
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        ws.offset_x += dx
        ws.offset_y += dy
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        ws.drawer.draw_all()

    def _on_pan_release(self, event):
        """Stops panning."""
        self.is_panning = False

    def _on_left_double_click(self, event):
        """
        New logic:
          1) Finds the polygon by current color.
          2) If that polygon is open and double-click is near the first point => close polygon + class ID.
          3) Otherwise, if that polygon is closed and double-click is near a segment => insert a new point.
        """
        ws = self.workspace
        pm = ws.poly_manager
        color = ws.line_color
        poly = pm.get_polygon_by_color(color)
        if not poly:
            # If there's no polygon for the selected color, do nothing
            return

        # poly_key, poly_data = poly # Removido: Linha original que causava erro (desnecessário aqui)
        poly_data = poly  # Adicionado: 'poly' já é o dicionário do polígono

        cx, cy = ws._to_image_coords(event.x, event.y)
        points = poly_data["points"]
        if not points:
            return

        first_pt = points[0]
        dist_to_first = math.dist((first_pt.x, first_pt.y), (cx, cy))

        # 1) Se polígono está aberto e double-click é perto do primeiro ponto => fechar polígono
        if not poly_data["is_closed"] and dist_to_first < 20 and len(points) >= 2:
            # Fecha polígono unindo último ao primeiro
            if points[-1] != first_pt:
                points.append(first_pt)
            poly_data["is_closed"] = True
            class_id = ws.prompt_class_selection()
            poly_data["class_id"] = class_id if class_id else "0"
            ws.drawer.draw_all()
            return

        # 2) Se o polígono está fechado, podemos inserir ponto extra se clique duplo ocorreu numa reta
        if poly_data["is_closed"]:
            found_segment = ws._find_segment_near(cx, cy, radius=10)
            if found_segment:
                seg_poly_key, seg_index, x_ins, y_ins = found_segment
                # Checar se a cor do segmento é a cor do polígono atual # Removido: Não precisa mais checar a cor, pois _find_segment_near já retorna a chave.
                pm.insert_point_on_segment(seg_poly_key, seg_index, x_ins, y_ins)
                ws.drawer.draw_all()

    def _on_mouse_move(self, event):
        """Updates cursor; no snap to pointer warping now."""
        self.workspace.canvas.config(cursor="tcross")

    def _on_mouse_wheel(self, event):
        """Zoom in/out based on mouse wheel, pivot at mouse cursor."""
        ws = self.workspace
        delta = 1
        if hasattr(event, "delta"):
            if event.delta < 0:
                delta = -1
        elif event.num == 5:
            delta = -1

        zoom_factor = 1.1
        if delta < 0:
            zoom_factor = 1 / zoom_factor

        pivot_cx, pivot_cy = event.x, event.y
        px, py = ws._to_image_coords(pivot_cx, pivot_cy)

        old_scale = ws.scale
        ws.scale *= zoom_factor
        if ws.scale < 0.1:
            ws.scale = 0.1
        if ws.scale > 10:
            ws.scale = 10

        new_x, new_y = ws._to_canvas_coords(px, py)
        ws.offset_x += pivot_cx - new_x
        ws.offset_y += pivot_cy - new_y

        zoom_val = int(round(ws.scale * 100))
        ws.parent.update_zoom_in_combo(zoom_val)

        ws.drawer.draw_all()
