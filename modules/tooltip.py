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
        y = self.widget.winfo_rooty() + int(self.widget.winfo_height())
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
