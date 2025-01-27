# -------------------------------------------------------------------------
# main_app.py (somente partes alteradas)
# -------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os

from modules.workspace import WorkspaceFrame
from modules.labels_handler import LabelHandler


class MainApplication(tk.Tk):
    """Main window with toolbar, including color squares for polygon selection."""

    def __init__(self):
        super().__init__()
        self.title("YOLO Bounding Box Labeling App")
        self.geometry("1200x800+50+50")
        self.attributes("-topmost", False)

        self.label_handler = LabelHandler()

        self.active_color = "#FF0000"

        self._create_toolbar()

        self.workspace_frame = WorkspaceFrame(self)
        self.workspace_frame.pack(fill=tk.BOTH, expand=True)

    def _create_toolbar(self):
        """Creates a toolbar with color squares, zoom combobox, etc."""
        toolbar = tk.Frame(self, bd=2, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # "Open Image" button
        btn_open_img = tk.Button(toolbar, text="Open Image", command=self.open_image)
        btn_open_img.pack(side=tk.LEFT, padx=5, pady=2)

        # "Open Label" button
        btn_open_label = tk.Button(toolbar, text="Open Label File", command=self.open_label_file)
        btn_open_label.pack(side=tk.LEFT, padx=5, pady=2)

        # Draw mode combobox (unchanged except removed references to polygon selection)
        tk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_combo = ttk.Combobox(toolbar, values=["box", "free"], state="readonly", width=6)
        self.mode_combo.current(1)  # default "box" or "free"
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combo.pack(side=tk.LEFT, padx=2)

        # Zoom combobox
        tk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=(10, 2))
        self.zoom_combo = ttk.Combobox(toolbar, values=["25%", "50%", "75%", "100%", "150%", "200%", "300%"], width=5)
        self.zoom_combo.set("100%")
        self.zoom_combo.bind("<<ComboboxSelected>>", self._on_zoom_combo_changed)
        self.zoom_combo.pack(side=tk.LEFT, padx=2)

        # "Generate Label" button
        btn_generate = tk.Button(toolbar, text="Generate Label", command=self.generate_label_file)
        btn_generate.pack(side=tk.LEFT, padx=5, pady=2)

        # Checkbutton "continuous" for free mode
        self.continuous_var = tk.BooleanVar(value=True)
        self.continuous_check = tk.Checkbutton(toolbar, text="Continuous", variable=self.continuous_var, command=self._on_continuous_switch)
        self.continuous_check.pack(side=tk.LEFT, padx=5, pady=2)
        self.continuous_check.config(state="active")

        # NOVO: Quadrados de cor para associar a cada polígono
        color_list = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#000000", "#FFFFFF"]
        self.color_buttons = {}
        for c in color_list:
            btn = tk.Button(toolbar, bg=c, width=2, command=lambda col=c: self._on_color_button_click(col))  # pequeno quadrado
            btn.pack(side=tk.LEFT, padx=2)

            # Armazena referência para podermos mudar o 'relief'
            self.color_buttons[c] = btn

        # Ajusta o relief da cor inicial
        self._update_color_button_relief()

    def _on_color_button_click(self, color):
        """
        Sets the active color, updates the button relief, and informs the workspace.
        """
        self.active_color = color
        self._update_color_button_relief()
        # Diz ao workspace para usar essa cor para o polígono a ser editado/criado
        self.workspace_frame.set_line_color(color)

    def _update_color_button_relief(self):
        """Updates relief so that only the active color button looks 'pressed'."""
        for c, btn in self.color_buttons.items():
            if c == self.active_color:
                btn.config(relief=tk.SUNKEN)
            else:
                btn.config(relief=tk.RAISED)

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


def main():
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
