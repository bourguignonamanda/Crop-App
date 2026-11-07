"""Recorta uma ou várias imagens em três faixas verticais.
Requer Pillow: pip install pillow
"""
from pathlib import Path
from tkinter import Tk, Button, Label, filedialog, messagebox
from PIL import Image


def cortar_arquivo(caminho):
    origem = Path(caminho)
    pasta_saida = origem.parent / f"{origem.stem} - Cut photo"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    with Image.open(origem) as imagem:
        # JPEG não suporta transparência; compõe PNGs transparentes sobre branco.
        if imagem.mode in ("RGBA", "LA") or "transparency" in imagem.info:
            rgba = imagem.convert("RGBA")
            fundo = Image.new("RGB", rgba.size, "white")
            fundo.paste(rgba, mask=rgba.getchannel("A"))
            imagem = fundo
        else:
            imagem = imagem.convert("RGB")

        largura, altura = imagem.size
        if largura < 3:
            raise ValueError("A imagem precisa ter pelo menos 3 pixels de largura")
        for i in range(3):
            esquerda = (i * largura) // 3
            direita = ((i + 1) * largura) // 3
            pedaco = imagem.crop((esquerda, 0, direita, altura))
            pedaco.save(pasta_saida / f"part_{i + 1}.jpg", quality=95)
    return pasta_saida


def cortar_imagens():
    caminhos = filedialog.askopenfilenames(
        title="Selecione uma ou mais imagens",
        filetypes=[("Arquivos de imagem", "*.jpg *.jpeg *.png"), ("Todos os arquivos", "*.*")],
    )
    if not caminhos:
        return

    sucessos = []
    erros = []
    for caminho in caminhos:
        try:
            sucessos.append(cortar_arquivo(caminho))
        except Exception as exc:
            erros.append(f"{Path(caminho).name}: {exc}")

    resultado = f"{len(sucessos)} de {len(caminhos)} imagem(ns) processada(s)."
    if erros:
        resultado += "\n\nFalhas:\n" + "\n".join(erros[:10])
        if len(erros) > 10:
            resultado += f"\n... e mais {len(erros) - 10} falha(s)."
        messagebox.showwarning("Processamento concluído com falhas", resultado)
    else:
        messagebox.showinfo("Processamento concluído", resultado)


def criar_interface():
    janela = Tk()
    janela.title("Cut Photo in 3 Equal Parts")
    janela.geometry("450x170")
    Label(janela, text="Dividir imagens em 3 partes verticais").pack(pady=(20, 8))
    Button(janela, text="Selecionar uma ou várias imagens", command=cortar_imagens).pack(pady=8)
    janela.mainloop()


if __name__ == "__main__":
    criar_interface()
