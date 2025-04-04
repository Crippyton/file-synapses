import os
import json
from fpdf import FPDF
from datetime import datetime
from utils.explorer import listar_estrutura_pasta

def gerar_nome(caminho, ext):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(caminho, f"estrutura_{timestamp}.{ext}")

def exportar_para_txt(txt_pasta, page):
    caminho = gerar_nome(txt_pasta.value, "txt")
    with open(caminho, "w", encoding="utf-8") as f:
        for nivel, linha in listar_estrutura_pasta(txt_pasta.value):
            f.write(f"{' ' * (nivel * 4)}{linha}\n")
    page.snack_bar = ft.SnackBar(ft.Text("Exportado TXT ✅"), open=True)
    page.update()

def exportar_para_pdf(txt_pasta, page):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for nivel, linha in listar_estrutura_pasta(txt_pasta.value):
        pdf.cell(0, 10, f"{' ' * (nivel * 4)}{linha}", ln=True)
    pdf.output(gerar_nome(txt_pasta.value, "pdf"))
    page.snack_bar = ft.SnackBar(ft.Text("Exportado PDF ✅"), open=True)
    page.update()

def exportar_para_md(txt_pasta, page):
    caminho = gerar_nome(txt_pasta.value, "md")
    with open(caminho, "w", encoding="utf-8") as f:
        for nivel, linha in listar_estrutura_pasta(txt_pasta.value):
            prefixo = "  " * nivel + "- "
            f.write(f"{prefixo}{linha}\n")
    page.snack_bar = ft.SnackBar(ft.Text("Exportado Markdown ✅"), open=True)
    page.update()

def exportar_para_json(txt_pasta, page):
    def build_json(path):
        try:
            children = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    children.append(build_json(full_path))
                else:
                    children.append({"nome": item, "tipo": "arquivo"})
            return {"nome": os.path.basename(path), "tipo": "diretorio", "filhos": children}
        except:
            return {"nome": os.path.basename(path), "tipo": "erro"}

    estrutura = build_json(txt_pasta.value)
    with open(gerar_nome(txt_pasta.value, "json"), "w", encoding="utf-8") as f:
        json.dump(estrutura, f, indent=2, ensure_ascii=False)
    page.snack_bar = ft.SnackBar(ft.Text("Exportado JSON ✅"), open=True)
    page.update()
