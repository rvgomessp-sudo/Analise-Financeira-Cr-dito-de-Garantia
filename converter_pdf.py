#!/usr/bin/env python3
"""
Conversor de Markdown para PDF
"""

import markdown
from weasyprint import HTML, CSS
import os

# CSS para formatação profissional
CSS_STYLE = """
@page {
    size: A4;
    margin: 2cm;
    @top-right {
        content: counter(page);
    }
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    max-width: 100%;
}

h1 {
    color: #1a365d;
    font-size: 20pt;
    border-bottom: 3px solid #2c5282;
    padding-bottom: 10px;
    margin-top: 30px;
    page-break-after: avoid;
}

h2 {
    color: #2c5282;
    font-size: 16pt;
    border-bottom: 2px solid #4299e1;
    padding-bottom: 5px;
    margin-top: 25px;
    page-break-after: avoid;
}

h3 {
    color: #2b6cb0;
    font-size: 13pt;
    margin-top: 20px;
    page-break-after: avoid;
}

h4 {
    color: #3182ce;
    font-size: 12pt;
    margin-top: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th {
    background-color: #2c5282;
    color: white;
    padding: 10px 8px;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 8px;
    border: 1px solid #e2e8f0;
}

tr:nth-child(even) {
    background-color: #f7fafc;
}

tr:hover {
    background-color: #edf2f7;
}

blockquote {
    background-color: #ebf8ff;
    border-left: 4px solid #3182ce;
    padding: 15px 20px;
    margin: 20px 0;
    font-style: italic;
    color: #2c5282;
    page-break-inside: avoid;
}

code {
    background-color: #edf2f7;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 10pt;
}

pre {
    background-color: #1a202c;
    color: #e2e8f0;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.4;
    page-break-inside: avoid;
}

pre code {
    background-color: transparent;
    padding: 0;
    color: #e2e8f0;
}

hr {
    border: none;
    border-top: 2px solid #e2e8f0;
    margin: 30px 0;
}

ul, ol {
    margin-left: 20px;
}

li {
    margin-bottom: 5px;
}

strong {
    color: #1a365d;
}

a {
    color: #3182ce;
    text-decoration: none;
}

.page-break {
    page-break-before: always;
}

/* Destaque para conclusões */
h2:contains("CONCLUS") + * {
    background-color: #f0fff4;
    padding: 15px;
    border-left: 4px solid #38a169;
}
"""

def convert_md_to_pdf(md_file, pdf_file):
    """Converte arquivo Markdown para PDF"""

    # Ler arquivo Markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Converter Markdown para HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br'
        ]
    )

    # Criar HTML completo
    full_html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Documento</title>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Converter para PDF
    html = HTML(string=full_html)
    css = CSS(string=CSS_STYLE)
    html.write_pdf(pdf_file, stylesheets=[css])

    print(f"✓ Convertido: {md_file} -> {pdf_file}")

def main():
    base_dir = "/home/user/Analise-Financeira-Cr-dito-de-Garantia"

    arquivos = [
        ("PESQUISA_RATING_LICITACOES_BRASIL.md", "PESQUISA_RATING_LICITACOES_BRASIL.pdf"),
        ("CSC_SEGURADORAS_GLOBAIS.md", "CSC_SEGURADORAS_GLOBAIS.pdf"),
        ("ARGUMENTACAO_RATING_ZURICH.md", "ARGUMENTACAO_RATING_ZURICH.pdf"),
    ]

    print("Convertendo arquivos Markdown para PDF...\n")

    for md_file, pdf_file in arquivos:
        md_path = os.path.join(base_dir, md_file)
        pdf_path = os.path.join(base_dir, pdf_file)

        if os.path.exists(md_path):
            try:
                convert_md_to_pdf(md_path, pdf_path)
            except Exception as e:
                print(f"✗ Erro ao converter {md_file}: {e}")
        else:
            print(f"✗ Arquivo não encontrado: {md_file}")

    print("\nConversão concluída!")

if __name__ == "__main__":
    main()
