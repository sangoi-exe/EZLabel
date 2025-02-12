import tkinter as tk


class ClassSelectionDialog:
    """
    Nova dialog para seleção após fechamento de polígono.
    Permite configurar botões em linhas, tamanho e fonte.
    Se não for fornecido o rows_config, ele simplesmente joga todas as classes em uma única linha.
    """

    def __init__(
        self,
        parent,
        class_definitions,
        rows_config=None,
        button_width=15,
        button_font_size=10,
        highlight_ids=None,
    ):
        """
        :param parent: Janela/toplevel pai.
        :param class_definitions: Dicionário {class_id: nome_da_classe}.
        :param rows_config: Lista de listas, determinando quais IDs vão em cada linha. Ex: [["0","1"], ["2"], ["3","4"]].
        :param button_width: Largura do botão (int).
        :param button_font_size: Tamanho da fonte usada no texto do botão (int).
        :param highlight_ids: Conjunto (set) de IDs de classe a serem destacados em cor rosa claro.
        """
        self.parent = parent
        self.class_definitions = class_definitions
        self.selected_class_id = None

        if rows_config is None or not rows_config:
            rows_config = [list(self.class_definitions.keys())]

        self.rows_config = rows_config
        self.button_width = button_width
        self.button_font_size = button_font_size
        self.highlight_ids = highlight_ids or set()

        self._create_dialog()

    def _create_dialog(self):
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Seleção de Classe")
        self.dialog.attributes("-topmost", True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        NUM_COLS = 3  # define sempre 3 colunas
        for row_index, row_classes in enumerate(self.rows_config):
            for col_index in range(NUM_COLS):
                if col_index < len(row_classes):
                    class_id = row_classes[col_index]
                    display_text = self.class_definitions.get(class_id, str(class_id))
                    btn = tk.Button(
                        self.dialog,
                        text=display_text,
                        width=self.button_width,
                        font=("Arial", self.button_font_size),
                        command=lambda cid=class_id: self._on_class_selected(cid),
                    )
                    # Se este ID de classe estiver nos 'highlight_ids', pinta o fundo em rosa claro.
                    if class_id in self.highlight_ids:
                        btn.config(bg="#ffb6c1")
                    btn.grid(
                        row=row_index, column=col_index, sticky="nsew", padx=5, pady=5
                    )
                else:
                    # insere uma célula vazia (para manter layout de 3 colunas mesmo com menos botões)
                    lbl = tk.Label(self.dialog, text="", width=self.button_width)
                    lbl.grid(
                        row=row_index, column=col_index, sticky="nsew", padx=5, pady=5
                    )

            self.dialog.grid_rowconfigure(row_index, weight=1)

        # configura o peso de cada coluna, para que todos os botões se estiquem igualmente
        for col in range(NUM_COLS):
            self.dialog.grid_columnconfigure(col, weight=1, uniform="col")

        # centraliza a dialog em relação à janela principal
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()

        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        x = parent_x + (parent_w // 2) - (width // 2)
        y = parent_y + (parent_h // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

    def _on_class_selected(self, class_id):
        self.selected_class_id = class_id
        self.dialog.destroy()

    def show(self):
        self.parent.wait_window(self.dialog)
        return self.selected_class_id
