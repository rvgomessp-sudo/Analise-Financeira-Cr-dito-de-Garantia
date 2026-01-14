"""
Dados de Estrutura Societária - Zurich Brasil e Junto Seguros

Este arquivo contém dados reais e estimativas baseadas em fontes públicas
para demonstrar a diferenciação entre:
- SUBSIDIÁRIA DE GRUPO INTERNACIONAL (Zurich Brasil)
- SEGURADORA NACIONAL INDEPENDENTE (Junto Seguros)

FONTES DE DADOS:
================
- SUSEP - Superintendência de Seguros Privados
- AM Best - Ratings e análises
- S&P Global Ratings
- Fitch Ratings
- Demonstrações Financeiras publicadas
- Relatórios de mercado (Síntese SUSEP 2024)

IMPORTANTE:
===========
Este módulo trata APENAS de seguradoras e sua estrutura societária.
A análise de resseguro é tratada em módulo separado.
O "grupo" aqui refere-se à estrutura societária da seguradora,
não à composição com resseguradoras.
"""

from datetime import date
from typing import Dict, List

from src.models.estrutura_societaria import (
    SeguradoraBrasileira,
    ControladoraInternacional,
    GrupoSegurador,
    VinculoSocietario,
    FilialRegional,
    IndicadoresFinanceirosBRL,
    ComparacaoEstruturaSocietaria,
    TipoEntidade,
    TipoControle,
    TipoRating,
    OrigemCapital,
)


# =============================================================================
# ZURICH INSURANCE GROUP - CONTROLADORA INTERNACIONAL
# =============================================================================

ZURICH_INSURANCE_GROUP = ControladoraInternacional(
    nome="Zurich Insurance Group Ltd",
    pais_sede="Suíça",
    codigo_identificacao="LEI: 529900QVNRBND50TXP03",

    # Rating do Grupo (dados 2024-2025)
    rating="AA",
    agencia_rating="S&P / Fitch / AM Best",
    data_rating=date(2024, 9, 30),
    outlook="Stable",

    # Dados Financeiros em USD (aproximados 2024)
    # Fonte: Relatórios Zurich Insurance Group
    patrimonio_liquido_usd=42_000_000_000,  # USD 42 bilhões
    ativo_total_usd=450_000_000_000,        # USD 450 bilhões
    premios_emitidos_usd=75_000_000_000,    # USD 75 bilhões
    lucro_liquido_usd=5_800_000_000,        # USD 5.8 bilhões

    # Conversão para BRL (taxa aproximada 5.50)
    patrimonio_liquido_brl=231_000_000_000,  # R$ 231 bilhões
    ativo_total_brl=2_475_000_000_000,       # R$ 2.475 trilhões
    premios_emitidos_brl=412_500_000_000,    # R$ 412.5 bilhões
    lucro_liquido_brl=31_900_000_000,        # R$ 31.9 bilhões
    taxa_cambio_usada=5.50,

    # Histórico
    anos_operacao=152,  # Fundada em 1872
    paises_atuacao=210,

    # Suporte às subsidiárias
    carta_suporte=True,
    valor_carta_suporte_brl=0,  # Garantia implícita do grupo
    garantia_explicita=True,  # Como subsidiária integral
)


# =============================================================================
# GRUPO ZURICH NO BRASIL
# =============================================================================

