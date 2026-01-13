#!/usr/bin/env python3
"""
Script para gerar PDF do Paper no padrão ABNT
Normas: NBR 14724 (Trabalhos acadêmicos) e NBR 6023 (Referências)

Autor: Rodrigo Vazquez - CORECON 32.884/SP
Produzido por: Vieira Mendonça Consultoria | Vazquez & Fonseca Corretora
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path


def gerar_pdf_abnt():
    """Converte o paper markdown para PDF no padrão ABNT"""

    # Caminhos
    arquivo_md = Path("PAPER_ABNT_FORCA_FINANCEIRA_ISOLADA.md")
    arquivo_pdf = Path("PAPER_ABNT_FORCA_FINANCEIRA_ISOLADA.pdf")

    # Lê o markdown
    with open(arquivo_md, 'r', encoding='utf-8') as f:
        conteudo_md = f.read()

    # Converte para HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    conteudo_html = md.convert(conteudo_md)

    # CSS padrão ABNT
    # - Margens: 3cm superior e esquerda, 2cm inferior e direita
    # - Fonte: Times New Roman ou Arial, 12pt
    # - Espaçamento: 1,5 entre linhas
    # - Recuo de parágrafo: 1,25cm
    css_abnt = """
    @page {
        size: A4;
        margin: 3cm 2cm 2cm 3cm;

        @bottom-center {
            content: counter(page);
            font-family: 'Times New Roman', 'DejaVu Serif', Georgia, serif;
            font-size: 12pt;
        }
    }

    @page :first {
        @bottom-center {
            content: none;
        }
    }

    body {
        font-family: 'Times New Roman', 'DejaVu Serif', Georgia, serif;
        font-size: 12pt;
        line-height: 1.5;
        color: #000;
        text-align: justify;
        hyphens: auto;
    }

    /* Título principal - capa */
    h1:first-of-type {
        text-align: center;
        font-size: 14pt;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 8cm;
        margin-bottom: 2cm;
        page-break-after: avoid;
    }

    /* Demais títulos de seção principal */
    h1 {
        font-size: 12pt;
        font-weight: bold;
        text-transform: uppercase;
        margin-top: 2cm;
        margin-bottom: 0.5cm;
        page-break-after: avoid;
        text-align: left;
    }

    /* Seções secundárias */
    h2 {
        font-size: 12pt;
        font-weight: bold;
        margin-top: 1.5cm;
        margin-bottom: 0.5cm;
        page-break-after: avoid;
        text-align: left;
    }

    /* Seções terciárias */
    h3 {
        font-size: 12pt;
        font-weight: bold;
        margin-top: 1cm;
        margin-bottom: 0.5cm;
        page-break-after: avoid;
        text-align: left;
    }

    /* Seções quaternárias */
    h4 {
        font-size: 12pt;
        font-weight: normal;
        font-style: italic;
        margin-top: 0.8cm;
        margin-bottom: 0.3cm;
        page-break-after: avoid;
    }

    /* Parágrafos - recuo de 1,25cm na primeira linha */
    p {
        margin-bottom: 0;
        margin-top: 0;
        text-indent: 1.25cm;
    }

    /* Parágrafos após títulos não têm recuo */
    h1 + p, h2 + p, h3 + p, h4 + p {
        text-indent: 0;
    }

    /* Separador horizontal - usado entre seções */
    hr {
        border: none;
        border-top: 1px solid #000;
        margin: 1cm 0;
        page-break-after: always;
    }

    /* Primeira hr (após título) - quebra de página para folha de rosto */
    hr:first-of-type {
        border: none;
        margin: 0;
    }

    /* Tabelas e Quadros - ABNT */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.5cm 0;
        font-size: 11pt;
        page-break-inside: avoid;
    }

    th {
        background-color: #f0f0f0;
        padding: 8px;
        text-align: left;
        font-weight: bold;
        border-top: 2px solid #000;
        border-bottom: 1px solid #000;
    }

    td {
        padding: 6px 8px;
        border-bottom: 1px solid #ccc;
        vertical-align: top;
    }

    /* Última linha da tabela */
    tr:last-child td {
        border-bottom: 2px solid #000;
    }

    /* Código */
    code {
        font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
        font-size: 10pt;
        background-color: #f5f5f5;
        padding: 2px 4px;
    }

    pre {
        background-color: #f5f5f5;
        padding: 10px;
        font-size: 10pt;
        line-height: 1.3;
        margin: 0.5cm 0;
        page-break-inside: avoid;
        border: 1px solid #ddd;
    }

    pre code {
        background-color: transparent;
        padding: 0;
    }

    /* Citações - recuo de 4cm, fonte 10pt, espaçamento simples */
    blockquote {
        margin: 0.5cm 0 0.5cm 4cm;
        font-size: 10pt;
        line-height: 1.0;
        text-align: justify;
    }

    /* Listas */
    ul, ol {
        margin: 0.3cm 0 0.3cm 1.25cm;
        padding-left: 0.5cm;
    }

    li {
        margin-bottom: 0.2cm;
        text-align: justify;
    }

    /* Lista com letras (alíneas) - padrão ABNT */
    ol[type="a"], ul {
        list-style-type: lower-alpha;
    }

    /* Negrito e itálico */
    strong {
        font-weight: bold;
    }

    em {
        font-style: italic;
    }

    /* Evitar quebras de página indesejadas */
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
        page-break-inside: avoid;
    }

    table, pre, blockquote {
        page-break-inside: avoid;
    }

    /* Referências - espaçamento simples, alinhado à esquerda */
    h2:contains("REFERÊNCIAS") + p,
    h2:contains("REFERÊNCIAS") ~ p {
        text-indent: 0;
        text-align: left;
        margin-bottom: 0.5cm;
        line-height: 1.0;
    }

    /* Notas de rodapé */
    .footnote {
        font-size: 10pt;
        line-height: 1.0;
    }

    /* Capa - centralização dos elementos iniciais */
    body > p:first-of-type,
    body > p:nth-of-type(2),
    body > p:nth-of-type(3) {
        text-align: center;
        text-indent: 0;
    }
    """

    # HTML completo
    html_completo = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Paper ABNT - Força Financeira Isolada de Seguradoras</title>
    </head>
    <body>
        {conteudo_html}
    </body>
    </html>
    """

    # Gera o PDF
    print("=" * 60)
    print("GERAÇÃO DE PDF - PADRÃO ABNT")
    print("=" * 60)
    print()
    print("Autor: Rodrigo Vazquez - CORECON 32.884/SP")
    print("Produção: Vieira Mendonça Consultoria | Vazquez & Fonseca Corretora")
    print()
    print("Configurações ABNT:")
    print("  - Margens: 3cm (sup/esq), 2cm (inf/dir)")
    print("  - Fonte: Times New Roman, 12pt")
    print("  - Espaçamento: 1,5 entre linhas")
    print("  - Recuo: 1,25cm na primeira linha")
    print()
    print("Gerando PDF...")

    HTML(string=html_completo).write_pdf(
        arquivo_pdf,
        stylesheets=[CSS(string=css_abnt)]
    )

    tamanho = arquivo_pdf.stat().st_size / 1024
    print()
    print(f"PDF gerado com sucesso!")
    print(f"Arquivo: {arquivo_pdf}")
    print(f"Tamanho: {tamanho:.1f} KB")
    print()
    print("=" * 60)

    return str(arquivo_pdf)


if __name__ == "__main__":
    gerar_pdf_abnt()
