import os
import flet as ft
from typing import Dict, Any, Union, List

# Reimplementação das funções necessárias

def listar_estrutura_pasta(caminho: str) -> Dict[str, str]:
    """
    Lista a estrutura de uma pasta e retorna um dicionário onde
    as chaves são os nomes dos arquivos/pastas e os valores são os tipos.
    """
    resultado = {}
    try:
        with os.scandir(caminho) as entradas:
            for entrada in entradas:
                if entrada.is_dir():
                    resultado[entrada.name] = "pasta"
                else:
                    resultado[entrada.name] = "arquivo"
    except Exception as e:
        print(f"Erro ao listar pasta {caminho}: {e}")
    return resultado

def gerar_arvore(estrutura: Dict[str, str], caminho: str, prefixo: str = "") -> str:
    """Gera uma representação em texto da estrutura de pastas"""
    texto = []
    items = sorted(estrutura.items(), key=lambda x: (x[1] != "pasta", x[0].lower()))
    
    for i, (nome, tipo) in enumerate(items):
        is_ultimo = i == len(items) - 1
        conector = "└── " if is_ultimo else "├── "
        linha = prefixo + conector + nome
        texto.append(linha)
        
        if tipo == "pasta":
            sub_prefixo = prefixo + ("    " if is_ultimo else "│   ")
            subpath = os.path.join(caminho, nome)
            try:
                subestrutura = listar_estrutura_pasta(subpath)
                texto.append(gerar_arvore(subestrutura, subpath, sub_prefixo))
            except Exception as e:
                texto.append(f"{sub_prefixo}└── [Erro: {e}]")
    
    return "\n".join(texto)

