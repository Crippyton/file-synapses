import os
import flet as ft
from flet import Colors, Icons

IGNORAR_PASTAS = {".git", "__pycache__"}

# Mapeamento de extensões para ícones e cores
ICONES_EXTENSOES = {
    # Código
    '.py': (Icons.CODE, Colors.GREEN_400),
    '.js': (Icons.CODE, Colors.YELLOW_700),
    '.html': (Icons.CODE, Colors.ORANGE_400),
    '.css': (Icons.CODE, Colors.BLUE_400),
    '.java': (Icons.CODE, Colors.ORANGE_700),
    '.cpp': (Icons.CODE, Colors.BLUE_700),
    '.c': (Icons.CODE, Colors.BLUE_800),
    # Imagens
    '.jpg': (Icons.IMAGE, Colors.PURPLE_300),
    '.jpeg': (Icons.IMAGE, Colors.PURPLE_300),
    '.png': (Icons.IMAGE, Colors.PURPLE_400),
    '.gif': (Icons.GIF_BOX, Colors.PURPLE_700),
    '.bmp': (Icons.IMAGE, Colors.PURPLE_200),
    '.svg': (Icons.IMAGE, Colors.PURPLE_500),
    # Documentos
    '.pdf': (Icons.PICTURE_AS_PDF, Colors.RED_400),
    '.doc': (Icons.ARTICLE, Colors.BLUE_300),
    '.docx': (Icons.ARTICLE, Colors.BLUE_300),
    '.xls': (Icons.GRID_ON, Colors.GREEN_600),
    '.xlsx': (Icons.GRID_ON, Colors.GREEN_600),
    '.ppt': (Icons.SLIDESHOW, Colors.ORANGE_500),
    '.pptx': (Icons.SLIDESHOW, Colors.ORANGE_500),
    '.txt': (Icons.TEXT_SNIPPET, Colors.GREY_600),
    '.md': (Icons.DESCRIPTION, Colors.BLUE_GREY_400),
    # Áudio
    '.mp3': (Icons.AUDIO_FILE, Colors.PINK_400),
    '.wav': (Icons.AUDIO_FILE, Colors.PINK_300),
    '.flac': (Icons.AUDIO_FILE, Colors.PINK_500),
    '.aac': (Icons.AUDIO_FILE, Colors.PINK_200),
    # Vídeo
    '.mp4': (Icons.VIDEO_FILE, Colors.RED_500),
    '.avi': (Icons.VIDEO_FILE, Colors.RED_400),
    '.mkv': (Icons.VIDEO_FILE, Colors.RED_600),
    '.mov': (Icons.VIDEO_FILE, Colors.RED_300),
    # Compactados
    '.zip': (Icons.FOLDER_ZIP, Colors.AMBER_500),
    '.rar': (Icons.FOLDER_ZIP, Colors.AMBER_600),
    '.7z': (Icons.FOLDER_ZIP, Colors.AMBER_700),
    '.tar': (Icons.FOLDER_ZIP, Colors.AMBER_400),
    '.gz': (Icons.FOLDER_ZIP, Colors.AMBER_300),
    # Padrão
    '': (Icons.DESCRIPTION, Colors.GREY_500)
}

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
        container.controls.append(ft.Text("Selecione uma pasta para visualizar"))
        return
    
    # Utiliza uma abordagem diferente para criar a árvore
    try:
        raiz_caminho = txt_pasta.value
        nome_raiz = os.path.basename(raiz_caminho) or raiz_caminho
        
        # Adiciona o título da pasta raiz
        container.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(Icons.FOLDER, color=Colors.BLUE_400, size=24),
                    ft.Text(nome_raiz, size=18, weight=ft.FontWeight.BOLD)
                ]),
                padding=10,
                bgcolor=Colors.BLUE_GREY_800,
                border_radius=10
            )
        )
        
        # Cria os itens da árvore
        itens = criar_itens_arvore(raiz_caminho, termo_busca)
        for item in itens:
            container.controls.append(item)
            
    except Exception as e:
        container.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(Icons.ERROR, color=Colors.RED_400),
                    ft.Text(f"Erro ao processar a pasta: {str(e)}", color=Colors.RED_400)
                ]),
                padding=10,
                border_radius=8
            )
        )

