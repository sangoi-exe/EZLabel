import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from modules.workspace import WorkspaceFrame
from modules.labels_handler import LabelHandler


class Tooltip:
    """Creates a tooltip that appears near a widget."""

    def __init__(self, widget, text, timeout=2000):
        self.widget = widget
        self.text = text
        self.timeout = timeout
        self.tipwindow = None

    def show(self):
        """Displays the tooltip at a fixed position relative to the main window."""
        if self.tipwindow:
            return
        master = self.widget.winfo_toplevel()
        x = master.winfo_x() + master.winfo_width() - 500
        y = master.winfo_y() + master.winfo_height() - 800
        self.tipwindow = tip = tk.Toplevel(master)
        tip.wm_overrideredirect(True)
        tip.geometry(f"200x50+{x}+{y}")
        label = tk.Label(
            tip, text=self.text, bg="yellow", relief="solid", borderwidth=1
        )
        label.pack(fill=tk.BOTH, expand=True)
        tip.after(self.timeout, tip.destroy)

    def hide(self):
        """Hides the tooltip."""
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YOLO Bounding Box Labeling App")
        self.attributes("-topmost", False)

        # Centraliza a janela no monitor onde o app foi iniciado.
        # Ajuste de posição baseado na posição atual do mouse (que deve estar no monitor desejado).
        self._place_on_current_monitor()

        self.class_definitions = {
            "0": "CNH aberta",
            "1": "CNH frente",
            "2": "CNH verso",
            "3": "RG aberto",
            "4": "RG frente",
            "5": "RG verso",
            "6": "CPF completo",
            "7": "CPF frente",
            "8": "CPF verso",
            "9": "Cic frente",
            "10": "Cic verso",
            "11": "Cert Nasc",
            "12": "Titulo aberto",
            "13": "Titulo frente",
            "14": "Titulo verso",
        }

        self.label_handler = LabelHandler()
        self.active_color = "#FF0000"

        # Bindings para teclas de navegação e modos de desenho
        self.bind_all("<Key-Down>", self._on_key_down)
        self.bind_all("<Key-Up>", self._on_key_up)
        self.bind_all("<Key-f>", self._on_shortcut_free)
        self.bind_all("<Key-b>", self._on_shortcut_box)
        self.bind_all("<Key-r>", self._on_shortcut_rect)
        self.bind_all("<Key-c>", self._on_shortcut_c_lection)
        self.bind_all("<Key-w>", self._on_key_up)
        self.bind_all("<Key-a>", self._on_key_up)
        self.bind_all("<Key-s>", self._on_key_down)
        self.bind_all("<Key-d>", self._on_key_down)
        self.bind_all("<Key-q>", self.generate_label_file)

        # Bind em cada cor usando as teclas numéricas (topo do teclado):
        self.bind_all("<Key-1>", lambda e: self._on_color_button_click("#FF0000"))
        self.bind_all("<Key-2>", lambda e: self._on_color_button_click("#00FF00"))
        self.bind_all("<Key-3>", lambda e: self._on_color_button_click("#0000FF"))
        self.bind_all("<Key-4>", lambda e: self._on_color_button_click("#FFFF00"))
        self.bind_all("<Key-5>", lambda e: self._on_color_button_click("#FF00FF"))
        self.bind_all("<Key-6>", lambda e: self._on_color_button_click("#00FFFF"))
        self.bind_all("<Key-7>", lambda e: self._on_color_button_click("#000000"))
        self.bind_all("<Key-8>", lambda e: self._on_color_button_click("#FFFFFF"))

        self._create_toolbar()

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.workspace_frame = WorkspaceFrame(self, self.class_definitions)
        self.workspace_frame.grid(row=1, column=0, sticky="nsew")

        self.files_frame = tk.Frame(self, bd=2, relief=tk.SUNKEN)
        self.files_frame.grid(row=1, column=1, sticky="ns")

        self._create_files_list()
        self.current_folder = None

    def _place_on_current_monitor(self, w=1200, h=600):
        """Centraliza a janela principal no monitor em que o mouse está,
        presumindo que seja o monitor onde o app foi aberto."""
        self.withdraw()
        self.update_idletasks()
        x_ptr = self.winfo_pointerx()
        y_ptr = self.winfo_pointery()
        x = x_ptr - w // 2
        y = y_ptr - h // 2
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.deiconify()

    def open_folder(self):
        """Opens a folder, lists image files and auto-selects the first image."""
        folder_selected = filedialog.askdirectory(
            parent=self, title="Select a folder", mustexist=True
        )
        if folder_selected:
            self.current_folder = folder_selected
            self._update_files_list()
            if self.files_listbox.size() > 0:
                self.files_listbox.selection_clear(0, tk.END)
                self.files_listbox.selection_set(0)
                self.files_listbox.activate(0)
                self._on_file_selected(index=0)

    def _on_shortcut_rect(self, event):
        """Shortcut: set drawing mode to 'rect'."""
        self.mode_combo.set("rect")
        self._on_mode_changed(event)

    def _on_shortcut_box(self, event):
        """Shortcut: set drawing mode to 'box'."""
        self.mode_combo.set("box")
        self._on_mode_changed(event)

    def _on_shortcut_free(self, event):
        """Shortcut: set drawing mode to 'free'."""
        self.mode_combo.set("free")
        self._on_mode_changed(event)

    def _on_shortcut_c_lection(self, event):
        """Shortcut: set drawing mode to 'selection'."""
        self.mode_combo.set("selection")
        self._on_mode_changed(event)

    def _create_toolbar(self):
        """Creates a toolbar with color squares, zoom combobox, etc."""
        toolbar = tk.Frame(self, bd=2, relief=tk.RAISED)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        btn_open_img = tk.Button(toolbar, text="Open Image", command=self.open_image)
        btn_open_img.pack(side=tk.LEFT, padx=5, pady=2)

        btn_open_label = tk.Button(
            toolbar, text="Open Label File", command=self.open_label_file
        )
        btn_open_label.pack(side=tk.LEFT, padx=5, pady=2)

        btn_open_folder = tk.Button(
            toolbar, text="Open Folder", command=self.open_folder
        )
        btn_open_folder.pack(side=tk.LEFT, padx=5, pady=2)

        tk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=5)
        # Adicionamos aqui o novo modo "selection"
        self.mode_combo = ttk.Combobox(
            toolbar,
            values=["box", "free", "rect", "selection"],
            state="readonly",
            width=9,
        )
        self.mode_combo.current(1)
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combo.pack(side=tk.LEFT, padx=2)

        tk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=(10, 2))
        self.zoom_combo = ttk.Combobox(
            toolbar,
            values=["25%", "50%", "75%", "100%", "150%", "200%", "300%"],
            width=5,
        )
        self.zoom_combo.set("100%")
        self.zoom_combo.bind("<<ComboboxSelected>>", self._on_zoom_combo_changed)
        self.zoom_combo.pack(side=tk.LEFT, padx=2)

        btn_zoom_fit = tk.Button(toolbar, text="Fit", command=self.zoom_fit)
        btn_zoom_fit.pack(side=tk.LEFT, padx=2)

        btn_generate = tk.Button(
            toolbar, text="Generate Label", command=self.generate_label_file
        )
        btn_generate.pack(side=tk.LEFT, padx=5, pady=2)
        self.btn_generate = btn_generate

        self.continuous_var = tk.BooleanVar(value=True)
        self.continuous_check = tk.Checkbutton(
            toolbar,
            text="Continuous",
            variable=self.continuous_var,
            command=self._on_continuous_switch,
        )
        self.continuous_check.pack(side=tk.LEFT, padx=5, pady=2)
        self.continuous_check.config(state="active")

        self.overwrite_label_var = tk.BooleanVar(value=False)
        self.overwrite_check = tk.Checkbutton(
            toolbar,
            text="Overwrite Label",
            variable=self.overwrite_label_var,
        )
        self.overwrite_check.pack(side=tk.LEFT, padx=5, pady=2)

        color_list = [
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FFFF00",
            "#FF00FF",
            "#00FFFF",
            "#000000",
            "#FFFFFF",
        ]
        self.color_buttons = {}
        for c in color_list:
            btn = tk.Button(
                toolbar,
                bg=c,
                width=2,
                command=lambda col=c: self._on_color_button_click(col),
            )
            btn.pack(side=tk.LEFT, padx=2)
            self.color_buttons[c] = btn

        self._update_color_button_relief()

    def _create_files_list(self):
        tk.Label(self.files_frame, text="Files:").pack(side=tk.TOP, padx=5, pady=5)
        self.files_listbox = tk.Listbox(
            self.files_frame, width=30, height=25, selectmode=tk.SINGLE
        )
        self.files_listbox.pack(side=tk.TOP, fill=tk.Y, expand=True)
        self.files_listbox.bind("<<ListboxSelect>>", self._on_file_selected)

    def _on_file_selected(self, event=None, index=None):
        if not self.current_folder:
            return
        if index is None:
            selection = event.widget.curselection() if event else None
            if selection:
                index = selection[0]
            else:
                return
        filename = self.files_listbox.get(index)
        filepath = os.path.join(self.current_folder, filename)
        if os.path.isfile(filepath):
            self.workspace_frame.load_image(filepath)
            self.label_handler.current_image_path = filepath

            base_name, ext = os.path.splitext(filename)
            txt_filename = base_name + ".txt"
            txt_filepath = os.path.join(self.current_folder, txt_filename)
            if os.path.exists(txt_filepath):
                self.label_handler.load_labels(txt_filepath, self.workspace_frame)
        else:
            messagebox.showwarning("Warning", f"File not found: {filepath}")

    def _on_key_up(self, event):
        current_selection = self.files_listbox.curselection()
        if current_selection:
            index = current_selection[0]
            if index > 0:
                self.files_listbox.selection_clear(index)
                index -= 1
                self.files_listbox.selection_set(index)
                self.files_listbox.activate(index)
                self.files_listbox.see(index)
                self._on_file_selected(index=index)
        else:
            if self.files_listbox.size() > 0:
                index = 0
                self.files_listbox.selection_set(index)
                self.files_listbox.activate(index)
                self._on_file_selected(index=index)

    def _on_key_down(self, event):
        current_selection = self.files_listbox.curselection()
        if current_selection:
            index = current_selection[0]
            if index < self.files_listbox.size() - 1:
                self.files_listbox.selection_clear(index)
                index += 1
                self.files_listbox.selection_set(index)
                self.files_listbox.activate(index)
                self.files_listbox.see(index)
                self._on_file_selected(index=index)
        else:
            if self.files_listbox.size() > 0:
                index = 0
                self.files_listbox.selection_set(index)
                self.files_listbox.activate(index)
                self._on_file_selected(index=index)

    def _update_files_list(self):
        self.files_listbox.delete(0, tk.END)
        if not self.current_folder:
            return
        image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
        for f in os.listdir(self.current_folder):
            if not f.lower().endswith(image_extensions):
                continue
            self.files_listbox.insert(tk.END, f)

    def zoom_fit(self):
        self.workspace_frame.zoom_to_fit()

    def _on_color_button_click(self, color):
        self.active_color = color
        self._update_color_button_relief()
        self.workspace_frame.set_line_color(color)

    def _update_color_button_relief(self):
        for c, btn in self.color_buttons.items():
            if c == self.active_color:
                btn.config(relief=tk.SUNKEN)
            else:
                btn.config(relief=tk.RAISED)

    def _on_continuous_switch(self):
        self.workspace_frame.set_continuous_mode(self.continuous_var.get())

    def _on_mode_changed(self, event):
        new_mode = self.mode_combo.get()
        self.workspace_frame.set_draw_mode(new_mode)
        # Desabilita o "Continuous" se for box ou selection; caso contrário, habilita
        if new_mode in ("box", "selection"):
            self.continuous_check.config(state="disabled")
        else:
            self.continuous_check.config(state="normal")

    def _on_zoom_combo_changed(self, event):
        val_str = self.zoom_combo.get().replace("%", "")
        try:
            val = float(val_str)
            self.workspace_frame.set_manual_zoom(val / 100.0)
        except ValueError:
            pass

    def update_zoom_in_combo(self, zoom_val):
        if zoom_val < 10:
            self.zoom_combo.set(f"0{zoom_val}%")
        else:
            self.zoom_combo.set(f"{zoom_val}%")

    def open_image(self):
        image_path = filedialog.askopenfilename(
            parent=self,
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")],
        )
        if image_path:
            self.workspace_frame.load_image(image_path)
            self.label_handler.current_image_path = image_path

    def open_label_file(self):
        if not self.workspace_frame.image:
            messagebox.showwarning("Warning", "Load an image before loading labels.")
            return
        txt_path = filedialog.askopenfilename(
            parent=self,
            title="Select a YOLO label file",
            filetypes=[("Text Files", "*.txt")],
        )
        if txt_path:
            if os.path.exists(txt_path):
                self.label_handler.load_labels(txt_path, self.workspace_frame)
            else:
                messagebox.showwarning("Warning", f"File not found: {txt_path}")

    def generate_label_file(self, event=None):
        if not self.workspace_frame.image:
            messagebox.showwarning("Warning", "No image loaded.")
            return

        if not self.workspace_frame.polygons:
            messagebox.showwarning("Warning", "No polygons drawn to generate labels.")
            return

        current_image_path = self.label_handler.current_image_path
        if not current_image_path:
            messagebox.showwarning("Warning", "No image path set.")
            return

        if self.overwrite_label_var.get():
            label_dest_path = os.path.splitext(current_image_path)[0] + ".txt"
            self.label_handler.save_labels(
                self.workspace_frame.polygons,
                self.workspace_frame.image.width,
                self.workspace_frame.image.height,
                label_dest_path=label_dest_path,
            )
        else:
            train_dir = os.path.join(os.getcwd(), "train")
            images_dir = os.path.join(train_dir, "images")
            labels_dir = os.path.join(train_dir, "labels")
            os.makedirs(images_dir, exist_ok=True)
            os.makedirs(labels_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(current_image_path))[0]
            label_dest_path = os.path.join(labels_dir, base_name + ".txt")

            self.label_handler.save_labels(
                self.workspace_frame.polygons,
                self.workspace_frame.image.width,
                self.workspace_frame.image.height,
                label_dest_path=label_dest_path,
            )

            image_dest_path = os.path.join(
                images_dir, os.path.basename(current_image_path)
            )
            try:
                shutil.move(current_image_path, image_dest_path)
            except Exception as e:
                messagebox.showerror("Error", f"Error moving image file: {str(e)}")
                return

            self.workspace_frame.clear_workspace()
            self._update_files_list()
            messagebox.showinfo(
                "Success", "Label generated and image moved successfully."
            )

        tip = Tooltip(self.btn_generate, "Label generated successfully")
        tip.show()

        if self.files_listbox.size() > 0:
            current_selection = self.files_listbox.curselection()
            if current_selection:
                current_index = current_selection[0]
                if self.overwrite_label_var.get():
                    new_index = (
                        current_index + 1
                        if current_index < self.files_listbox.size() - 1
                        else current_index
                    )
                else:
                    new_index = (
                        current_index
                        if current_index < self.files_listbox.size()
                        else self.files_listbox.size() - 1
                    )
            else:
                new_index = 0
            self.files_listbox.selection_clear(0, tk.END)
            self.files_listbox.selection_set(new_index)
            self.files_listbox.activate(new_index)
            self._on_file_selected(index=new_index)
            self._on_shortcut_free(event)
            

    def set_zoom_percentage(self):
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
