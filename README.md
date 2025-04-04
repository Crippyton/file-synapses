# 📁 Visualizador de Estrutura de Pastas

---
Aplicação Python com interface gráfica feita em **Flet**, que permite visualizar, navegar, exportar e analisar a estrutura de diretórios do sistema de forma prática e moderna.

---

## 🚀 Funcionalidades

- 📂 Seleção interativa de pastas
- 🧭 Visualização hierárquica com árvore colapsável
- 🔍 Busca por arquivos/pastas
- 📄 Exportação:
  - `.txt`
  - `.pdf`
  - `.md`
  - `.json`
- 📦 Compactação em `.zip`
- 📊 Geração de relatório com estatísticas:
  - Número de arquivos e pastas
  - Tamanho total (em MB)
  - Extensões mais comuns
- 🧠 Preferências salvas automaticamente
- 🌑 Tema escuro ativado por padrão

---

## 🖥️ Interface

> Adicione aqui uma imagem da interface renderizada

---

## ▶️ Como Executar

```bash
pip install flet fpdf
python app.py
```

## 📂 Estrutura de Projeto

📁 projeto/
├── app.py
├── utils/
│   ├── explorer.py
│   ├── exporter.py
│   ├── stats.py
│   ├── config.py
│   └── zipping.py
└── assets/
    └── config.json

## 🤝 Contribuições

Sinta-se livre para contribuir com novas ideias, melhorias ou correções!