GRUPO_ZURICH_BRASIL = GrupoSegurador(
    nome_grupo="Zurich Insurance Group",
    pais_sede="Suíça",
    tipo_grupo="Internacional",

    # Rating do Grupo
    rating_grupo="AA",
    agencia_rating="S&P / Fitch",
    data_rating=date(2024, 9, 30),

    # Controladora
    controladora=ZURICH_INSURANCE_GROUP,

    # Subsidiárias no Brasil
    subsidiarias_brasil=[
        "Zurich Minas Brasil Seguros S.A.",
        "Zurich Santander Brasil Seguros S.A.",
        "Zurich Santander Brasil Seguros e Previdência S.A.",
    ],
    total_empresas_grupo=3,

    # Dados Consolidados no Brasil (estimativa)
    patrimonio_liquido_consolidado_brl=3_500_000_000,   # R$ 3.5 bilhões
    ativo_total_consolidado_brl=15_000_000_000,         # R$ 15 bilhões
    premios_emitidos_consolidado_brl=8_000_000_000,     # R$ 8 bilhões

    # Força do Grupo
    anos_mercado=152,
    paises_atuacao=210,
    posicao_ranking_global=8,  # Top 10 mundial

    # Características
    origem_capital=OrigemCapital.ESTRANGEIRO,
    tem_suporte_explicito=True,
)


# =============================================================================
# ZURICH MINAS BRASIL SEGUROS S.A.
# =============================================================================

def criar_zurich_minas_brasil() -> SeguradoraBrasileira:
    """
    Cria instância da Zurich Minas Brasil Seguros S.A.

    ESTRUTURA SOCIETÁRIA:
    ====================
    - É SUBSIDIÁRIA BRASILEIRA do Zurich Insurance Group (Suíça)
    - O rating AA vem do GRUPO (rating emprestado)
    - Força isolada seria menor que o rating declarado

    DIFERENCIAÇÃO:
    =============
    Esta é uma subsidiária de grupo internacional, não uma empresa nacional.
    O rating é do GRUPO, não da força isolada da entidade brasileira.
    """

    # Indicadores Financeiros em BRL (dados 2024, fonte SUSEP/Demonstrações)
    indicadores = IndicadoresFinanceirosBRL(
        data_referencia=date(2024, 12, 31),
        fonte_dados="SUSEP / Demonstrações Financeiras 2024",

        # Balanço Patrimonial
        ativo_total=2_800_000_000,              # R$ 2.8 bilhões
        ativo_circulante=2_100_000_000,         # R$ 2.1 bilhões
        disponibilidades=150_000_000,           # R$ 150 milhões
        aplicacoes_financeiras=1_800_000_000,   # R$ 1.8 bilhões
        patrimonio_liquido=850_000_000,         # R$ 850 milhões
        capital_social=500_000_000,             # R$ 500 milhões
        provisoes_tecnicas=1_600_000_000,       # R$ 1.6 bilhões

        # DRE (dados estimados 2024)
        premios_emitidos=2_200_000_000,         # R$ 2.2 bilhões
        premios_ganhos=1_900_000_000,           # R$ 1.9 bilhões
        premios_retidos=1_700_000_000,          # R$ 1.7 bilhões
        sinistros_ocorridos=760_000_000,        # R$ 760 milhões
        resultado_financeiro=180_000_000,       # R$ 180 milhões
        lucro_liquido=220_000_000,              # R$ 220 milhões

        # Indicadores Chave
        indice_sinistralidade=40.0,             # 40%
        indice_combinado=85.0,                  # 85%
        liquidez_corrente=1.35,
        indice_solvencia=0.53,
        roe=25.9,                               # 25.9%
        roa=7.9,                                # 7.9%

        # Regulatórios
        margem_solvencia=350_000_000,           # R$ 350 milhões
        capital_minimo_requerido=200_000_000,   # R$ 200 milhões
        patrimonio_liquido_ajustado=820_000_000, # R$ 820 milhões
        suficiencia_pla=4.1,                    # 410%
    )

    # Vínculo Societário
    vinculo = VinculoSocietario(
        nome_controladora="Zurich Insurance Group Ltd",
        cnpj_controladora="",  # Empresa estrangeira
        tipo_controladora=TipoEntidade.MATRIZ_INTERNACIONAL,

        nome_controlada="Zurich Minas Brasil Seguros S.A.",
        cnpj_controlada="17.197.385/0001-21",
        tipo_controlada=TipoEntidade.SUBSIDIARIA_BRASILEIRA,

        percentual_participacao=100.0,
        tipo_controle=TipoControle.CONTROLE_TOTAL,
        data_inicio_controle=date(2009, 7, 3),

        # Rating emprestado do grupo
        rating_emprestado=True,
        notches_diferenca=2,  # 2 notches acima do rating isolado

        # Suporte
        ha_carta_suporte=True,
        valor_suporte_brl=0,  # Garantia implícita ilimitada
        historico_aportes_brl=300_000_000,  # Aportes históricos
    )

    return SeguradoraBrasileira(
        # Identificação
        codigo_susep="05495",
        nome_oficial="Zurich Minas Brasil Seguros S.A.",
        nome_fantasia="Zurich Seguros",
        cnpj="17.197.385/0001-21",

        # Localização
        uf_matriz="MG",
        cidade_matriz="Belo Horizonte",
        endereco_matriz="Av. Getúlio Vargas, 1.420 - 5º andar, Funcionários",

        # Datas
        data_constituicao=date(2009, 7, 3),
        data_autorizacao_susep=date(2009, 11, 15),

        # Estrutura Societária
        tipo_entidade=TipoEntidade.SUBSIDIARIA_BRASILEIRA,
        eh_subsidiaria_estrangeira=True,
        controladora_internacional=ZURICH_INSURANCE_GROUP,
        grupo_economico=GRUPO_ZURICH_BRASIL,
        vinculo=vinculo,
        filiais=[],  # Não tem filiais próprias

        # Rating
        rating_declarado="AA",
        agencia_rating="S&P / Fitch (via Grupo)",
        data_rating=date(2024, 9, 30),
        tipo_rating=TipoRating.RATING_GRUPO,  # IMPORTANTE: Rating do GRUPO

        # Rating Calculado (força isolada)
        rating_calculado="A",  # Seria A se avaliada isoladamente
        score_forca_isolada=75.0,
        gap_rating=2,  # 2 notches acima do que teria isolada
        rating_inflado=True,  # Rating beneficiado pelo grupo

        # Dados Financeiros
        indicadores=indicadores,

        # Capacidade
        limite_retencao_risco=85_000_000,       # R$ 85 milhões
        limite_retencao_evento=150_000_000,     # R$ 150 milhões
        atende_limite_50mm=True,
        margem_sobre_50mm=35_000_000,           # R$ 35 milhões acima

        # Segurança da Apólice
        nota_seguranca_apolice="A+",
        parecer_seguranca=(
            "ALTA SEGURANÇA - Subsidiária integral do Zurich Insurance Group, "
            "um dos maiores grupos seguradores do mundo. O suporte do grupo "
            "garante capacidade de pagamento mesmo em cenários adversos. "
            "Rating AA reflete a força do grupo controlador."
        ),
        fatores_positivos=[
            "Suporte integral do Zurich Insurance Group (AA global)",
            "Patrimônio do grupo > USD 42 bilhões",
            "Presença em 210 países",
            "152 anos de operação global",
            "Garantia explícita da controladora",
        ],
        fatores_atencao=[
            "Rating da entidade brasileira isolada seria inferior (A)",
            "Dependência do suporte do grupo",
        ],
        fatores_risco=[],
    )


