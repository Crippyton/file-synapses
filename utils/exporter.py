import os
import json
import flet as ft
from flet import Colors, Icons
from fpdf import FPDF
from datetime import datetime
from utils.explorer import listar_estrutura_pasta

def gerar_nome(caminho, ext):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_pasta = os.path.basename(caminho) or 'estrutura'
    diretorio_pai = os.path.dirname(caminho)
    return os.path.join(diretorio_pai, f"{nome_pasta}_estrutura_{timestamp}.{ext}")

def exportar_para_txt(txt_pasta, page):
    try:
        caminho = gerar_nome(txt_pasta.value, "txt")
        
        # Gera representação ASCII da árvore
        with open(caminho, "w", encoding="utf-8") as f:
            # Escreve cabeçalho
            f.write(f"Estrutura da pasta: {txt_pasta.value}\n")
            f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Função para gerar a árvore com linhas conectoras
            def gerar_arvore_txt(diretorio, prefixo=""):
                itens = sorted(os.listdir(diretorio))
                # Separar pastas e arquivos para organizar pastas primeiro
                pastas = [i for i in itens if os.path.isdir(os.path.join(diretorio, i))]
                arquivos = [i for i in itens if os.path.isfile(os.path.join(diretorio, i))]
                
                # Processar pastas
                for i, pasta in enumerate(pastas):
                    caminho_completo = os.path.join(diretorio, pasta)
                    
                    # Determina se é o último item
                    is_ultimo = i == len(pastas) - 1 and len(arquivos) == 0
                    
                    # Símbolos para conexão
                    if is_ultimo:
                        f.write(f"{prefixo}└── 📁 {pasta}/\n")
                        novo_prefixo = prefixo + "    "
                    else:
                        f.write(f"{prefixo}├── 📁 {pasta}/\n")
                        novo_prefixo = prefixo + "│   "
                    
                    try:
                        gerar_arvore_txt(caminho_completo, novo_prefixo)
                    except PermissionError:
                        f.write(f"{novo_prefixo}└── 🚫 Sem permissão de acesso\n")
                    except Exception as e:
                        f.write(f"{novo_prefixo}└── ⚠️ Erro: {str(e)}\n")
                
                # Processar arquivos
                for i, arquivo in enumerate(arquivos):
                    # Determina se é o último item
                    is_ultimo = i == len(arquivos) - 1
                    
                    # Define o emoji baseado na extensão
                    ext = os.path.splitext(arquivo)[1].lower()
                    emoji = "📄"
                    if ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
                        emoji = "📝"
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                        emoji = "🖼️"
                    elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                        emoji = "📑"
                    elif ext in ['.mp3', '.wav', '.flac', '.aac']:
                        emoji = "🎵"
                    elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                        emoji = "🎬"
                    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                        emoji = "📦"
                    
                    # Adiciona o item à árvore
                    if is_ultimo:
                        f.write(f"{prefixo}└── {emoji} {arquivo}\n")
                    else:
                        f.write(f"{prefixo}├── {emoji} {arquivo}\n")
            
            # Gera a estrutura de árvore
            diretorio_raiz = txt_pasta.value
            nome_raiz = os.path.basename(diretorio_raiz) or diretorio_raiz
            f.write(f"📁 {nome_raiz}\n")
            try:
                gerar_arvore_txt(diretorio_raiz)
            except Exception as e:
                f.write(f"⚠️ Erro ao ler a estrutura: {str(e)}\n")
        
        # Notifica o usuário
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Arquivo exportado para: {caminho} ✅"), 
            action=ft.TextButton("Ver", on_click=lambda e: os.startfile(caminho)),
            open=True
        )
        page.update()
    except Exception as e:
        # Exibe mensagem de erro
        page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao exportar TXT: {str(e)} ❌"), open=True)
        page.update()