def criar_itens_arvore(caminho_pasta, termo_busca="", nivel=0):
    """Cria os itens da árvore recursivamente sem usar ExpansionTile"""
    itens = []
    
    # Limita a profundidade máxima para evitar problemas de performance
    MAX_PROFUNDIDADE = 2
    
    try:
        entradas = sorted(os.listdir(caminho_pasta))
        
        # Separar pastas e arquivos
        pastas = [e for e in entradas if os.path.isdir(os.path.join(caminho_pasta, e)) and e not in IGNORAR_PASTAS]
        arquivos = [e for e in entradas if os.path.isfile(os.path.join(caminho_pasta, e))]
        
        # Filtro de busca
        if termo_busca:
            termo_busca = termo_busca.lower()
            pastas_filtradas = []
            arquivos_filtrados = []
            
            # Filtra arquivos diretamente
            arquivos_filtrados = [a for a in arquivos if termo_busca in a.lower()]
            
            # Para pastas, verifica se o nome da pasta contém o termo ou se algum filho contém
            for pasta in pastas:
                if termo_busca in pasta.lower():
                    pastas_filtradas.append(pasta)
                    continue
                
                # Verifica filhos apenas no primeiro nível para não impactar a performance
                if nivel < 1:
                    try:
                        caminho_pasta_filho = os.path.join(caminho_pasta, pasta)
                        filhos = os.listdir(caminho_pasta_filho)
                        if any(termo_busca in filho.lower() for filho in filhos):
                            pastas_filtradas.append(pasta)
                    except:
                        pass
            
            pastas = pastas_filtradas
            arquivos = arquivos_filtrados
        
        # Processar pastas
        for pasta in pastas:
            caminho_completo = os.path.join(caminho_pasta, pasta)
            
            try:
                qtd_itens = len(os.listdir(caminho_completo))
                icone_pasta = Icons.FOLDER_SPECIAL if qtd_itens > 50 else Icons.FOLDER
                
                # Determina se deve expandir a pasta ou mostrar apenas um link para clicar
                deve_expandir = nivel < MAX_PROFUNDIDADE and (nivel == 0 or termo_busca)
                
                # Cabeçalho da pasta sempre visível
                cabecalho_pasta = ft.Container(
                    content=ft.Row([
                        ft.Icon(icone_pasta, color=Colors.BLUE_400, size=20),
                        ft.Text(pasta, weight=ft.FontWeight.BOLD),
                        ft.Text(f" ({qtd_itens} itens)", size=12, color=Colors.GREY_400)
                    ]),
                    padding=ft.padding.only(left=5, top=8, bottom=8, right=5),
                    bgcolor=Colors.BLUE_GREY_800,
                    border_radius=ft.border_radius.only(top_left=5, top_right=5),
                    on_click=lambda e, p=caminho_completo: expandir_pasta(e, p)
                )
                
                # Conteúdo da pasta
                if deve_expandir:
                    # Expande a pasta e mostra o conteúdo
                    conteudo_pasta = ft.Container(
                        content=ft.Column(
                            criar_itens_arvore(caminho_completo, termo_busca, nivel + 1),
                            spacing=2
                        ),
                        padding=ft.padding.only(left=20),
                        bgcolor=Colors.BLUE_GREY_900,
                        border_radius=ft.border_radius.only(bottom_left=5, bottom_right=5)
                    )
                else:
                    # Mostra apenas um link para expandir
                    conteudo_pasta = ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(Icons.ARROW_FORWARD, color=Colors.BLUE_300, size=14),
                                    ft.Text("Clique para explorar...", italic=True, color=Colors.BLUE_300)
                                ]),
                                on_click=lambda e, p=caminho_completo: expandir_pasta(e, p)
                            )
                        ]),
                        padding=ft.padding.only(left=20, top=5, bottom=5),
                        bgcolor=Colors.BLUE_GREY_900,
                        border_radius=ft.border_radius.only(bottom_left=5, bottom_right=5)
                    )
                
                # Container da pasta completa
                container_pasta = ft.Container(
                    content=ft.Column([cabecalho_pasta, conteudo_pasta]),
                    margin=ft.margin.only(left=nivel * 10, top=3, bottom=3)
                )
                itens.append(container_pasta)
                
            except PermissionError:
                # Pasta sem permissão
                container_pasta = ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(Icons.FOLDER, color=Colors.RED_400, size=20),
                                ft.Text(pasta, weight=ft.FontWeight.BOLD),
                                ft.Text(" (Sem permissão)", size=12, color=Colors.RED_400, italic=True)
                            ]),
                            padding=ft.padding.only(left=5, top=8, bottom=8, right=5),
                            bgcolor=Colors.RED_50,
                            border_radius=5
                        )
                    ]),
                    margin=ft.margin.only(left=nivel * 10, top=3, bottom=3)
                )
                itens.append(container_pasta)
                
            except Exception as e:
                # Erro ao processar pasta
                container_pasta = ft.Container(
                    content=ft.Row([
                        ft.Icon(Icons.FOLDER, color=Colors.AMBER_400, size=20),
                        ft.Text(pasta, weight=ft.FontWeight.BOLD),
                        ft.Text(f" (Erro: {str(e)[:30]}...)", size=12, color=Colors.AMBER_400, italic=True)
                    ]),
                    padding=ft.padding.all(5),
                    margin=ft.margin.only(left=nivel * 10, top=3, bottom=3),
                    bgcolor=Colors.AMBER_50,
                    border_radius=5
                )
                itens.append(container_pasta)
        
        # Processar arquivos
        for arquivo in arquivos:
            caminho_completo = os.path.join(caminho_pasta, arquivo)
            try:
                extensao = os.path.splitext(arquivo)[1].lower()
                icone, cor = ICONES_EXTENSOES.get(extensao, ICONES_EXTENSOES[''])
                
                container_arquivo = ft.Container(
                    content=ft.Row([
                        ft.Icon(icone, color=cor, size=18),
                        ft.Text(arquivo)
                    ]),
                    padding=ft.padding.only(left=10, top=5, bottom=5),
                    margin=ft.margin.only(left=nivel * 20 + 20)
                )
                itens.append(container_arquivo)
            except:
                # Ignora erros em arquivos individuais
                pass
            
    except PermissionError:
        itens.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(Icons.ERROR, color=Colors.RED_400, size=20),
                    ft.Text("Sem permissão de acesso", color=Colors.RED_400)
                ]),
                padding=10,
                margin=ft.margin.only(left=nivel * 20)
            )
        )
    except Exception as e:
        itens.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(Icons.ERROR, color=Colors.RED_400, size=20),
                    ft.Text(f"Erro: {str(e)[:50]}...", color=Colors.RED_400)
                ]),
                padding=10,
                margin=ft.margin.only(left=nivel * 20)
            )
        )
        
    return itens

