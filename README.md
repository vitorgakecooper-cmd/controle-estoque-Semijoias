# 💎 Controle de Estoque de Semijoias

Sistema desenvolvido em Python para auxiliar no controle e gerenciamento de estoque de semijoias.

## 🎯 Objetivo

Automatizar parte do processo de cadastro de produtos, reduzindo tarefas manuais e facilitando a organização das informações recebidas em romaneios de mercadorias.

## ⚙️ Funcionalidades

- Importação de romaneios em PDF.
- Extração e identificação de informações dos produtos.
- Organização dos dados em tabelas.
- Separação dos custos de preço bruto e banho.
- Exportação de dados para Excel.
- Visualização das informações do estoque.

## 🛠️ Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Pdfplumber
- Openpyxl
- HTML
- CSS

## 📁 Estrutura do projeto

```text
Pasta.Projeto Semijóias/
│
├── backend/
│
├── frontend/
│   ├── componentes.py
│   ├── estilo.css
│   ├── index.html
│   └── requirements.txt
│
├── app.py
├── README.md
└── .gitignore
```

## ▶️ Como executar

1. Clone o repositório.
2. Entre na pasta do projeto.
3. Crie um ambiente virtual.
4. Instale as dependências:

```bash
pip install -r frontend/requirements.txt
```

5. Execute a aplicação:

```bash
streamlit run app.py
```

## 🚧 Status

Projeto em desenvolvimento.