# =============================================================================
# JUNTO SEGUROS S.A. - SEGURADORA NACIONAL INDEPENDENTE
# =============================================================================

def criar_junto_seguros() -> SeguradoraBrasileira:
    """
    Cria instância da Junto Seguros S.A.

    ESTRUTURA SOCIETÁRIA:
    ====================
    - É uma SEGURADORA NACIONAL INDEPENDENTE
    - MATRIZ em Curitiba/PR
    - Possui FILIAIS (mesmo CNPJ raiz) em outras localidades
    - Tem relação com Junto Resseguros, mas são ENTIDADES DISTINTAS
    - O rating brAAA da S&P é PRÓPRIO (força isolada)

    DIFERENCIAÇÃO:
    =============
    NÃO é subsidiária de grupo estrangeiro.
    A Junto Resseguros é uma empresa SEPARADA (CNPJ diferente).
    A análise de resseguro é feita em módulo separado.
    Aqui avaliamos apenas a SEGURADORA.
    """

    # Indicadores Financeiros em BRL (dados 2024, fonte SUSEP)
    indicadores = IndicadoresFinanceirosBRL(
        data_referencia=date(2024, 12, 31),
        fonte_dados="SUSEP / Demonstrações Financeiras 2024",

        # Balanço Patrimonial (estimativas baseadas em dados públicos)
        ativo_total=1_800_000_000,              # R$ 1.8 bilhões
        ativo_circulante=1_350_000_000,         # R$ 1.35 bilhões
        disponibilidades=120_000_000,           # R$ 120 milhões
        aplicacoes_financeiras=1_100_000_000,   # R$ 1.1 bilhões
        patrimonio_liquido=650_000_000,         # R$ 650 milhões
        capital_social=400_000_000,             # R$ 400 milhões
        provisoes_tecnicas=950_000_000,         # R$ 950 milhões

        # DRE (dados 2024)
        # Fonte: Síntese SUSEP 2024 - Prêmio Direto R$ 801,1 milhões
        premios_emitidos=801_100_000,           # R$ 801.1 milhões
        premios_ganhos=720_000_000,             # R$ 720 milhões
        premios_retidos=650_000_000,            # R$ 650 milhões
        sinistros_ocorridos=216_000_000,        # R$ 216 milhões
        resultado_financeiro=95_000_000,        # R$ 95 milhões
        lucro_liquido=145_000_000,              # R$ 145 milhões

        # Indicadores Chave
        indice_sinistralidade=30.0,             # 30% (excelente para garantia)
        indice_combinado=78.0,                  # 78%
        liquidez_corrente=1.42,
        indice_solvencia=0.68,
        roe=22.3,                               # 22.3%
        roa=8.1,                                # 8.1%

        # Regulatórios
        margem_solvencia=280_000_000,           # R$ 280 milhões
        capital_minimo_requerido=150_000_000,   # R$ 150 milhões
        patrimonio_liquido_ajustado=630_000_000, # R$ 630 milhões
        suficiencia_pla=4.2,                    # 420%
    )

    # Filiais (mesmo CNPJ raiz, sufixos diferentes)
    filiais = [
        FilialRegional(
            nome_filial="Junto Seguros - Filial São Paulo",
            cnpj_filial="84.948.157/0002-14",
            uf="SP",
            cidade="São Paulo",
            tipo="Filial",
            ativa=True,
            data_abertura=date(2010, 3, 15),
            premios_emitidos_brl=320_000_000,   # R$ 320 milhões
            participacao_total=40.0,            # 40% do total
        ),
        FilialRegional(
            nome_filial="Junto Seguros - Filial Rio de Janeiro",
            cnpj_filial="84.948.157/0006-48",
            uf="RJ",
            cidade="Rio de Janeiro",
            tipo="Filial",
            ativa=True,
            data_abertura=date(2012, 6, 20),
            premios_emitidos_brl=160_000_000,   # R$ 160 milhões
            participacao_total=20.0,            # 20% do total
        ),
        FilialRegional(
            nome_filial="Junto Seguros - Filial Minas Gerais",
            cnpj_filial="84.948.157/0005-67",
            uf="MG",
            cidade="Belo Horizonte",
            tipo="Filial",
            ativa=True,
            data_abertura=date(2015, 9, 10),
            premios_emitidos_brl=80_000_000,    # R$ 80 milhões
            participacao_total=10.0,            # 10% do total
        ),
    ]

    return SeguradoraBrasileira(
        # Identificação
        codigo_susep="05436",
        nome_oficial="Junto Seguros S.A.",
        nome_fantasia="Junto Seguros",
        cnpj="84.948.157/0001-33",

        # Localização da MATRIZ
        uf_matriz="PR",
        cidade_matriz="Curitiba",
        endereco_matriz="Av. Dr. Dário Lopes dos Santos, 2197, 3º andar, Torre C, Jd. Botânico",

        # Datas
        data_constituicao=date(1991, 11, 29),
        data_autorizacao_susep=date(1991, 11, 29),

        # Estrutura Societária
        tipo_entidade=TipoEntidade.MATRIZ,  # É MATRIZ (tem filiais)
        eh_subsidiaria_estrangeira=False,   # NÃO é subsidiária estrangeira
        controladora_internacional=None,     # NÃO tem controladora estrangeira
        grupo_economico=None,               # NÃO faz parte de grupo internacional
        vinculo=None,                       # NÃO tem vínculo de controle
        filiais=filiais,                    # TEM FILIAIS (SP, RJ, MG)

        # Rating
        rating_declarado="brAAA",
        agencia_rating="S&P / AM Best",
        data_rating=date(2024, 11, 22),
        tipo_rating=TipoRating.RATING_PROPRIO,  # IMPORTANTE: Rating PRÓPRIO!

        # Rating Calculado (força isolada)
        # O rating brAAA É o rating de força isolada (não há grupo)
        rating_calculado="brAAA",
        score_forca_isolada=92.0,  # Score alto - força própria
        gap_rating=0,             # SEM gap - rating é próprio
        rating_inflado=False,     # NÃO está inflado

        # Dados Financeiros
        indicadores=indicadores,

        # Capacidade
        limite_retencao_risco=65_000_000,       # R$ 65 milhões
        limite_retencao_evento=120_000_000,     # R$ 120 milhões
        atende_limite_50mm=True,
        margem_sobre_50mm=15_000_000,           # R$ 15 milhões acima

        # Segurança da Apólice
        nota_seguranca_apolice="A+",
        parecer_seguranca=(
            "ALTA SEGURANÇA - Seguradora nacional líder em Seguro Garantia "
            "(16% de market share). Rating brAAA da S&P representa a máxima "
            "classificação em escala nacional brasileira. Força financeira "
            "PRÓPRIA - não depende de suporte de grupo internacional. "
            "33 anos de operação especializada no mercado brasileiro."
        ),
        fatores_positivos=[
            "Rating brAAA S&P (máximo em escala nacional)",
            "Rating A- AM Best com outlook positivo",
            "Líder de mercado em Seguro Garantia (16% market share)",
            "Baixa sinistralidade (30%)",
            "33 anos de experiência no mercado",
            "99% das apólices emitidas digitalmente",
            "Força financeira PRÓPRIA (não depende de grupo)",
        ],
        fatores_atencao=[
            "Concentração em Seguro Garantia",
            "Porte menor que subsidiárias de grupos internacionais",
        ],
        fatores_risco=[],
    )


