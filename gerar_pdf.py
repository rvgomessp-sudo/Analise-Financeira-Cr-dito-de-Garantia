#!/usr/bin/env python3
"""
Script para gerar PDF do Paper de Força Financeira Isolada
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path


def gerar_pdf():
    """Converte o paper markdown para PDF"""

    # Caminhos
    arquivo_md = Path("PAPER_FORCA_FINANCEIRA_ISOLADA.md")
    arquivo_pdf = Path("PAPER_FORCA_FINANCEIRA_ISOLADA.pdf")

    # Lê o markdown
    with open(arquivo_md, 'r', encoding='utf-8') as f:
        conteudo_md = f.read()

    # Converte para HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    conteudo_html = md.convert(conteudo_md)

    # CSS para formatação profissional
    css = """
    @page {
        size: A4;
        margin: 2.5cm 2cm 2.5cm 2cm;
        @top-center {
            content: "Força Financeira Isolada de Seguradoras";
            font-size: 9pt;
            color: #666;
        }
        @bottom-center {
            content: "Página " counter(page) " de " counter(pages);
            font-size: 9pt;
            color: #666;
        }
    }

    body {
        font-family: 'DejaVu Sans', 'Helvetica', 'Arial', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        text-align: justify;
    }

    h1 {
        font-size: 18pt;
        color: #1a365d;
        border-bottom: 3px solid #2b6cb0;
        padding-bottom: 10px;
        margin-top: 30px;
        margin-bottom: 20px;
        page-break-after: avoid;
    }

    h2 {
        font-size: 14pt;
        color: #2c5282;
        border-bottom: 1px solid #bee3f8;
        padding-bottom: 5px;
        margin-top: 25px;
        margin-bottom: 15px;
        page-break-after: avoid;
    }

    h3 {
        font-size: 12pt;
        color: #2b6cb0;
        margin-top: 20px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }

    h4 {
        font-size: 11pt;
        color: #4a5568;
        margin-top: 15px;
        margin-bottom: 8px;
    }

    p {
        margin-bottom: 12px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 10pt;
        page-break-inside: avoid;
    }

    th {
        background-color: #2b6cb0;
        color: white;
        padding: 10px 8px;
        text-align: left;
        font-weight: bold;
        border: 1px solid #2c5282;
    }

    td {
        padding: 8px;
        border: 1px solid #e2e8f0;
        vertical-align: top;
    }

    tr:nth-child(even) {
        background-color: #f7fafc;
    }

    tr:hover {
        background-color: #edf2f7;
    }

    code {
        font-family: 'DejaVu Sans Mono', 'Courier New', monospace;
        background-color: #f1f5f9;
        padding: 2px 5px;
        border-radius: 3px;
        font-size: 9pt;
    }

    pre {
        background-color: #1e293b;
        color: #e2e8f0;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
        font-size: 9pt;
        line-height: 1.4;
        margin: 15px 0;
        page-break-inside: avoid;
    }

    pre code {
        background-color: transparent;
        padding: 0;
        color: #e2e8f0;
    }

    blockquote {
        border-left: 4px solid #2b6cb0;
        margin: 15px 0;
        padding: 10px 20px;
        background-color: #ebf8ff;
        font-style: italic;
    }

    strong {
        color: #1a202c;
    }

    ul, ol {
        margin: 10px 0;
        padding-left: 25px;
    }

    li {
        margin-bottom: 5px;
    }

    hr {
        border: none;
        border-top: 2px solid #e2e8f0;
        margin: 30px 0;
    }

    /* Destaque para valores críticos */
    td strong {
        color: #c53030;
    }

    /* Cabeçalho do documento */
    body > h1:first-child {
        text-align: center;
        font-size: 22pt;
        border-bottom: none;
        margin-bottom: 5px;
    }

    /* Evitar quebras de página indesejadas */
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }

    table, pre, blockquote {
        page-break-inside: avoid;
    }
    """

    # HTML completo
    html_completo = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Paper - Força Financeira Isolada de Seguradoras</title>
    </head>
    <body>
        {conteudo_html}
    </body>
    </html>
    """

    # Gera o PDF
    print("Gerando PDF...")
    HTML(string=html_completo).write_pdf(
        arquivo_pdf,
        stylesheets=[CSS(string=css)]
    )

    print(f"PDF gerado com sucesso: {arquivo_pdf}")
    print(f"Tamanho: {arquivo_pdf.stat().st_size / 1024:.1f} KB")

    return str(arquivo_pdf)


if __name__ == "__main__":
    gerar_pdf()
