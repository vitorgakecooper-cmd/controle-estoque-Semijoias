import re
from io import BytesIO

import pandas as pd
import pdfplumber
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Controle de Semijoias",
    page_icon="💎",
    layout="wide"
)
def carregar_css():
    caminho_css = Path(__file__).parent / "frontend" / "estilo.css"

    with open(caminho_css, encoding="utf-8") as arquivo:
        css = arquivo.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )


carregar_css()
st.markdown("""
    <div class="cabecalho-rosalia">
        <h1>ROSALIA</h1>
        <div class="subtitulo-marca">SEMIJÓIAS</div>
        <div class="linha-dourada"></div>
        <p>Sistema de recebimento e conferência de mercadorias</p>
    </div>
""", unsafe_allow_html=True)


def converter_valor(valor):
    """Converte um valor brasileiro, como 10,18, para número."""
    valor = valor.strip().replace("R$", "").strip()
    valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except ValueError:
        return 0.0


def gerar_excel(df):
    """Cria um arquivo Excel com os produtos extraídos."""
    arquivo_excel = BytesIO()

    with pd.ExcelWriter(
        arquivo_excel,
        engine="openpyxl"
    ) as escritor:
        df.to_excel(
            escritor,
            index=False,
            sheet_name="Produtos"
        )

    arquivo_excel.seek(0)
    return arquivo_excel.getvalue()


def extrair_texto_pdf(arquivo):
    """Extrai o texto de todas as páginas do PDF."""
    textos = []

    arquivo.seek(0)

    with pdfplumber.open(arquivo) as pdf:
        for numero, pagina in enumerate(pdf.pages, start=1):
            texto = pagina.extract_text()

            if texto:
                textos.append(texto)

    return "\n".join(textos)

def identificar_produtos(texto):
    produtos = []

    categorias = [
        "PULSEIRAS",
        "COLARES",
        "BRINCOS",
        "ANÉIS",
        "PINGENTES"
    ]

    padrao_categoria = re.compile(
        r"(?im)^\s*(" + "|".join(categorias) + r")\s*$"
    )

    marcadores = list(padrao_categoria.finditer(texto))

    for i, marcador in enumerate(marcadores):

        categoria = marcador.group(1).title()
        inicio = marcador.end()

        fim = (
            marcadores[i + 1].start()
            if i + 1 < len(marcadores)
            else len(texto)
        )

        bloco = texto[inicio:fim]

        codigo_match = re.search(
            r"\b([A-Z]{2}\d{3,})\b",
            bloco
        )

        if not codigo_match:
            continue

        codigo = codigo_match.group(1)

        pesos = re.findall(
            r"(\d+[,.]\d+)\s*g",
            bloco,
            re.IGNORECASE
        )

        quantidade_match = re.search(
            r"\d+[,.]\d+\s*g\s+"
            r"\d+[,.]\d+\s*g\s+"
            r"(\d+)\s+R\$",
            bloco,
            re.IGNORECASE
        )

        valores = re.findall(
            r"R\$\s*([\d.]+,\d{2})",
            bloco
        )

        cor_match = re.search(
    r"Cor:\s*(.*?)\s+(?=\d+[,.]\d+\s*g)",
    bloco,
    re.IGNORECASE
)
        tamanho_match = re.search(r"Tamanho:\s*([^\n]+)", bloco)
        referencia_match = re.search(r"Ref\.:\s*([^\n]+)", bloco)

        cor = cor_match.group(1).strip() if cor_match else ""
        tamanho = tamanho_match.group(1).strip() if tamanho_match else ""
        referencia = referencia_match.group(1).strip() if referencia_match else ""

        linhas_nome = []

        for linha in bloco.splitlines():

            if "Observações:" in linha:
                break

            if any(item in linha for item in [
                "ROMANEIO DE MERCADORIAS",
                "Documento fictício",
                "Fornecedor:",
                "Peso UN",
                "Itens:",
                "S E M I J O I A S"
            ]):
                continue

            linha = re.sub(r"\bFOTO\b", "", linha, flags=re.IGNORECASE)
            linha = re.sub(r"\b" + re.escape(codigo) + r"\b", "", linha)
            linha = re.sub(r"\bREBANHO\b", "", linha)

            linha = re.sub(
                r"Cor:\s*[A-Za-zÀ-ÿ]+",
                "",
                linha,
                flags=re.IGNORECASE
            )

            linha = re.sub(r"Tamanho:.*", "", linha, flags=re.IGNORECASE)
            linha = re.sub(r"Ref\.:.*", "", linha, flags=re.IGNORECASE)
            linha = re.sub(r"\d+[,.]\d+\s*g", "", linha, flags=re.IGNORECASE)
            linha = re.sub(r"R\$\s*[\d.]+,\d{2}", "", linha)
            linha = re.sub(r"\b\d+\s*$", "", linha)

            linha = " ".join(linha.split()).strip()

            if linha:
                linhas_nome.append(linha)

        nome = " ".join(linhas_nome).strip()

        peso_unitario = converter_valor(pesos[0]) if len(pesos) >= 1 else None
        peso_total = converter_valor(pesos[1]) if len(pesos) >= 2 else None

        quantidade = int(quantidade_match.group(1)) if quantidade_match else None

        preco_bruto = converter_valor(valores[0]) if len(valores) >= 1 else None
        preco_banho = converter_valor(valores[1]) if len(valores) >= 2 else None
        valor_aproximado = converter_valor(valores[2]) if len(valores) >= 3 else None

        custo_unitario = (
            preco_bruto + preco_banho
            if preco_bruto is not None and preco_banho is not None
            else None
        )

        problemas = []

        if not nome:
            problemas.append("Nome não identificado")

        if not quantidade:
            problemas.append("Quantidade não identificada")

        if len(valores) < 2:
            problemas.append("Valores incompletos")

        produtos.append({
            "codigo_romaneio": codigo,
            "nome": nome,
            "categoria": categoria,
            "fornecedor": "REBANHO",
            "cor": cor,
            "tamanho": tamanho,
            "referencia": referencia,
            "peso_unitario_g": peso_unitario,
            "peso_total_g": peso_total,
            "quantidade": quantidade,
            "preco_bruto": preco_bruto,
            "preco_banho": preco_banho,
            "custo_unitario": custo_unitario,
            "valor_aproximado": valor_aproximado,
            "preco_venda": None,
            "problemas": "; ".join(problemas)
        })

    return pd.DataFrame(produtos)


