# modules/workspace.py
# ------------------------------------------------------------------------------
# File: modules/workspace.py
# Description: Contains the WorkspaceFrame class with canvas, zoom, pan, etc.
# ------------------------------------------------------------------------------

import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import math

from .balloon_zoom import BalloonZoom
from .shapes import PolygonData, PointData


class WorkspaceFrame(tk.Frame):
    """
    This frame contains the main drawing canvas, manages the image,
    zooming, panning, polygons, and user interactions for bounding boxes.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.image = None
        self.photo_image = None

        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Zoom / Pan
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.base_width = 1
        self.base_height = 1

        # Modo de desenho: "box" ou "free"
        self.draw_mode = "free"
        self.current_free_polygon = None  # usado em modo "free"

        # Modo continuous no free
        self.is_continuous_free_mode = True

        # Polygons
        self.polygons = {}  # dictionary of polygons
        self.selected_polygon_key = None  # Guarda qual polígono está em edição

        # Active line segment
        self.temp_point = None
        self.is_drawing_segment = False

        # For dragging existing points
        self.dragged_point = None
        self.drag_start_x = None
        self.drag_start_y = None

        # For panning
        self.is_panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

        # Balloon zoom helper
        self.balloon_zoom = BalloonZoom(self.canvas)

        # Default line color
        self.line_color = "#FF0000"

        # Bind events
        self._bind_events()

    def set_continuous_mode(self, val):
        """Ativa/desativa o modo continuous dentro do free mode."""
        self.is_continuous_free_mode = val
        # Também reinicia estados temporários
        self.temp_free_point = None
        self.current_free_polygon = None
        self._redraw()

    def set_draw_mode(self, mode):
        """Define se é 'box' ou 'free'."""
        self.draw_mode = mode
        # Zera as variáveis temporárias caso o usuário mude de modo no meio do desenho
        self.temp_point = None
        self.temp_free_point = None
        self.current_free_polygon = None
        self.is_drawing_segment = False
        self.dragged_point = None
        self._redraw()

    def _bind_events(self):
        self.canvas.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Button-1>", self._on_left_click)
        self.canvas.bind("<B1-Motion>", self._on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
        self.canvas.bind("<Button-3>", self._on_right_click)
        self.canvas.bind("<B3-Motion>", self._on_pan_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_pan_release)

        # Captura duplo-clique com botão esquerdo:
        self.canvas.bind("<Double-Button-1>", self._on_left_double_click)

        # Zoom com wheel
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)

        self.canvas.bind("<Motion>", self._on_mouse_move)

    def load_image(self, path):
        """
        Loads the image, resets zoom/pan, and redraws.
        """
        self.image = Image.open(path)
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.base_width = self.image.width
        self.base_height = self.image.height
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.polygons.clear()
        self._redraw()

    def _on_configure(self, event):
        """
        Adjusts the canvas content when the frame is resized.
        Keeps current zoom scale intact (no auto zoom).
        """
        self._redraw()

    def set_line_color(self, color):
        if color:
            self.line_color = color

    def _on_left_click(self, event):
        """
        If user has a 'selected_polygon_key', new points go to that polygon.
        Otherwise, normal logic: if there's a point near, we drag. If not, we handle 'box' or 'free'.
        """
        cx, cy = self._to_image_coords(event.x, event.y)

        # 1) Tenta achar ponto próximo para arrastar
        found_point, poly_key, pt_idx = self._find_point_near(cx, cy)
        if found_point:
            self.dragged_point = found_point
            self.drag_start_x = cx
            self.drag_start_y = cy
            return

        # 2) Se há polígono selecionado, adicionar ponto nele (a não ser que estejamos em 'box' mode)
        if self.selected_polygon_key and self.draw_mode == "free":
            poly = self.polygons[self.selected_polygon_key]
            # Se o polígono estava fechado, acabamos de abrir em set_selected_polygon
            poly["points"].append(PointData(cx, cy))
            self._redraw()
            return

        # 3) Se não há polígono selecionado, mantém lógica pré-existente
        if self.draw_mode == "box":
            self._handle_box_click(cx, cy)
        else:
            self._handle_free_click(cx, cy)

        self._redraw()

    # ----------------------------------------------------
    # Novo handler para duplo clique
    # ----------------------------------------------------
    def _on_left_double_click(self, event):
        """
        Se temos polígono selecionado, e ele não estiver fechado,
        checar se duplo-clique foi perto do primeiro ponto para fechar.
        Caso contrário, mantém a lógica adicional de inserir ponto no meio do segmento etc.
        """
        cx, cy = self._to_image_coords(event.x, event.y)

        # Prioridade 1: se polígono selecionado existir e não estiver fechado,
        # e duplo-clique for perto do primeiro ponto => fechar
        if self.selected_polygon_key:
            poly = self.polygons.get(self.selected_polygon_key)
            if poly and not poly["is_closed"]:
                first_pt = poly["points"][0]
                dist = math.dist((first_pt.x, first_pt.y), (cx, cy))
                if dist < 10 and len(poly["points"]) >= 3:
                    # Fecha
                    poly["is_closed"] = True
                    if poly["points"][-1] != first_pt:
                        poly["points"].append(first_pt)
                    class_id = tk.simpledialog.askstring("Class ID", "Enter class number:")
                    poly["class_id"] = class_id if class_id else "0"
                    # Continua selecionado, mas agora está fechado
                    self._redraw()
                    return

        # Se não foi esse caso, usamos a lógica anterior (inserir ponto etc.)
        # 2) Verifica se está perto de um ponto existente
        found_point, pk, pt_idx = self._find_point_near(cx, cy, radius=10)
        if found_point:
            self._insert_point_after_point(pk, pt_idx, cx, cy)
            self._redraw()
            return

        # 3) Verificar se está perto de um segmento
        found_segment = self._find_segment_near(cx, cy, radius=10)
        if found_segment:
            seg_poly_key, seg_index, x_ins, y_ins = found_segment
            self._insert_point_on_segment(seg_poly_key, seg_index, x_ins, y_ins)
            self._redraw()
            return

    def _find_segment_near(self, x, y, radius=10):
        """
        Searches all polygons for a line segment near (x, y).
        Returns (polygon_key, segment_index, x_proj, y_proj) if found; None otherwise.
        The 'segment_index' is the index of the first point in that segment.
        """
        best_dist = float("inf")
        best_result = None

        for key, poly in self.polygons.items():
            pts = poly["points"]
            # Check each pair of consecutive points
            for i in range(len(pts) - 1):
                p1, p2 = pts[i], pts[i + 1]
                dist, x_proj, y_proj, _ = self._point_to_segment_distance(x, y, p1.x, p1.y, p2.x, p2.y)
                # Convert projection + click coords to canvas for correct radius check
                cx_proj, cy_proj = self._to_canvas_coords(x_proj, y_proj)
                cx_click, cy_click = self._to_canvas_coords(x, y)
                canvas_dist = math.dist((cx_proj, cy_proj), (cx_click, cy_click))

                if canvas_dist < best_dist and canvas_dist <= radius:
                    best_dist = canvas_dist
                    best_result = (key, i, x_proj, y_proj)

        return best_result

    def _point_to_segment_distance(self, px, py, x1, y1, x2, y2):
        """
        Computes the minimal distance from (px, py) to the segment (x1, y1)-(x2, y2).
        Returns (dist, x_proj, y_proj, t):
        - dist: minimal distance
        - (x_proj, y_proj): the projection on the segment
        - t: param in [0..1] indicating where the projection falls
        """
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            # Segment is actually a single point
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

    def _insert_point_on_segment(self, poly_key, seg_index, x_ins, y_ins):
        """
        Inserts a new point at (x_ins, y_ins) in the polygon 'poly_key',
        splitting the segment [seg_index, seg_index+1].
        """
        if poly_key not in self.polygons:
            return
        poly = self.polygons[poly_key]
        pts = poly["points"]
        new_pt = PointData(x_ins, y_ins)
        pts.insert(seg_index + 1, new_pt)

    def _insert_point_after_point(self, poly_key, point_index, x_new, y_new):
        """
        Inserts a new point immediately after 'point_index' within the polygon 'poly_key'.
        (x_new, y_new) is the location where the user double-clicked.
        """
        if poly_key not in self.polygons:
            return
        polygon = self.polygons[poly_key]
        pts = polygon["points"]
        new_pt = PointData(x_new, y_new)
        pts.insert(point_index + 1, new_pt)

    def _handle_box_click(self, cx, cy):
        """Comportamento antigo de 2 pontos (bounding box)."""
        snapped = self._check_near_point(cx, cy)
        if snapped:
            cx, cy = snapped.x, snapped.y

        if self.dragged_point:
            return

        if not self.is_drawing_segment:
            self.temp_point = PointData(cx, cy)
            self.is_drawing_segment = True
        else:
            p1 = self.temp_point
            p2 = PointData(cx, cy)
            first_point_key = (int(p1.x), int(p1.y))
            self.polygons[first_point_key] = {"points": [p1, p2], "color": self.line_color, "class_id": "", "is_closed": False}
            class_id = simpledialog.askstring("Class ID", "Enter class number:")
            self.polygons[first_point_key]["class_id"] = class_id if class_id else "0"
            self.is_drawing_segment = False
            self.temp_point = None

    def _handle_free_click(self, cx, cy):
        """
        Polígono livre: a cada clique adiciona 1 ponto.
        Se clicar próximo do primeiro ponto, fecha o polígono.
        """
        if not self.current_free_polygon:
            # Inicia um novo polígono
            p = PointData(cx, cy)
            self.current_free_polygon = {"points": [p], "color": self.line_color, "class_id": "", "is_closed": False}
            first_point_key = (int(p.x), int(p.y))
            self.polygons[first_point_key] = self.current_free_polygon
        else:
            # Verifica se está perto do primeiro ponto => fecha polígono
            first_pt = self.current_free_polygon["points"][0]
            dist = math.dist((first_pt.x, first_pt.y), (cx, cy))
            if dist < 10 and not self.current_free_polygon["is_closed"]:
                # Unifica o último ponto ao primeiro para fechar o polígono
                self.current_free_polygon["is_closed"] = True
                # Remove o último ponto se já estiver igual ao primeiro para evitar duplicatas
                if self.current_free_polygon["points"][-1] != first_pt:
                    self.current_free_polygon["points"].append(first_pt)
                # Pergunta classe e finaliza
                class_id = simpledialog.askstring("Class ID", "Enter class number:")
                self.current_free_polygon["class_id"] = class_id if class_id else "0"
                self.current_free_polygon = None
            else:
                # Adiciona ponto e continua
                self.current_free_polygon["points"].append(PointData(cx, cy))

    def _on_left_drag(self, event):
        """
        Drags the point if 'dragged_point' is set. Now we clamp coordinates
        so the point cannot leave the image boundary. We also call balloon zoom
        passing the mouse pointer's root coords for correct positioning.
        """
        if not self.dragged_point or not self.image:
            return

        # Convert mouse event coords to image coords
        cx, cy = self._to_image_coords(event.x, event.y)

        # Clamp the point inside the image
        if cx < 0:
            cx = 0
        if cx > self.image.width:
            cx = self.image.width
        if cy < 0:
            cy = 0
        if cy > self.image.height:
            cy = self.image.height

        self.dragged_point.x = cx
        self.dragged_point.y = cy

        # Snap to nearby existing point if close enough
        snap_target = self._check_near_point(cx, cy)
        if snap_target and snap_target is not self.dragged_point:
            dist = math.dist((snap_target.x, snap_target.y), (cx, cy))
            if dist < 10:
                self.dragged_point.x = snap_target.x
                self.dragged_point.y = snap_target.y

        # Update balloon zoom with pointer's absolute coords
        self.balloon_zoom.update_zoom_view(
            self.image,
            self.dragged_point.x,
            self.dragged_point.y,
            self.scale,
            mouse_x_root=self.canvas.winfo_pointerx(),
            mouse_y_root=self.canvas.winfo_pointery(),
        )

        self._redraw()

    def _on_left_release(self, event):
        """Solta o ponto arrastado, se houver."""
        if self.dragged_point:
            # Se o ponto arrastado for o primeiro ponto do polígono fechado,
            # não faz nada especial, pois o primeiro e último pontos já estão unidos
            # Se for outro ponto, apenas solta o arraste
            self.dragged_point = None
            self.balloon_zoom.hide_zoom_view()
            self._redraw()

    def _on_right_click(self, event):
        """
        Right click: either delete point or start panning.
        If right-click on a point, asks to delete.
        Otherwise, prepare for panning.
        """
        cx, cy = self._to_image_coords(event.x, event.y)
        found_point, polygon_key, point_idx = self._find_point_near(cx, cy)
        if found_point:
            ans = messagebox.askyesno("Delete Point", "Do you want to delete this point?")
            if ans:
                # Delete the point from that polygon
                self._delete_point(polygon_key, point_idx)
            return
        # If no point found, we start panning
        self.is_panning = True
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def _on_pan_drag(self, event):
        """
        Right mouse button drag for panning.
        """
        if not self.is_panning:
            return
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.offset_x += dx
        self.offset_y += dy
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self._redraw()

    def _on_pan_release(self, event):
        """
        Release right mouse button to stop panning.
        """
        self.is_panning = False

    def _on_mouse_wheel(self, event):
        """
        Zooms the image in/out based on mouse wheel.
        The pivot is the mouse cursor, so that point under the cursor stays in place.
        """
        delta = 1
        if hasattr(event, "delta"):
            if event.delta < 0:
                delta = -1
        elif event.num == 5:  # Linux
            delta = -1

        zoom_factor = 1.1
        if delta < 0:
            zoom_factor = 1 / zoom_factor

        pivot_cx, pivot_cy = event.x, event.y
        # Convert canvas coords -> image coords
        px, py = self._to_image_coords(pivot_cx, pivot_cy)

        # Apply the new scale
        old_scale = self.scale
        self.scale *= zoom_factor
        if self.scale < 0.1:
            self.scale = 0.1
        if self.scale > 10:
            self.scale = 10

        # Recalculate the offset so that (px, py) remains under the cursor
        new_x, new_y = self._to_canvas_coords(px, py)
        self.offset_x += pivot_cx - new_x
        self.offset_y += pivot_cy - new_y

        # Update zoom combo in main app
        zoom_val = int(round(self.scale * 100))
        self.parent.update_zoom_in_combo(zoom_val)

        self._redraw()

    def _on_mouse_move(self, event):
        """
        Remove o warp pointer (snap de cursor) que existia antes.
        Agora, se não estamos arrastando um ponto, não há snap.
        Somente ajustamos o cursor para 'tcross'.
        """
        self.canvas.config(cursor="tcross")

    def set_manual_zoom(self, scale):
        """
        Set the zoom level based on a scale factor (0.1 to 10).
        """
        if scale < 0.1:
            scale = 0.1
        if scale > 10:
            scale = 10
        self.scale = scale
        self._redraw()

    def _delete_point(self, polygon_key, point_idx):
        """
        Deletes a point and the associated segment from polygons.
        """
        if polygon_key in self.polygons:
            self.polygons[polygon_key]["points"].pop(point_idx)
            # Se for o primeiro ponto e houver mais pontos, atualiza a chave
            if point_idx == 0 and self.polygons[polygon_key]["points"]:
                new_key = (int(self.polygons[polygon_key]["points"][0].x), int(self.polygons[polygon_key]["points"][0].y))
                self.polygons[new_key] = self.polygons.pop(polygon_key)
            # Se o polígono tem menos de 2 pontos, remove-o
            if len(self.polygons[polygon_key]["points"]) < 2:
                del self.polygons[polygon_key]
        self._redraw()

    def _find_point_near(self, x, y, radius=10):
        """
        Retorna (ponto_mais_prox, chave_poligono, idx_ponto) para
        o ponto mais próximo dentro de (x, y), ou (None, None, None).
        """
        nearest_point = None
        nearest_poly_key = None
        nearest_pt_idx = None
        min_dist = float("inf")
        for key, poly in self.polygons.items():
            for i, pt in enumerate(poly["points"]):
                dist = math.dist((pt.x, pt.y), (x, y))
                if dist < min_dist and dist <= radius / self.scale:
                    min_dist = dist
                    nearest_point = pt
                    nearest_poly_key = key
                    nearest_pt_idx = i
        return (nearest_point, nearest_poly_key, nearest_pt_idx) if nearest_point else (None, None, None)

    def _to_image_coords(self, cx, cy):
        """
        Converts canvas coords to image coords, considering offset and scale.
        """
        x = (cx - self.offset_x) / self.scale
        y = (cy - self.offset_y) / self.scale
        return x, y

    def _to_canvas_coords(self, x, y):
        """
        Converts image coords to canvas coords.
        """
        cx = x * self.scale + self.offset_x
        cy = y * self.scale + self.offset_y
        return cx, cy

    def _draw_image(self):
        """
        Draws the image on the canvas at current offset and scale.
        """
        if not self.image:
            return
        # Resized image
        w = int(self.base_width * self.scale)
        h = int(self.base_height * self.scale)
        if w < 1:
            w = 1
        if h < 1:
            h = 1

        resized_img = self.image.resize((w, h), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(resized_img)
        self.canvas.create_image(self.offset_x, self.offset_y, image=self.photo_image, anchor=tk.NW)

    def _draw_polygons(self):
        """
        Desenha todos os polígonos armazenados no dicionário.
        """
        for key, poly in self.polygons.items():
            pts = poly["points"]
            color = poly["color"]
            is_closed = poly["is_closed"]

            if len(pts) >= 2:
                for i in range(len(pts) - 1):
                    p1, p2 = pts[i], pts[i + 1]
                    x1, y1 = self._to_canvas_coords(p1.x, p1.y)
                    x2, y2 = self._to_canvas_coords(p2.x, p2.y)
                    self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
                if is_closed and len(pts) > 2:
                    # Conectar o último ponto ao primeiro (já está unificado)
                    pass  # Não precisa desenhar novamente

            # Desenha pontos
            for pt in pts:
                cx, cy = self._to_canvas_coords(pt.x, pt.y)
                self.canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=color, outline="")

    def set_selected_polygon(self, poly_key):
        """
        Sets which polygon is currently selected for editing.
        If 'poly_key' is None, no polygon is selected.
        """
        if poly_key and poly_key in self.polygons:
            self.selected_polygon_key = poly_key
            # Se esse polígono estiver marcado como fechado, vamos "abrir" se quisermos editar mais.
            # (Opcional) Pergunta se o usuário quer reabrir.
            if self.polygons[poly_key].get("is_closed", False):
                # Retiramos o último ponto se for igual ao primeiro, para 'reabrir' adequadamente:
                pts = self.polygons[poly_key]["points"]
                if len(pts) > 2 and pts[0] == pts[-1]:
                    pts.pop()  # remove o último igual ao primeiro
                self.polygons[poly_key]["is_closed"] = False
        else:
            self.selected_polygon_key = None

    def _redraw(self):
        """
        Clears the canvas and redraws the image and polygons.
        Also triggers a refresh of the polygon list in the main app.
        """
        self.canvas.delete("all")
        self._draw_image()
        self._draw_polygons()
        self._draw_temp_segment()

        # Dispara evento para o MainApp atualizar combobox de polígonos
        self.event_generate("<<RefreshPolygonList>>", when="tail")

    def _draw_temp_segment(self):
        """
        Draws a temporary line segment if the user has started drawing a segment.
        """
        if self.is_drawing_segment and self.temp_point:
            # Mostrar um marcador para o primeiro ponto
            x1, y1 = self._to_canvas_coords(self.temp_point.x, self.temp_point.y)
            self.canvas.create_oval(x1 - 3, y1 - 3, x1 + 3, y1 + 3, fill=self.line_color, outline="")

    def _check_near_point(self, x, y, radius=10):
        """
        Retorna o ponto mais próximo de (x, y) se estiver dentro do raio,
        caso contrário retorna None.
        """
        nearest_point = None
        min_dist = float("inf")
        for poly in self.polygons.values():
            for pt in poly["points"]:
                dist = math.dist((pt.x, pt.y), (x, y))
                if dist < min_dist and dist <= radius / self.scale:
                    min_dist = dist
                    nearest_point = pt
        return nearest_point

    def _handle_free_continuous(self, cx, cy):
        """Vários pontos em sequência, fecha ao clicar perto do primeiro."""
        if not self.current_free_polygon:
            # cria novo polígono
            p = PointData(cx, cy)
            self.current_free_polygon = PolygonData([p], self.line_color)
            first_point_key = (int(p.x), int(p.y))
            self.polygons[first_point_key] = {"points": [p], "color": self.line_color, "class_id": "", "is_closed": False}
        else:
            # verifica se está perto do primeiro para fechar
            first_pt = self.current_free_polygon["points"][0]
            dist = math.dist((first_pt.x, first_pt.y), (cx, cy))
            if dist < 10 and not self.current_free_polygon["is_closed"]:
                # cria ponto final igual ao primeiro => polígono fechado
                self.current_free_polygon["points"].append(self.current_free_polygon["points"][0])
                self.current_free_polygon["is_closed"] = True
                class_id = simpledialog.askstring("Class ID", "Enter class number:")
                self.current_free_polygon["class_id"] = class_id if class_id else "0"
                self.current_free_polygon = None
            else:
                # apenas adiciona mais um ponto
                self.current_free_polygon["points"].append(PointData(cx, cy))

    def _handle_free_two_points(self, cx, cy):
        """
        Modo free NÃO contínuo => cada par de pontos gera um polígono (linha) e já finaliza.
        """
        if not self.temp_free_point:
            # primeiro ponto do segmento
            self.temp_free_point = PointData(cx, cy)
        else:
            # segundo ponto => cria polígono 2 pts
            p2 = PointData(cx, cy)
            first_point_key = (int(self.temp_free_point.x), int(self.temp_free_point.y))
            self.polygons[first_point_key] = {
                "points": [self.temp_free_point, p2],
                "color": self.line_color,
                "class_id": "",
                "is_closed": False,
            }
            class_id = simpledialog.askstring("Class ID", "Enter class number:")
            self.polygons[first_point_key]["class_id"] = class_id if class_id else "0"

            self.temp_free_point = None  # zera para próxima linha