def exportar_para_pdf(txt_pasta, page):
    try:
        caminho = gerar_nome(txt_pasta.value, "pdf")
        
        # Cria o PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Configura o título e cabeçalho
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Estrutura da pasta: {os.path.basename(txt_pasta.value)}", 0, 1)
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1)
        pdf.line(10, 30, 200, 30)
        pdf.ln(10)
        
        # Configura a fonte para o conteúdo
        pdf.set_font("Courier", "", 10)
        
        # Altura da linha
        linha_altura = 6
        
        # Função recursiva para gerar a árvore no PDF
        def gerar_arvore_pdf(diretorio, nivel=0):
            try:
                itens = sorted(os.listdir(diretorio))
                # Separar pastas e arquivos
                pastas = [i for i in itens if os.path.isdir(os.path.join(diretorio, i))]
                arquivos = [i for i in itens if os.path.isfile(os.path.join(diretorio, i))]
                
                # Processar pastas
                for i, pasta in enumerate(pastas):
                    caminho_completo = os.path.join(diretorio, pasta)
                    
                    # Verifica se é o último item
                    is_ultimo = i == len(pastas) - 1 and len(arquivos) == 0
                    
                    # Gera os conectores da árvore
                    if is_ultimo:
                        conector = "└── "
                        prefixo_filho = "    "
                    else:
                        conector = "├── "
                        prefixo_filho = "│   "
                    
                    # Desenha a linha com o nome da pasta
                    indentacao = "    " * nivel
                    pdf.cell(0, linha_altura, f"{indentacao}{conector}📁 {pasta}/", 0, 1)
                    
                    # Processa recursivamente o conteúdo da pasta
                    try:
                        if os.access(caminho_completo, os.R_OK):
                            gerar_arvore_pdf(caminho_completo, nivel + 1)
                        else:
                            pdf.cell(0, linha_altura, f"{indentacao}{prefixo_filho}└── 🚫 Sem permissão de acesso", 0, 1)
                    except Exception as e:
                        pdf.cell(0, linha_altura, f"{indentacao}{prefixo_filho}└── ⚠️ Erro: {str(e)[:50]}", 0, 1)
                
                # Processar arquivos
                for i, arquivo in enumerate(arquivos):
                    # Verifica se é o último item
                    is_ultimo = i == len(arquivos) - 1
                    
                    # Gera o conector
                    conector = "└── " if is_ultimo else "├── "
                    
                    # Define o emoji baseado na extensão
                    ext = os.path.splitext(arquivo)[1].lower()
                    emoji = "📄"
                    if ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
                        emoji = "📝"
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                        emoji = "🖼️"
                    elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                        emoji = "📑"
                    elif ext in ['.mp3', '.wav', '.flac', '.aac']:
                        emoji = "🎵"
                    elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                        emoji = "🎬"
                    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                        emoji = "📦"
                    elif ext in ['.md', '.markdown']:
                        emoji = "📝"
                    
                    # Desenha a linha para o arquivo
                    indentacao = "    " * nivel
                    pdf.cell(0, linha_altura, f"{indentacao}{conector}{emoji} {arquivo}", 0, 1)
            except PermissionError:
                pdf.cell(0, linha_altura, f"{'    ' * nivel}└── 🚫 Sem permissão de acesso", 0, 1)
            except Exception as e:
                pdf.cell(0, linha_altura, f"{'    ' * nivel}└── ⚠️ Erro: {str(e)[:50]}", 0, 1)
        
        # Começa a gerar a árvore
        pdf.cell(0, linha_altura, f"📁 {os.path.basename(txt_pasta.value) or txt_pasta.value}", 0, 1)
        gerar_arvore_pdf(txt_pasta.value)
        
        # Adiciona rodapé
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "Gerado pelo File Synapses", 0, 0, "C")
        
        # Salva o PDF
        pdf.output(caminho)
        
        # Notifica o usuário
        page.snack_bar = ft.SnackBar(
            ft.Text(f"PDF exportado para: {caminho} ✅"), 
            action=ft.TextButton("Ver", on_click=lambda e: os.startfile(caminho)),
            open=True
        )
        page.update()
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao exportar PDF: {str(e)} ❌"), open=True)
        page.update()

def exportar_para_md(txt_pasta, page):
    try:
        caminho = gerar_nome(txt_pasta.value, "md")
        
        with open(caminho, "w", encoding="utf-8") as f:
            # Escreve o cabeçalho do Markdown
            nome_pasta = os.path.basename(txt_pasta.value) or txt_pasta.value
            f.write(f"# Estrutura da pasta: {nome_pasta}\n\n")
            f.write(f"*Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n\n")
            f.write("---\n\n")
            
            # Função recursiva para gerar a árvore em Markdown
            def gerar_arvore_md(diretorio, nivel=0):
                try:
                    itens = sorted(os.listdir(diretorio))
                    # Separar pastas e arquivos
                    pastas = [i for i in itens if os.path.isdir(os.path.join(diretorio, i))]
                    arquivos = [i for i in itens if os.path.isfile(os.path.join(diretorio, i))]
                    
                    # Processar pastas
                    for pasta in pastas:
                        caminho_completo = os.path.join(diretorio, pasta)
                        
                        # Escreve o item com indentação baseada no nível
                        # Usa ícones diferentes para pastas
                        f.write(f"{'  ' * nivel}- 📁 **{pasta}/**\n")
                        
                        # Processa recursivamente
                        gerar_arvore_md(caminho_completo, nivel + 1)
                    
                    # Processar arquivos
                    for arquivo in arquivos:
                        # Define o emoji baseado na extensão
                        ext = os.path.splitext(arquivo)[1].lower()
                        emoji = "📄"
                        if ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
                            emoji = "📝"
                        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                            emoji = "🖼️"
                        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                            emoji = "📑"
                        elif ext in ['.mp3', '.wav', '.flac', '.aac']:
                            emoji = "🎵"
                        elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                            emoji = "🎬"
                        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                            emoji = "📦"
                        elif ext in ['.md', '.markdown']:
                            emoji = "📝"
                        
                        # Escreve o arquivo com indentação
                        f.write(f"{'  ' * nivel}- {emoji} {arquivo}\n")
                except PermissionError:
                    f.write(f"{'  ' * nivel}- 🚫 **Sem permissão de acesso**\n")
                except Exception as e:
                    f.write(f"{'  ' * nivel}- ⚠️ Erro: {str(e)}\n")
            
            # Começa a gerar a árvore a partir da raiz
            gerar_arvore_md(txt_pasta.value)
            
            # Adiciona footer
            f.write("\n\n---\n")
            f.write("\n*Gerado pelo File Synapses*")
        
        # Notifica o usuário
        page.snack_bar = ft.SnackBar(
            ft.Text(f"Markdown exportado para: {caminho} ✅"), 
            action=ft.TextButton("Ver", on_click=lambda e: os.startfile(caminho)),
            open=True
        )
        page.update()
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao exportar Markdown: {str(e)} ❌"), open=True)
        page.update()

