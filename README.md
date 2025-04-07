# File Synapses 📂

Um visualizador e gerenciador de estrutura de pastas desenvolvido com Python e Flet.

## Funcionalidades

- 🔍 Visualização dinâmica da estrutura de pastas
- 📃 Exportação em diferentes formatos (TXT, PDF, Markdown, JSON)
- 📊 Estatísticas de arquivos e pastas
- 🗜️ Compactação de pastas em ZIP
- 🌓 Modo escuro/claro
- 🔎 Busca de arquivos/pastas

## Requisitos

- Python 3.8+
- Dependências: flet, fpdf

## Instalação

1. Clone o repositório
   ```
   git clone https://github.com/seuusuario/file-synapses.git
   cd file-synapses
   ```

2. Instale as dependências
   ```
   pip install flet fpdf
   ```

3. Execute o aplicativo
   ```
   python app.py
   ```

## Estrutura do Projeto

- `app.py`: Aplicativo principal
- `utils/`: Módulos de utilidades
  - `explorer.py`: Funções de exploração de pastas
  - `exporter.py`: Funções de exportação
  - `stats.py`: Geração de estatísticas
  - `zipping.py`: Funções de compactação
  - `config.py`: Gerenciamento de configurações
- `assets/`: Arquivos de recursos
  - `config.json`: Arquivo de configuração

## Funcionalidades em Detalhe

### Visualização de Estrutura
O aplicativo mostra a estrutura de pastas de forma hierárquica, com ícones diferentes para cada tipo de arquivo.

### Exportação
- **TXT**: Exporta a estrutura em formato de texto
- **PDF**: Cria um documento PDF com a estrutura
- **Markdown**: Exporta em formato Markdown para documentação
- **JSON**: Exporta a estrutura em formato JSON para integração com outros sistemas

### Estatísticas
Gera estatísticas da pasta selecionada, incluindo:
- Total de arquivos
- Total de pastas
- Tamanho total
- Tipos de arquivos mais comuns

### Compactação
Permite compactar a pasta selecionada em um arquivo ZIP.

## Licença
MIT
