# ------------------------------------------------------------------------------
# File: modules/balloon_zoom.py
# Description: Manages a small zoomed-in window (balloon) to help move points.
# ------------------------------------------------------------------------------

import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class BalloonZoom:
    """
    Shows a small balloon window with a zoomed-in portion of the image
    while dragging a point.
    """

    def __init__(self, parent_canvas):
        self.parent_canvas = parent_canvas
        self.zoom_window = None
        self.zoom_factor = 2.0  # how much to magnify
        self.zoom_size = 50  # size of balloon region

    def _create_window(self):
        if self.zoom_window is None:
            self.zoom_window = tk.Toplevel(self.parent_canvas)
            self.zoom_window.attributes("-topmost", True)
            self.zoom_window.overrideredirect(True)
            self.zoom_canvas = tk.Canvas(self.zoom_window, width=100, height=100, highlightthickness=1, bg="black")
            self.zoom_canvas.pack()

    def update_zoom_view(self, image, x, y, scale, mouse_x_root=None, mouse_y_root=None, point_radius=3):
        """
        Displays a cropped region of 'image' around (x, y) with zoom_factor.
        The balloon will be positioned near the mouse pointer if mouse coords are provided.
        """
        if not image:
            return
        self._create_window()

        half = self.zoom_size / 2.0
        left = int(x - half)
        top = int(y - half)
        right = int(x + half)
        bottom = int(y + half)
        if left < 0:
            left = 0
        if top < 0:
            top = 0
        if right > image.width:
            right = image.width
        if bottom > image.height:
            bottom = image.height

        region = image.crop((left, top, right, bottom))

        # Draw the dragged point inside the region
        from PIL import ImageDraw

        draw = ImageDraw.Draw(region)
        px = x - left
        py = y - top
        r = point_radius
        draw.ellipse((px - r, py - r, px + r, py + r), fill="yellow", outline="yellow")

        # Resize for zoom
        new_w = int(region.width * self.zoom_factor)
        new_h = int(region.height * self.zoom_factor)
        if new_w < 1:
            new_w = 1
        if new_h < 1:
            new_h = 1
        region = region.resize((new_w, new_h), Image.Resampling.LANCZOS)

        import tkinter as tk
        from PIL import ImageTk

        photo = ImageTk.PhotoImage(region)
        self.zoom_canvas.delete("all")
        self.zoom_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.zoom_canvas.image = photo

        # Position the balloon near the mouse pointer if we have root coords
        offset_x = 20
        offset_y = -100
        if mouse_x_root is not None and mouse_y_root is not None:
            # Just add some offset from the pointer
            pos_x = mouse_x_root + offset_x
            pos_y = mouse_y_root + offset_y
            self.zoom_window.geometry(f"+{pos_x}+{pos_y}")
        else:
            # Fallback to original logic
            root_x = self.parent_canvas.winfo_rootx()
            root_y = self.parent_canvas.winfo_rooty()
            self.zoom_window.geometry(f"+{root_x + int((x*scale)+20)}+{root_y + int((y*scale)-100)}+")

    def hide_zoom_view(self):
        """
        Hides the balloon zoom window.
        """
        if self.zoom_window:
            self.zoom_window.destroy()
            self.zoom_window = None
