import os
import flet as ft
from flet import Colors
from collections import Counter, defaultdict
from datetime import datetime, timedelta

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

def gerar_estatisticas(txt_pasta, page):
    try:
        # Inicializa contadores e variáveis
        total_arquivos = 0
        total_diretorios = 0
        total_tamanho = 0
        maior_arquivo = {"nome": "", "tamanho": 0, "caminho": ""}
        arquivo_mais_recente = {"nome": "", "data": 0, "caminho": ""}
        arquivo_mais_antigo = {"nome": "", "data": datetime.now().timestamp(), "caminho": ""}
        extensoes = Counter()
        tipos_arquivos = defaultdict(int)
        profundidade_max = 0
        
        # Novas estatísticas
        arquivos_por_mes = defaultdict(int)
        tamanho_por_mes = defaultdict(int)
        arquivos_vazios = 0
        arquivos_grandes = 0  # Arquivos maiores que 10MB
        arquivos_pequenos = 0  # Arquivos menores que 10KB
        arquivos_ocultos = 0
        arquivos_somente_leitura = 0
        
        # Mapeamento de extensões para categorias
        mapa_categorias = {
            "código": ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h', '.php'],
            "imagem": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            "documento": ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.odt', '.ods'],
            "áudio": ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            "vídeo": ['.mp4', '.avi', '.mkv', '.mov', '.webm'],
            "compactado": ['.zip', '.rar', '.7z', '.tar', '.gz']
        }
        
        # Percorre a estrutura da pasta
        for root, dirs, files in os.walk(txt_pasta.value):
            # Calcula a profundidade
            nivel = root[len(txt_pasta.value):].count(os.sep)
            profundidade_max = max(profundidade_max, nivel)
            
            # Conta os diretórios
            total_diretorios += len(dirs)
            
            # Processa os arquivos
            for file in files:
                total_arquivos += 1
                caminho = os.path.join(root, file)
                
                try:
                    # Informações do arquivo
                    if os.path.exists(caminho):
                        # Verifica se é arquivo oculto (começa com .)
                        if file.startswith("."):
                            arquivos_ocultos += 1
                            
                        # Verifica permissões
                        if not os.access(caminho, os.W_OK) and os.access(caminho, os.R_OK):
                            arquivos_somente_leitura += 1
                        
                        # Tamanho
                        tamanho = os.path.getsize(caminho)
                        total_tamanho += tamanho
                        
                        # Categoriza por tamanho
                        if tamanho == 0:
                            arquivos_vazios += 1
                        elif tamanho < 10 * 1024:  # < 10KB
                            arquivos_pequenos += 1
                        elif tamanho > 10 * 1024 * 1024:  # > 10MB
                            arquivos_grandes += 1
                        
                        # Extensão
                        ext = os.path.splitext(file)[1].lower()
                        extensoes[ext] += 1
                        
                        # Categoriza o arquivo
                        categoria = "outro"
                        for cat, exts in mapa_categorias.items():
                            if ext in exts:
                                categoria = cat
                                break
                        tipos_arquivos[categoria] += 1
                        
                        # Verifica se é o maior arquivo
                        if tamanho > maior_arquivo["tamanho"]:
                            maior_arquivo = {"nome": file, "tamanho": tamanho, "caminho": caminho}
                        
                        # Datas de modificação
                        data_mod = os.path.getmtime(caminho)
                        data_mod_dt = datetime.fromtimestamp(data_mod)
                        mes_ano = data_mod_dt.strftime("%Y-%m")
                        
                        # Agrupa por mês/ano
                        arquivos_por_mes[mes_ano] += 1
                        tamanho_por_mes[mes_ano] += tamanho
                        
                        if data_mod > arquivo_mais_recente["data"]:
                            arquivo_mais_recente = {"nome": file, "data": data_mod, "caminho": caminho}
                        if data_mod < arquivo_mais_antigo["data"]:
                            arquivo_mais_antigo = {"nome": file, "data": data_mod, "caminho": caminho}
                except:
                    # Ignora erros ao ler informações do arquivo
                    pass
        
        # Análise temporal
        meses_ordenados = sorted(arquivos_por_mes.keys())
        
        # Previsão simples de crescimento (último mês vs. média)
        taxa_crescimento = 0
        previsao_tamanho_6meses = total_tamanho
        
        if meses_ordenados:
            # Se temos dados suficientes para análise temporal
            if len(meses_ordenados) >= 2:
                ultimo_mes = meses_ordenados[-1]
                penultimo_mes = meses_ordenados[-2]
                
                # Taxa de crescimento baseada nos últimos dois meses
                if tamanho_por_mes[penultimo_mes] > 0:
                    taxa_crescimento = (tamanho_por_mes[ultimo_mes] - tamanho_por_mes[penultimo_mes]) / tamanho_por_mes[penultimo_mes] * 100
                
                # Previsão simples para 6 meses (crescimento composto)
                if taxa_crescimento > 0:
                    previsao_tamanho_6meses = total_tamanho * (1 + taxa_crescimento/100) ** 6
        
        # Extensões mais comuns
        extensoes_comuns = dict(extensoes.most_common(5))
        ext_info = "\n".join([f"• {ext or 'sem extensão'}: {qtd} arquivo(s)" for ext, qtd in extensoes_comuns.items()])
        
        # Tipos de arquivo
        tipos_info = "\n".join([f"• {tipo.title()}: {qtd} arquivo(s)" for tipo, qtd in tipos_arquivos.items()])
        
        # Prepara o conteúdo do diálogo com várias abas
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                # Aba 1: Visão Geral
                ft.Tab(
                    text="Visão Geral",
                    icon=ft.icons.DASHBOARD,
                    content=ft.Container(
                        content=ft.Column([
                            # Estatísticas básicas
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📊 Visão Geral", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"• Pasta: {txt_pasta.value}"),
                                    ft.Text(f"• Total de arquivos: {total_arquivos}"),
                                    ft.Text(f"• Total de pastas: {total_diretorios}"),
                                    ft.Text(f"• Tamanho total: {formatar_tamanho(total_tamanho)}"),
                                    ft.Text(f"• Profundidade máxima: {profundidade_max} níveis")
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10
                            ),
                            
                            # Estatísticas avançadas
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("🔍 Detalhes", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"• Arquivos vazios: {arquivos_vazios}"),
                                    ft.Text(f"• Arquivos pequenos (<10KB): {arquivos_pequenos}"),
                                    ft.Text(f"• Arquivos grandes (>10MB): {arquivos_grandes}"),
                                    ft.Text(f"• Arquivos ocultos: {arquivos_ocultos}"),
                                    ft.Text(f"• Arquivos somente leitura: {arquivos_somente_leitura}")
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10,
                                margin=ft.margin.only(top=10)
                            ),
                            
                            # Estatísticas de arquivos específicos
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📦 Arquivos Notáveis", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text("Maior arquivo:"),
                                    ft.Text(f"• {maior_arquivo['nome']} ({formatar_tamanho(maior_arquivo['tamanho'])})", 
                                           overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text("Arquivo mais recente:"),
                                    ft.Text(f"• {arquivo_mais_recente['nome']} " + 
                                           f"({datetime.fromtimestamp(arquivo_mais_recente['data']).strftime('%d/%m/%Y %H:%M:%S')})", 
                                           overflow=ft.TextOverflow.ELLIPSIS),
                                    ft.Text("Arquivo mais antigo:"),
                                    ft.Text(f"• {arquivo_mais_antigo['nome']} " + 
                                           f"({datetime.fromtimestamp(arquivo_mais_antigo['data']).strftime('%d/%m/%Y %H:%M:%S')})", 
                                           overflow=ft.TextOverflow.ELLIPSIS)
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10,
                                margin=ft.margin.only(top=10)
                            )
                        ], scroll=ft.ScrollMode.AUTO),
                        padding=10
                    )
                ),
                
                # Aba 2: Distribuição
                ft.Tab(
                    text="Distribuição",
                    icon=ft.icons.PIE_CHART,
                    content=ft.Container(
                        content=ft.Column([
                            # Tipos e extensões
                            ft.Row([
                                # Extensões mais comuns
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("🧩 Extensões mais comuns", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(ext_info)
                                    ]),
                                    padding=10,
                                    bgcolor=Colors.BLUE_GREY_800,
                                    border_radius=10,
                                    margin=ft.margin.only(right=5),
                                    expand=1
                                ),
                                
                                # Tipos de arquivo
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("🗂️ Tipos de Arquivo", size=16, weight=ft.FontWeight.BOLD),
                                        ft.Text(tipos_info)
                                    ]),
                                    padding=10,
                                    bgcolor=Colors.BLUE_GREY_800,
                                    border_radius=10,
                                    margin=ft.margin.only(left=5),
                                    expand=1
                                )
                            ]),
                            
                            # Gráfico de tipos de arquivo
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📊 Distribuição por Categoria", size=16, weight=ft.FontWeight.BOLD),
                                    *[criar_barra_grafico(tipo.title(), qtd, total_arquivos) for tipo, qtd in tipos_arquivos.items()]
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10,
                                margin=ft.margin.only(top=10)
                            ),
                            
                            # Proporção de tamanhos
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📏 Distribuição por Tamanho", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Row([
                                        # Pequenos
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text("Pequenos (<10KB)"),
                                                ft.Container(
                                                    bgcolor=Colors.BLUE_300,
                                                    width=100 * arquivos_pequenos / max(total_arquivos, 1),
                                                    height=20,
                                                    border_radius=5,
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text(f"{round(100 * arquivos_pequenos / max(total_arquivos, 1))}%") if arquivos_pequenos > 0 else None
                                                )
                                            ]),
                                            expand=True
                                        ),
                                        # Médios
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text("Médios"),
                                                ft.Container(
                                                    bgcolor=Colors.GREEN_300,
                                                    width=100 * (total_arquivos - arquivos_pequenos - arquivos_grandes - arquivos_vazios) / max(total_arquivos, 1),
                                                    height=20,
                                                    border_radius=5,
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text(f"{round(100 * (total_arquivos - arquivos_pequenos - arquivos_grandes - arquivos_vazios) / max(total_arquivos, 1))}%") if (total_arquivos - arquivos_pequenos - arquivos_grandes - arquivos_vazios) > 0 else None
                                                )
                                            ]),
                                            expand=True
                                        ),
                                        # Grandes
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text("Grandes (>10MB)"),
                                                ft.Container(
                                                    bgcolor=Colors.ORANGE_300,
                                                    width=100 * arquivos_grandes / max(total_arquivos, 1),
                                                    height=20,
                                                    border_radius=5,
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text(f"{round(100 * arquivos_grandes / max(total_arquivos, 1))}%") if arquivos_grandes > 0 else None
                                                )
                                            ]),
                                            expand=True
                                        ),
                                        # Vazios
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Text("Vazios"),
                                                ft.Container(
                                                    bgcolor=Colors.GREY_300,
                                                    width=100 * arquivos_vazios / max(total_arquivos, 1),
                                                    height=20,
                                                    border_radius=5,
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text(f"{round(100 * arquivos_vazios / max(total_arquivos, 1))}%") if arquivos_vazios > 0 else None
                                                )
                                            ]),
                                            expand=True
                                        )
                                    ])
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10,
                                margin=ft.margin.only(top=10)
                            )
                        ], scroll=ft.ScrollMode.AUTO),
                        padding=10
                    )
                ),
                
                # Aba 3: Tendências
                ft.Tab(
                    text="Tendências",
                    icon=ft.icons.SHOW_CHART,
                    content=ft.Container(
                        content=ft.Column([
                            # Análise Temporal
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("📈 Análise Temporal", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Arquivos analisados por período de modificação:"),
                                    *([criar_linha_tempo(mes, arquivos_por_mes[mes], max(arquivos_por_mes.values())) 
                                      for mes in meses_ordenados[-6:]] if meses_ordenados else [ft.Text("Sem dados temporais disponíveis")])
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10
                            ),
                            
                            # Previsões
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("🔮 Previsões", size=18, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Taxa de crescimento recente: {taxa_crescimento:.1f}% por mês"),
                                    ft.Text(f"Previsão de tamanho em 6 meses: {formatar_tamanho(previsao_tamanho_6meses)}"),
                                    ft.Text(f"Previsão de arquivos em 6 meses: {round(total_arquivos * (1 + taxa_crescimento/100))} arquivos" if taxa_crescimento > 0 else "Sem crescimento significativo recente")
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10,
                                margin=ft.margin.only(top=10)
                            ),
                            
                            # Histórico de tamanho
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("💾 Evolução de Armazenamento", size=18, weight=ft.FontWeight.BOLD),
                                    *([criar_barra_tempo(mes, tamanho_por_mes[mes], max(tamanho_por_mes.values())) 
                                      for mes in meses_ordenados[-6:]] if meses_ordenados else [ft.Text("Sem dados temporais disponíveis")])
                                ]),
                                padding=10,
                                bgcolor=Colors.BLUE_GREY_800,
                                border_radius=10,
                                margin=ft.margin.only(top=10)
                            )
                        ], scroll=ft.ScrollMode.AUTO),
                        padding=10
                    )
                )
            ]
        )
        
        # Mostra o diálogo com as estatísticas
        page.dialog = ft.AlertDialog(
            title=ft.Text("📊 Estatísticas da Pasta"), 
            content=ft.Container(
                content=tabs,
                width=700,
                height=500
            ),
            actions=[
                ft.TextButton("Fechar", on_click=lambda e: close_dlg(e, page))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.update()
    except Exception as e:
        # Em caso de erro, mostra mensagem simplificada
        page.dialog = ft.AlertDialog(
            title=ft.Text("⚠️ Erro"), 
            content=ft.Text(f"Erro ao gerar estatísticas: {str(e)}"),
            actions=[
                ft.TextButton("OK", on_click=lambda e: close_dlg(e, page))
            ]
        )
        page.dialog.open = True
        page.update()

def criar_barra_grafico(rotulo, valor, total):
    if total == 0:
        porcentagem = 0
    else:
        porcentagem = (valor / total) * 100
    
    # Determina a cor baseada no tipo
    cor = Colors.BLUE
    if "código" in rotulo.lower():
        cor = Colors.GREEN
    elif "imagem" in rotulo.lower():
        cor = Colors.PURPLE
    elif "documento" in rotulo.lower():
        cor = Colors.BLUE
    elif "áudio" in rotulo.lower():
        cor = Colors.PINK
    elif "vídeo" in rotulo.lower():
        cor = Colors.RED
    elif "compactado" in rotulo.lower():
        cor = Colors.AMBER
    
    return ft.Column([
        ft.Text(f"{rotulo}: {valor} ({porcentagem:.1f}%)"),
        ft.Container(
            content=ft.Container(
                bgcolor=cor,
                width=porcentagem * 2,  # Escala a barra para melhor visualização
                height=20,
                border_radius=ft.border_radius.all(5)
            ),
            bgcolor=Colors.BLUE_GREY_900,
            width=200,
            height=20,
            border_radius=ft.border_radius.all(5)
        )
    ])

def criar_linha_tempo(periodo, valor, max_valor):
    """Cria uma barra para visualização de dados temporais"""
    if max_valor == 0:
        porcentagem = 0
    else:
        porcentagem = (valor / max_valor) * 100
    
    # Converte o período para um nome mais amigável
    ano, mes = periodo.split("-")
    nomes_meses = {
        "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr", 
        "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
        "09": "Set", "10": "Out", "11": "Nov", "12": "Dez"
    }
    nome_mes = nomes_meses.get(mes, mes)
    periodo_formatado = f"{nome_mes}/{ano}"
    
    return ft.Row([
        ft.Container(
            content=ft.Text(periodo_formatado),
            width=60
        ),
        ft.Container(
            content=ft.Container(
                bgcolor=Colors.BLUE,
                width=porcentagem * 2,  # Escala a barra para melhor visualização
                height=20,
                border_radius=ft.border_radius.all(5),
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(right=5),
                content=ft.Text(f"{valor}", color=Colors.WHITE) if valor > 0 else None
            ),
            bgcolor=Colors.BLUE_GREY_900,
            width=200,
            height=20,
            border_radius=ft.border_radius.all(5)
        )
    ])

def criar_barra_tempo(periodo, valor, max_valor):
    """Cria uma barra para visualização de tamanho por período"""
    if max_valor == 0:
        porcentagem = 0
    else:
        porcentagem = (valor / max_valor) * 100
    
    # Converte o período para um nome mais amigável
    ano, mes = periodo.split("-")
    nomes_meses = {
        "01": "Jan", "02": "Fev", "03": "Mar", "04": "Abr", 
        "05": "Mai", "06": "Jun", "07": "Jul", "08": "Ago",
        "09": "Set", "10": "Out", "11": "Nov", "12": "Dez"
    }
    nome_mes = nomes_meses.get(mes, mes)
    periodo_formatado = f"{nome_mes}/{ano}"
    
    return ft.Row([
        ft.Container(
            content=ft.Text(periodo_formatado),
            width=60
        ),
        ft.Container(
            content=ft.Container(
                bgcolor=Colors.GREEN,
                width=porcentagem * 2,  # Escala a barra para melhor visualização
                height=20,
                border_radius=ft.border_radius.all(5),
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(right=5),
                content=ft.Text(formatar_tamanho(valor), color=Colors.WHITE) if valor > 0 else None
            ),
            bgcolor=Colors.BLUE_GREY_900,
            width=200,
            height=20,
            border_radius=ft.border_radius.all(5)
        )
    ])

def close_dlg(e, page):
    page.dialog.open = False
    page.update()
