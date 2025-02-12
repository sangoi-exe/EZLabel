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

        # Variáveis para o modo de seleção
        self.is_selecting_area = False
        self.sel_rect_id = None
        self.sel_rect_start_x = None
        self.sel_rect_start_y = None

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
        ws = self.workspace
        cx, cy = ws._to_image_coords(event.x, event.y)

        # -----------------------------
        # Novo modo: SELECTION
        # -----------------------------
        if ws.draw_mode == "selection":
            self.is_selecting_area = True
            self.sel_rect_start_x = event.x
            self.sel_rect_start_y = event.y
            self.sel_rect_id = ws.canvas.create_rectangle(
                self.sel_rect_start_x,
                self.sel_rect_start_y,
                self.sel_rect_start_x,
                self.sel_rect_start_y,
                outline="blue",
                dash=(2, 2),
            )
            return

        # -----------------------------
        # EXISTENTE: modo 'rect'
        # -----------------------------
        if ws.draw_mode == "rect":
            color = ws.line_color
            if color in ws.poly_manager.polygons:
                if ws._check_near_point(cx, cy) is None:
                    return
                else:
                    new_color = self.get_unused_color(ws)
                    if new_color is None:
                        return
                    ws.set_line_color(new_color)
                    color = new_color
            if not ws.is_drawing_segment:
                ws.temp_point = ws.PointDataClass(cx, cy)
                ws.is_drawing_segment = True
            else:
                p1 = ws.temp_point
                p2 = ws.PointDataClass(cx, cy)
                ws.poly_manager.create_box_polygon(p1, p2, color)
                ws.is_drawing_segment = False
                ws.temp_point = None
            ws.drawer.draw_all()
            return

        # -----------------------------
        # Lógica para arrastar pontos
        # -----------------------------
        found_point, poly_key, pt_idx = ws._find_point_near(cx, cy)
        if found_point:
            self.dragged_point = found_point
            self.drag_start_x = cx
            self.drag_start_y = cy
            return

        color = ws.line_color
        if ws.draw_mode == "free":
            poly = ws.poly_manager.get_polygon_by_color(color)
            if poly:
                if not poly["is_closed"]:
                    poly["points"].append(ws.PointDataClass(cx, cy))
                    ws.drawer.draw_all()
                    return
            else:
                ws.poly_manager.create_or_append_free_polygon(cx, cy, color)
                ws.drawer.draw_all()
                return

        if ws.draw_mode == "box":
            self._handle_box_click(cx, cy, color)

        ws.drawer.draw_all()

    def _on_left_drag(self, event):
        ws = self.workspace

        # Se estamos no modo selection e arrastando:
        if ws.draw_mode == "selection" and self.is_selecting_area and self.sel_rect_id:
            ws.canvas.coords(
                self.sel_rect_id,
                self.sel_rect_start_x,
                self.sel_rect_start_y,
                event.x,
                event.y,
            )
            return

        # Drag de ponto normal:
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
        ws = self.workspace

        # Finaliza seleção se estivermos no modo selection
        if ws.draw_mode == "selection" and self.is_selecting_area and self.sel_rect_id:
            x1 = self.sel_rect_start_x
            y1 = self.sel_rect_start_y
            x2 = event.x
            y2 = event.y
            # Remove o retângulo de seleção do canvas
            ws.canvas.delete(self.sel_rect_id)
            self.sel_rect_id = None
            self.is_selecting_area = False

            # Ordena as coordenadas do canvas
            min_cx, max_cx = sorted([x1, x2])
            min_cy, max_cy = sorted([y1, y2])

            # Converte do espaço do canvas para as coordenadas da imagem
            ix1, iy1 = ws._to_image_coords(min_cx, min_cy)
            ix2, iy2 = ws._to_image_coords(max_cx, max_cy)

            # Obtém o polígono ativo com base na cor atual
            active_poly = ws.poly_manager.get_polygon_by_color(ws.line_color)
            if not active_poly:
                messagebox.showinfo("Seleção", "Nenhum polígono ativo para seleção.")
                return

            # Coleta os pontos que estão dentro da área de seleção
            selected_points = []
            for pt in active_poly["points"]:
                if ix1 <= pt.x <= ix2 and iy1 <= pt.y <= iy2:
                    selected_points.append(pt)

            if not selected_points:
                # Se nada for selecionado, encerra.
                return

            # Ordenação circular (apenas para manter uma sequência coerente)
            if len(selected_points) > 1:
                cx = sum(pt.x for pt in selected_points) / len(selected_points)
                cy = sum(pt.y for pt in selected_points) / len(selected_points)
                selected_points.sort(key=lambda pt: math.atan2(pt.y - cy, pt.x - cx))

            # Cria cópias dos pontos selecionados nas mesmas coordenadas
            new_points = []
            for old_pt in selected_points:
                new_points.append(ws.PointDataClass(old_pt.x, old_pt.y))

            # Pergunta a classe e cria nova polyline fechada
            class_id = ws.prompt_class_selection()
            if class_id is not None:
                new_color = self.get_unused_color(ws)
                if new_color:
                    new_poly = {
                        "points": new_points,
                        "color": new_color,
                        "class_id": class_id,
                        "is_closed": True, 
                    }
                    ws.poly_manager.polygons[new_color] = new_poly
                    ws.drawer.draw_all()
            return

        # Se estávamos arrastando ponto, encerramos arrasto
        if self.dragged_point:
            self.dragged_point = None
            self.workspace.balloon_zoom.hide_zoom_view()
            self.workspace.drawer.draw_all()

    def _on_right_click(self, event):
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
        self.is_panning = False

    def _on_left_double_click(self, event):
        ws = self.workspace
        pm = ws.poly_manager
        color = ws.line_color
        poly = pm.get_polygon_by_color(color)
        if not poly:
            return

        poly_data = poly
        cx, cy = ws._to_image_coords(event.x, event.y)
        points = poly_data["points"]
        if not points:
            return

        first_pt = points[0]
        dist_to_first = math.dist((first_pt.x, first_pt.y), (cx, cy))

        # Fecha polígono se estiver aberto e o clique duplo for próximo do primeiro ponto
        if not poly_data["is_closed"] and dist_to_first < 20 and len(points) >= 2:
            if points[-1] != first_pt:
                points.append(first_pt)
            poly_data["is_closed"] = True
            class_id = ws.prompt_class_selection()
            poly_data["class_id"] = class_id if class_id else "0"
            ws.drawer.draw_all()
            return

        # Se o polígono está fechado, podemos inserir ponto no segmento
        if poly_data["is_closed"]:
            found_segment = ws._find_segment_near(cx, cy, radius=10)
            if found_segment:
                seg_poly_key, seg_index, x_ins, y_ins = found_segment
                pm.insert_point_on_segment(seg_poly_key, seg_index, x_ins, y_ins)
                ws.drawer.draw_all()

    def _on_mouse_move(self, event):
        self.workspace.canvas.config(cursor="tcross")

    def _on_mouse_wheel(self, event):
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

    def _handle_box_click(self, cx, cy, color):
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

    def get_unused_color(self, ws):
        """Returns a color from the available palette that is not used in any polygon."""
        available_colors = list(ws.parent.color_buttons.keys())
        used_colors = set(ws.poly_manager.polygons.keys())
        for col in available_colors:
            if col not in used_colors:
                return col
        return None