# Funções de exportação
def exportar_para_txt(txt_pasta, page):
    caminho = txt_pasta.value
    if not caminho or caminho == "Nenhuma pasta selecionada":
        page.dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text("Selecione uma pasta primeiro"))
        page.dialog.open = True
        page.update()
        return
    
    try:
        estrutura = listar_estrutura_pasta(caminho)
        texto = gerar_arvore(estrutura, caminho)
        
        output_file = os.path.join(os.path.dirname(caminho), f"{os.path.basename(caminho)}_estrutura.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(texto)
        
        page.dialog = ft.AlertDialog(
            title=ft.Text("Sucesso"), 
            content=ft.Text(f"Arquivo exportado para: {output_file}")
        )
        page.dialog.open = True
        page.update()
    except Exception as e:
        page.dialog = ft.AlertDialog(title=ft.Text("Erro"), content=ft.Text(f"Erro ao exportar: {str(e)}"))
        page.dialog.open = True
        page.update()

def exportar_para_pdf(txt_pasta, page):
    page.dialog = ft.AlertDialog(title=ft.Text("Info"), content=ft.Text("Função de exportação para PDF não implementada"))
    page.dialog.open = True
    page.update()

def exportar_para_md(txt_pasta, page):
    page.dialog = ft.AlertDialog(title=ft.Text("Info"), content=ft.Text("Função de exportação para Markdown não implementada"))
    page.dialog.open = True
    page.update()

def exportar_para_json(txt_pasta, page):
    page.dialog = ft.AlertDialog(title=ft.Text("Info"), content=ft.Text("Função de exportação para JSON não implementada"))
    page.dialog.open = True
    page.update()

def gerar_estatisticas(txt_pasta, page):
    page.dialog = ft.AlertDialog(title=ft.Text("Info"), content=ft.Text("Função de estatísticas não implementada"))
    page.dialog.open = True
    page.update()

def zipar_pasta(txt_pasta, page):
    page.dialog = ft.AlertDialog(title=ft.Text("Info"), content=ft.Text("Função de compactação não implementada"))
    page.dialog.open = True
    page.update()

# Funções de configuração
def carregar_config(config_path: str) -> Dict[str, Any]:
    """Carrega a configuração do arquivo JSON"""
    import json
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
    return {}

def salvar_config(config_path: str, config: Dict[str, Any]) -> None:
    """Salva a configuração em um arquivo JSON"""
    import json
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Erro ao salvar configuração: {e}")

CONFIG_PATH = "assets/config.json"

def main(page: ft.Page):
    config = carregar_config(CONFIG_PATH)
    page.title = "Visualizador de Estrutura de Pastas"
    
    page.window_width = 800
    page.window_height = 750
    
    page.theme_mode = ft.ThemeMode.DARK if config.get("tema_escuro", True) else ft.ThemeMode.LIGHT
    page.scroll = "AUTO"
    
    txt_pasta = ft.Text("Nenhuma pasta selecionada", size=16, color=ft.colors.GREY)
    estrutura_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, spacing=10)
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    def criar_visualizacao_arvore(pasta_path, termo_busca=None):
        estrutura_container.controls.clear()
        
        if not pasta_path or pasta_path == "Nenhuma pasta selecionada":
            estrutura_container.controls.append(ft.Text("Selecione uma pasta para visualizar sua estrutura"))
            page.update()
            return
        
        try:
            estrutura = listar_estrutura_pasta(pasta_path)
            
            # Criar árvore usando ExpansionTiles
            root_name = os.path.basename(pasta_path) or pasta_path
            
            def criar_arvore_recursiva(items, parent_path, nivel=0, prefixo=""):
                controles = []
                
                # Verificar se items é um dicionário
                if not isinstance(items, dict):
                    controles.append(ft.Text(f"Erro: Estrutura de pasta inválida", color=ft.colors.RED_400))
                    return controles
                    
                # Ordena - primeiro pastas, depois arquivos, ambos em ordem alfabética
                itens_ordenados = sorted(items.items(), key=lambda x: (x[1] != "pasta", x[0].lower()))
                
                for i, (nome, tipo) in enumerate(itens_ordenados):
                    # Filtra por termo de busca se houver
                    if termo_busca and termo_busca.lower() not in nome.lower():
                        continue
                    
                    # Determinar ícones e cores baseados no tipo do arquivo
                    icone = ft.icons.FOLDER if tipo == "pasta" else ft.icons.DESCRIPTION
                    cor_icone = ft.colors.BLUE_400 if tipo == "pasta" else ft.colors.GREY_400
                    
                    if tipo != "pasta":
                        ext = os.path.splitext(nome)[1].lower()
                        if ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
                            icone = ft.icons.CODE
                            cor_icone = ft.colors.GREEN_400
                        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                            icone = ft.icons.IMAGE
                            cor_icone = ft.colors.PURPLE_400
                        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']:
                            icone = ft.icons.ARTICLE
                            cor_icone = ft.colors.ORANGE_400
                        elif ext in ['.mp3', '.wav', '.flac', '.aac']:
                            icone = ft.icons.AUDIO_FILE
                            cor_icone = ft.colors.PINK_400
                        elif ext in ['.mp4', '.avi', '.mkv', '.mov']:
                            icone = ft.icons.VIDEO_FILE
                            cor_icone = ft.colors.RED_400
                        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
                            icone = ft.icons.FOLDER_ZIP
                            cor_icone = ft.colors.AMBER_400
                    
                    # Criar indicadores visuais para a estrutura de árvore
                    is_last_item = i == len(itens_ordenados) - 1
                    linha_vertical = "    " if is_last_item else "│   "
                    
                    if nivel == 0:
                        linha_item = ""
                    else:
                        linha_item = prefixo + ("└── " if is_last_item else "├── ")
                    
                    if tipo == "pasta":
                        # Para pastas, criar um Container expandível
                        subpasta_path = os.path.join(parent_path, nome)
                        
                        try:
                            subitems = listar_estrutura_pasta(subpasta_path)
                            
                            # Cria o container para o conteúdo da pasta
                            conteudo_container = ft.Container(
                                visible=nivel < 1,  # Expandido por padrão apenas no primeiro nível
                                content=ft.Column(
                                    [],  # Será preenchido após a criação do botão expandir
                                    spacing=2,
                                    tight=True
                                ),
                                padding=ft.padding.only(left=16)
                            )
                            
                            # Botão para expandir/colapsar
                            icone_expandir = ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if nivel < 1 else ft.icons.KEYBOARD_ARROW_RIGHT)
                            
                            # Título clicável para a pasta
                            titulo_row = ft.Row([
                                icone_expandir,
                                ft.Icon(icone, color=cor_icone),
                                ft.Text(f"{linha_item}{nome}", weight=ft.FontWeight.BOLD)
                            ])
                            
                            # Botão para expandir/colapsar a pasta
                            botao_expandir = ft.Container(
                                content=titulo_row,
                                on_click=lambda e, container=conteudo_container, icon=icone_expandir: toggle_expand(container, icon),
                                padding=ft.padding.only(top=5, bottom=5),
                            )
                            
                            # Função local para expandir/colapsar
                            def toggle_expand(container, icon):
                                container.visible = not container.visible
                                icon.name = ft.icons.KEYBOARD_ARROW_DOWN if container.visible else ft.icons.KEYBOARD_ARROW_RIGHT
                                page.update()
                            
                            # Conteúdo da pasta - chamada recursiva
                            novo_prefixo = prefixo + (linha_vertical if nivel > 0 else "")
                            subcontroles = criar_arvore_recursiva(subitems, subpasta_path, nivel + 1, novo_prefixo)
                            
                            # Adiciona subcontroles ao container
                            conteudo_container.content.controls = subcontroles
                            
                            # Adiciona botão e conteúdo
                            pasta_container = ft.Column([
                                botao_expandir,
                                conteudo_container
                            ], spacing=0, tight=True)
                            
                            controles.append(pasta_container)
                        except Exception as e:
                            # Erro ao acessar subpasta
                            controles.append(ft.Row([
                                ft.Icon(ft.icons.FOLDER, color=ft.colors.BLUE_400),
                                ft.Text(f"{linha_item}{nome}", weight=ft.FontWeight.BOLD),
                                ft.Text(f" (Erro: {str(e)})", color=ft.colors.RED_400, italic=True)
                            ]))
                    else:
                        # Para arquivos, apenas mostrar o nome com ícone
                        controles.append(ft.Container(
                            content=ft.Row([
                                ft.Container(width=24),  # Espaço para alinhar com as pastas
                                ft.Icon(icone, color=cor_icone),
                                ft.Text(f"{linha_item}{nome}")
                            ]),
                            padding=ft.padding.only(top=5, bottom=5)
                        ))
                
                return controles
            
            # Criar o contêiner raiz
            root_container = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.FOLDER, color=ft.colors.BLUE_400),
                        ft.Text(root_name, size=18, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Container(
                        content=ft.Column(
                            criar_arvore_recursiva(estrutura, pasta_path, 1),
                            tight=True
                        ),
                        padding=ft.padding.only(left=16)
                    )
                ]),
                padding=10,
                border_radius=8
            )
            
            estrutura_container.controls.append(root_container)
            
        except Exception as e:
            estrutura_container.controls.append(ft.Text(f"Erro ao ler a pasta: {str(e)}", color=ft.colors.RED_400))
        
        page.update()
    
    busca_input = ft.TextField(
        label="🔍 Buscar...",
        width=500,
        on_change=lambda e: criar_visualizacao_arvore(txt_pasta.value, e.control.value)
    )
    
    def selecionar_pasta(e):
        def on_result(e):
            if e.path:
                txt_pasta.value = e.path
                config["ultima_pasta"] = e.path
                salvar_config(CONFIG_PATH, config)
                criar_visualizacao_arvore(txt_pasta.value)
                page.update()
        
        file_picker.on_result = on_result
        file_picker.get_directory_path()
    
    btn_export_txt = ft.ElevatedButton("Exportar TXT", on_click=lambda e: exportar_para_txt(txt_pasta, page))
    btn_export_pdf = ft.ElevatedButton("Exportar PDF", on_click=lambda e: exportar_para_pdf(txt_pasta, page))
    btn_export_md = ft.ElevatedButton("Exportar Markdown", on_click=lambda e: exportar_para_md(txt_pasta, page))
    btn_export_json = ft.ElevatedButton("Exportar JSON", on_click=lambda e: exportar_para_json(txt_pasta, page))
    btn_zipar = ft.ElevatedButton("Compactar ZIP", on_click=lambda e: zipar_pasta(txt_pasta, page))
    btn_stats = ft.ElevatedButton("📊 Estatísticas", on_click=lambda e: gerar_estatisticas(txt_pasta, page))
    
    layout = ft.Column([
        ft.Container(
            content=ft.Row([
                ft.ElevatedButton("Selecionar Pasta", icon=ft.icons.FOLDER_OPEN, on_click=selecionar_pasta),
                txt_pasta
            ]),
            padding=10,
            bgcolor=ft.colors.BLUE_GREY_900,
            border_radius=8
        ),
        busca_input,
        ft.Row([btn_export_txt, btn_export_pdf, btn_export_md, btn_export_json, btn_zipar, btn_stats],
               scroll=ft.ScrollMode.ALWAYS),
        ft.Divider(),
        ft.Text("📂 Estrutura da Pasta:", size=18, weight=ft.FontWeight.BOLD),
        estrutura_container
    ], expand=True)
    
    # Carregar a última pasta usada, se existir
    if "ultima_pasta" in config and os.path.exists(config["ultima_pasta"]):
        txt_pasta.value = config["ultima_pasta"]
        criar_visualizacao_arvore(txt_pasta.value)
    
    page.add(layout)
    page.update()

ft.app(target=main)