# IMPORTAÇÃO DO PDF
arquivo = st.file_uploader(
    "Selecione o PDF do romaneio",
    type=["pdf"]
)

if arquivo is not None:

    try:
        with st.spinner("Lendo o PDF..."):

            texto = extrair_texto_pdf(arquivo)

        if not texto.strip():

            st.warning(
                "Não foi possível extrair texto deste PDF. "
                "Ele pode conter páginas digitalizadas como imagens."
            )

        else:

            st.success("Texto extraído do PDF.")

            with st.expander("Visualizar texto extraído"):
                st.text(texto)

            df = identificar_produtos(texto)

            if df.empty:

                st.warning(
                    "O texto foi extraído, mas nenhum produto foi identificado."
                )

            else:

                           # INDICADORES DO ROMANEIO

                unidades = pd.to_numeric(
                    df["quantidade"], errors="coerce"
                ).fillna(0).sum()

                total_bruto = pd.to_numeric(
                    df["preco_bruto"], errors="coerce"
                ).fillna(0).sum()

                total_banho = pd.to_numeric(
                    df["preco_banho"], errors="coerce"
                ).fillna(0).sum()

                total_custo = total_bruto + total_banho

                # Formatação dos valores
                bruto_formatado = f"R$ {total_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                banho_formatado = f"R$ {total_banho:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                custo_formatado = f"R$ {total_custo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                # Primeira linha
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Produtos identificados", len(df))

                with col2:
                    st.metric("Unidades recebidas", int(unidades))

                with col3:
                    st.metric("Custo total", custo_formatado)

                # Segunda linha
                col4, col5 = st.columns(2)

                with col4:
                    st.metric("Total do preço bruto", bruto_formatado)

                with col5:
                    st.metric("Total do preço do banho", banho_formatado)

                st.divider()

                # TABELA DE PRODUTOS

                st.subheader("Produtos identificados")

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                # EXPORTAÇÃO EXCEL

                st.download_button(
                    label="Baixar Excel",
                    data=gerar_excel(df),
                    file_name="produtos_semijoias.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
                )

    except Exception as erro:

        st.error(f"Erro ao processar o PDF: {erro}")