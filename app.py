import os
import flet as ft
import json
import difflib
from datetime import datetime

# Importando funções dos módulos utils
from utils.explorer import listar_estrutura_pasta, gerar_arvore
from utils.exporter import exportar_para_txt, exportar_para_pdf, exportar_para_md, exportar_para_json
from utils.stats import gerar_estatisticas
from utils.zipping import zipar_pasta
from utils.config import carregar_config, salvar_config

CONFIG_PATH = "assets/config.json"

def main(page: ft.Page):
    config = carregar_config(CONFIG_PATH)
    page.title = "File Synapses - Visualizador de Estrutura de Pastas"
    
    page.window_width = 800
    page.window_height = 750
    
    page.theme_mode = ft.ThemeMode.DARK if config.get("tema_escuro", True) else ft.ThemeMode.LIGHT
    page.scroll = "AUTO"
    
    # Inicializa histórico de pastas
    if "pastas_recentes" not in config:
        config["pastas_recentes"] = []
    
    txt_pasta = ft.Text("Nenhuma pasta selecionada", size=16, color=ft.Colors.GREY)
    estrutura_container = ft.Column(scroll=ft.ScrollMode.ALWAYS, spacing=10)
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    def criar_visualizacao_arvore(pasta_path, termo_busca=None):
        if not pasta_path or pasta_path == "Nenhuma pasta selecionada":
            estrutura_container.controls.clear()
            estrutura_container.controls.append(ft.Text("Selecione uma pasta para visualizar sua estrutura"))
            page.update()
            return
        
        # Atualiza interface para mostrar o carregamento
        estrutura_container.controls.clear()
        estrutura_container.controls.append(
            ft.Row([
                ft.ProgressRing(),
                ft.Text("Carregando estrutura, aguarde...", italic=True)
            ])
        )
        page.update()
        
        # Carrega a estrutura
        gerar_arvore(ft.Text(pasta_path), estrutura_container, termo_busca or "")
        
        # Atualiza o histórico de pastas recentes
        atualizar_historico_pastas(pasta_path)
        
        page.update()
    
    def atualizar_historico_pastas(pasta_path):
        """Atualiza o histórico de pastas recentes"""
        if not pasta_path or pasta_path == "Nenhuma pasta selecionada":
            return
            
        # Adiciona ao início e remove duplicatas
        if pasta_path in config["pastas_recentes"]:
            config["pastas_recentes"].remove(pasta_path)
        config["pastas_recentes"].insert(0, pasta_path)
        
        # Limita o número de pastas recentes
        config["pastas_recentes"] = config["pastas_recentes"][:5]
        
        # Salva a configuração
        salvar_config(CONFIG_PATH, config)
        
        # Atualiza a UI
        criar_chips_pastas_recentes()
    
    pastas_recentes_container = ft.Row(
        scroll=ft.ScrollMode.AUTO,
        spacing=5
    )
    
    def criar_chips_pastas_recentes():
        """Cria os chips de pastas recentes"""
        pastas_recentes_container.controls.clear()
        
        if not config["pastas_recentes"]:
            pastas_recentes_container.controls.append(
                ft.Text("Nenhuma pasta recente", italic=True, size=12)
            )
        else:
            for pasta in config["pastas_recentes"]:
                # Verifica se a pasta ainda existe
                if not os.path.exists(pasta):
                    continue
                    
                nome_pasta = os.path.basename(pasta) or pasta
                pastas_recentes_container.controls.append(
                    ft.Chip(
                        leading=ft.Icon(ft.Icons.FOLDER),
                        label=ft.Text(nome_pasta),
                        tooltip=pasta,
                        on_click=lambda e, p=pasta: selecionar_pasta_recente(p)
                    )
                )
        page.update()
    
    def selecionar_pasta_recente(pasta_path):
        """Seleciona uma pasta recente"""
        if os.path.exists(pasta_path):
            txt_pasta.value = pasta_path
            config["ultima_pasta"] = pasta_path
            salvar_config(CONFIG_PATH, config)
            criar_visualizacao_arvore(pasta_path)
    
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
    
    def alternar_tema(e):
        config["tema_escuro"] = not config.get("tema_escuro", True)
        page.theme_mode = ft.ThemeMode.DARK if config["tema_escuro"] else ft.ThemeMode.LIGHT
        salvar_config(CONFIG_PATH, config)
        page.update()
    
    def atualizar_visualizacao(e):
        if txt_pasta.value and txt_pasta.value != "Nenhuma pasta selecionada":
            criar_visualizacao_arvore(txt_pasta.value, busca_input.value)
    
    # Atalhos de teclado
    def keyboard_handler(e: ft.KeyboardEvent):
        if e.key == "F5":
            # F5 para atualizar
            atualizar_visualizacao(None)
        elif e.key == "O" and e.ctrl:
            # Ctrl+O para selecionar pasta
            selecionar_pasta(None)
        elif e.key == "F" and e.ctrl:
            # Ctrl+F para focar na busca
            page.focus(busca_input)
    
    page.on_keyboard_event = keyboard_handler
    
    # Função para comparar duas pastas
    def comparar_pastas(e):
        dlg = ft.AlertDialog(
            title=ft.Text("Comparação de Pastas"),
            content=ft.Column([
                ft.Text("Selecione a pasta para comparar com a pasta atual:"),
                ft.ElevatedButton(
                    "Selecionar Pasta para Comparação",
                    icon=ft.Icons.FOLDER_OPEN,
                    on_click=lambda e: selecionar_pasta_comparacao()
                ),
                ft.Row([
                    ft.Text("Pasta atual: "),
                    ft.Text(txt_pasta.value, color=ft.Colors.BLUE, italic=True)
                ]),
                ft.Row([
                    ft.Text("Pasta de comparação: "),
                    (txt_pasta_comp := ft.Text("Não selecionada", color=ft.Colors.GREY, italic=True))
                ]),
                (progress_comp := ft.ProgressBar(width=400, visible=False)),
                (container_resultado_comp := ft.Container(
                    height=300,
                    content=(resultado_comp := ft.Column([], scroll=ft.ScrollMode.ALWAYS)),
                    visible=False
                ))
            ], height=450, width=550, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: close_comp_dlg(e))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: print("Diálogo de comparação fechado")
        )
        
        # Função para fechar o diálogo
        def close_comp_dlg(e):
            dlg.open = False
            page.update()
        
        # Função para selecionar pasta de comparação
        def selecionar_pasta_comparacao():
            def on_result(e):
                if e.path:
                    # Atualiza o texto da pasta de comparação
                    txt_pasta_comp.value = e.path
                    page.update()
                    
                    # Inicia a comparação
                    realizar_comparacao(txt_pasta.value, e.path)
            
            file_picker.on_result = on_result
            file_picker.get_directory_path()
        
        # Função para realizar comparação
        def realizar_comparacao(pasta1, pasta2):
            # Mostra a barra de progresso
            progress_comp.visible = True
            page.update()
            
            # Gera a estrutura das pastas
            estrutura1 = gerar_estrutura_para_comparacao(pasta1)
            estrutura2 = gerar_estrutura_para_comparacao(pasta2)
            
            # Compara as estruturas
            resultados = comparar_estruturas(estrutura1, estrutura2, pasta1, pasta2)
            
            # Exibe os resultados
            container_resultado_comp.visible = True
            resultado_comp.controls.clear()
            
            if not resultados["diferenças"]:
                resultado_comp.controls.append(
                    ft.Text("As estruturas das pastas são idênticas!", color=ft.Colors.GREEN)
                )
            else:
                # Título e resumo
                resultado_comp.controls.append(
                    ft.Text(f"Resumo da comparação:", weight=ft.FontWeight.BOLD, size=16)
                )
                resultado_comp.controls.append(
                    ft.Text(f"• Total de arquivos na pasta 1: {resultados['stats']['pasta1']['arquivos']}")
                )
                resultado_comp.controls.append(
                    ft.Text(f"• Total de arquivos na pasta 2: {resultados['stats']['pasta2']['arquivos']}")
                )
                resultado_comp.controls.append(
                    ft.Text(f"• Total de pastas na pasta 1: {resultados['stats']['pasta1']['pastas']}")
                )
                resultado_comp.controls.append(
                    ft.Text(f"• Total de pastas na pasta 2: {resultados['stats']['pasta2']['pastas']}")
                )
                resultado_comp.controls.append(
                    ft.Text(f"• Diferenças encontradas: {len(resultados['diferenças'])}")
                )
                
                resultado_comp.controls.append(ft.Divider())
                resultado_comp.controls.append(
                    ft.Text("Diferenças encontradas:", weight=ft.FontWeight.BOLD, size=16)
                )
                
                # Lista as diferenças
                for i, diff in enumerate(resultados["diferenças"][:50]):  # Limita a 50 diferenças para performance
                    if diff["tipo"] == "ausente_1":
                        resultado_comp.controls.append(
                            ft.Text(f"• Ausente na pasta 1: {diff['caminho']}", color=ft.Colors.RED_400)
                        )
                    elif diff["tipo"] == "ausente_2":
                        resultado_comp.controls.append(
                            ft.Text(f"• Ausente na pasta 2: {diff['caminho']}", color=ft.Colors.BLUE_400)
                        )
                    elif diff["tipo"] == "modificado":
                        resultado_comp.controls.append(
                            ft.Text(f"• Modificado: {diff['caminho']} (tamanho, data)")
                        )
                
                # Se houver mais diferenças, mostrar aviso
                if len(resultados["diferenças"]) > 50:
                    resultado_comp.controls.append(
                        ft.Text(f"... e mais {len(resultados['diferenças']) - 50} diferenças não mostradas", italic=True)
                    )
                
                # Botão para exportar resultados
                resultado_comp.controls.append(ft.Divider())
                resultado_comp.controls.append(
                    ft.ElevatedButton(
                        "Exportar Resultados",
                        icon=ft.Icons.SAVE,
                        on_click=lambda e: exportar_resultados_comparacao(resultados, pasta1, pasta2)
                    )
                )
            
            # Esconde a barra de progresso
            progress_comp.visible = False
            page.update()
            
            # Exibe o diálogo
            page.dialog = dlg
            page.dialog.open = True
            page.update()
    
    def gerar_estrutura_para_comparacao(pasta_raiz):
        """Gera um dicionário com a estrutura da pasta para comparação"""
        estrutura = {
            "pastas": {},
            "arquivos": {},
            "stats": {"pastas": 0, "arquivos": 0}
        }
        
        for root, dirs, files in os.walk(pasta_raiz):
            caminho_relativo = os.path.relpath(root, pasta_raiz)
            if caminho_relativo == ".":
                caminho_relativo = ""
            
            # Registra a pasta
            if caminho_relativo:
                estrutura["pastas"][caminho_relativo] = {
                    "modificado": os.path.getmtime(root)
                }
                estrutura["stats"]["pastas"] += 1
            
            # Registra os arquivos
            for file in files:
                file_path = os.path.join(root, file)
                file_relpath = os.path.join(caminho_relativo, file).replace("\\", "/")
                
                try:
                    estrutura["arquivos"][file_relpath] = {
                        "tamanho": os.path.getsize(file_path),
                        "modificado": os.path.getmtime(file_path)
                    }
                    estrutura["stats"]["arquivos"] += 1
                except Exception as e:
                    print(f"Erro ao processar arquivo {file_path}: {e}")
        
        return estrutura
    
    def comparar_estruturas(estrutura1, estrutura2, pasta1, pasta2):
        """Compara duas estruturas de pastas e retorna as diferenças"""
        resultados = {
            "stats": {
                "pasta1": estrutura1["stats"],
                "pasta2": estrutura2["stats"]
            },
            "diferenças": []
        }
        
        # Compara arquivos
        for arquivo, info in estrutura1["arquivos"].items():
            if arquivo not in estrutura2["arquivos"]:
                resultados["diferenças"].append({
                    "tipo": "ausente_2",
                    "caminho": arquivo
                })
            else:
                # Verifica se o arquivo foi modificado
                info2 = estrutura2["arquivos"][arquivo]
                if info["tamanho"] != info2["tamanho"] or abs(info["modificado"] - info2["modificado"]) > 1:
                    resultados["diferenças"].append({
                        "tipo": "modificado",
                        "caminho": arquivo,
                        "diferença": {
                            "tamanho1": info["tamanho"],
                            "tamanho2": info2["tamanho"],
                            "modificado1": info["modificado"],
                            "modificado2": info2["modificado"]
                        }
                    })
        
        # Verifica arquivos presentes em estrutura2 mas não em estrutura1
        for arquivo in estrutura2["arquivos"]:
            if arquivo not in estrutura1["arquivos"]:
                resultados["diferenças"].append({
                    "tipo": "ausente_1",
                    "caminho": arquivo
                })
        
        # Compara pastas
        for pasta in estrutura1["pastas"]:
            if pasta not in estrutura2["pastas"]:
                resultados["diferenças"].append({
                    "tipo": "ausente_2",
                    "caminho": pasta + "/"
                })
        
        for pasta in estrutura2["pastas"]:
            if pasta not in estrutura1["pastas"]:
                resultados["diferenças"].append({
                    "tipo": "ausente_1",
                    "caminho": pasta + "/"
                })
        
        # Ordena as diferenças por caminho
        resultados["diferenças"].sort(key=lambda x: x["caminho"])
        
        return resultados
    
    def exportar_resultados_comparacao(resultados, pasta1, pasta2):
        """Exporta os resultados da comparação para um arquivo JSON"""
        try:
            # Gera nome do arquivo baseado nas pastas
            nome_pasta1 = os.path.basename(pasta1)
            nome_pasta2 = os.path.basename(pasta2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Diretório de saída será o mesmo da pasta1
            diretorio_saida = os.path.dirname(pasta1)
            nome_arquivo = f"comparacao_{nome_pasta1}_vs_{nome_pasta2}_{timestamp}.json"
            caminho_completo = os.path.join(diretorio_saida, nome_arquivo)
            
            # Dados para exportar
            dados_exportacao = {
                "data_comparacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pasta1": pasta1,
                "pasta2": pasta2,
                "estatisticas": resultados["stats"],
                "diferencas": resultados["diferenças"]
            }
            
            # Salva o arquivo
            with open(caminho_completo, "w", encoding="utf-8") as f:
                json.dump(dados_exportacao, f, indent=2, ensure_ascii=False)
            
            # Notifica o usuário
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Resultados exportados para: {caminho_completo}"),
                action=ft.TextButton("Ver", on_click=lambda e: os.startfile(caminho_completo)),
                open=True
            )
            page.update()
        except Exception as e:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Erro ao exportar resultados: {str(e)}"),
                open=True
            )
            page.update()
    
    # Botões de ações
    btn_export_txt = ft.ElevatedButton("Exportar TXT", on_click=lambda e: exportar_para_txt(txt_pasta, page))
    btn_export_pdf = ft.ElevatedButton("Exportar PDF", on_click=lambda e: exportar_para_pdf(txt_pasta, page))
    btn_export_md = ft.ElevatedButton("Exportar Markdown", on_click=lambda e: exportar_para_md(txt_pasta, page))
    btn_export_json = ft.ElevatedButton("Exportar JSON", on_click=lambda e: exportar_para_json(txt_pasta, page))
    btn_zipar = ft.ElevatedButton("Compactar ZIP", on_click=lambda e: zipar_pasta(txt_pasta, page))
    btn_stats = ft.ElevatedButton("📊 Estatísticas", on_click=lambda e: gerar_estatisticas(txt_pasta, page))
    btn_comparar = ft.ElevatedButton("🔄 Comparar", on_click=comparar_pastas, tooltip="Comparar com outra pasta")
    btn_tema = ft.IconButton(
        icon=ft.Icons.DARK_MODE if config.get("tema_escuro", True) else ft.Icons.LIGHT_MODE,
        on_click=alternar_tema,
        tooltip="Alternar tema"
    )
    
    # Cabeçalho
    cabecalho = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("📂 File Synapses", size=24, weight=ft.FontWeight.BOLD),
                btn_tema
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Visualizador e Gerenciador de Estrutura de Pastas", size=14, italic=True)
        ]),
        padding=ft.padding.only(left=10, right=10, top=5, bottom=5),
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8)
    )
    
    # Seletor de pasta
    seletor_pasta = ft.Container(
        content=ft.Row([
            ft.ElevatedButton("Selecionar Pasta", icon=ft.Icons.FOLDER_OPEN, on_click=selecionar_pasta),
            txt_pasta,
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Atualizar visualização (F5)",
                on_click=atualizar_visualizacao
            )
        ]),
        padding=10,
        bgcolor=ft.Colors.BLUE_GREY_800,
        border_radius=8
    )
    
    # Container de pastas recentes
    pastas_recentes_secao = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=14),
                ft.Text("Pastas Recentes:", size=14, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Atualizar lista",
                    icon_size=14,
                    on_click=lambda _: criar_chips_pastas_recentes()
                )
            ]),
            pastas_recentes_container
        ]),
        padding=ft.padding.all(10),
        bgcolor=ft.Colors.BLUE_GREY_800,
        border_radius=8
    )
    
    # Barra de ajuda de atalhos
    atalhos_secao = ft.Container(
        content=ft.Row([
            ft.Text("Atalhos: ", weight=ft.FontWeight.BOLD, size=12),
            ft.Text("F5 = Atualizar | Ctrl+O = Abrir pasta | Ctrl+F = Buscar", size=12)
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.all(5),
        bgcolor=ft.Colors.BLUE_GREY_700,
        border_radius=8
    )
    
    # Barra de ações
    barra_acoes = ft.Container(
        content=ft.Row(
            [btn_export_txt, btn_export_pdf, btn_export_md, btn_export_json, btn_zipar, btn_stats, btn_comparar],
            scroll=ft.ScrollMode.ALWAYS,
            alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=ft.padding.only(top=10, bottom=10),
        bgcolor=ft.Colors.BLUE_GREY_800,
        border_radius=8
    )
    
    # Rodapé
    rodape = ft.Container(
        content=ft.Row([
            ft.Text("📂 File Synapses v1.1", italic=True),
            ft.Text("Desenvolvido com ❤️ usando Flet", italic=True)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(10),
        bgcolor=ft.Colors.BLUE_GREY_900,
        border_radius=ft.border_radius.only(top_left=8, top_right=8)
    )
    
    layout = ft.Column([
        cabecalho,
        ft.Container(height=10),  # Espaçamento
        seletor_pasta,
        ft.Container(height=5),  # Espaçamento
        pastas_recentes_secao,
        ft.Container(height=5),  # Espaçamento
        atalhos_secao,
        ft.Container(height=5),  # Espaçamento
        busca_input,
        ft.Container(height=5),  # Espaçamento
        barra_acoes,
        ft.Container(height=10),  # Espaçamento
        ft.Text("📂 Estrutura da Pasta:", size=18, weight=ft.FontWeight.BOLD),
        estrutura_container,
        ft.Container(height=10),  # Espaçamento
        rodape
    ], expand=True)
    
    # Carregar a última pasta usada, se existir
    if "ultima_pasta" in config and os.path.exists(config["ultima_pasta"]):
        txt_pasta.value = config["ultima_pasta"]
        criar_visualizacao_arvore(txt_pasta.value)
    
    # Inicializa os chips de pastas recentes
    criar_chips_pastas_recentes()
    
    page.add(layout)
    page.update()

ft.app(target=main)