# ------------------------------------------------------------------------------
# File: modules\class_selection_dialog.py
# Description: Custom dialog to select class ID using buttons.
# ------------------------------------------------------------------------------

import tkinter as tk


class ClassSelectionDialog:
    def __init__(self, parent, class_definitions):
        self.parent = parent
        self.class_definitions = class_definitions
        self.selected_class_id = None
        self._create_dialog()

    def _create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Select Class")
        self.dialog.attributes("-topmost", True)
        self.dialog.transient(self.parent)  # Modal
        self.dialog.grab_set()

        num_classes = len(self.class_definitions)
        num_columns = 4  # Adjust columns as needed
        row = 0
        column = 0

        for class_id, class_name in self.class_definitions.items():
            btn = tk.Button(
                self.dialog,
                text=class_name,
                width=15,
                command=lambda cid=class_id: self._on_class_selected(cid),
            )
            btn.grid(row=row, column=column, padx=5, pady=5)

            column += 1
            if column >= num_columns:
                column = 0
                row += 1

    def _on_class_selected(self, class_id):
        self.selected_class_id = class_id
        self.dialog.destroy()

    def show(self):
        self.parent.wait_window(self.dialog)
        return self.selected_class_id
