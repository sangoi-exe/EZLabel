import os
from tkinter import Tk
from ultralytics import YOLO
from tkinter import filedialog
from PIL import Image, ImageDraw

# Variável global para controlar o modo de operação: True para contorno, False para cortar
DRAW_NOT_CROP = True  # Defina como False para cortar as bounding boxes

# Define o número máximo de bounding boxes a serem processadas por imagem
MAX_BOXES_TO_PROCESS = 4  # Ajuste este valor conforme necessário


def process_images(input_folder):
    output_folder = os.path.join(input_folder, "output")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Carregue o modelo YOLO
    model = YOLO(r"C:\Users\lucas.sangoi\Documents\EZLabel\best.pt")

    # Verifique se o modelo possui os nomes das classes
    if not hasattr(model, "names"):
        print("O modelo YOLO não possui o atributo 'names' para mapeamento de classes.")
        return

    # Obtenha os nomes das classes
    class_names = (
        model.names
    )  # Assumindo que model.names é um dicionário {id: nome_classe}

    # Definir o valor do offset aqui
    offset = 0  # Este valor pode ser ajustado conforme necessário

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            file_path = os.path.join(input_folder, file_name)

            try:
                results = model(file_path, conf=0.80)

                img = Image.open(file_path).convert(
                    "RGB"
                )  # Garante que a imagem está em RGB
                width, height = img.size

                # Verifica se há resultados
                if not results:
                    print(f"Nenhuma caixa detectada na imagem: {file_name}")
                    continue

                # Considera todas as caixas detectadas
                num_boxes_detected = (
                    len(results[0].boxes) if results and len(results) > 0 else 0
                )
                print(f"Detected {num_boxes_detected} boxes in image: {file_name}")

                processed_box_count = (
                    0  # Inicializa o contador de caixas processadas para esta imagem
                )

                for result in results:
                    boxes = result.boxes.xyxy  # Todas as caixas delimitadoras
                    classes = result.boxes.cls  # IDs das classes

                    for box, cls_id in zip(boxes, classes):
                        if processed_box_count >= MAX_BOXES_TO_PROCESS:
                            break  # Limita o número de caixas processadas

                        try:
                            x1, y1, x2, y2 = map(
                                int, box.tolist()
                            )  # Converte para lista e depois para inteiros

                            # Aplicar offset diretamente nas coordenadas da bounding box
                            new_x1 = max(0, x1 - offset)
                            new_y1 = max(0, y1 - offset)
                            new_x2 = min(width, x2 + offset)
                            new_y2 = min(height, y2 + offset)

                            # Obter o nome da classe
                            cls_id_int = int(
                                cls_id
                            )  # Converte para inteiro, se necessário
                            class_name = class_names.get(
                                cls_id_int, f"class_{cls_id_int}"
                            )  # Obtém o nome da classe ou usa um fallback

                            if DRAW_NOT_CROP:
                                # Modo de desenhar contorno
                                draw = ImageDraw.Draw(img)
                                draw.rectangle(
                                    [(new_x1, new_y1), (new_x2, new_y2)],
                                    outline="red",
                                    width=3,
                                )  # Desenha um retângulo vermelho

                                # Atualiza o nome do arquivo para incluir o nome da classe
                                output_file_name = f"{os.path.splitext(file_name)[0]}_{class_name}_outlined{os.path.splitext(file_name)[1]}"
                                img.save(os.path.join(output_folder, output_file_name))

                            else:
                                # Modo de cortar a bounding box (modo original)
                                crop_img = img.crop((new_x1, new_y1, new_x2, new_y2))
                                output_file_name = f"{os.path.splitext(file_name)[0]}_{class_name}_face{os.path.splitext(file_name)[1]}"
                                crop_img.save(
                                    os.path.join(output_folder, output_file_name)
                                )

                            processed_box_count += (
                                1  # Incrementa o contador de caixas processadas
                            )

                        except Exception as e:
                            print(
                                f"Erro ao processar a caixa na imagem {file_name} (box {processed_box_count+1}): {e}"
                            )
                            continue  # Pula para a próxima caixa

            except FileNotFoundError as e:
                print(f"Erro ao abrir a imagem {file_name}: {e}")
            except Exception as e:
                print(f"Erro ao processar a imagem {file_name}: {e}")


def select_folder():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    folder_selected = filedialog.askdirectory()
    root.destroy()
    return folder_selected


if __name__ == "__main__":
    input_folder = select_folder()
    if input_folder:
        process_images(input_folder)
    else:
        print("No folder selected.")
