# ------------------------------------------------------------------------------
# File: main_app.py
# Description: Entry point for the bounding box labeling application.
# ------------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os

from modules.workspace import WorkspaceFrame
from modules.labels_handler import LabelHandler
from modules.color_palette import ColorPaletteDialog


class MainApplication(tk.Tk):
    """Janela principal com toolbar, combobox de zoom e modo de desenho."""

    def __init__(self):
        super().__init__()
        self.title("YOLO Bounding Box Labeling App")
        self.geometry("1200x800+50+50")
        self.attributes("-topmost", False)

        self.label_handler = LabelHandler()

        self._create_toolbar()

        self.workspace_frame = WorkspaceFrame(self)
        self.workspace_frame.pack(fill=tk.BOTH, expand=True)

        self.workspace_frame.bind("<<RefreshPolygonList>>", self._on_refresh_polygon_list)

    def _create_toolbar(self):
        """Cria uma toolbar com botões e o combobox de zoom."""
        toolbar = tk.Frame(self, bd=2, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Botão 'Open Image'
        btn_open_img = tk.Button(toolbar, text="Open Image", command=self.open_image)
        btn_open_img.pack(side=tk.LEFT, padx=5, pady=2)

        # Botão 'Open Label'
        btn_open_label = tk.Button(toolbar, text="Open Label File", command=self.open_label_file)
        btn_open_label.pack(side=tk.LEFT, padx=5, pady=2)

        # Modo de desenho (combobox) - sem mudanças exceto que guardamos referência:
        tk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_combo = ttk.Combobox(toolbar, values=["box", "free"], state="readonly", width=6)
        self.mode_combo.current(1)  # "box" default
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combo.pack(side=tk.LEFT, padx=2)

        # ComboBox de zoom
        tk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=(10, 2))
        self.zoom_combo = ttk.Combobox(toolbar, values=["25%", "50%", "75%", "100%", "150%", "200%", "300%"], width=5, state="normal")
        self.zoom_combo.set("100%")
        self.zoom_combo.bind("<<ComboboxSelected>>", self._on_zoom_combo_changed)
        self.zoom_combo.pack(side=tk.LEFT, padx=2)

        # Botão 'Line Color'
        btn_color = tk.Button(toolbar, text="Line Color", command=self.choose_line_color)
        btn_color.pack(side=tk.LEFT, padx=5, pady=2)

        # Botão 'Generate Label'
        btn_generate = tk.Button(toolbar, text="Generate Label", command=self.generate_label_file)
        btn_generate.pack(side=tk.LEFT, padx=5, pady=2)

        # Checkbutton 'continuous' - agora guardamos a referência em self.continuous_check
        self.continuous_var = tk.BooleanVar(value=True)
        self.continuous_check = tk.Checkbutton(toolbar, text="Continuous", variable=self.continuous_var, command=self._on_continuous_switch)
        self.continuous_check.pack(side=tk.LEFT, padx=5, pady=2)
        self.continuous_check.config(state="active")  # inicia desabilitado se modo='box'

        # NOVO: Combobox para escolher polígono
        tk.Label(toolbar, text="Polygon:").pack(side=tk.LEFT, padx=(10, 2))
        self.poly_combo = ttk.Combobox(toolbar, values=[], state="readonly", width=15)
        self.poly_combo.bind("<<ComboboxSelected>>", self._on_poly_selected)
        self.poly_combo.pack(side=tk.LEFT, padx=2)

    def _on_continuous_switch(self):
        """Envia True/False para o workspace para ativar/desativar continuous no free mode."""
        self.workspace_frame.set_continuous_mode(self.continuous_var.get())

    def _on_mode_changed(self, event):
        """
        Quando o modo muda, habilita ou desabilita a checkbutton 'continuous'
        e informa o workspace.
        """
        new_mode = self.mode_combo.get()
        self.workspace_frame.set_draw_mode(new_mode)
        if new_mode == "box":
            self.continuous_check.config(state="disabled")
        else:
            self.continuous_check.config(state="normal")

    def _on_zoom_combo_changed(self, event):
        """
        Lê o valor do combobox (ex.: "150%") e seta no workspace.
        Não trava o zoom, apenas altera para esse valor.
        """
        val_str = self.zoom_combo.get().replace("%", "")
        try:
            val = float(val_str)
            self.workspace_frame.set_manual_zoom(val / 100.0)
        except ValueError:
            pass  # ignora se o usuário digitou algo inválido

    def _on_refresh_polygon_list(self, event=None):
        """
        Atualiza a combobox de polígonos com base no dicionário self.workspace_frame.polygons.
        """
        polygon_keys = []
        for k in self.workspace_frame.polygons:
            # k normalmente é (int_x, int_y). Transformamos em string para exibir na combobox.
            polygon_keys.append(str(k))
        self.poly_combo["values"] = polygon_keys

        # Se não houver polígonos, limpamos
        if not polygon_keys:
            self.poly_combo.set("")
        else:
            # Seleciona o primeiro como padrão (ou nenhum)
            self.poly_combo.set("")

    def _on_poly_selected(self, event):
        """
        Quando o usuário seleciona um polígono na combobox, enviamos essa informação
        para o workspace para que ele fique 'ativo' para edição.
        """
        selection = self.poly_combo.get()
        if not selection:
            self.workspace_frame.set_selected_polygon(None)
            return

        # Transformar string "(x, y)" de volta em tupla (x, y)
        # Caso falhe, setamos None
        try:
            poly_key = eval(selection)  # ex: "(10, 20)" -> (10, 20)
            if isinstance(poly_key, tuple) and len(poly_key) == 2:
                self.workspace_frame.set_selected_polygon(poly_key)
            else:
                self.workspace_frame.set_selected_polygon(None)
        except:
            self.workspace_frame.set_selected_polygon(None)

    def update_zoom_in_combo(self, zoom_val):
        """
        Atualiza a combobox de zoom ao usar a wheel.
        zoom_val é inteiro (por ex. 77), mas se for < 10, exibimos com zero à esquerda.
        """
        if zoom_val < 10:
            self.zoom_combo.set(f"0{zoom_val}%")
        else:
            self.zoom_combo.set(f"{zoom_val}%")

    def open_image(self):
        """
        Opens file dialog to select an image and load it into the workspace.
        """
        file_dialog = tk.Toplevel(self)
        file_dialog.attributes("-topmost", True)
        file_dialog.withdraw()
        image_path = filedialog.askopenfilename(
            parent=file_dialog, title="Select an image", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        file_dialog.destroy()

        if image_path:
            self.workspace_frame.load_image(image_path)
            self.label_handler.current_image_path = image_path

    def open_label_file(self):
        """
        Opens file dialog to select a YOLO label file and loads existing bounding boxes.
        """
        if not self.workspace_frame.image:
            messagebox.showwarning("Warning", "Load an image before loading labels.")
            return

        file_dialog = tk.Toplevel(self)
        file_dialog.attributes("-topmost", True)
        file_dialog.withdraw()
        txt_path = filedialog.askopenfilename(parent=file_dialog, title="Select a YOLO label file", filetypes=[("Text Files", "*.txt")])
        file_dialog.destroy()

        if txt_path:
            if os.path.exists(txt_path):
                self.label_handler.load_labels(txt_path, self.workspace_frame)
            else:
                messagebox.showwarning("Warning", f"File not found: {txt_path}")

    def generate_label_file(self):
        """
        Generates the YOLO label file with all bounding boxes drawn.
        """
        if not self.workspace_frame.image:
            messagebox.showwarning("Warning", "No image loaded.")
            return

        if not self.workspace_frame.polygons:
            messagebox.showwarning("Warning", "No polygons drawn to generate labels.")
            return

        self.label_handler.save_labels(self.workspace_frame.polygons, self.workspace_frame.image.width, self.workspace_frame.image.height)

    def set_zoom_percentage(self):
        """
        Prompts the user to input a new zoom percentage and updates the workspace.
        """

        def apply_zoom():
            try:
                val = float(entry_zoom.get())
                self.workspace_frame.set_manual_zoom(val / 100.0)
            except ValueError:
                pass
            dialog_zoom.destroy()

        dialog_zoom = tk.Toplevel(self)
        dialog_zoom.title("Set Zoom %")
        dialog_zoom.attributes("-topmost", True)
        dialog_zoom.geometry("+200+200")

        label_info = tk.Label(dialog_zoom, text="Enter new zoom percentage:")
        label_info.pack(padx=10, pady=5)

        entry_zoom = tk.Entry(dialog_zoom)
        entry_zoom.insert(0, "100")
        entry_zoom.pack(padx=10, pady=5)

        btn_ok = tk.Button(dialog_zoom, text="OK", command=apply_zoom)
        btn_ok.pack(pady=5)

    def choose_line_color(self):
        """
        Opens a color palette dialog for choosing the line color.
        """
        cp = ColorPaletteDialog(self)
        self.workspace_frame.set_line_color(cp.result_color)


def main():
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
