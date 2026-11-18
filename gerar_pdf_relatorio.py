#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de PDF do Relatório de Cruzamento CC17/2025
Usando ReportLab
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os


def gerar_pdf():
    output_path = '/home/user/Analise-Financeira-Cr-dito-de-Garantia/RELATORIO_CC17_2025_IRREGULARIDADES.pdf'

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name='TituloPrincipal',
        parent=styles['Title'],
        fontSize=20,
        textColor=HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    ))

    styles.add(ParagraphStyle(
        name='Secao',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=HexColor('#2c3e50'),
        spaceBefore=20,
        spaceAfter=10,
        backColor=HexColor('#ecf0f1'),
        borderPadding=5
    ))

    styles.add(ParagraphStyle(
        name='SubSecao',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=HexColor('#34495e'),
        spaceBefore=12,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='TextoNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name='Destaque',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#c0392b'),
        fontName='Helvetica-Bold',
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name='Gravissima',
        parent=styles['Normal'],
        fontSize=10,
        textColor=white,
        backColor=HexColor('#c0392b'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
        borderPadding=3
    ))

    styles.add(ParagraphStyle(
        name='Alta',
        parent=styles['Normal'],
        fontSize=10,
        textColor=white,
        backColor=HexColor('#e67e22'),
        fontName='Helvetica-Bold',
        spaceAfter=4,
        borderPadding=3
    ))

    story = []

    # CAPA
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph('RELATÓRIO DE ANÁLISE', styles['TituloPrincipal']))
    story.append(Paragraph('IRREGULARIDADES NO CERTAME', styles['TituloPrincipal']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph('CC17/2025 - CSC/SEAP MANAUS', styles['TituloPrincipal']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph('Contratação de Seguro-Garantia', styles['TextoNormal']))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(f'Data: {datetime.now().strftime("%d/%m/%Y")}', styles['TextoNormal']))
    story.append(Paragraph('Documento gerado pelo Sistema de Análise Jurídica', styles['TextoNormal']))

    story.append(PageBreak())

    # 1. SUMÁRIO EXECUTIVO
    story.append(Paragraph('1. SUMÁRIO EXECUTIVO', styles['Secao']))
    story.append(Paragraph(
        'Este relatório apresenta a análise de cruzamento entre os documentos do certame '
        'CC17/2025 da SEAP Manaus, identificando irregularidades na seleção de seguradora '
        'para prestação de seguro-garantia.',
        styles['TextoNormal']
    ))
    story.append(Paragraph(
        'CONCLUSÃO: Foram identificadas 4 IRREGULARIDADES, sendo 1 de gravidade '
        'GRAVÍSSIMA e 3 de gravidade ALTA.',
        styles['Destaque']
    ))

    # 2. ANÁLISE DE RATINGS
    story.append(PageBreak())
    story.append(Paragraph('2. ANÁLISE COMPARATIVA DE RATINGS', styles['Secao']))

    story.append(Paragraph('2.1 ZURICH INSURANCE (Dados Oficiais)', styles['SubSecao']))
    story.append(Paragraph('Fonte: List of financial strength and issuer credit ratings _ Zurich Insurance.pdf', styles['TextoNormal']))

    dados_zurich = [
        ['Agência', 'Rating'],
        ["Standard & Poor's", 'AA / estável'],
        ["Moody's", 'Aa2 / estável'],
        ['AM Best', 'A+ (Superior) / estável'],
        ['Score Internacional', '90/100'],
        ['Classificação', 'PRIMEIRA LINHA - Muito Forte'],
    ]
    t = Table(dados_zurich, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('2.2 JUNTO SEGUROS (Demonstrações Financeiras 2024)', styles['SubSecao']))
    story.append(Paragraph('Fonte: JUNTO-SEGUROS-DIGITAL-Assinado_2024.pdf', styles['TextoNormal']))

    dados_junto = [
        ['Indicador', 'Valor'],
        ['Rating S&P Brasil', 'brAAA (escala local)'],
        ['Rating AM Best Internacional', 'A- (Excelente)'],
        ['Score Internacional', '70/100'],
        ['Patrimônio Líquido', 'R$ 271,7 milhões'],
        ['Classificação', 'SEGUNDA LINHA - Forte (inferior)'],
    ]
    t = Table(dados_junto, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph(
        'DIFERENÇA: 20 pontos (22,2%) - ZURICH possui rating significativamente SUPERIOR',
        styles['Destaque']
    ))

    # 3. IRREGULARIDADES
    story.append(PageBreak())
    story.append(Paragraph('3. IRREGULARIDADES IDENTIFICADAS', styles['Secao']))

    # IRR-1
    story.append(Paragraph('IRR-2025-0001 - GRAVIDADE: GRAVÍSSIMA', styles['Gravissima']))
    story.append(Paragraph('<b>Descarte de Seguradora com Rating AA (Zurich) por A- (Junto)</b>', styles['TextoNormal']))
    story.append(Paragraph(
        'Foi selecionada a seguradora Junto Seguros S.A. com rating internacional A- (AM Best), '
        'preterindo a Zurich Insurance que possui rating AA (S&P) / Aa2 (Moody\'s) / A+ (AM Best). '
        'A escolha de seguradora com rating inferior expõe o Estado do Amazonas a risco de '
        'inadimplemento em caso de sinistro.',
        styles['TextoNormal']
    ))
    story.append(Paragraph(
        '<b>Fundamento:</b> Art. 11, I e parágrafo único - Lei 14.133/2021; Acórdão TCU 2891/2021-Plenário',
        styles['TextoNormal']
    ))
    story.append(Spacer(1, 0.3*cm))

    # IRR-2
    story.append(Paragraph('IRR-2025-0002 - GRAVIDADE: ALTA', styles['Alta']))
    story.append(Paragraph('<b>Seleção de Garantia Baseada Exclusivamente em Menor Preço</b>', styles['TextoNormal']))
    story.append(Paragraph(
        'A seleção da seguradora foi realizada exclusivamente pelo critério de menor preço, '
        'sem considerar a solidez financeira e capacidade de honrar eventual sinistro. '
        'O TCU estabelece que a vantajosidade não se confunde com o menor preço nominal.',
        styles['TextoNormal']
    ))
    story.append(Paragraph(
        '<b>Fundamento:</b> Art. 5º e Art. 11, III - Lei 14.133/2021; Acórdão TCU 2656/2019-Plenário',
        styles['TextoNormal']
    ))
    story.append(Spacer(1, 0.3*cm))

    # IRR-3
    story.append(Paragraph('IRR-2025-0003 - GRAVIDADE: ALTA', styles['Alta']))
    story.append(Paragraph('<b>Exposição do Estado a Risco por Decisão Não Fundamentada</b>', styles['TextoNormal']))
    story.append(Paragraph(
        'A decisão de selecionar seguradora com rating inferior foi tomada sem a devida '
        'fundamentação técnica e sem observar as orientações do TCU sobre gestão de riscos. '
        'Não há nos autos análise de riscos ou justificativa técnica.',
        styles['TextoNormal']
    ))
    story.append(Paragraph(
        '<b>Fundamento:</b> Art. 11, parágrafo único - Lei 14.133/2021; Acórdão TCU 2328/2018-Plenário',
        styles['TextoNormal']
    ))
    story.append(Spacer(1, 0.3*cm))

    # IRR-4
    story.append(Paragraph('IRR-2025-0004 - GRAVIDADE: ALTA', styles['Alta']))
    story.append(Paragraph('<b>Estudo de Rating Disponível Não Considerado na Decisão</b>', styles['TextoNormal']))
    story.append(Paragraph(
        'Existe estudo técnico de rating de seguradoras que demonstra claramente a superioridade '
        'da Zurich Insurance em relação à Junto Seguros. Este estudo foi desconsiderado na '
        'tomada de decisão, o que pode caracterizar má gestão.',
        styles['TextoNormal']
    ))
    story.append(Paragraph(
        '<b>Fundamento:</b> Art. 18 - Lei 14.133/2021; Acórdão TCU 2891/2021-Plenário',
        styles['TextoNormal']
    ))

    # 4. VIOLAÇÕES LEGAIS
    story.append(PageBreak())
    story.append(Paragraph('4. VIOLAÇÕES LEGAIS IDENTIFICADAS', styles['Secao']))

    story.append(Paragraph('4.1 Lei 14.133/2021 - Nova Lei de Licitações', styles['SubSecao']))

    violacoes_lei = [
        ['Dispositivo', 'Descrição'],
        ['Art. 5º', 'Princípio da Economicidade'],
        ['Art. 11, I', 'Proposta mais vantajosa'],
        ['Art. 11, III', 'Evitar sobrepreço'],
        ['Art. 11, par. único', 'Gestão de riscos'],
        ['Art. 18', 'Fase preparatória e estudos'],
        ['Art. 25', 'Critério de julgamento'],
    ]
    t = Table(violacoes_lei, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#c0392b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph('4.2 Jurisprudência TCU Violada', styles['SubSecao']))

    violacoes_tcu = [
        ['Acórdão', 'Tema'],
        ['2891/2021-Plenário', 'Vedação descarte melhor rating por custo'],
        ['3089/2020-Plenário', 'Rating mínimo em grandes contratações'],
        ['2656/2019-Plenário', 'Vantajosidade não é menor preço'],
        ['2622/2015-Plenário', 'Solidez financeira da seguradora'],
        ['2328/2018-Plenário', 'Gestão de riscos obrigatória'],
    ]
    t = Table(violacoes_tcu, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e67e22')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#bdc3c7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    # 5. CONSEQUÊNCIAS
    story.append(PageBreak())
    story.append(Paragraph('5. CONSEQUÊNCIAS DAS IRREGULARIDADES', styles['Secao']))

    story.append(Paragraph('5.1 Consequências Administrativas', styles['SubSecao']))
    story.append(Paragraph(
        '• Nulidade da decisão de seleção da seguradora<br/>'
        '• Suspensão do procedimento licitatório<br/>'
        '• Instauração de processo administrativo disciplinar<br/>'
        '• Responsabilização funcional dos gestores envolvidos',
        styles['TextoNormal']
    ))

    story.append(Paragraph('5.2 Consequências Jurídicas', styles['SubSecao']))
    story.append(Paragraph(
        '• Representação ao Tribunal de Contas do Estado<br/>'
        '• Ação de improbidade administrativa (Lei 8.429/92)<br/>'
        '• Responsabilização por dano ao erário em caso de sinistro<br/>'
        '• Possível crime de prevaricação (Art. 319, CP)',
        styles['TextoNormal']
    ))

    story.append(Paragraph('5.3 Consequências Regulatórias', styles['SubSecao']))
    story.append(Paragraph(
        '• Fiscalização especial do TCE-AM<br/>'
        '• Determinação de medidas corretivas<br/>'
        '• Glosa de valores em caso de dano<br/>'
        '• Multa aos responsáveis',
        styles['TextoNormal']
    ))

    # 6. MEDIDAS
    story.append(PageBreak())
    story.append(Paragraph('6. MEDIDAS PARA IMPEDIR O AVANÇO DO CERTAME', styles['Secao']))

    story.append(Paragraph('6.1 Medidas Administrativas', styles['SubSecao']))
    story.append(Paragraph(
        '• Notificação de Irregularidades ao Presidente da Comissão de Licitação<br/>'
        '• Pedido de Suspensão do Procedimento à Autoridade Superior<br/>'
        '• Impugnação ao Edital / Recurso Administrativo',
        styles['TextoNormal']
    ))

    story.append(Paragraph('6.2 Medidas de Controle Externo', styles['SubSecao']))
    story.append(Paragraph(
        '• Representação ao TCE-AM (Art. 113, Lei 14.133/2021)<br/>'
        '• Comunicação ao Ministério Público - Promotoria de Defesa do Patrimônio Público',
        styles['TextoNormal']
    ))

    story.append(Paragraph('6.3 Medidas Judiciais', styles['SubSecao']))
    story.append(Paragraph(
        '• Mandado de Segurança (Lei 12.016/2009) - Prazo: 120 dias<br/>'
        '• Ação Popular (Lei 4.717/1965) - Prazo: 5 anos',
        styles['TextoNormal']
    ))

    # 7. CONCLUSÃO
    story.append(PageBreak())
    story.append(Paragraph('7. CONCLUSÃO E RECOMENDAÇÃO', styles['Secao']))

    story.append(Paragraph(
        'A análise de cruzamento entre os documentos disponíveis demonstra de forma inequívoca que:',
        styles['TextoNormal']
    ))

    story.append(Paragraph(
        '<b>1.</b> A ZURICH INSURANCE possui rating significativamente superior à JUNTO SEGUROS '
        'nas escalas internacionais (AA vs A-).<br/><br/>'
        '<b>2.</b> A seleção da JUNTO SEGUROS foi baseada exclusivamente em MENOR PREÇO, '
        'desconsiderando a solidez financeira.<br/><br/>'
        '<b>3.</b> Existia ESTUDO TÉCNICO de rating disponível que foi DESCONSIDERADO na tomada de decisão.<br/><br/>'
        '<b>4.</b> A decisão VIOLA múltiplos dispositivos da Lei 14.133/2021 e da jurisprudência do TCU.<br/><br/>'
        '<b>5.</b> O Estado do Amazonas está EXPOSTO A RISCO SIGNIFICATIVO de inadimplemento.',
        styles['TextoNormal']
    ))

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        'RECOMENDAÇÃO FINAL: SUSPENSÃO IMEDIATA DO PROCEDIMENTO E REVISÃO DA DECISÃO',
        styles['Destaque']
    ))

    # Build PDF
    doc.build(story)
    return output_path


if __name__ == '__main__':
    arquivo = gerar_pdf()
    print(f'PDF gerado com sucesso: {arquivo}')