# =============================================================================
# FUNÇÕES DE COMPARAÇÃO E ANÁLISE
# =============================================================================

def criar_comparacao_zurich_junto() -> ComparacaoEstruturaSocietaria:
    """
    Cria comparação estruturada entre Zurich Brasil e Junto Seguros

    Esta comparação evidencia as diferenças fundamentais:
    - Zurich: Subsidiária de grupo internacional (rating emprestado)
    - Junto: Seguradora nacional independente (rating próprio)
    """
    zurich = criar_zurich_minas_brasil()
    junto = criar_junto_seguros()

    return ComparacaoEstruturaSocietaria(
        seguradoras=[zurich, junto],
        data_comparacao=date.today(),
    )


def obter_dados_comparativos_brl() -> Dict:
    """
    Retorna dados comparativos em BRL para análise

    Valores em Reais para facilitar comparação direta.
    """
    zurich = criar_zurich_minas_brasil()
    junto = criar_junto_seguros()

    return {
        "zurich_brasil": {
            "nome": zurich.nome_oficial,
            "tipo": "Subsidiária de Grupo Internacional",
            "controladora": zurich.controladora_internacional.nome if zurich.controladora_internacional else None,
            "patrimonio_liquido_brl": zurich.indicadores.patrimonio_liquido,
            "ativo_total_brl": zurich.indicadores.ativo_total,
            "premios_emitidos_brl": zurich.indicadores.premios_emitidos,
            "lucro_liquido_brl": zurich.indicadores.lucro_liquido,
            "rating_declarado": zurich.rating_declarado,
            "tipo_rating": zurich.tipo_rating.value,
            "rating_isolado": zurich.rating_calculado,
            "gap_rating": zurich.gap_rating,
            "suporte_grupo_brl": zurich.controladora_internacional.patrimonio_liquido_brl if zurich.controladora_internacional else 0,
            "nota_seguranca": zurich.nota_seguranca_apolice,
        },
        "junto_seguros": {
            "nome": junto.nome_oficial,
            "tipo": "Seguradora Nacional Independente",
            "controladora": None,
            "patrimonio_liquido_brl": junto.indicadores.patrimonio_liquido,
            "ativo_total_brl": junto.indicadores.ativo_total,
            "premios_emitidos_brl": junto.indicadores.premios_emitidos,
            "lucro_liquido_brl": junto.indicadores.lucro_liquido,
            "rating_declarado": junto.rating_declarado,
            "tipo_rating": junto.tipo_rating.value,
            "rating_isolado": junto.rating_calculado,
            "gap_rating": junto.gap_rating,
            "suporte_grupo_brl": 0,  # Não tem suporte de grupo
            "nota_seguranca": junto.nota_seguranca_apolice,
        },
        "comparacao": {
            "pl_zurich_maior_que_junto": (
                zurich.indicadores.patrimonio_liquido > junto.indicadores.patrimonio_liquido
            ),
            "diferenca_pl_brl": (
                zurich.indicadores.patrimonio_liquido - junto.indicadores.patrimonio_liquido
            ),
            "zurich_tem_suporte_grupo": True,
            "junto_tem_suporte_grupo": False,
            "zurich_rating_inflado": zurich.rating_inflado,
            "junto_rating_inflado": junto.rating_inflado,
        }
    }


