# ------------------------------------------------------------------------------
# File: modules/color_palette.py
# Description: Displays a simple color palette dialog for picking a line color.
# ------------------------------------------------------------------------------

import tkinter as tk

class ColorPaletteDialog:
    """
    Presents a few color options for the user to pick. 
    This can be extended to a full color chooser if desired.
    """
    def __init__(self, parent):
        self.parent = parent
        self.result_color = None
        self._create_dialog()

    def _create_dialog(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Choose Line Color")
        dialog.attributes("-topmost", True)
        dialog.geometry("+200+200")

        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#000000", "#FFFFFF"]

        frame = tk.Frame(dialog)
        frame.pack(padx=10, pady=10)

        def select_color(c):
            self.result_color = c
            dialog.destroy()

        for c in colors:
            btn = tk.Button(frame, bg=c, width=4, command=lambda col=c: select_color(col))
            btn.pack(side=tk.LEFT, padx=5)
