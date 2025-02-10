import os
import tkinter as tk
from tkinter import filedialog


def remover_prefixo_result(pasta):
    """
    Itera sobre os arquivos em uma pasta e remove o prefixo 'result_' dos nomes dos arquivos.

    Args:
        pasta (str): O caminho para a pasta a ser processada.
    """
    for nome_arquivo in os.listdir(pasta):
        caminho_completo = os.path.join(pasta, nome_arquivo)
        if os.path.isfile(
            caminho_completo
        ):  # Verifica se é um arquivo (e não uma pasta)
            if nome_arquivo.startswith("results_"):
                novo_nome_arquivo = nome_arquivo[len("results_") :]  # Remove o prefixo
                novo_caminho_completo = os.path.join(pasta, novo_nome_arquivo)
                try:
                    os.rename(caminho_completo, novo_caminho_completo)
                    print(
                        f"Arquivo renomeado: '{nome_arquivo}' para '{novo_nome_arquivo}'"
                    )
                except OSError as e:
                    print(f"Erro ao renomear '{nome_arquivo}': {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal do Tkinter

    pasta_alvo = filedialog.askdirectory(title="Selecione a pasta para processar")

    if pasta_alvo:  # Verifica se o usuário selecionou uma pasta
        if os.path.isdir(pasta_alvo):
            remover_prefixo_result(pasta_alvo)
            print("Processo concluído.")
        else:
            print("Caminho da pasta inválido.")
    else:
        print("Nenhuma pasta selecionada.")
