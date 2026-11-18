#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o PDF do estudo de rating Zurich x Junto (CC17/2025). Requer: pip install reportlab"""

from datetime import date

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

from analise_completa_rating_cc17_2025 import (
    ART_23, JUNTO, PONTOS_DE_ATENCAO, TABELA_3_SP_BRASIL_2023, ZURICH_MINAS,
    _br, atende_braaa, brl_mi, exposicao_sobre_pl,
)

SAIDA = "ESTUDO_RATING_ZURICH_CC17_2025.pdf"
AZUL = HexColor("#1f3a5f")
CINZA = HexColor("#eef1f5")
VERMELHO = HexColor("#a12a2a")
LINHA = HexColor("#c4cbd4")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=13.5, textColor=AZUL, spaceBefore=14, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11, textColor=AZUL, spaceBefore=8, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["Normal"], fontSize=9.6, leading=13.4, alignment=TA_JUSTIFY, spaceAfter=6)
CIT = ParagraphStyle("CIT", parent=P, leftIndent=14, rightIndent=10, textColor=HexColor("#333333"),
                     fontName="Helvetica-Oblique", backColor=CINZA, borderPadding=6, spaceBefore=4, spaceAfter=10)
FONTE = ParagraphStyle("FONTE", parent=P, fontSize=8.2, leading=11, textColor=HexColor("#555555"))
DEST = ParagraphStyle("DEST", parent=P, textColor=VERMELHO, fontName="Helvetica-Bold")
CEL = ParagraphStyle("CEL", parent=ss["Normal"], fontSize=8.6, leading=11)
CELB = ParagraphStyle("CELB", parent=CEL, fontName="Helvetica-Bold", textColor=white)


def tabela(linhas, larguras, destaque_linha=None):
    dados = [[Paragraph(str(c), CELB if i == 0 else CEL) for c in row] for i, row in enumerate(linhas)]
    t = Table(dados, colWidths=larguras, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, LINHA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if destaque_linha is not None:
        estilo.append(("BACKGROUND", (0, destaque_linha), (-1, destaque_linha), HexColor("#fdf1d6")))
    t.setStyle(TableStyle(estilo))
    return t


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(HexColor("#777777"))
    canvas.drawString(2 * cm, 1.2 * cm, "Estudo técnico - rating e capacidade das seguradoras - CC17/2025 CSC/SEAP-AM")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"página {doc.page}")
    canvas.restoreState()