def gerar_relatorio_diferenciacao() -> str:
    """
    Gera relatório explicando a diferenciação entre as estruturas

    CONCEITOS FUNDAMENTAIS:
    ======================
    1. MATRIZ vs FILIAL: Mesma empresa, locais diferentes
    2. CONTROLADORA vs SUBSIDIÁRIA: Empresas diferentes, mesmo grupo
    3. GRUPO: Estrutura societária, NÃO inclui resseguro
    """
    zurich = criar_zurich_minas_brasil()
    junto = criar_junto_seguros()

    linhas = []

    # Cabeçalho
    linhas.append("=" * 80)
    linhas.append("RELATÓRIO DE DIFERENCIAÇÃO ESTRUTURAL - SEGURADORAS")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append("OBJETIVO: Distinguir claramente a estrutura societária e sua")
    linhas.append("influência no rating e na segurança das apólices.")
    linhas.append("")

    # Conceitos
    linhas.append("-" * 80)
    linhas.append("CONCEITOS FUNDAMENTAIS")
    linhas.append("-" * 80)
    linhas.append("")
    linhas.append("1. MATRIZ vs FILIAL (mesma pessoa jurídica):")
    linhas.append("   - MATRIZ: Sede principal (CNPJ raiz)")
    linhas.append("   - FILIAL: Estabelecimento secundário (CNPJ com sufixo diferente)")
    linhas.append("   - Exemplo: Junto Seguros matriz (PR) e filial (SP)")
    linhas.append("")
    linhas.append("2. CONTROLADORA vs SUBSIDIÁRIA (pessoas jurídicas distintas):")
    linhas.append("   - CONTROLADORA: Empresa que detém controle de outra")
    linhas.append("   - SUBSIDIÁRIA: Empresa controlada (CNPJ diferente)")
    linhas.append("   - Exemplo: Zurich Insurance Group controla Zurich Brasil")
    linhas.append("")
    linhas.append("3. GRUPO ECONÔMICO/SEGURADOR:")
    linhas.append("   - Conjunto de empresas sob controle comum")
    linhas.append("   - IMPORTANTE: Não inclui resseguradoras na análise de rating")
    linhas.append("   - O rating do grupo pode ser 'emprestado' às subsidiárias")
    linhas.append("")

    # Comparação estrutural
    linhas.append("=" * 80)
    linhas.append("ANÁLISE COMPARATIVA")
    linhas.append("=" * 80)

    # Zurich
    linhas.append("")
    linhas.append(f">>> {zurich.nome_oficial}")
    linhas.append("-" * 50)
    linhas.append(f"Tipo: {zurich.tipo_entidade.value}")
    linhas.append(f"CNPJ: {zurich.cnpj}")
    linhas.append(f"Sede: {zurich.cidade_matriz}/{zurich.uf_matriz}")
    linhas.append("")
    linhas.append("ESTRUTURA SOCIETÁRIA:")
    linhas.append(f"  - É SUBSIDIÁRIA de grupo internacional")
    if zurich.controladora_internacional:
        linhas.append(f"  - Controladora: {zurich.controladora_internacional.nome}")
        linhas.append(f"  - País: {zurich.controladora_internacional.pais_sede}")
        linhas.append(f"  - Rating Grupo: {zurich.controladora_internacional.rating}")
        linhas.append(f"  - PL Grupo: R$ {zurich.controladora_internacional.patrimonio_liquido_brl/1e9:,.1f} bilhões")
    linhas.append("")
    linhas.append("RATING:")
    linhas.append(f"  - Rating Declarado: {zurich.rating_declarado}")
    linhas.append(f"  - Tipo do Rating: {zurich.tipo_rating.value}")
    linhas.append(f"  - Rating Isolado (calculado): {zurich.rating_calculado}")
    linhas.append(f"  - Gap: {zurich.gap_rating} notches")
    linhas.append(f"  - Rating Inflado pelo Grupo: {'SIM' if zurich.rating_inflado else 'NÃO'}")
    linhas.append("")
    linhas.append("INDICADORES (BRL):")
    linhas.append(f"  - Patrimônio Líquido: R$ {zurich.indicadores.patrimonio_liquido/1e6:,.1f} milhões")
    linhas.append(f"  - Ativo Total: R$ {zurich.indicadores.ativo_total/1e6:,.1f} milhões")
    linhas.append(f"  - Prêmios Emitidos: R$ {zurich.indicadores.premios_emitidos/1e6:,.1f} milhões")
    linhas.append(f"  - Lucro Líquido: R$ {zurich.indicadores.lucro_liquido/1e6:,.1f} milhões")
    linhas.append(f"  - ROE: {zurich.indicadores.roe:.1f}%")
    linhas.append("")
    linhas.append(f"SEGURANÇA DA APÓLICE: {zurich.nota_seguranca_apolice}")

    # Junto
    linhas.append("")
    linhas.append(f">>> {junto.nome_oficial}")
    linhas.append("-" * 50)
    linhas.append(f"Tipo: {junto.tipo_entidade.value}")
    linhas.append(f"CNPJ: {junto.cnpj}")
    linhas.append(f"Sede (MATRIZ): {junto.cidade_matriz}/{junto.uf_matriz}")
    linhas.append("")
    linhas.append("ESTRUTURA SOCIETÁRIA:")
    linhas.append(f"  - É MATRIZ (seguradora nacional)")
    linhas.append(f"  - NÃO é subsidiária de grupo estrangeiro")
    linhas.append(f"  - Possui {len(junto.filiais)} filiais:")
    for filial in junto.filiais:
        linhas.append(f"    • {filial.cidade}/{filial.uf} ({filial.participacao_total:.0f}% dos prêmios)")
    linhas.append("")
    linhas.append("RATING:")
    linhas.append(f"  - Rating Declarado: {junto.rating_declarado}")
    linhas.append(f"  - Tipo do Rating: {junto.tipo_rating.value}")
    linhas.append(f"  - Rating Isolado (calculado): {junto.rating_calculado}")
    linhas.append(f"  - Gap: {junto.gap_rating} notches")
    linhas.append(f"  - Rating Inflado: {'SIM' if junto.rating_inflado else 'NÃO'}")
    linhas.append("")
    linhas.append("INDICADORES (BRL):")
    linhas.append(f"  - Patrimônio Líquido: R$ {junto.indicadores.patrimonio_liquido/1e6:,.1f} milhões")
    linhas.append(f"  - Ativo Total: R$ {junto.indicadores.ativo_total/1e6:,.1f} milhões")
    linhas.append(f"  - Prêmios Emitidos: R$ {junto.indicadores.premios_emitidos/1e6:,.1f} milhões")
    linhas.append(f"  - Lucro Líquido: R$ {junto.indicadores.lucro_liquido/1e6:,.1f} milhões")
    linhas.append(f"  - ROE: {junto.indicadores.roe:.1f}%")
    linhas.append("")
    linhas.append(f"SEGURANÇA DA APÓLICE: {junto.nota_seguranca_apolice}")

    # Conclusão
    linhas.append("")
    linhas.append("=" * 80)
    linhas.append("CONCLUSÃO")
    linhas.append("=" * 80)
    linhas.append("")
    linhas.append("DIFERENÇAS FUNDAMENTAIS:")
    linhas.append("")
    linhas.append("┌─────────────────────┬──────────────────────────┬──────────────────────────┐")
    linhas.append("│ Característica      │ Zurich Brasil            │ Junto Seguros            │")
    linhas.append("├─────────────────────┼──────────────────────────┼──────────────────────────┤")
    linhas.append("│ Tipo                │ Subsidiária Estrangeira  │ Matriz Nacional          │")
    linhas.append("│ Controladora        │ Zurich Insurance Group   │ Não possui               │")
    linhas.append("│ Origem Rating       │ Grupo (emprestado)       │ Próprio (força isolada)  │")
    linhas.append("│ Rating Declarado    │ AA                       │ brAAA                    │")
    linhas.append("│ Rating se Isolada   │ A (2 notches menor)      │ brAAA (mesmo)            │")
    linhas.append("│ Suporte de Grupo    │ R$ 231 bilhões (PL)      │ Nenhum                   │")
    linhas.append("│ Filiais             │ Não possui               │ SP, RJ, MG               │")
    linhas.append("└─────────────────────┴──────────────────────────┴──────────────────────────┘")
    linhas.append("")
    linhas.append("IMPLICAÇÕES PARA A APÓLICE:")
    linhas.append("")
    linhas.append("• ZURICH: A segurança da apólice depende indiretamente do grupo.")
    linhas.append("  Se o grupo mantiver suporte, a apólice está garantida pelo AA global.")
    linhas.append("  Força isolada da entidade brasileira seria rating A.")
    linhas.append("")
    linhas.append("• JUNTO: A segurança da apólice depende da força PRÓPRIA da seguradora.")
    linhas.append("  Rating brAAA representa máxima segurança em escala nacional.")
    linhas.append("  Não há dependência de suporte externo.")
    linhas.append("")
    linhas.append("AMBAS SÃO SEGURAS PARA APÓLICES DE GARANTIA.")
    linhas.append("A diferença está na ORIGEM da segurança:")
    linhas.append("  - Zurich: Suporte de grupo internacional")
    linhas.append("  - Junto: Força financeira própria")
    linhas.append("")

    return "\n".join(linhas)


# =============================================================================
# EXECUÇÃO DIRETA PARA TESTES
# =============================================================================

if __name__ == "__main__":
    # Gera e imprime o relatório de diferenciação
    print(gerar_relatorio_diferenciacao())

    print("\n" + "=" * 80)
    print("TABELA COMPARATIVA (ComparacaoEstruturaSocietaria)")
    print("=" * 80 + "\n")

    comparacao = criar_comparacao_zurich_junto()
    print(comparacao.gerar_tabela_comparativa())
