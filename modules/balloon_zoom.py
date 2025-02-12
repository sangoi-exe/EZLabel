import tkinter as tk
from PIL import Image, ImageTk, ImageDraw


class BalloonZoom:
    """
    Exibe uma mini-janela (balloon) com parte da imagem ampliada
    enquanto um ponto de polígono é arrastado.
    """

    def __init__(self, parent_canvas):
        self.parent_canvas = parent_canvas
        self.zoom_window = None
        # Aumentamos o tamanho da região do baloon e a ampliação.
        # Se antes era 50 e zoom_factor=2.0, agora dobramos ambos.
        self.zoom_size = 100  # área crua recortada da imagem
        self.zoom_factor = 2.0  # fator de ampliação aplicado ao recorte
        self.zoom_canvas = None

    def _create_window(self):
        """Cria a janela de zoom (balloon), caso ainda não exista."""
        if self.zoom_window is None:
            self.zoom_window = tk.Toplevel(self.parent_canvas)
            self.zoom_window.attributes("-topmost", True)
            # Deixa o balloon 50% transparente:
            self.zoom_window.attributes("-alpha", 1)
            # Remove a decoração da janela:
            self.zoom_window.overrideredirect(True)
            # Aqui definimos um tamanho inicial maior, pois tudo foi dobrado:
            self.zoom_canvas = tk.Canvas(
                self.zoom_window,
                width=200,
                height=200,
                highlightthickness=1,
                bg="black",
            )
            self.zoom_canvas.pack()

    def update_zoom_view(
        self, image, x, y, scale, mouse_x_root=None, mouse_y_root=None, point_radius=3
    ):
        """
        Atualiza e exibe o recorte ampliado da imagem em torno de (x, y).
        O parâmetro (x, y) está em coordenadas da imagem (não do canvas).
        'mouse_x_root' e 'mouse_y_root' são as coordenadas do mouse em tela,
        usadas para posicionar a janela do balloon.
        """
        if not image:
            return

        # Garante que a janela de zoom exista:
        self._create_window()

        # Tamanho (em pixels da imagem) que queremos recortar ao redor do ponto:
        balloon_size = self.zoom_size
        half = balloon_size / 2.0

        # Coordenadas "ideais" do recorte na imagem, sem clamping:
        balloon_x1 = x - half
        balloon_y1 = y - half
        balloon_x2 = balloon_x1 + balloon_size
        balloon_y2 = balloon_y1 + balloon_size

        # Calcula a região que efetivamente cai dentro da imagem:
        overlap_x1 = max(0, balloon_x1)
        overlap_y1 = max(0, balloon_y1)
        overlap_x2 = min(image.width, balloon_x2)
        overlap_y2 = min(image.height, balloon_y2)

        # Cria uma base toda em preto, do tamanho exato de balloon_size:
        base = Image.new("RGB", (balloon_size, balloon_size), color=(0, 0, 0))

        # Recorta apenas a parte que existe dentro da imagem:
        if overlap_x2 > overlap_x1 and overlap_y2 > overlap_y1:
            region = image.crop((overlap_x1, overlap_y1, overlap_x2, overlap_y2))
        else:
            # Se não há interseção, retorna rapidamente (estamos fora da imagem).
            region = None

        # Calcula onde a região recortada deve ser "colada" dentro de 'base':
        paste_x = overlap_x1 - balloon_x1
        paste_y = overlap_y1 - balloon_y1

        if region:
            base.paste(region, (int(paste_x), int(paste_y)))

        # Desenha o ponto amarelo na base (o ponto está em coords do balloon):
        px = x - balloon_x1
        py = y - balloon_y1
        draw = ImageDraw.Draw(base)
        r = point_radius
        draw.ellipse((px - r, py - r, px + r, py + r), fill="yellow", outline="yellow")

        # Aplica o fator de zoom final:
        final_w = int(balloon_size * self.zoom_factor)
        final_h = int(balloon_size * self.zoom_factor)
        if final_w < 1:
            final_w = 1
        if final_h < 1:
            final_h = 1
        zoomed = base.resize((final_w, final_h), Image.Resampling.NEAREST)

        # Atualiza o canvas com a imagem final ampliada:
        photo = ImageTk.PhotoImage(zoomed)
        self.zoom_canvas.delete("all")
        # Ajusta dinamicamente o tamanho do canvas à imagem resultante
        self.zoom_canvas.config(width=final_w, height=final_h)
        self.zoom_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.zoom_canvas.image = photo

        # Posiciona o balloon perto do cursor:
        offset_x = 20
        offset_y = -100
        if mouse_x_root is not None and mouse_y_root is not None:
            pos_x = mouse_x_root + offset_x
            pos_y = mouse_y_root + offset_y
            self.zoom_window.geometry(f"+{pos_x}+{pos_y}")
        else:
            # Fallback: posiciona relativo ao canvas e ao ponto.
            root_x = self.parent_canvas.winfo_rootx()
            root_y = self.parent_canvas.winfo_rooty()
            self.zoom_window.geometry(
                f"+{root_x + int((x*scale)+20)}" f"+{root_y + int((y*scale)-100)}"
            )

    def hide_zoom_view(self):
        """Esconde a janela (balloon) de zoom."""
        if self.zoom_window:
            self.zoom_window.destroy()
            self.zoom_window = None
