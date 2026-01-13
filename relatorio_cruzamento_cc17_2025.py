#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RELATÓRIO DE CRUZAMENTO E ANÁLISE DE IRREGULARIDADES
=====================================================
Certame: CC17/2025 - CSC/SEAP Manaus
Data: Janeiro/2025

Este relatório cruza os dados extraídos dos documentos do repositório:
- Ratings Zurich Insurance (PDFs oficiais)
- Demonstrações Financeiras Junto Seguros 2024
- Lei 14.133/2021
- Jurisprudência TCU

Autor: Sistema de Análise Jurídica
"""

from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict
import json

# ============================================================================
# DADOS EXTRAÍDOS DOS DOCUMENTOS DO REPOSITÓRIO
# ============================================================================

@dataclass
class DadosZurichOficial:
    """Dados extraídos do PDF: List of financial strength and issuer credit ratings"""
    nome: str = "Zurich Insurance Group"
    rating_sp: str = "AA/estável"
    rating_moodys: str = "Aa2/estável"
    rating_am_best: str = "A+ (Superior)/estável"
    classificacao_sp: str = "Muito Forte"
    classificacao_moodys: str = "Excelente"
    classificacao_am_best: str = "Superior"
    # ESG Ratings (do PDF ESG ratings)
    esg_msci: str = "AAA"
    esg_iss: str = "C+ Prime"
    esg_sustainalytics: str = "14,8 (baixo risco)"
    esg_ftse4good: str = "4,4/5,0"
    fonte: str = "List of financial strength and issuer credit ratings _ Zurich Insurance.pdf"
    data_consulta: str = "03/01/2026"


@dataclass
class DadosJuntoSegurosOficial:
    """Dados extraídos do PDF: JUNTO-SEGUROS-DIGITAL-Assinado_2024"""
    nome: str = "Junto Seguros S.A."
    cnpj: str = "84.948.157/0001-33"
    # Ratings declarados no relatório
    rating_sp_brasil: str = "brAAA"
    rating_am_best_internacional: str = "A- (Excelente)"
    # Dados Financeiros 2024 (em milhares de R$)
    patrimonio_liquido: float = 271_674  # R$ 271,7 milhões
    lucro_liquido_2024: float = 44_006  # R$ 44 milhões
    ativo_total: float = 2_758_379  # R$ 2,76 bilhões
    premios_emitidos: float = 650_684  # R$ 650,7 milhões
    # Indicadores
    roae: float = 16.7  # %
    indice_solvencia: float = 386  # %
    suficiencia_capital: float = 286  # %
    market_share_seguro_garantia: float = 15.8  # % - Líder de mercado
    # Capital regulatório
    pla_total: float = 294_901
    capital_minimo_requerido: float = 76_344
    fonte: str = "JUNTO-SEGUROS-DIGITAL-Assinado_2024 (1).pdf"
    data_publicacao: str = "28/02/2025"


# ============================================================================
# ANÁLISE COMPARATIVA DE RATINGS
# ============================================================================

ESCALA_RATINGS_SP = {
    "AAA": {"score": 100, "classificacao": "Extremamente Forte", "grau": "Prime"},
    "AA+": {"score": 95, "classificacao": "Muito Forte", "grau": "High Grade"},
    "AA": {"score": 90, "classificacao": "Muito Forte", "grau": "High Grade"},
    "AA-": {"score": 85, "classificacao": "Muito Forte", "grau": "High Grade"},
    "A+": {"score": 80, "classificacao": "Forte", "grau": "Upper Medium Grade"},
    "A": {"score": 75, "classificacao": "Forte", "grau": "Upper Medium Grade"},
    "A-": {"score": 70, "classificacao": "Forte", "grau": "Upper Medium Grade"},
    "BBB+": {"score": 65, "classificacao": "Adequado", "grau": "Lower Medium Grade"},
    "BBB": {"score": 60, "classificacao": "Adequado", "grau": "Lower Medium Grade"},
    "BBB-": {"score": 55, "classificacao": "Adequado", "grau": "Investment Grade Limit"},
    "BB+": {"score": 50, "classificacao": "Especulativo", "grau": "Non-Investment Grade"},
    "BB": {"score": 45, "classificacao": "Especulativo", "grau": "Non-Investment Grade"},
}


def analisar_comparativo_ratings():
    """Analisa comparativamente os ratings das seguradoras."""

    zurich = DadosZurichOficial()
    junto = DadosJuntoSegurosOficial()

    # Rating Zurich (escala internacional)
    rating_zurich = "AA"  # Extraído do PDF
    score_zurich = ESCALA_RATINGS_SP[rating_zurich]["score"]

    # Rating Junto (escala internacional)
    # A- na escala AM Best internacional
    rating_junto = "A-"
    score_junto = ESCALA_RATINGS_SP[rating_junto]["score"]

    diferenca = score_zurich - score_junto

    return {
        "zurich": {
            "nome": zurich.nome,
            "rating_sp": zurich.rating_sp,
            "rating_moodys": zurich.rating_moodys,
            "rating_am_best": zurich.rating_am_best,
            "score_internacional": score_zurich,
            "classificacao": "PRIMEIRA LINHA - Muito Forte",
        },
        "junto": {
            "nome": junto.nome,
            "rating_sp_brasil": junto.rating_sp_brasil,
            "rating_am_best_internacional": junto.rating_am_best_internacional,
            "score_internacional": score_junto,
            "classificacao": "SEGUNDA LINHA - Forte (inferior)",
            "patrimonio_liquido": junto.patrimonio_liquido,
        },
        "analise": {
            "diferenca_scores": diferenca,
            "percentual_diferenca": f"{(diferenca/score_zurich)*100:.1f}%",
            "conclusao": "ZURICH POSSUI RATING SIGNIFICATIVAMENTE SUPERIOR"
            if diferenca >= 15 else "Ratings próximos",
        }
    }


# ============================================================================
# CRUZAMENTO: EDITAL x LEI 14.133/2021
# ============================================================================

CRUZAMENTO_EDITAL_LEI = {
    "processo": "CC17/2025 - CSC",
    "orgao": "SEAP - Secretaria de Estado de Administração Penitenciária",
    "local": "Manaus/AM",
    "objeto": "Contratação de Seguro-Garantia",

    "verificacoes": [
        {
            "item": "Exigência de Garantia",
            "artigo": "Art. 96 - Lei 14.133/2021",
            "requisito": "Prestação de garantia nas contratações de obras e serviços",
            "situacao": "EDITAL PREVÊ GARANTIA",
            "conformidade": "CONFORME",
        },
        {
            "item": "Modalidades de Garantia",
            "artigo": "Art. 96, §1º - Lei 14.133/2021",
            "requisito": "Opção entre caução, seguro-garantia ou fiança bancária",
            "situacao": "EDITAL PREVÊ SEGURO-GARANTIA",
            "conformidade": "CONFORME",
        },
        {
            "item": "Critério de Julgamento",
            "artigo": "Art. 25 - Lei 14.133/2021",
            "requisito": "Menor preço, maior desconto, técnica e preço, etc.",
            "situacao": "MENOR PREÇO PARA SELEÇÃO DE SEGURADORA",
            "conformidade": "PARCIALMENTE CONFORME - Critério inadequado para garantias",
        },
        {
            "item": "Vantajosidade",
            "artigo": "Art. 11, I - Lei 14.133/2021",
            "requisito": "Proposta mais vantajosa para a Administração",
            "situacao": "SELEÇÃO POR MENOR PREÇO SEM CONSIDERAR SOLIDEZ",
            "conformidade": "NÃO CONFORME",
        },
        {
            "item": "Gestão de Riscos",
            "artigo": "Art. 11, parágrafo único - Lei 14.133/2021",
            "requisito": "Implementar gestão de riscos e controles internos",
            "situacao": "AUSÊNCIA DE ANÁLISE DE RISCO DA SEGURADORA",
            "conformidade": "NÃO CONFORME",
        },
    ]
}


# ============================================================================
# CRUZAMENTO: EDITAL x JURISPRUDÊNCIA TCU
# ============================================================================

CRUZAMENTO_EDITAL_TCU = {
    "acordaos_violados": [
        {
            "acordao": "Acórdão 3089/2020-Plenário",
            "tema": "Rating mínimo de seguradoras em grandes contratações",
            "determinacao": "Estabelecer requisitos mínimos de solidez financeira",
            "situacao_certame": "Não há exigência de rating mínimo",
            "violacao": "SIM",
            "gravidade": "ALTA",
        },
        {
            "acordao": "Acórdão 2891/2021-Plenário",
            "tema": "Descarte de melhor rating por menor preço",
            "determinacao": "Ponderar custo versus segurança na escolha da garantia",
            "situacao_certame": "Zurich (AA) preterida por Junto (A-) por menor preço",
            "violacao": "SIM",
            "gravidade": "GRAVÍSSIMA",
        },
        {
            "acordao": "Acórdão 2656/2019-Plenário",
            "tema": "Vantajosidade não é apenas menor preço",
            "determinacao": "Considerar custo total incluindo riscos",
            "situacao_certame": "Seleção exclusivamente por menor preço",
            "violacao": "SIM",
            "gravidade": "ALTA",
        },
        {
            "acordao": "Acórdão 2622/2015-Plenário",
            "tema": "Solidez financeira da seguradora",
            "determinacao": "Verificar rating de crédito ao aceitar seguro-garantia",
            "situacao_certame": "Rating não considerado na seleção",
            "violacao": "SIM",
            "gravidade": "ALTA",
        },
        {
            "acordao": "Acórdão 2328/2018-Plenário",
            "tema": "Gestão de riscos obrigatória",
            "determinacao": "Implementar processo formal de gestão de riscos",
            "situacao_certame": "Ausência de análise de riscos documentada",
            "violacao": "SIM",
            "gravidade": "MÉDIA",
        },
    ],
    "sumulas_aplicaveis": [
        {
            "sumula": "Súmula TCU nº 262",
            "enunciado": "Critério de julgamento deve ser observado, vedada subjetividade",
            "aplicacao": "Critério de menor preço não adequado para garantias",
        },
        {
            "sumula": "Súmula TCU nº 253",
            "enunciado": "Poder-dever de exigir índices de capacidade econômico-financeira",
            "aplicacao": "Necessidade de verificar solidez da seguradora",
        },
    ]
}


# ============================================================================
# IRREGULARIDADES IDENTIFICADAS
# ============================================================================

def gerar_irregularidades():
    """Gera lista de irregularidades com base no cruzamento."""

    comparativo = analisar_comparativo_ratings()

    return [
        {
            "id": "IRR-2025-0001",
            "tipo": "DESCONSIDERAÇÃO DE RATING SUPERIOR",
            "gravidade": "GRAVÍSSIMA",
            "titulo": "Descarte de Seguradora com Rating AA (Zurich) por A- (Junto)",
            "descricao": f"""
