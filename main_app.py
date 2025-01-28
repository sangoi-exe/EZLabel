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
        """Displays the tooltip."""
        if self.tipwindow:
            return

        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 10
        y = self.widget.winfo_rooty() + int(self.widget.winfo_height() / 2)
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)
        self.widget.after(self.timeout, self.hide)

    def hide(self):
        """Hides the tooltip."""
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class MainApplication(tk.Tk):
    """Main window with toolbar, including color squares for polygon selection."""

    def __init__(self):
        super().__init__()
        self.title("YOLO Bounding Box Labeling App")
        self.geometry("1200x600+50+50")
        self.attributes("-topmost", False)

        self.class_definitions = {
            # "0": "CNH_Aberta",
            # "1": "CNH_Frente",
            # "3": "CNH_Verso",
            # "4": "RG_Aberta",
            # "5": "RG_Frente",
            # "6": "RG_Verso",
            # "7": "CPF_Frente",
            # "8": "CPF_Verso",
            # "9": "Doc_Foto",
            "0": "Fatura_Luz",
            "1": "Fatura_Agua",
            "2": "Fatura_Telefone",
            "3": "Cabeçalho",
        }

        self.label_handler = LabelHandler()

        self.active_color = "#FF0000"

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

    def _create_toolbar(self):
        """Creates a toolbar with color squares, zoom combobox, etc."""
        toolbar = tk.Frame(self, bd=2, relief=tk.RAISED)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # "Open Image" button
        btn_open_img = tk.Button(toolbar, text="Open Image", command=self.open_image)
        btn_open_img.pack(side=tk.LEFT, padx=5, pady=2)

        # "Open Label" button
        btn_open_label = tk.Button(
            toolbar, text="Open Label File", command=self.open_label_file
        )
        btn_open_label.pack(side=tk.LEFT, padx=5, pady=2)

        # "Open Folder" button
        btn_open_folder = tk.Button(
            toolbar, text="Open Folder", command=self.open_folder
        )
        btn_open_folder.pack(side=tk.LEFT, padx=5, pady=2)

        # Draw mode combobox
        tk.Label(toolbar, text="Mode:").pack(side=tk.LEFT, padx=5)
        self.mode_combo = ttk.Combobox(
            toolbar, values=["box", "free"], state="readonly", width=6
        )
        self.mode_combo.current(1)
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)
        self.mode_combo.pack(side=tk.LEFT, padx=2)

        # Zoom combobox
        tk.Label(toolbar, text="Zoom:").pack(side=tk.LEFT, padx=(10, 2))
        self.zoom_combo = ttk.Combobox(
            toolbar,
            values=["25%", "50%", "75%", "100%", "150%", "200%", "300%"],
            width=5,
        )
        self.zoom_combo.set("100%")
        self.zoom_combo.bind("<<ComboboxSelected>>", self._on_zoom_combo_changed)
        self.zoom_combo.pack(side=tk.LEFT, padx=2)

        # 'Zoom Fit' button
        btn_zoom_fit = tk.Button(toolbar, text="Fit", command=self.zoom_fit)
        btn_zoom_fit.pack(side=tk.LEFT, padx=2)

        # "Generate Label" button
        btn_generate = tk.Button(
            toolbar, text="Generate Label", command=self.generate_label_file
        )
        btn_generate.pack(side=tk.LEFT, padx=5, pady=2)
        self.btn_generate = btn_generate  # Store reference for tooltip

        # Checkbutton "continuous" for free mode
        self.continuous_var = tk.BooleanVar(value=True)
        self.continuous_check = tk.Checkbutton(
            toolbar,
            text="Continuous",
            variable=self.continuous_var,
            command=self._on_continuous_switch,
        )
        self.continuous_check.pack(side=tk.LEFT, padx=5, pady=2)
        self.continuous_check.config(state="active")

        # Color squares for polygon selection
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
        """Creates the listbox to display files in the selected folder."""
        tk.Label(self.files_frame, text="Files:").pack(side=tk.TOP, padx=5, pady=5)
        self.files_listbox = tk.Listbox(
            self.files_frame, width=30, height=25, selectmode=tk.SINGLE
        )
        self.files_listbox.pack(side=tk.TOP, fill=tk.Y, expand=True)
        self.files_listbox.bind("<<ListboxSelect>>", self._on_file_selected)

    def _on_file_selected(self, event):
        """Handles the selection of a file from the listbox."""
        if not self.current_folder:
            return
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            filename = event.widget.get(index)
            filepath = os.path.join(self.current_folder, filename)
            if os.path.isfile(filepath):
                self.workspace_frame.load_image(filepath)
                self.label_handler.current_image_path = filepath

    def open_folder(self):
        """Opens a folder and lists the image files in the files frame."""
        folder_selected = filedialog.askdirectory(
            parent=self, title="Select a folder", mustexist=True
        )
        if folder_selected:
            self.current_folder = folder_selected
            self._update_files_list()

    def _update_files_list(self):
        """Updates the files listbox with files from the current folder."""
        self.files_listbox.delete(0, tk.END)
        if not self.current_folder:
            return
        image_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
        files = [
            f
            for f in os.listdir(self.current_folder)
            if f.lower().endswith(image_extensions)
        ]
        for f in files:
            self.files_listbox.insert(tk.END, f)

    def zoom_fit(self):
        """Zooms to fit the image in the workspace."""
        self.workspace_frame.zoom_to_fit()

    def _on_color_button_click(self, color):
        """Sets the active color and updates button relief."""
        self.active_color = color
        self._update_color_button_relief()
        self.workspace_frame.set_line_color(color)

    def _update_color_button_relief(self):
        """Updates relief so that only the active color button looks 'pressed'."""
        for c, btn in self.color_buttons.items():
            if c == self.active_color:
                btn.config(relief=tk.SUNKEN)
            else:
                btn.config(relief=tk.RAISED)

    def _on_continuous_switch(self):
        """Activates or deactivates continuous mode in free drawing."""
        self.workspace_frame.set_continuous_mode(self.continuous_var.get())

    def _on_mode_changed(self, event):
        """Handles changes in drawing mode."""
        new_mode = self.mode_combo.get()
        self.workspace_frame.set_draw_mode(new_mode)
        if new_mode == "box":
            self.continuous_check.config(state="disabled")
        else:
            self.continuous_check.config(state="normal")

    def _on_zoom_combo_changed(self, event):
        """Handles zoom level changes from the combobox."""
        val_str = self.zoom_combo.get().replace("%", "")
        try:
            val = float(val_str)
            self.workspace_frame.set_manual_zoom(val / 100.0)
        except ValueError:
            pass

    def update_zoom_in_combo(self, zoom_val):
        """Updates the zoom combobox value."""
        if zoom_val < 10:
            self.zoom_combo.set(f"0{zoom_val}%")
        else:
            self.zoom_combo.set(f"{zoom_val}%")

    def open_image(self):
        """Opens an image file and loads it into the workspace."""
        image_path = filedialog.askopenfilename(
            parent=self,
            title="Select an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")],
        )
        if image_path:
            self.workspace_frame.load_image(image_path)
            self.label_handler.current_image_path = image_path

    def open_label_file(self):
        """Opens a YOLO label file and loads existing bounding boxes."""
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

    def generate_label_file(self):
        """Generates the YOLO label file with all bounding boxes drawn."""
        if not self.workspace_frame.image:
            messagebox.showwarning("Warning", "No image loaded.")
            return

        if not self.workspace_frame.polygons:
            messagebox.showwarning("Warning", "No polygons drawn to generate labels.")
            return

        self.label_handler.save_labels(
            self.workspace_frame.polygons,
            self.workspace_frame.image.width,
            self.workspace_frame.image.height,
        )

        # Show tooltip near the 'Generate Label' button
        tip = Tooltip(self.btn_generate, "Label generated successfully")
        tip.show()

    def set_zoom_percentage(self):
        """Prompts the user to input a new zoom percentage and updates the workspace."""

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