def expandir_pasta(e, caminho):
    """Expande uma pasta ao clicar nela"""
    try:
        # Determina se o clique foi no cabeçalho ou no link "Clique para explorar"
        # Se foi no link, o parent do control é a coluna, e precisamos do container pai
        container = e.control
        
        # Se o container pai for uma coluna, precisamos subir mais um nível
        if isinstance(container.content, ft.Row) and "Clique para explorar" in str(container.content.controls):
            # Foi clicado no link "Clique para explorar"
            # O pai da coluna é o container da pasta
            coluna_pai = container.parent
            if coluna_pai and isinstance(coluna_pai, ft.Column):
                container_pasta = coluna_pai.parent
                if container_pasta:
                    # Substitui o conteúdo do segundo item (o conteúdo da pasta)
                    coluna = container_pasta.content
                    if isinstance(coluna, ft.Column) and len(coluna.controls) > 1:
                        # Substitui o container de conteúdo pelo conteúdo novo
                        coluna.controls[1] = ft.Container(
                            content=ft.Column(criar_itens_arvore(caminho), spacing=2),
                            padding=ft.padding.only(left=20),
                            bgcolor=Colors.BLUE_GREY_900,
                            border_radius=ft.border_radius.only(bottom_left=5, bottom_right=5)
                        )
                        coluna.update()
        else:
            # Foi clicado no cabeçalho da pasta
            # Procura o container da pasta (pai da coluna que contém o cabeçalho)
            container_pasta = container.parent
            if container_pasta and isinstance(container_pasta, ft.Column):
                # O container da pasta tem uma coluna com [cabeçalho, conteúdo]
                if len(container_pasta.controls) > 1:
                    container_pasta.controls[1] = ft.Container(
                        content=ft.Column(criar_itens_arvore(caminho), spacing=2),
                        padding=ft.padding.only(left=20),
                        bgcolor=Colors.BLUE_GREY_900,
                        border_radius=ft.border_radius.only(bottom_left=5, bottom_right=5)
                    )
                    container_pasta.update()
    except Exception as e:
        print(f"Erro ao expandir pasta: {str(e)}")
        # Não faz nada no caso de erro para evitar quebrar a UI