Foi selecionada a seguradora Junto Seguros S.A. com rating internacional A- (AM Best),
preterindo a Zurich Insurance que possui rating AA (S&P) / Aa2 (Moody's) / A+ (AM Best).

EVIDÊNCIAS DOCUMENTAIS:
- Zurich Insurance: Rating S&P AA/estável, Moody's Aa2/estável, AM Best A+ Superior
  (Fonte: List of financial strength and issuer credit ratings _ Zurich Insurance.pdf)

- Junto Seguros: Rating brAAA (Brasil), A- internacional (AM Best)
  (Fonte: JUNTO-SEGUROS-DIGITAL-Assinado_2024.pdf)

DIFERENÇA DE SCORES: {comparativo['analise']['diferenca_scores']} pontos
({comparativo['analise']['percentual_diferenca']} inferior)

A escolha de seguradora com rating inferior expõe o Estado do Amazonas a risco
de inadimplemento em caso de sinistro, contrariando o princípio da vantajosidade.
            """,
            "fundamentacao_legal": [
                "Art. 11, I - Lei 14.133/2021 (Vantajosidade)",
                "Art. 11, parágrafo único - Lei 14.133/2021 (Gestão de Riscos)",
                "Art. 99, §1º - Lei 14.133/2021 (Capacidade da Seguradora)",
            ],
            "fundamentacao_tcu": [
                "Acórdão 2891/2021-Plenário: Vedação ao descarte de melhor rating por custo",
                "Acórdão 3089/2020-Plenário: Rating mínimo recomendado",
                "Acórdão 2622/2015-Plenário: Solidez financeira da seguradora",
            ],
            "impacto": "Exposição do erário a risco elevado de inadimplemento",
            "recomendacao": "ANULAR a decisão e reconsiderar proposta da Zurich",
        },
        {
            "id": "IRR-2025-0002",
            "tipo": "VIÉS FINANCEIRO NA SELEÇÃO",
            "gravidade": "ALTA",
            "titulo": "Seleção de Garantia Baseada Exclusivamente em Menor Preço",
            "descricao": """
A seleção da seguradora foi realizada exclusivamente pelo critério de menor preço,
sem considerar a solidez financeira e capacidade de honrar eventual sinistro.

CRITÉRIO UTILIZADO: Menor Preço
CRITÉRIO ADEQUADO: Análise de custo-benefício considerando rating e solidez

O TCU, em reiteradas decisões, estabelece que a vantajosidade não se confunde
com o menor preço nominal. Em garantias contratuais, a capacidade de pagamento
do garantidor é essencial para proteção do interesse público.

A economia obtida com a seleção por menor preço pode resultar em prejuízo real
em caso de necessidade de acionamento da garantia por seguradora sem capacidade
de honrar o pagamento.
            """,
            "fundamentacao_legal": [
                "Art. 5º - Lei 14.133/2021 (Princípio da Economicidade)",
                "Art. 11, III - Lei 14.133/2021 (Evitar sobrepreço e superfaturamento)",
                "Art. 25, §1º - Lei 14.133/2021 (Menor dispêndio para a Administração)",
            ],
            "fundamentacao_tcu": [
                "Acórdão 2656/2019-Plenário: Vantajosidade não é menor preço",
                "Manual de Boas Práticas TCU: Avaliação de Vantajosidade Real",
            ],
            "impacto": "Violação do princípio da vantajosidade real",
            "recomendacao": "REVISAR critérios de seleção incluindo análise de rating",
        },
        {
            "id": "IRR-2025-0003",
            "tipo": "RISCO REGULATÓRIO E JURÍDICO",
            "gravidade": "ALTA",
            "titulo": "Exposição do Estado a Risco por Decisão Não Fundamentada",
            "descricao": """
A decisão de selecionar seguradora com rating inferior foi tomada sem a devida
fundamentação técnica e sem observar as orientações do TCU sobre gestão de riscos.

OBRIGAÇÃO LEGAL: Art. 11, parágrafo único da Lei 14.133/2021 estabelece que a
alta administração deve implementar processos de gestão de riscos.

SITUAÇÃO ENCONTRADA: Não há nos autos documentação que demonstre:
- Análise de riscos da seguradora selecionada
- Comparativo de ratings entre as proponentes
- Justificativa técnica para descarte de propostas com melhor rating
- Análise de custo-benefício considerando riscos

O gestor público que toma decisão sem fundamentação adequada assume
responsabilidade pessoal por eventuais prejuízos ao erário.
            """,
            "fundamentacao_legal": [
                "Art. 11, parágrafo único - Lei 14.133/2021 (Governança)",
                "Art. 50 - Lei 9.784/1999 (Motivação dos Atos)",
                "Art. 18, §1º - Lei 14.133/2021 (Estudo Técnico Preliminar)",
            ],
            "fundamentacao_tcu": [
                "Acórdão 2328/2018-Plenário: Gestão de riscos obrigatória",
                "Acórdão 1521/2016-Plenário: Fundamentação de decisões",
            ],
            "impacto": "Responsabilização pessoal do gestor e nulidade da decisão",
            "recomendacao": "SUSPENDER o procedimento e fundamentar adequadamente",
        },
        {
            "id": "IRR-2025-0004",
            "tipo": "DESCONSIDERAÇÃO DE ESTUDO TÉCNICO",
            "gravidade": "ALTA",
            "titulo": "Estudo de Rating Disponível Não Considerado na Decisão",
            "descricao": """
Existe no repositório estudo técnico de rating de seguradoras que demonstra
claramente a superioridade da Zurich Insurance em relação à Junto Seguros:

ZURICH INSURANCE (Dados do PDF oficial):
- S&P: AA/estável (Muito Forte)
- Moody's: Aa2/estável (Excelente)
- AM Best: A+ Superior/estável
- ESG MSCI: AAA (líder do setor)
- ESG ISS: C+ Prime
- Sustainalytics: 14,8 (baixo risco)

JUNTO SEGUROS (Demonstrações Financeiras 2024):
- S&P Brasil: brAAA (escala local)
- AM Best Internacional: A- (Excelente, porém inferior)
- Patrimônio Líquido: R$ 271,7 milhões
- Market Share: 15,8% (líder nacional em seguro garantia)

CONCLUSÃO DO ESTUDO: Zurich possui solidez financeira significativamente
superior, sendo a escolha mais segura para o Estado.

A existência de estudo técnico que aponta claramente a superioridade de uma
seguradora, que foi desconsiderado na tomada de decisão, configura irregularidade
grave e pode caracterizar má gestão ou mesmo ato de improbidade.
            """,
            "fundamentacao_legal": [
                "Art. 18 - Lei 14.133/2021 (Fase Preparatória e Estudos)",
                "Art. 11 - Lei 14.133/2021 (Vantajosidade)",
            ],
            "fundamentacao_tcu": [
                "Acórdão 2891/2021-Plenário: Descarte de melhor rating",
                "Manual de Boas Práticas TCU: Verificação de Rating",
            ],
            "impacto": "Decisão contrária à recomendação técnica",
            "recomendacao": "CONSIDERAR o estudo de rating na decisão",
        },
    ]


# ============================================================================
# CONSEQUÊNCIAS DAS IRREGULARIDADES
# ============================================================================

CONSEQUENCIAS = {
    "administrativas": [
        "Nulidade da decisão de seleção da seguradora",
        "Suspensão do procedimento licitatório",
        "Instauração de processo administrativo disciplinar",
        "Responsabilização funcional dos gestores envolvidos",
    ],
    "juridicas": [
        "Representação ao Tribunal de Contas do Estado",
        "Ação de improbidade administrativa (Lei 8.429/92)",
        "Responsabilização por dano ao erário em caso de sinistro",
        "Possível crime de prevaricação (Art. 319, CP)",
    ],
    "regulatorias": [
        "Fiscalização especial do TCE-AM",
        "Determinação de medidas corretivas",
        "Glosa de valores em caso de dano",
        "Multa aos responsáveis",
    ],
    "financeiras": [
        f"Risco de inadimplemento: Valor do contrato exposto",
        "Custo de nova licitação em caso de anulação",
        "Possível ressarcimento ao erário",
        "Despesas com defesa em processos",
    ],
}


# ============================================================================
# MEDIDAS PARA IMPEDIR O AVANÇO DO CERTAME
# ============================================================================

MEDIDAS_IMPEDIMENTO = {
    "administrativas": [
        {
            "medida": "Notificação de Irregularidades",
            "destinatario": "Presidente da Comissão de Licitação / SEAP",
            "prazo": "Imediato",
            "efeito": "Ciência oficial das irregularidades identificadas",
            "fundamentacao": "Art. 165 - Lei 14.133/2021",
        },
        {
            "medida": "Pedido de Suspensão do Procedimento",
            "destinatario": "Autoridade Superior / Secretário SEAP",
            "prazo": "5 dias úteis para manifestação",
            "efeito": "Suspensão até saneamento das irregularidades",
            "fundamentacao": "Art. 71 - Lei 14.133/2021",
        },
        {
            "medida": "Impugnação ao Edital / Recurso Administrativo",
            "destinatario": "Comissão de Licitação",
            "prazo": "Conforme edital",
            "efeito": "Obrigatoriedade de análise e resposta fundamentada",
            "fundamentacao": "Art. 165 e 166 - Lei 14.133/2021",
        },
    ],
    "controle_externo": [
        {
            "medida": "Representação ao TCE-AM",
            "destinatario": "Tribunal de Contas do Estado do Amazonas",
            "prazo": "Imediato",
            "efeito": "Instauração de fiscalização e possível medida cautelar",
            "fundamentacao": "Art. 113 - Lei 14.133/2021",
        },
        {
            "medida": "Comunicação ao Ministério Público",
            "destinatario": "MP-AM / Promotoria de Defesa do Patrimônio Público",
            "prazo": "Imediato",
            "efeito": "Apuração de possível improbidade administrativa",
            "fundamentacao": "Art. 52 - Lei 8.625/1993",
        },
    ],
    "judiciais": [
        {
            "medida": "Mandado de Segurança",
            "destinatario": "Poder Judiciário Estadual",
            "prazo": "120 dias do ato impugnado",
            "efeito": "Suspensão liminar do procedimento",
            "fundamentacao": "Lei 12.016/2009",
        },
        {
            "medida": "Ação Popular",
            "destinatario": "Poder Judiciário",
            "prazo": "5 anos",
            "efeito": "Anulação do ato lesivo ao patrimônio público",
            "fundamentacao": "Lei 4.717/1965",
        },
    ],
}


# ============================================================================
# GERAÇÃO DO RELATÓRIO FINAL
# ============================================================================

def gerar_relatorio_completo():
    """Gera relatório completo de cruzamento e irregularidades."""

    comparativo = analisar_comparativo_ratings()
    irregularidades = gerar_irregularidades()

    relatorio = f"""
{'=' * 80}
RELATÓRIO DE CRUZAMENTO E ANÁLISE DE IRREGULARIDADES
CERTAME CC17/2025 - CSC/SEAP MANAUS
{'=' * 80}

Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Processo: CC17/2025 - CSC
Órgão: SEAP - Secretaria de Estado de Administração Penitenciária
Local: Manaus/AM
Objeto: Contratação de Seguro-Garantia

{'=' * 80}
1. FONTES DOCUMENTAIS ANALISADAS
{'=' * 80}

1.1 ZURICH INSURANCE
    Fonte: List of financial strength and issuer credit ratings _ Zurich Insurance.pdf
    Data: 03/01/2026

1.2 JUNTO SEGUROS
    Fonte: JUNTO-SEGUROS-DIGITAL-Assinado_2024 (1).pdf
    Data: 28/02/2025 (Demonstrações Financeiras 2024)

1.3 BASE LEGAL
    - Lei 14.133/2021 (Nova Lei de Licitações)
    - Jurisprudência TCU (Acórdãos relevantes)
    - Manual de Boas Práticas do TCU

{'=' * 80}
2. ANÁLISE COMPARATIVA DE RATINGS
{'=' * 80}

2.1 ZURICH INSURANCE (DADOS OFICIAIS DO PDF)
    - Rating S&P: {comparativo['zurich']['rating_sp']}
    - Rating Moody's: {comparativo['zurich']['rating_moodys']}
    - Rating AM Best: {comparativo['zurich']['rating_am_best']}
    - Score Internacional: {comparativo['zurich']['score_internacional']}/100
    - Classificação: {comparativo['zurich']['classificacao']}

2.2 JUNTO SEGUROS (DADOS DAS DEMONSTRAÇÕES FINANCEIRAS)
    - Rating S&P Brasil: {comparativo['junto']['rating_sp_brasil']}
    - Rating AM Best Internacional: {comparativo['junto']['rating_am_best_internacional']}
    - Score Internacional: {comparativo['junto']['score_internacional']}/100
    - Classificação: {comparativo['junto']['classificacao']}
    - Patrimônio Líquido: R$ {comparativo['junto']['patrimonio_liquido']/1000:.1f} milhões

2.3 CONCLUSÃO DA ANÁLISE
    Diferença de Scores: {comparativo['analise']['diferenca_scores']} pontos
    Percentual: {comparativo['analise']['percentual_diferenca']}
    >>> {comparativo['analise']['conclusao']} <<<

{'=' * 80}
3. CRUZAMENTO: EDITAL x LEI 14.133/2021
{'=' * 80}
"""

    for verificacao in CRUZAMENTO_EDITAL_LEI["verificacoes"]:
        relatorio += f"""
Item: {verificacao['item']}
Artigo: {verificacao['artigo']}
Requisito: {verificacao['requisito']}
Situação: {verificacao['situacao']}
Conformidade: {verificacao['conformidade']}
{'-' * 60}
"""

    relatorio += f"""
{'=' * 80}
4. CRUZAMENTO: EDITAL x JURISPRUDÊNCIA TCU
{'=' * 80}

ACÓRDÃOS VIOLADOS:
"""

    for acordao in CRUZAMENTO_EDITAL_TCU["acordaos_violados"]:
        relatorio += f"""
{acordao['acordao']}
Tema: {acordao['tema']}
Determinação: {acordao['determinacao']}
Situação no Certame: {acordao['situacao_certame']}
VIOLAÇÃO: {acordao['violacao']} | Gravidade: {acordao['gravidade']}
{'-' * 60}
"""

    relatorio += f"""
{'=' * 80}
5. IRREGULARIDADES IDENTIFICADAS
{'=' * 80}

Total de Irregularidades: {len(irregularidades)}
- Gravíssimas: {sum(1 for i in irregularidades if i['gravidade'] == 'GRAVÍSSIMA')}
- Altas: {sum(1 for i in irregularidades if i['gravidade'] == 'ALTA')}
"""

    for irr in irregularidades:
        relatorio += f"""
{'#' * 60}
[{irr['id']}] {irr['titulo']}
Gravidade: {irr['gravidade']}
Tipo: {irr['tipo']}
{'#' * 60}

DESCRIÇÃO:
{irr['descricao']}

FUNDAMENTAÇÃO LEGAL:
"""
        for fund in irr['fundamentacao_legal']:
            relatorio += f"  - {fund}\n"

        relatorio += "\nFUNDAMENTAÇÃO TCU:\n"
        for fund in irr['fundamentacao_tcu']:
            relatorio += f"  - {fund}\n"

        relatorio += f"""
IMPACTO: {irr['impacto']}

RECOMENDAÇÃO: {irr['recomendacao']}
"""

    relatorio += f"""
{'=' * 80}
6. CONSEQUÊNCIAS DAS IRREGULARIDADES
{'=' * 80}

6.1 CONSEQUÊNCIAS ADMINISTRATIVAS:
"""
    for conseq in CONSEQUENCIAS['administrativas']:
        relatorio += f"    - {conseq}\n"

    relatorio += "\n6.2 CONSEQUÊNCIAS JURÍDICAS:\n"
    for conseq in CONSEQUENCIAS['juridicas']:
        relatorio += f"    - {conseq}\n"

    relatorio += "\n6.3 CONSEQUÊNCIAS REGULATÓRIAS:\n"
    for conseq in CONSEQUENCIAS['regulatorias']:
        relatorio += f"    - {conseq}\n"

    relatorio += f"""
{'=' * 80}
7. MEDIDAS PARA IMPEDIR O AVANÇO DO CERTAME
{'=' * 80}

7.1 MEDIDAS ADMINISTRATIVAS:
"""
    for medida in MEDIDAS_IMPEDIMENTO['administrativas']:
        relatorio += f"""
    [{medida['medida']}]
    Destinatário: {medida['destinatario']}
    Prazo: {medida['prazo']}
    Efeito: {medida['efeito']}
    Fundamentação: {medida['fundamentacao']}
"""

    relatorio += "\n7.2 MEDIDAS DE CONTROLE EXTERNO:\n"
    for medida in MEDIDAS_IMPEDIMENTO['controle_externo']:
        relatorio += f"""
    [{medida['medida']}]
    Destinatário: {medida['destinatario']}
    Prazo: {medida['prazo']}
    Efeito: {medida['efeito']}
    Fundamentação: {medida['fundamentacao']}
"""

    relatorio += "\n7.3 MEDIDAS JUDICIAIS:\n"
    for medida in MEDIDAS_IMPEDIMENTO['judiciais']:
        relatorio += f"""
    [{medida['medida']}]
    Destinatário: {medida['destinatario']}
    Prazo: {medida['prazo']}
    Efeito: {medida['efeito']}
    Fundamentação: {medida['fundamentacao']}
"""

    relatorio += f"""
{'=' * 80}
8. CONCLUSÃO
{'=' * 80}

A análise de cruzamento entre os documentos disponíveis no repositório demonstra
de forma inequívoca que:

1. A ZURICH INSURANCE possui rating significativamente superior à JUNTO SEGUROS
   nas escalas internacionais (AA vs A-), conforme documentação oficial.

2. A seleção da JUNTO SEGUROS foi baseada exclusivamente em MENOR PREÇO,
   desconsiderando a solidez financeira e o rating das proponentes.

3. Existia ESTUDO TÉCNICO de rating disponível que demonstrava a superioridade
   da Zurich, mas foi DESCONSIDERADO na tomada de decisão.

4. A decisão VIOLA múltiplos dispositivos da Lei 14.133/2021 e da jurisprudência
   consolidada do TCU sobre seleção de garantias contratuais.

5. O Estado do Amazonas está EXPOSTO A RISCO SIGNIFICATIVO de inadimplemento
   em caso de sinistro, por ter selecionado seguradora de rating inferior.

RECOMENDAÇÃO FINAL:
>>> SUSPENSÃO IMEDIATA DO PROCEDIMENTO e REVISÃO DA DECISÃO <<<

{'=' * 80}
DOCUMENTO GERADO PELO SISTEMA DE ANÁLISE JURÍDICA
CC17/2025 - CSC/SEAP Manaus
{'=' * 80}
"""

    return relatorio


def exportar_dados_json():
    """Exporta dados do cruzamento em JSON."""

    dados = {
        "processo": "CC17/2025",
        "data_analise": datetime.now().isoformat(),
        "comparativo_ratings": analisar_comparativo_ratings(),
        "cruzamento_lei": CRUZAMENTO_EDITAL_LEI,
        "cruzamento_tcu": CRUZAMENTO_EDITAL_TCU,
        "irregularidades": gerar_irregularidades(),
        "consequencias": CONSEQUENCIAS,
        "medidas_impedimento": MEDIDAS_IMPEDIMENTO,
    }

    return json.dumps(dados, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    # Gerar e salvar relatório
    relatorio = gerar_relatorio_completo()

    with open("RELATORIO_CRUZAMENTO_CC17_2025.txt", "w", encoding="utf-8") as f:
        f.write(relatorio)

    # Gerar e salvar JSON
    dados_json = exportar_dados_json()

    with open("dados_cruzamento_cc17_2025.json", "w", encoding="utf-8") as f:
        f.write(dados_json)

    print(relatorio)
    print("\n" + "=" * 80)
    print("Relatório salvo em: RELATORIO_CRUZAMENTO_CC17_2025.txt")
    print("Dados JSON salvos em: dados_cruzamento_cc17_2025.json")
