#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera o estudo técnico (identidade Vieira Mendonça) sobre o rating da Zurich no CC17/2025.
Requer: pip install reportlab pillow
Fontes e brasão: pasta marca/ (Cormorant Garamond, Inter, brasão sobre grafite).
"""

import os
from datetime import date

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

from analise_completa_rating_cc17_2025 import (
    ART_23, EXIGENCIA_EDITAL, JUNTO, RATINGS_ZURICH_CARTA, TABELA_MOODYS_2020,
    TABELA_SP_2023, ZURICH_MINAS, _br, brl_mi, exposicao_sobre_pl, margem_de_seguranca,
)

SAIDA = "ESTUDO_RATING_ZURICH_CC17_2025.pdf"
MARCA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marca")

GRAFITE = HexColor("#14110f")
GRAFITE_ELEV = HexColor("#1e1a16")
TINTA = HexColor("#f4efe6")
ROSE = HexColor("#c8976f")
ROSE_FORTE = HexColor("#d8ad86")
ROSE_SUAVE = HexColor("#5c4330")
PEDRA = HexColor("#f3ede3")
PEDRA_RECUADA = HexColor("#eae2d4")
FILETE = HexColor("#c0b49f")
TEXTO = HexColor("#2a2420")
TEXTO_SUAVE = HexColor("#6b6158")

for nome, arq in [("Cormorant", "CormorantGaramond-500.ttf"), ("Cormorant-SB", "CormorantGaramond-600.ttf"),
                  ("Cormorant-It", "CormorantGaramond-500i.ttf"), ("Inter", "Inter-400.ttf"),
                  ("Inter-SB", "Inter-600.ttf")]:
    pdfmetrics.registerFont(TTFont(nome, os.path.join(MARCA, "fonts", arq)))
pdfmetrics.registerFontFamily("Inter", normal="Inter", bold="Inter-SB", italic="Inter", boldItalic="Inter-SB")
pdfmetrics.registerFontFamily("Cormorant", normal="Cormorant", bold="Cormorant-SB", italic="Cormorant-It",
                              boldItalic="Cormorant-SB")

ROTULO = ParagraphStyle("rotulo", fontName="Inter-SB", fontSize=7.6, leading=10, textColor=ROSE,
                        spaceBefore=16, spaceAfter=2)
H1 = ParagraphStyle("h1", fontName="Cormorant-SB", fontSize=21, leading=24, textColor=GRAFITE, spaceAfter=8)
H2 = ParagraphStyle("h2", fontName="Cormorant-SB", fontSize=14, leading=17, textColor=GRAFITE,
                    spaceBefore=8, spaceAfter=4)
P = ParagraphStyle("p", fontName="Inter", fontSize=9.2, leading=13.6, textColor=TEXTO, alignment=TA_JUSTIFY,
                   spaceAfter=6)
P_ITEM = ParagraphStyle("item", parent=P, leftIndent=12, bulletIndent=0, spaceAfter=4)
CITA = ParagraphStyle("cita", fontName="Cormorant-It", fontSize=11.5, leading=15, textColor=TEXTO,
                      leftIndent=14, rightIndent=8, spaceBefore=4, spaceAfter=10, borderPadding=(6, 8, 6, 10),
                      backColor=PEDRA_RECUADA)
NOTA = ParagraphStyle("nota", fontName="Inter", fontSize=7.6, leading=10.5, textColor=TEXTO_SUAVE, spaceAfter=4)
CEL = ParagraphStyle("cel", fontName="Inter", fontSize=8.2, leading=11, textColor=TEXTO)
CEL_CAB = ParagraphStyle("celcab", fontName="Inter-SB", fontSize=7.8, leading=10.5, textColor=TINTA)
FAIXA = ParagraphStyle("faixa", fontName="Cormorant-It", fontSize=13, leading=17, textColor=TINTA,
                       alignment=TA_LEFT)


OBJECOES = [
    ("“A subsidiária brasileira não tem rating próprio.”",
     "O edital não exige rating emitido para a subsidiária, e sim nota igual ou superior ao patamar na escala "
     "nacional. As agências derivam a nota nacional da global e atribuem à subsidiária core a nota do grupo. A "
     "Zurich Minas é controlada diretamente pela entidade classificada, e a Zurich declarou por escrito que a "
     "aferição se faz pela equivalência técnica, sem necessidade de nota específica da subsidiária."),
    ("“Rating global não é rating em escala nacional.”",
     "A escala nacional é obtida a partir da global pelas tabelas oficiais (seção 3). Aplicadas à Zurich, "
     "resultam na nota máxima nacional, brAAA / Aaa.br. Além disso, brAAA é o teto da escala: a única forma de "
     "demonstrar qualidade superior a ele é a escala global, que o próprio edital admite ao falar em "
     "“igual ou superior”."),
    ("“As notas citadas pela Zurich diferem das publicadas.”",
     "A carta de 18/12/2025 cita S&amp;P AA-, Moody's Aa3 e Fitch AA-; a página oficial de RI registra S&amp;P AA "
     "e Moody's Aa2, após elevações (a da Moody's em setembro de 2024). Em qualquer das duas séries a folga sobre "
     "o patamar do edital é de 9 a 11 degraus."),
    ("“A S&amp;P mudou sua estrutura no Brasil em 2025.”",
     "A mudança é organizacional (S&amp;P National Ratings, desde 18/08/2025). Nenhuma recalibração pode levar o "
     "patamar brAA- para acima de AA na escala global num país cujo soberano é BB (seção 3.6)."),
    ("“A Junto tem melhor índice de solvência.”",
     "O índice PLA/CMR mede folga relativa ao próprio risco. Em capacidade absoluta, que é o que protege o Estado "
     "num contrato de R$ 1 bilhão, a Zurich Minas tem patrimônio 8,6 vezes maior e o respaldo de um grupo AA."),
]


def rotulo(texto):
    palavras = ["&nbsp;".join(p) for p in texto.upper().split()]
    return Paragraph("&nbsp;&nbsp;&nbsp;".join(palavras), ROTULO)


def tabela(linhas, larguras, destaque=None):
    dados = [[Paragraph(str(c), CEL_CAB if i == 0 else CEL) for c in row] for i, row in enumerate(linhas)]
    t = Table(dados, colWidths=larguras, repeatRows=1)
    estilo = [("BACKGROUND", (0, 0), (-1, 0), GRAFITE_ELEV),
              ("LINEBELOW", (0, 0), (-1, -1), 0.4, FILETE),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
              ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
              ("LEFTPADDING", (0, 0), (-1, -1), 6)]
    for r in range(1, len(linhas)):
        if r % 2 == 0:
            estilo.append(("BACKGROUND", (0, r), (-1, r), PEDRA_RECUADA))
    if destaque is not None:
        estilo.append(("BACKGROUND", (0, destaque), (-1, destaque), HexColor("#ead7c4")))
    t.setStyle(TableStyle(estilo))
    return t


def faixa(texto):
    t = Table([[Paragraph(texto, FAIXA)]], colWidths=[17 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ROSE_SUAVE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                           ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    return t


def texto_espacado(c, x, y, texto, fonte, tam, cor, espaco, centro=True):
    c.saveState()
    c.setFillColor(cor)
    largura = pdfmetrics.stringWidth(texto, fonte, tam) + espaco * (len(texto) - 1)
    inicio = x - largura / 2 if centro else x
    obj = c.beginText(inicio, y)
    obj.setFont(fonte, tam)
    obj.setCharSpace(espaco)
    obj.textLine(texto)
    c.drawText(obj)
    c.restoreState()


def capa(c, doc):
    w, h = A4
    c.saveState()
    c.setFillColor(GRAFITE)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    texto_espacado(c, w / 2, h - 2.6 * cm, "GRUPO VAZQUEZ & FONSECA", "Inter-SB", 7.5, TEXTO_SUAVE, 2.4)
    c.drawImage(os.path.join(MARCA, "brasao_grafite.png"), w / 2 - 3.2 * cm, h - 10.6 * cm,
                width=6.4 * cm, height=6.26 * cm, mask="auto")
    texto_espacado(c, w / 2, h - 12.2 * cm, "VIEIRA MENDONÇA", "Cormorant-SB", 26, TINTA, 2.2)
    texto_espacado(c, w / 2, h - 13.0 * cm, "CONSULTORIA EM SEGUROS E GARANTIAS", "Inter", 7.8, ROSE, 2.6)
    c.setStrokeColor(ROSE)
    c.setLineWidth(0.6)
    c.line(w / 2 - 1.6 * cm, h - 13.8 * cm, w / 2 + 1.6 * cm, h - 13.8 * cm)

    texto_espacado(c, w / 2, h - 16.0 * cm, "ESTUDO TÉCNICO", "Inter-SB", 8, ROSE, 3)
    c.setFillColor(TINTA)
    c.setFont("Cormorant-SB", 24)
    c.drawCentredString(w / 2, h - 17.4 * cm, "A Zurich atende ao requisito")
    c.drawCentredString(w / 2, h - 18.4 * cm, "de rating do edital CC17/2025")
    c.setFont("Cormorant-It", 13)
    c.setFillColor(ROSE_FORTE)
    c.drawCentredString(w / 2, h - 19.5 * cm, "Conversão oficial de escalas, autorização SUSEP e unidade com o grupo")

    c.setFont("Inter", 8.2)
    c.setFillColor(TEXTO_SUAVE)
    c.drawCentredString(w / 2, 4.0 * cm, "Certame CC17/2025 · Centro de Serviços Compartilhados / SEAP Amazonas")
    c.drawCentredString(w / 2, 3.5 * cm, "Cogestão do sistema prisional · valor de referência R$ 1 bilhão")
    c.drawCentredString(w / 2, 2.4 * cm, f"São Paulo, {date.today().strftime('%d/%m/%Y')}")
    c.setFont("Inter", 6.8)
    c.drawCentredString(w / 2, 1.5 * cm, "Vieira Mendonça Consultoria em Seguros Ltda. · CNPJ 59.622.302/0001-44")
    c.restoreState()


def interna(c, doc):
    w, h = A4
    c.saveState()
    c.setFillColor(PEDRA)
    c.rect(0, 0, w, h, stroke=0, fill=1)
    texto_espacado(c, 2 * cm, h - 1.35 * cm, "VIEIRA MENDONÇA", "Cormorant-SB", 9.5, GRAFITE, 1.4, centro=False)
    c.setFont("Inter", 7)
    c.setFillColor(TEXTO_SUAVE)
    c.drawRightString(w - 2 * cm, h - 1.35 * cm, "Estudo técnico · rating Zurich · CC17/2025")
    c.setStrokeColor(FILETE)
    c.setLineWidth(0.4)
    c.line(2 * cm, h - 1.6 * cm, w - 2 * cm, h - 1.6 * cm)
    c.line(2 * cm, 1.55 * cm, w - 2 * cm, 1.55 * cm)
    c.drawString(2 * cm, 1.05 * cm, "Estratégia para o seu amanhã")
    c.setFillColor(ROSE)
    c.setFont("Inter-SB", 7)
    c.drawRightString(w - 2 * cm, 1.05 * cm, f"{doc.page - 1:02d}")
    c.restoreState()


def corpo():
    s = []
    margem = margem_de_seguranca()
    exig_sp, exig_fitch, exig_moodys = EXIGENCIA_EDITAL["S&P"], EXIGENCIA_EDITAL["Fitch"], EXIGENCIA_EDITAL["Moody's"]
    carta_sp, carta_moodys, carta_fitch = (RATINGS_ZURICH_CARTA["S&P"], RATINGS_ZURICH_CARTA["Moody's"],
                                           RATINGS_ZURICH_CARTA["Fitch"])

    # 1. Síntese
    s += [rotulo("Síntese da defesa"),
          Paragraph("A Zurich não só atende ao requisito de rating: ela o supera por dez degraus ou mais", H1),
          Paragraph(
              "A tese atribuída à RH Multi sustenta que a Zurich não atenderia ao edital porque seu rating é "
              "<b>global</b>, e não em <b>escala nacional</b>, e porque a subsidiária brasileira não teria nota "
              "própria. Os documentos oficiais das agências, da SUSEP e da própria Zurich mostram o contrário.", P)]
    for item in [
        f"<b>O patamar do edital é baixo na régua global.</b> {exig_sp} na S&amp;P equivale, pela tabela oficial, "
        f"a uma nota global a partir de <b>B+</b>; {exig_moodys} na Moody's, a partir de <b>Ba3</b>.",
        "<b>A Zurich está em AA (S&amp;P) e Aa2 (Moody's)</b>: 11 e 10 degraus acima desse patamar. "
        "Convertida pelas mesmas tabelas, sua nota é a máxima da escala nacional (brAAA / Aaa.br).",
        "<b>A emissora é brasileira e autorizada pela SUSEP</b> (Zurich Minas Brasil Seguros S.A., código 05495), "
        "com R$ 2,71 bilhões em ativos garantidores no país.",
        "<b>A controladora direta é a entidade classificada</b>: a Zurich Insurance Company Ltd detém 99,9999% "
        "da Zurich Minas, e a Zurich declarou por escrito o vínculo pleno com o grupo.",
        "<b>A tese excluiria também a Junto</b>, cujo rating é atribuído em conjunto com a resseguradora do grupo "
        "e apoiado na controladora Travelers.",
    ]:
        s.append(Paragraph(item, P_ITEM, bulletText="—"))
    s.append(Spacer(1, 8))
    s.append(faixa("Para a Zurich deixar de atender ao patamar do edital, sua nota global teria de cair "
                   "dez degraus: de AA para a faixa B, o grau especulativo."))

    # 2. O que o edital exige
    s += [rotulo("O requisito"), Paragraph("Três condições convergentes", H1),
          Paragraph(
              "A cláusula de garantia combina três condições, que devem ser lidas em conjunto e não "
              "isoladamente. A terceira define um <b>patamar de qualidade</b> e a <b>régua</b> em que ele é "
              "medido; não exige que a nota tenha sido emitida no Brasil, nem que a subsidiária tenha relatório "
              "nacional próprio.", P),
          tabela([
              ["Condição do edital", "Zurich Minas Brasil", "Junto Seguros"],
              ["1. Seguradora nacional ou estrangeira, autorizada a funcionar no país",
               "Atende: S.A. brasileira, código SUSEP 05495", "Atende"],
              ["2. Força financeira", f"PL {brl_mi(ZURICH_MINAS.patrimonio_liquido)}; grupo com PL de USD 26,5 bi",
               f"PL {brl_mi(JUNTO.patrimonio_liquido)}"],
              [f"3. Rating igual ou superior, em escala nacional, a {exig_sp} (S&amp;P), "
               f"{exig_fitch} (Fitch) ou {exig_moodys} (Moody's)",
               "Atende: AA / Aa2 convertem em brAAA / Aaa.br", "Atende: brAAA"],
          ], [7.4 * cm, 5.0 * cm, 4.6 * cm]),
          Paragraph("Patamar conforme a cláusula de rating do edital, transcrita na solicitação à Zurich de 17/12/2025. "
                    "A conclusão se mantém mesmo se o patamar fosse o teto brAAA (seção 3.4).", NOTA)]

    # 3. Conversão
    s += [PageBreak(), rotulo("A régua oficial"),
          Paragraph("As próprias agências convertem a nota global em nacional", H1),
          Paragraph(
              "S&amp;P e Moody's publicam, para o Brasil, tabelas que derivam a nota nacional da qualidade de "
              "crédito na escala global. A Moody's descreve o método assim:", P),
          Paragraph(
              "“A atribuição de NSRs começa com uma análise da idoneidade creditícia do emissor, conforme "
              "indicado pelas aplicações da metodologia apropriada de rating na escala global (GSR) [...]. O rating "
              "em escala global do emissor é então ‘mapeado’ para o NSR, de acordo com um mapeamento entre "
              "GSRs e NSRs.” — Moody's América Latina, Formulário de Referência (data-base 31/12/2020)", CITA),
          Paragraph(
              "“An indicative national scale long-term credit rating is the initial result from the application "
              "of the mapping table.” — S&amp;P Global Ratings, National And Regional Scale Credit Ratings "
              "Methodology, 19/12/2023, p. 2", CITA),
          Paragraph("3.1 Margem de segurança", H2),
          tabela([["Tabela oficial", "Exigência do edital", "Equivale na escala global a partir de",
                   "Nota da Zurich", "Zurich na escala nacional", "Folga"]] +
                 [[m["agencia"], m["exigencia_edital"], m["equivale_na_escala_global_a_partir_de"], m["nota_zurich"],
                   ", ".join(m["nota_zurich_na_escala_nacional"]), f"<b>{m['degraus_de_folga']} degraus</b>"]
                  for m in margem],
                 [3.3 * cm, 2.4 * cm, 3.3 * cm, 2.2 * cm, 3.2 * cm, 2.6 * cm]),
          Spacer(1, 10)]
    linhas_sp = [["Global (moeda local)", "Escala nacional Brasil"]] + [[f, ", ".join(n)] for f, n in TABELA_SP_2023]
    linhas_md = [["Escala global", "Escala nacional"]] + [[f, ", ".join(n)] for f, n in TABELA_MOODYS_2020]
    lado = Table([[
        [Paragraph("3.2 S&amp;P — Tabela 3, 19/12/2023", H2), tabela(linhas_sp, [3.6 * cm, 4.5 * cm], destaque=4)],
        [Paragraph("3.3 Moody's — mapa vigente desde 20/11/2020", H2), tabela(linhas_md, [3.4 * cm, 4.5 * cm], destaque=3)],
    ]], colWidths=[8.6 * cm, 8.4 * cm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    s += [lado,
          Paragraph("Linhas destacadas: faixa global em que se encontra o patamar do edital. Linhas inferiores omitidas.",
                    NOTA),
          Paragraph("3.4 Mesmo no teto da escala", H2),
          Paragraph(
              "brAAA é a nota máxima da escala nacional; não existe nota nacional acima dela. Por isso o "
              "“superior” da cláusula só pode ser demonstrado pela escala global. Se o patamar fosse brAAA, "
              "a Zurich ainda atenderia: pela tabela de 2023, brAAA começa em BB, e AA está 9 degraus acima.", P),
          Paragraph("3.5 A Fitch segue a mesma lógica", H2),
          Paragraph(
              "Pelos seus critérios, a Fitch parte da nota internacional e usa a tabela de correspondência de cada "
              "país para chegar à nota nacional; a escala nacional exclui o risco de transferência e "
              "conversibilidade. Na prática, emissores brasileiros com nota internacional BB recebem AAA(bra), "
              "a nota máxima, como a Petrobras (Fitch, abril de 2025).", P),
          Paragraph(
              "“Issuer-level national ratings [...] exclude transfer and convertibility risk. [...] Fitch then "
              "uses the applicable country's National Rating Correspondence Table to identify a range of appropriate "
              "national ratings.” — Fitch, National Scale Rating Criteria, p. 1", CITA),
          Paragraph("3.6 A mudança de 2025 na S&amp;P não altera a conclusão", H2),
          Paragraph(
              "Desde 18/08/2025 as notas “br” são emitidas pela S&amp;P National Ratings, com metodologias "
              "próprias, e em 16/12/2025 a S&amp;P global retirou o Brasil da sua tabela de prefixos. Uma eventual "
              "recalibração não mudaria o resultado: para a Zurich deixar de alcançar brAA-, a nova régua teria de "
              "exigir, para essa nota, uma qualidade global acima de AA, o que é incompatível com um país cujo "
              "rating soberano é BB.", P)]

    # 4. Autorização SUSEP
    s += [PageBreak(), rotulo("Requisito 1"), Paragraph("Autorizada a funcionar no país", H1),
          Paragraph(
              "No Brasil só operam seguros privados sociedades anônimas ou cooperativas autorizadas, sob "
              "supervisão da SUSEP (Decreto-Lei 73/1966, arts. 24 e 74). Grupos estrangeiros atuam por meio de "
              "sociedades constituídas no país, exatamente o caso da Zurich Minas.", P),
          tabela([
              ["Prova", "Conteúdo", "Fonte"],
              ["Autorização SUSEP", "“... CNPJ sob o nº 17.197.385/0001-21, devidamente autorizada pela SUSEP "
               "sob o código nº 05495.”", "Condições gerais do Seguro Garantia Zurich (Circular SUSEP 662/2022)"],
              ["Natureza e objeto", "Sociedade anônima de capital fechado, sede em Belo Horizonte, operações de "
               "seguros dos ramos elementares em todo o território nacional", "DFs Zurich Minas 30/06/2024, Nota 1"],
              ["Seguro-garantia", "Opera garantia segurado — setor público e setor privado",
               "DFs Zurich Minas 30/06/2024"],
              ["Declaração da seguradora", "“plenamente autorizada pela SUSEP a operar no território nacional no "
               "ramo de Seguro Garantia”", "Carta da Zurich, 18/12/2025, item 2"],
          ], [3.4 * cm, 8.6 * cm, 5.0 * cm])]

    # 5. Força financeira
    s += [rotulo("Requisito 2"), Paragraph("Força financeira para um contrato de R$ 1 bilhão", H1),
          Paragraph("Comparação entre as duas seguradoras brasileiras, pelo mesmo critério regulatório "
                    "(Resolução CNSP 432/2021).", P),
          tabela([
              ["Indicador", "Zurich Minas (30/06/2024)", "Junto Seguros (31/12/2024)"],
              ["Patrimônio líquido", brl_mi(ZURICH_MINAS.patrimonio_liquido), brl_mi(JUNTO.patrimonio_liquido)],
              ["Patrimônio líquido ajustado (PLA)", brl_mi(ZURICH_MINAS.pla), brl_mi(JUNTO.pla)],
              ["Capital mínimo requerido", brl_mi(ZURICH_MINAS.capital_minimo_requerido),
               brl_mi(JUNTO.capital_minimo_requerido)],
              ["Suficiência de capital", brl_mi(ZURICH_MINAS.suficiencia_capital), brl_mi(JUNTO.suficiencia_capital)],
              ["Ativos garantidores das provisões", brl_mi(ZURICH_MINAS.ativos_garantidores), "não extraído"],
              ["Grupo controlador", "PL USD 26,5 bi · S&amp;P AA", "Grupo Junto: PL R$ 755,4 mi (2025)"],
          ], [6.2 * cm, 5.4 * cm, 5.4 * cm]),
          Spacer(1, 8),
          tabela([["Garantia sobre R$ 1 bi", "Valor", "% do PL Zurich Minas", "% do PL Junto"]] + [
              [f"{int(p * 100)}%", f"R$ {int(p * 1000)} mi", _br(f"{exposicao_sobre_pl(ZURICH_MINAS, p):.1f}%"),
               _br(f"{exposicao_sobre_pl(JUNTO, p):.1f}%")] for p in (0.05, 0.10, 0.30)],
              [4.2 * cm, 3.4 * cm, 4.7 * cm, 4.7 * cm]),
          Paragraph(f"O patrimônio da Zurich Minas é {_br(f'{ZURICH_MINAS.patrimonio_liquido / JUNTO.patrimonio_liquido:.1f}')} "
                    "vezes o da Junto. No índice relativo PLA/CMR a Junto é maior (386% contra 157%), mas esse "
                    "índice mede folga em relação ao próprio risco, não a capacidade de absorver um sinistro de "
                    "dezenas ou centenas de milhões.", NOTA)]

    # 6. Unidade com o grupo
    s += [PageBreak(), rotulo("Requisito 3 · a subsidiária"),
          Paragraph("Uma única unidade econômica com a entidade classificada", H1),
          Paragraph(
              "A tese da RH trata a Zurich Minas como empresa isolada e sem nota. Os documentos mostram uma "
              "sociedade brasileira, autorizada pela SUSEP, controlada diretamente pela entidade que detém o AA, "
              "com reservas no país e resseguro dentro do grupo.", P),
          tabela([
              ["Fato", "Prova"],
              ["Zurich Insurance Company Ltd (S&amp;P AA, Moody's Aa2, AM Best A+) detém 99,9999% das ações da "
               "Zurich Minas; o restante é da Zurich Life Insurance Company Ltd", "DFs Zurich Minas 30/06/2024, Nota 1"],
              ["Listada como subsidiária significativa, 100% de voto e capital, capital social de R$ 2.316 mi",
               "Zurich Annual results 2024, Nota 27, Tabela 27.1, p. 132"],
              ["R$ 2,71 bi em ativos garantidores: LTN R$ 1,18 bi, NTN-F R$ 844 mi, LF R$ 356 mi, LFT R$ 150 mi",
               "DFs Zurich Minas 30/06/2024"],
              ["Ativos garantidores só valem se custodiados em instituições autorizadas pelo BCB ou CVM",
               "Res. CMN 4.993/2022, Regulamento, art. 4º"],
              ["Resseguro com a Zurich Resseguradora Brasil (S&amp;P AA-) e a Zurich Insurance Company",
               "DFs Zurich Minas 30/06/2024, resseguradores"],
          ], [11.4 * cm, 5.6 * cm]),
          Paragraph("O que diz a própria Zurich", H2),
          Paragraph(
              "“A Zurich Minas Brasil Seguros S.A. [...] está plenamente vinculada ao conglomerado global, cuja "
              "solidez financeira, governança, políticas de risco e capitalização sustentam e respaldam a operação "
              "em todos os mercados em que o Grupo atua, incluindo o mercado brasileiro.” [...] “Para fins "
              "de licitação, a aferição do atendimento ao requisito de rating é realizada com base na equivalência "
              "técnica entre as metodologias de classificação global e nacional, não sendo necessária a existência "
              "de rating nacional específico da subsidiária local.” — Zurich no Brasil, Head of Surety LatAm, "
              "18/12/2025 (Anexo A)", CITA),
          Paragraph(
              "Esse é também o método das agências. Na metodologia de grupos da S&amp;P, a subsidiária "
              "“core” recebe a nota do grupo, porque o grupo a apoiará em qualquer circunstância previsível. "
              "A S&amp;P já aplicou esse raciocínio a seguradora brasileira: em 2013 reafirmou o brAAA da Bradesco "
              "Seguros com base em seu “status core” em relação ao controlador.", P)]

    # 7. Simetria
    s += [rotulo("Coerência"), Paragraph("A tese da RH desqualificaria a própria Junto", H1),
          tabela([
              ["Fato sobre a Junto", "Fonte"],
              ["Descreve seus ratings como “equivalentes a ‘brAAA’ pela Standard &amp; Poor's”",
               "DFs Junto 2024, Relatório da Administração"],
              ["Cede 99,4% do saldo de resseguro à resseguradora local do próprio grupo", "DFs Junto 2024"],
              ["AM Best classifica Junto Re e Junto Seg em conjunto; a perspectiva reflete o “ongoing support "
               "from its parent, The Travelers Companies”", "AM Best, 12/11/2026"],
              ["Em 2016 a S&amp;P rebaixou a J. Malucelli (nome da Junto até nov/2018) de brAA- para brA após ação "
               "sobre o controlador Paraná Banco", "Grupo Amanhã; RI Paraná Banco"],
          ], [11.4 * cm, 5.6 * cm]),
          Spacer(1, 8),
          faixa("Se rating apoiado no grupo não servisse, a Junto também não atenderia ao edital.")]

    # 8. Art. 23
    s += [rotulo("Questão autônoma"), Paragraph("A garantia concorrente", H1),
          Paragraph(f"Circular SUSEP 662/2022, art. 23: “{ART_23}”", CITA),
          Paragraph(
              "Conforme relatado, a garantia de proposta da Zurich (prêmio de R$ 136 mil, com limite de R$ 50 milhões "
              "aprovado para a garantia de execução) já estava emitida quando a Junto emitiu outra apólice para a "
              "mesma obrigação, 48 horas antes do certame, por R$ 9 mil. Esse ponto independe da discussão de rating "
              "e deve ser instruído com as duas apólices, datas de emissão e comprovantes de pagamento.", P)]

    # 9. Objeções previsíveis
    s += [PageBreak(), rotulo("Antecipação"), Paragraph("Objeções previsíveis e respostas", H1)]
    for titulo, texto in OBJECOES:
        s.append(KeepTogether([Paragraph(titulo, H2), Paragraph(texto, P)]))

    # 10. Conclusão
    s += [rotulo("Conclusão"), Paragraph("Não há dúvida técnica a resolver", H1),
          Paragraph(
              "Pelas tabelas oficiais da S&amp;P e da Moody's, o patamar exigido pelo edital corresponde a uma nota "
              "global na faixa B/BB, e a Zurich está 10 a 11 degraus acima, com nota máxima na escala nacional. A "
              "emissora é brasileira, autorizada pela SUSEP, com reservas no país e controlada diretamente pela "
              "entidade classificada, o que a própria Zurich confirmou por escrito. A tese de que um rating global "
              "ou derivado do grupo não serviria não tem apoio no edital nem na metodologia das agências e, "
              "aplicada com coerência, excluiria também a Junto.", P),
          Spacer(1, 6),
          faixa("A Zurich atende ao requisito de rating do edital CC17/2025, com folga de dez degraus.")]

    # Anexo A
    s += [PageBreak(), rotulo("Anexo A"), Paragraph("Declaração técnica da Zurich", H1),
          Paragraph("E-mail de Guilherme Henrique Sieiro Ramiro, Head of Surety LatAm, Zurich no Brasil, a Rodrigo "
                    "Vazquez (Vazquez &amp; Fonseca), 18/12/2025, em resposta à solicitação de 17/12/2025. A Zurich "
                    "“confirma concordância com a utilização deste parecer técnico no dossiê a ser apresentado "
                    "na sessão pública”. Transcrição dos itens:", P),
          Paragraph("<b>1. Subsidiária no Brasil.</b> A Zurich Minas Brasil Seguros S.A. é uma companhia integrante do "
                    "Zurich Insurance Group, um dos maiores grupos seguradores globais, com atuação internacional "
                    "diversificada. A seguradora opera regularmente no Brasil, sob supervisão da Superintendência de "
                    "Seguros Privados – SUSEP, e está plenamente vinculada ao conglomerado global, cuja solidez "
                    "financeira, governança, políticas de risco e capitalização sustentam e respaldam a operação em "
                    "todos os mercados em que o Grupo atua, incluindo o mercado brasileiro.", P),
          Paragraph("<b>2. Aptidão regulatória.</b> A Zurich Minas Brasil Seguros S.A. é plenamente autorizada pela "
                    "SUSEP a operar no território nacional no ramo de Seguro Garantia, em estrita conformidade com a "
                    "legislação vigente, normas regulatórias e requisitos prudenciais aplicáveis às sociedades "
                    "seguradoras no Brasil.", P),
          Paragraph("<b>3. Classificação de força financeira (Rating).</b> O Zurich Insurance Group possui "
                    "classificações de força financeira atribuídas por agências internacionais de rating de primeira "
                    "linha, amplamente reconhecidas no mercado, as quais superam de forma significativa os níveis "
                    "mínimos exigidos no edital quando analisadas por equivalência às escalas nacionais brasileiras. "
                    f"[...] S&amp;P Global Ratings: {carta_sp}; Moody's Investors Service: {carta_moodys}; "
                    f"Fitch Ratings: {carta_fitch}. Para fins de licitação, a aferição do atendimento ao requisito "
                    "de rating é realizada com base na equivalência técnica entre as metodologias de classificação "
                    "global e nacional, não sendo necessária a existência de rating nacional específico da subsidiária "
                    "local, conforme previsto no próprio edital. O Zurich Insurance Group divulga seus ratings de forma "
                    "pública, oficial e auditada, em conformidade com as melhores práticas internacionais de "
                    "transparência e governança.", P),
          Paragraph("Nota: as notas citadas na carta são anteriores às elevações registradas na página oficial de RI "
                    "(S&amp;P AA; Moody's Aa2 desde set/2024). Mesmo as notas da carta superam o patamar do edital "
                    "com folga de 10 (S&amp;P AA-) e 9 (Moody's Aa3) degraus.", NOTA)]

    # Fontes
    s += [rotulo("Fontes"), Paragraph("Documentos consultados", H1)]
    for f in [
        "S&amp;P Global Ratings. National And Regional Scale Credit Ratings Methodology, 19/12/2023, Tabela 3 (evidencias/).",
        "S&amp;P Global Ratings. National And Regional Scale Mapping Specifications, 25/06/2018, Tabela 3 (evidencias/).",
        "S&amp;P Global Ratings. Ratings Definitions, republicado em 16/12/2025 (nota do editor).",
        "S&amp;P National Ratings. Critérios de rating na Escala Nacional Brasil, 18/08/2025 (brazil.ratings.spglobal.com).",
        "Moody's América Latina. Formulário de Referência, data-base 31/12/2020, mapa Brasil de 20/11/2020 (evidencias/).",
        "Fitch Ratings. National Scale Rating Criteria (evidencias/).",
        "Zurich Minas Brasil Seguros S.A. Demonstrações financeiras intermediárias, 30/06/2024 (evidencias/).",
        "Zurich Seguros. Condições gerais do Seguro Garantia, Circular SUSEP 662/2022, versão 2025 (evidencias/).",
        "Zurich Insurance Group. Annual results 2024, Nota 27; página de ratings capturada em 03/01/2026.",
        "Zurich no Brasil. Declaração técnica de 18/12/2025 (Anexo A).",
        "Junto Seguros S.A. Demonstrações financeiras 2024, publicadas em 28/02/2025.",
        "AM Best. Affirms Credit Ratings of Junto Resseguros S.A. and Junto Seguros S.A., 12/11/2026.",
        "Grupo Amanhã (2016); RI Paraná Banco (nov/2018); Sonho Seguro (2013).",
        "Resolução CMN 4.993/2022, Regulamento, art. 4º; Circular SUSEP 662/2022, art. 23; Decreto-Lei 73/1966.",
    ]:
        s.append(Paragraph(f, NOTA, bulletText="·"))
    s += [Spacer(1, 14),
          Paragraph("Documento de trabalho elaborado para instruir a defesa no certame. Não constitui parecer jurídico.",
                    NOTA)]
    return s


def main():
    doc = BaseDocTemplate(SAIDA, pagesize=A4, title="Estudo técnico — rating Zurich — CC17/2025",
                          author="Vieira Mendonça Consultoria em Seguros")
    w, h = A4
    capa_frame = Frame(0, 0, w, h, id="capa")
    corpo_frame = Frame(2 * cm, 2.0 * cm, w - 4 * cm, h - 4.0 * cm, id="corpo")
    doc.addPageTemplates([PageTemplate(id="Capa", frames=[capa_frame], onPage=capa),
                          PageTemplate(id="Interna", frames=[corpo_frame], onPage=interna)])
    doc.build([NextPageTemplate("Interna"), PageBreak()] + corpo())
    print(f"PDF gerado: {SAIDA}")


if __name__ == "__main__":
    main()
