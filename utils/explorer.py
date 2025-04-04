import os
import flet as ft

IGNORAR_PASTAS = {".git", "__pycache__"}

def listar_estrutura_pasta(raiz):
    estrutura = []

    def walk(dir_path, nivel):
        try:
            for item in sorted(os.listdir(dir_path)):
                caminho = os.path.join(dir_path, item)
                if os.path.isdir(caminho) and item not in IGNORAR_PASTAS:
                    estrutura.append((nivel, f"📁 {item}"))
                    walk(caminho, nivel + 1)
                elif os.path.isfile(caminho):
                    estrutura.append((nivel, f"📄 {item}"))
        except PermissionError:
            estrutura.append((nivel, "🚫 Sem permissão"))

    walk(raiz, 0)
    return estrutura

def gerar_arvore(txt_pasta, container, termo_busca=""):
    container.controls.clear()
    if not txt_pasta.value:
        return

    def gerar_expansao(caminho, nivel=0):
        try:
            filhos = []
            for item in sorted(os.listdir(caminho)):
                caminho_item = os.path.join(caminho, item)
                if termo_busca.lower() in item.lower():
                    if os.path.isdir(caminho_item):
                        filhos.append(
                            ft.ExpansionTile(title=ft.Text(f"📁 {item}"),
                                             controls=gerar_expansao(caminho_item, nivel + 1)))
                    else:
                        filhos.append(ft.Text(f"📄 {item}"))
            return filhos
        except:
            return [ft.Text("🚫 Sem permissão")]

    container.controls.append(ft.ExpansionTile(title=ft.Text(os.path.basename(txt_pasta.value)),
                                               controls=gerar_expansao(txt_pasta.value)))
