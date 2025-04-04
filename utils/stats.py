import os
from collections import Counter

def gerar_estatisticas(txt_pasta, page):
    total_arquivos = 0
    total_diretorios = 0
    total_tamanho = 0
    extensoes = Counter()

    for root, dirs, files in os.walk(txt_pasta.value):
        total_diretorios += len(dirs)
        for file in files:
            total_arquivos += 1
            caminho = os.path.join(root, file)
            if os.path.exists(caminho):
                total_tamanho += os.path.getsize(caminho)
                ext = os.path.splitext(file)[1]
                extensoes[ext] += 1

    info = f"""📊 Estatísticas:
- Arquivos: {total_arquivos}
- Diretórios: {total_diretorios}
- Tamanho total: {round(total_tamanho / (1024*1024), 2)} MB
- Extensões comuns: {dict(extensoes.most_common(5))}
"""
    page.dialog = ft.AlertDialog(title=ft.Text("📊 Estatísticas"), content=ft.Text(info))
    page.dialog.open = True
    page.update()