def exportar_para_json(txt_pasta, page):
    try:
        caminho = gerar_nome(txt_pasta.value, "json")
        
        def build_json(path):
            try:
                item_nome = os.path.basename(path) or path
                item_info = {
                    "nome": item_nome,
                    "caminho": path,
                    "ultima_modificacao": datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S"),
                }
                
                if os.path.isdir(path):
                    # Informações da pasta
                    item_info.update({
                        "tipo": "diretorio",
                        "permissao_leitura": os.access(path, os.R_OK),
                        "permissao_escrita": os.access(path, os.W_OK),
                        "filhos": []
                    })
                    
                    # Processa os filhos
                    try:
                        itens = sorted(os.listdir(path))
                        # Pastas primeiro, depois arquivos
                        pastas = [os.path.join(path, i) for i in itens if os.path.isdir(os.path.join(path, i))]
                        arquivos = [os.path.join(path, i) for i in itens if os.path.isfile(os.path.join(path, i))]
                        
                        # Adiciona pastas e arquivos à lista de filhos
                        for item_path in pastas + arquivos:
                            filho = build_json(item_path)
                            if filho:
                                item_info["filhos"].append(filho)
                    except PermissionError:
                        item_info["erro"] = "Sem permissão de acesso"
                    except Exception as e:
                        item_info["erro"] = str(e)
                else:
                    # Informações do arquivo
                    tamanho = os.path.getsize(path)
                    ext = os.path.splitext(path)[1].lower()
                    
                    # Determina a categoria do arquivo
                    categoria = "documento"
                    if ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php']:
                        categoria = "código"
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
                        categoria = "imagem"
                    elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.odt', '.ods']:
                        categoria = "documento"
                    elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
                        categoria = "áudio"
                    elif ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                        categoria = "vídeo"
                    elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                        categoria = "compactado"
                    elif ext in ['.md', '.markdown', '.txt']:
                        categoria = "texto"
                    
                    item_info.update({
                        "tipo": "arquivo",
                        "extensao": ext,
                        "categoria": categoria,
                        "tamanho_bytes": tamanho,
                        "tamanho_formatado": formatar_tamanho(tamanho),
                        "permissao_leitura": os.access(path, os.R_OK),
                        "permissao_escrita": os.access(path, os.W_OK),
                    })
                
                return item_info
            except Exception as e:
                # Informação básica em caso de erro
                return {
                    "nome": os.path.basename(path) or path,
                    "caminho": path,
                    "tipo": "erro",
                    "mensagem": str(e)
                }
        
        # Função auxiliar para formatar o tamanho
        def formatar_tamanho(tamanho_bytes):
            # Converte bytes para KB, MB, GB conforme apropriado
            if tamanho_bytes < 1024:
                return f"{tamanho_bytes} bytes"
            elif tamanho_bytes < 1024 * 1024:
                return f"{tamanho_bytes / 1024:.2f} KB"
            elif tamanho_bytes < 1024 * 1024 * 1024:
                return f"{tamanho_bytes / (1024 * 1024):.2f} MB"
            else:
                return f"{tamanho_bytes / (1024 * 1024 * 1024):.2f} GB"
        
        # Metadados do JSON
        estrutura = {
            "metadados": {
                "nome_aplicativo": "File Synapses",
                "versao": "1.0",
                "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pasta_raiz": txt_pasta.value
            },
            "estrutura": build_json(txt_pasta.value)
        }
        
        # Salva o JSON
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(estrutura, f, indent=2, ensure_ascii=False)
        
        # Notifica o usuário
        page.snack_bar = ft.SnackBar(
            ft.Text(f"JSON exportado para: {caminho} ✅"), 
            action=ft.TextButton("Ver", on_click=lambda e: os.startfile(caminho)),
            open=True
        )
        page.update()
    except Exception as e:
        page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao exportar JSON: {str(e)} ❌"), open=True)
        page.update()