def construir():
    s = []
    conv = atende_braaa("AA")

    # Capa
    s += [Spacer(1, 4 * cm),
          Paragraph("ESTUDO TÉCNICO", ParagraphStyle("c0", parent=H1, alignment=TA_CENTER, fontSize=12)),
          Paragraph("A Zurich atende ao requisito de rating do edital CC17/2025",
                    ParagraphStyle("c1", parent=H1, alignment=TA_CENTER, fontSize=20, leading=26)),
          Spacer(1, 0.6 * cm),
          Paragraph("Conversão oficial de escalas, autorização SUSEP, controle societário e simetria com a Junto Seguros",
                    ParagraphStyle("c2", parent=P, alignment=TA_CENTER, fontSize=11)),
          Spacer(1, 2.5 * cm),
          Paragraph("Certame CC17/2025 - Centro de Serviços Compartilhados (CSC) / SEAP Amazonas<br/>"
                    "Objeto: cogestão do sistema prisional - valor de referência R$ 1 bilhão",
                    ParagraphStyle("c3", parent=P, alignment=TA_CENTER)),
          Spacer(1, 1.2 * cm),
          Paragraph(f"Data: {date.today().strftime('%d/%m/%Y')}", ParagraphStyle("c4", parent=P, alignment=TA_CENTER)),
          Paragraph("Documento de trabalho. Não constitui parecer jurídico.",
                    ParagraphStyle("c5", parent=FONTE, alignment=TA_CENTER)),
          PageBreak()]

    # 1. Resumo
    s.append(Paragraph("1. Resumo", H1))
    s.append(Paragraph(
        "A tese atribuída à RH Multi é que a Zurich não atenderia ao edital porque seu rating AA é "
        "<b>global</b>, e não em <b>escala nacional</b>, e porque a subsidiária brasileira não teria "
        "rating próprio. Os documentos levantados mostram o contrário:", P))
    for item in [
        "<b>A própria S&amp;P publica a régua de conversão.</b> Pela Tabela 3 da sua metodologia (dez/2023), "
        "toda qualidade de crédito global de BB+ para cima corresponde a <b>brAAA</b>. O AA da Zurich, convertido, dá brAAA.",
        "<b>brAAA é o teto da escala nacional.</b> Não existe nota nacional acima dele; a única forma de demonstrar "
        "qualidade <i>superior</i> é pela escala global, e o AA está 8 degraus acima do limiar de brAAA.",
        "<b>A seguradora que emite é brasileira e autorizada pela SUSEP</b> (Zurich Minas Brasil Seguros S.A., "
        "código SUSEP 05495), com R$ 2,71 bilhões em ativos garantidores no país, majoritariamente títulos do Tesouro Nacional.",
        "<b>A controladora direta é a própria entidade classificada como AA.</b> A Zurich Insurance Company Ltd detém "
        "99,9999% das ações da Zurich Minas, listada pelo grupo como subsidiária significativa.",
        "<b>A tese desqualificaria também a Junto.</b> O rating da Junto é atribuído em conjunto com a resseguradora do grupo, "
        "apoiado na controladora Travelers, e já foi rebaixado em 2016 por causa do controlador Paraná Banco.",
    ]:
        s.append(Paragraph("• " + item, P))

    # 2. Os três requisitos
    s.append(Paragraph("2. O que o edital exige: três requisitos convergentes", H1))
    s.append(Paragraph(
        "Segundo o relato, a cláusula de garantia combina três condições que devem ser lidas em conjunto. "
        "<i>A redação literal da cláusula deve ser transcrita na peça final.</i>", P))
    s.append(tabela([
        ["Requisito", "O que ele mede", "Zurich Minas", "Junto"],
        ["1. Seguradora nacional ou estrangeira autorizada a funcionar no país",
         "Habilitação regulatória (SUSEP)", "Atende: S.A. brasileira, código SUSEP 05495", "Atende"],
        ["2. Força financeira", "Capacidade de pagar o sinistro",
         f"PL {brl_mi(ZURICH_MINAS.patrimonio_liquido)}; grupo com USD 26,5 bi", f"PL {brl_mi(JUNTO.patrimonio_liquido)}"],
        ["3. Rating igual ou superior a brAAA em escala nacional (S&amp;P, Fitch)",
         "Patamar de qualidade de crédito medido na régua nacional",
         "Atende: AA global = brAAA pela Tabela 3 da S&amp;P", "Atende: brAAA"],
    ], [5.0 * cm, 3.6 * cm, 4.6 * cm, 3.8 * cm]))
    s.append(Spacer(1, 6))
    s.append(Paragraph(
        "O requisito 3 fala em nota <b>na escala nacional</b>. Ele define a régua em que o patamar é medido, "
        "não o país em que a classificação é emitida nem exige um relatório nacional próprio da seguradora. "
        "Ler a cláusula como \"rating emitido no Brasil\" acrescenta uma exigência que o texto não contém.", P))

    # 3. Requisito 1
    s.append(Paragraph("3. Requisito 1: autorização para funcionar no país", H1))
    s.append(Paragraph(
        "No Brasil, só sociedades anônimas ou cooperativas autorizadas podem operar seguros privados, e a autorização "
        "é concedida pelo poder público mediante processo conduzido pela SUSEP (Decreto-Lei 73/1966, arts. 24 e 74; "
        "<i>conferir a redação vigente no Planalto</i>). Grupos estrangeiros atuam por meio de sociedades "
        "constituídas no Brasil e autorizadas, exatamente como a Zurich Minas.", P))
    s.append(tabela([
        ["Prova", "Conteúdo", "Fonte"],
        ["Autorização e código SUSEP", "\"... CNPJ sob o nº 17.197.385/0001-21, devidamente autorizada pela SUSEP sob o código nº 05495.\"",
         "Condições gerais do Seguro Garantia Zurich (regido pela Circular SUSEP 662/2022)"],
        ["Natureza jurídica e objeto", "Sociedade anônima de capital fechado, sede em Belo Horizonte, para operações de seguros "
         "dos ramos elementares em todo o território nacional", "DFs Zurich Minas 30/06/2024, Nota 1"],
        ["Ramo garantia", "Opera garantia segurado - setor público e setor privado", "DFs Zurich Minas 30/06/2024, quadros de provisões"],
    ], [3.6 * cm, 8.4 * cm, 5.0 * cm]))

    # 4. Requisito 2
    s.append(Paragraph("4. Requisito 2: força financeira", H1))
    s.append(Paragraph(
        "A comparação justa é entre as duas seguradoras brasileiras, pelo mesmo critério regulatório "
        "(Resolução CNSP 432/2021). Valores em reais, conforme as demonstrações publicadas.", P))
    s.append(tabela([
        ["Indicador", "Zurich Minas (30/06/2024)", "Junto Seguros (31/12/2024)"],
        ["Patrimônio líquido", brl_mi(ZURICH_MINAS.patrimonio_liquido), brl_mi(JUNTO.patrimonio_liquido)],
        ["Patrimônio líquido ajustado (PLA)", brl_mi(ZURICH_MINAS.pla), brl_mi(JUNTO.pla)],
        ["Capital mínimo requerido (CMR)", brl_mi(ZURICH_MINAS.capital_minimo_requerido), brl_mi(JUNTO.capital_minimo_requerido)],
        ["Suficiência de capital", brl_mi(ZURICH_MINAS.suficiencia_capital), brl_mi(JUNTO.suficiencia_capital)],
        ["Índice PLA / CMR", f"{ZURICH_MINAS.indice_solvencia:.0%}", f"{JUNTO.indice_solvencia:.0%}"],
        ["Ativos oferecidos em garantia das provisões", brl_mi(ZURICH_MINAS.ativos_garantidores), "não extraído"],
        ["Grupo controlador", "Zurich Insurance Group: PL USD 26,5 bi; S&amp;P AA", "Grupo Junto: PL R$ 755,4 mi (2025)"],
    ], [6.0 * cm, 5.5 * cm, 5.5 * cm]))
    s.append(Spacer(1, 6))
    razao = _br(f"{ZURICH_MINAS.patrimonio_liquido / JUNTO.patrimonio_liquido:.1f}")
    s.append(Paragraph(
        f"O patrimônio da Zurich Minas é <b>{razao} vezes</b> o da Junto Seguros. A tabela abaixo mostra quanto "
        "do patrimônio de cada seguradora uma garantia sobre o contrato de R$ 1 bilhão representaria:", P))
    s.append(tabela([["Garantia", "Valor", "% do PL Zurich Minas", "% do PL Junto"]] + [
        [f"{int(p * 100)}%", f"R$ {int(p * 1000)} mi",
         _br(f"{exposicao_sobre_pl(ZURICH_MINAS, p):.1f}%"), _br(f"{exposicao_sobre_pl(JUNTO, p):.1f}%")]
        for p in (0.05, 0.10, 0.30)], [3.0 * cm, 3.5 * cm, 5.2 * cm, 5.3 * cm]))
    s.append(Spacer(1, 4))
    s.append(Paragraph(
        "<i>Ressalva:</i> no índice relativo PLA/CMR a Junto é maior. Esse índice mede a folga de cada empresa "
        "em relação ao próprio risco; não mede a capacidade absoluta de absorver um sinistro de dezenas ou centenas "
        "de milhões, que é o que interessa ao Estado num contrato de R$ 1 bilhão.", FONTE))

    # 5. Requisito 3
    s.append(PageBreak())
    s.append(Paragraph("5. Requisito 3: rating na escala nacional", H1))
    s.append(Paragraph("5.1 A régua oficial de conversão da S&amp;P", H2))
    s.append(Paragraph(
        "A S&amp;P Global Ratings publica, para cada país com escala nacional, uma tabela que converte a qualidade "
        "de crédito na escala global em rating na escala nacional. A metodologia afirma:", P))
    s.append(Paragraph(
        "\"An indicative national scale long-term credit rating is the initial result from the application of the "
        "mapping table, subject to any adjustments included in the proposed criteria.\" "
        "(S&amp;P, National And Regional Scale Credit Ratings Methodology, 19/12/2023, p. 2)", CIT))
    linhas = [["Qualidade de crédito global (moeda local)", "Rating indicativo na escala nacional Brasil"]]
    linhas += [[f, ", ".join(n)] for f, n in TABELA_3_SP_BRASIL_2023[:6]]
    s.append(KeepTogether([
        Paragraph("Tabela 3 - Brazil mapping specification (S&amp;P, 19/12/2023, p. 3)", H2),
        tabela(linhas, [8.5 * cm, 8.5 * cm], destaque_linha=1),
        Paragraph("Linhas inferiores (CCC+ a D) omitidas. Na versão de 25/06/2018, a primeira linha era \"BB e acima -> brAAA\".", FONTE),
    ]))
    s.append(Paragraph("5.2 Aplicação à Zurich", H2))
    s.append(tabela([
        ["Passo", "Resultado"],
        ["Rating S&amp;P de força financeira da controladora (Zurich Insurance Company Ltd)", "AA / estável"],
        ["Limiar global para brAAA (Tabela 3, 2023)", "BB+"],
        ["Distância entre AA e o limiar", f"{conv['degraus_acima_do_limiar_brAAA']} degraus acima"],
        ["Rating indicativo na escala nacional", ", ".join(conv["escala_nacional_indicativa"])],
        ["Atende \"igual ou superior a brAAA\"?", "Sim"],
    ], [10 * cm, 7 * cm]))
    s.append(Spacer(1, 6))
    s.append(Paragraph(
        "<b>Por que \"superior\" só existe na escala global.</b> brAAA é a nota máxima da escala nacional. A tabela "
        "agrupa em brAAA tudo o que vai de BB+ a AAA: uma seguradora brasileira brAAA pode ter qualidade global de "
        "apenas BB+, enquanto a Zurich está em AA. Quando o edital admite rating <i>superior</i> a brAAA, a única "
        "forma de demonstrá-lo é pela escala global. Recusar a escala global anularia a palavra \"superior\" da cláusula.", P))
    s.append(Paragraph("5.3 A Fitch funciona do mesmo modo", H2))
    s.append(Paragraph(
        "\"Issuer-level national ratings evaluate relative vulnerability to default on local-currency (LC)/legal "
        "obligations only for local issuers within the country concerned. They exclude transfer and convertibility risk.\" "
        "(...) \"Fitch then uses the applicable country's National Rating Correspondence Table to identify a range of "
        "appropriate national ratings.\" (Fitch, National Scale Rating Criteria, p. 1)", CIT))
    s.append(Paragraph(
        "Duas consequências: (i) as duas agências citadas pelo edital derivam a nota nacional da nota internacional por "
        "tabela de correspondência; (ii) a escala nacional exclui o risco de transferência e conversibilidade, ou seja, "
        "o \"teto soberano\" não rebaixa a nota de quem opera em moeda local dentro do país.", P))

    # 6. Core / unidade única
    s.append(Paragraph("6. A Zurich Minas é parte integrante do grupo classificado como AA", H1))
    s.append(Paragraph(
        "A tese da RH trata a subsidiária brasileira como uma empresa isolada e sem nota. Os documentos mostram uma "
        "sociedade brasileira, autorizada pela SUSEP, controlada diretamente pela entidade que detém o AA:", P))
    s.append(tabela([
        ["Fato", "Prova"],
        ["Zurich Insurance Company Ltd (S&amp;P AA, Moody's Aa2, AM Best A+) detém 99,9999% das ações da Zurich Minas; "
         "o restante (0,0001%) é da Zurich Life Insurance Company Ltd", "DFs Zurich Minas 30/06/2024, Nota 1"],
        ["O grupo lista a Zurich Minas como subsidiária significativa, 100% de voto e de capital, capital social R$ 2.316 mi",
         "Zurich Annual results 2024, Nota 27, Tabela 27.1, p. 132"],
        ["Ativos garantidores de R$ 2,71 bi: LTN R$ 1,18 bi, NTN-F R$ 844 mi, LF R$ 356 mi, LFT R$ 150 mi, debêntures R$ 137 mi",
         "DFs Zurich Minas 30/06/2024, cobertura das provisões técnicas"],
        ["Ativos garantidores só valem se registrados/custodiados em instituições autorizadas pelo BCB ou pela CVM",
         "Res. CMN 4.993/2022, Regulamento, art. 4º"],
        ["Resseguro do grupo no Brasil: Zurich Resseguradora Brasil S.A. informada com S&amp;P AA-",
         "DFs Zurich Minas 30/06/2024, discriminação dos resseguradores"],
    ], [11.2 * cm, 5.8 * cm]))
    s.append(Spacer(1, 6))
    s.append(Paragraph(
        "<b>O conceito de \"core\".</b> Na metodologia de grupos da S&amp;P (Group Rating Methodology, 2019), uma "
        "subsidiária \"core\" é classificada no nível do perfil de crédito do grupo, porque a agência considera que "
        "o grupo a apoiará em qualquer circunstância previsível. A S&amp;P já aplicou esse raciocínio a seguradora "
        "brasileira: em 2013 reafirmou o brAAA da Bradesco Seguros com base no seu \"status core\" em relação ao "
        "controlador Banco Bradesco. Ou seja, rating derivado do grupo é a regra das agências, não uma exceção.", P))

    # 7. Simetria Junto
    s.append(Paragraph("7. A tese da RH desqualificaria a própria Junto", H1))
    s.append(Paragraph(
        "Se valesse o argumento de que \"rating que depende do grupo não serve\", a Junto também não atenderia ao edital:", P))
    s.append(tabela([
        ["Fato sobre a Junto", "Fonte"],
        ["Descreve seus ratings como \"equivalentes a 'brAAA' pela Standard &amp; Poor's\"", "DFs Junto 2024, Relatório da Administração"],
        ["Cede 99,4% do saldo de resseguro à resseguradora local do próprio grupo", "DFs Junto 2024, nota de resseguro"],
        ["AM Best classifica Junto Re e Junto Seg em conjunto (\"collectively referred to as Junto\"); "
         "a perspectiva reflete o \"ongoing support from its parent, The Travelers Companies\"", "AM Best, 12/11/2026"],
        ["Em 2016, a S&amp;P rebaixou a J. Malucelli Seguradora (nome da Junto até nov/2018) de brAA- para brA "
         "após ação sobre o controlador Paraná Banco", "Grupo Amanhã; RI Paraná Banco"],
    ], [11.2 * cm, 5.8 * cm]))

    # 8. Art. 23
    s.append(Paragraph("8. Questão autônoma: a garantia concorrente", H1))
    s.append(Paragraph(f"Circular SUSEP 662/2022, art. 23: \"{ART_23}\"", CIT))
    s.append(Paragraph(
        "Conforme relatado, a apólice de garantia de proposta da Zurich (prêmio R$ 136 mil, com limite de R$ 50 milhões "
        "aprovado para a garantia de execução) já estava emitida quando a Junto emitiu outra apólice para a mesma "
        "obrigação, 48 horas antes do certame, por R$ 9 mil. Esse ponto independe da discussão de rating e deve ser "
        "instruído com as duas apólices, datas de emissão e comprovantes de pagamento.", P))

    # 9. Pontos de atenção
    s.append(Paragraph("9. Pontos de atenção", H1))
    for titulo, texto in PONTOS_DE_ATENCAO:
        s.append(Paragraph(f"<b>{titulo}.</b> {texto}", P))

    # 10. Conclusão
    s.append(Paragraph("10. Conclusão", H1))
    s.append(Paragraph(
        "Pela régua oficial publicada pela S&amp;P, o AA da controladora direta da Zurich Minas corresponde a brAAA "
        "na escala nacional, cumprindo o \"igual\" e, por estar 8 degraus acima do limiar, demonstrando o \"superior\". "
        "A seguradora emissora é brasileira, autorizada pela SUSEP e mantém seus ativos garantidores no país. "
        "A tese de que um rating global ou derivado do grupo não serviria não tem apoio no texto do edital nem na "
        "metodologia das agências, e, aplicada com coerência, excluiria também a Junto.", DEST))

    # Fontes
    s.append(PageBreak())
    s.append(Paragraph("Fontes", H1))
    for f in [
        "S&amp;P Global Ratings. National And Regional Scale Credit Ratings Methodology, 19/12/2023 (Tabela 3). "
        "Cópia: maalot.co.il/Publications/GCG20231220140254.PDF - arquivo em evidencias/.",
        "S&amp;P Global Ratings. National And Regional Scale Mapping Specifications, 25/06/2018 (Tabela 3). "
        "Cópia: maalot.co.il/Publications/GCG20180626140102.PDF - arquivo em evidencias/.",
        "Fitch Ratings. National Scale Rating Criteria. your.fitch.group - arquivo em evidencias/.",
        "Zurich Minas Brasil Seguros S.A. Demonstrações financeiras intermediárias, 30/06/2024 - arquivo em evidencias/.",
        "Zurich Seguros. Condições gerais do Seguro Garantia (Circular SUSEP 662/2022), versão 2025 - arquivo em evidencias/.",
        "Zurich Insurance Group. Annual results 2024 - Consolidated financial statements, Nota 27 (repositório).",
        "Zurich Insurance Group. List of financial strength and issuer credit ratings, capturado em 03/01/2026 (repositório).",
        "Junto Seguros S.A. Demonstrações financeiras 2024, publicadas em 28/02/2025 (repositório).",
        "AM Best. Affirms Credit Ratings of Junto Resseguros S.A. and Junto Seguros S.A., 12/11/2026 (insurancenewsnet.com).",
        "Grupo Amanhã. S&amp;P rebaixa rating de empresas ligadas ao Paraná Banco (2016).",
        "Paraná Banco RI. JMalucelli Seguradora passa a se chamar Junto Seguros (nov/2018).",
        "Sonho Seguro. Bradesco Seguros tem rating reafirmado pela Standard &amp; Poor's (2013).",
        "Resolução CMN 4.993/2022, Regulamento anexo, art. 4º (legismap.com.br).",
        "Circular SUSEP 662/2022, art. 23.",
        "Decreto-Lei 73/1966, arts. 24 e 74 (conferir redação vigente).",
    ]:
        s.append(Paragraph("• " + f, FONTE))
    return s


def main():
    doc = SimpleDocTemplate(SAIDA, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Estudo de rating - Zurich x Junto - CC17/2025")
    doc.build(construir(), onFirstPage=rodape, onLaterPages=rodape)
    print(f"PDF gerado: {SAIDA}")


if __name__ == "__main__":
    main()
