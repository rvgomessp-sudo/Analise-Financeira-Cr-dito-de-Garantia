"""
Dados de exemplo de informações de resseguro e grupo econômico
para análise de força financeira isolada

Inclui cenários diversos:
- Seguradoras independentes fortes
- Seguradoras dependentes de grupo com rating inflado
- Seguradoras fronting (alta cessão ao resseguro)
- Seguradoras com capacidade própria insuficiente para 50MM
"""

from typing import List, Tuple
from datetime import date

from ..models.forca_isolada import (
    InformacoesGrupo,
    InformacoesResseguro,
    SeguradoraComResseguro
)
from ..models.seguradora import Seguradora, BalancoPatrimonial, DRE


def carregar_dados_resseguro_grupo() -> List[Tuple[InformacoesGrupo, InformacoesResseguro]]:
    """
    Carrega dados de resseguro e grupo para as seguradoras de exemplo

    Returns:
        Lista de tuplas (InformacoesGrupo, InformacoesResseguro)
    """

    dados = []

    # ============================================================================
    # 1. ALPHA GARANTIAS S.A. - Líder independente, baixa dependência
    # ============================================================================
    alpha_grupo = InformacoesGrupo(
        nome_grupo="Grupo Alpha",
        rating_grupo="AA",
        agencia_rating="S&P",
        patrimonio_liquido_grupo=2_500_000_000,
        carta_suporte_valor=0,  # Não precisa de suporte
        garantia_explicita=False,
        premios_cedidos_grupo=0,  # Não cede para o grupo
        ativos_grupo=50_000_000,  # Pouco investido no grupo
        dividas_grupo=0,
        historico_aportes=0,
        anos_operacao_grupo=25
    )

    alpha_resseguro = InformacoesResseguro(
        premios_cedidos_total=112_500_000,  # 15% - baixa cessão
        sinistros_recuperados_resseguro=41_000_000,
        provisoes_ressegurador=85_000_000,
        retencao_maxima_risco=40_000_000,  # Alta retenção própria
        retencao_maxima_evento=80_000_000,
        quota_parte_percentual=0.10,
        excesso_danos_valor=30_000_000,
        catastrofe_cobertura=200_000_000,
        rating_medio_resseguradores="A+",
        concentracao_principal_ressegurador=0.25,
        ressegurador_grupo=False,
        creditos_resseguro_total=95_000_000,
        provisao_reducao_resseguro=5_000_000
    )
    dados.append((alpha_grupo, alpha_resseguro))

    # ============================================================================
    # 2. BETA CRÉDITO S.A. - Boa performance, moderada dependência de grupo
    # ============================================================================
    beta_grupo = InformacoesGrupo(
        nome_grupo="Grupo Beta Financeiro",
        rating_grupo="A+",
        agencia_rating="Fitch",
        patrimonio_liquido_grupo=1_800_000_000,
        carta_suporte_valor=100_000_000,  # Tem carta de suporte
        garantia_explicita=True,
        premios_cedidos_grupo=30_000_000,  # Alguma cessão intragrupo
        ativos_grupo=80_000_000,  # Investido no grupo
        dividas_grupo=25_000_000,
        historico_aportes=50_000_000,  # Já recebeu aporte
        anos_operacao_grupo=18
    )

    beta_resseguro = InformacoesResseguro(
        premios_cedidos_total=78_000_000,  # 15% - moderada
        sinistros_recuperados_resseguro=33_000_000,
        provisoes_ressegurador=62_000_000,
        retencao_maxima_risco=25_000_000,
        retencao_maxima_evento=50_000_000,
        quota_parte_percentual=0.12,
        excesso_danos_valor=20_000_000,
        catastrofe_cobertura=150_000_000,
        rating_medio_resseguradores="A",
        concentracao_principal_ressegurador=0.35,
        ressegurador_grupo=True,  # Parte do resseguro é do grupo
        creditos_resseguro_total=72_000_000,
        provisao_reducao_resseguro=4_000_000
    )
    dados.append((beta_grupo, beta_resseguro))

    # ============================================================================
    # 3. GAMMA FIANÇA S.A. - Performance mediana, dependência alta
    # ============================================================================
    gamma_grupo = InformacoesGrupo(
        nome_grupo="Grupo Gamma",
        rating_grupo="A",  # Rating do grupo alto
        agencia_rating="AM Best",
        patrimonio_liquido_grupo=1_200_000_000,
        carta_suporte_valor=150_000_000,  # Depende de suporte
        garantia_explicita=True,
        premios_cedidos_grupo=25_000_000,
        ativos_grupo=120_000_000,  # Alto investimento no grupo
        dividas_grupo=40_000_000,
        historico_aportes=80_000_000,  # Múltiplos aportes
        anos_operacao_grupo=12
    )

    gamma_resseguro = InformacoesResseguro(
        premios_cedidos_total=48_000_000,  # 15%
        sinistros_recuperados_resseguro=23_000_000,
        provisoes_ressegurador=42_000_000,
        retencao_maxima_risco=15_000_000,  # Baixa retenção
        retencao_maxima_evento=30_000_000,
        quota_parte_percentual=0.15,
        excesso_danos_valor=12_000_000,
        catastrofe_cobertura=80_000_000,
        rating_medio_resseguradores="A-",
        concentracao_principal_ressegurador=0.45,  # Alta concentração
        ressegurador_grupo=True,
        creditos_resseguro_total=48_000_000,
        provisao_reducao_resseguro=3_000_000
    )
    dados.append((gamma_grupo, gamma_resseguro))

    # ============================================================================
    # 4. DELTA SEGUROS S.A. - Em dificuldade, altíssima dependência
    # ============================================================================
    delta_grupo = InformacoesGrupo(
        nome_grupo="Grupo Delta",
        rating_grupo="BBB+",  # Rating declarado
        agencia_rating="S&P",
        patrimonio_liquido_grupo=600_000_000,
        carta_suporte_valor=80_000_000,
        garantia_explicita=True,
        premios_cedidos_grupo=15_000_000,
        ativos_grupo=60_000_000,
        dividas_grupo=35_000_000,
        historico_aportes=120_000_000,  # Muitos aportes
        anos_operacao_grupo=8
    )

    delta_resseguro = InformacoesResseguro(
        premios_cedidos_total=29_250_000,  # 15%
        sinistros_recuperados_resseguro=18_000_000,
        provisoes_ressegurador=28_000_000,
        retencao_maxima_risco=8_000_000,  # Muito baixa
        retencao_maxima_evento=15_000_000,
        quota_parte_percentual=0.15,
        excesso_danos_valor=6_000_000,
        catastrofe_cobertura=40_000_000,
        rating_medio_resseguradores="BBB",
        concentracao_principal_ressegurador=0.55,  # Muito concentrado
        ressegurador_grupo=True,
        creditos_resseguro_total=32_000_000,
        provisao_reducao_resseguro=2_500_000
    )
    dados.append((delta_grupo, delta_resseguro))

    # ============================================================================
    # 5. EPSILON GARANTIA S.A. - Nova entrante, capacidade limitada
    # ============================================================================
    epsilon_grupo = InformacoesGrupo(
        nome_grupo="Grupo Epsilon",
        rating_grupo="A-",  # Rating do grupo
        agencia_rating="Fitch",
        patrimonio_liquido_grupo=800_000_000,
        carta_suporte_valor=50_000_000,
        garantia_explicita=True,
        premios_cedidos_grupo=10_000_000,
        ativos_grupo=40_000_000,
        dividas_grupo=15_000_000,
        historico_aportes=30_000_000,
        anos_operacao_grupo=5
    )

    epsilon_resseguro = InformacoesResseguro(
        premios_cedidos_total=33_000_000,  # 20%
        sinistros_recuperados_resseguro=9_500_000,
        provisoes_ressegurador=22_000_000,
        retencao_maxima_risco=10_000_000,  # Baixa
        retencao_maxima_evento=20_000_000,
        quota_parte_percentual=0.20,
        excesso_danos_valor=8_000_000,
        catastrofe_cobertura=50_000_000,
        rating_medio_resseguradores="A-",
        concentracao_principal_ressegurador=0.40,
        ressegurador_grupo=True,
        creditos_resseguro_total=28_000_000,
        provisao_reducao_resseguro=2_000_000
    )
    dados.append((epsilon_grupo, epsilon_resseguro))

    # ============================================================================
    # 6. ZETA CRÉDITO GARANTIDO S.A. - Performance sólida, boa independência
    # ============================================================================
    zeta_grupo = InformacoesGrupo(
        nome_grupo="Grupo Zeta Holdings",
        rating_grupo="AA-",
        agencia_rating="S&P",
        patrimonio_liquido_grupo=2_200_000_000,
        carta_suporte_valor=50_000_000,  # Pouco suporte necessário
        garantia_explicita=False,
        premios_cedidos_grupo=20_000_000,
        ativos_grupo=70_000_000,
        dividas_grupo=15_000_000,
        historico_aportes=20_000_000,
        anos_operacao_grupo=20
    )

    zeta_resseguro = InformacoesResseguro(
        premios_cedidos_total=93_000_000,  # 15%
        sinistros_recuperados_resseguro=36_000_000,
        provisoes_ressegurador=75_000_000,
        retencao_maxima_risco=35_000_000,  # Boa retenção
        retencao_maxima_evento=70_000_000,
        quota_parte_percentual=0.12,
        excesso_danos_valor=25_000_000,
        catastrofe_cobertura=180_000_000,
        rating_medio_resseguradores="A+",
        concentracao_principal_ressegurador=0.28,
        ressegurador_grupo=False,
        creditos_resseguro_total=85_000_000,
        provisao_reducao_resseguro=4_500_000
    )
    dados.append((zeta_grupo, zeta_resseguro))

    return dados


def carregar_seguradoras_fronting() -> List[Tuple[Seguradora, InformacoesGrupo, InformacoesResseguro]]:
    """
    Carrega exemplos de seguradoras que operam como fronting
    (alta cessão ao resseguro, baixa retenção própria)

    Estas são seguradoras que usam rating do grupo mas não têm
    capacidade própria para assumir riscos significativos.
    """

    seguradoras_fronting = []

    # ============================================================================
    # FRONTING SEGUROS S.A. - Opera como fronting para grupo internacional
    # ============================================================================
    fronting = Seguradora(
        codigo_susep="11111",
        nome="Fronting Seguros S.A.",
        cnpj="11.111.111/0001-11",
        grupo_economico="Mega Insurance Group",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=30_000_000,
        patrimonio_liquido_ajustado=85_000_000,
        balanco=BalancoPatrimonial(
            disponibilidades=12_000_000,
            aplicacoes_financeiras_cp=45_000_000,
            premios_a_receber=180_000_000,  # Alto - espera recuperar do resseg
            creditos_operacionais=25_000_000,
            outros_creditos_cp=8_000_000,
            aplicacoes_financeiras_lp=35_000_000,
            investimentos=15_000_000,
            imobilizado=5_000_000,
            intangivel=3_000_000,
            outros_ativos_lp=2_000_000,
            provisoes_tecnicas_cp=180_000_000,
            debitos_operacionais=35_000_000,
            depositos_terceiros=15_000_000,
            emprestimos_cp=10_000_000,
            outras_obrigacoes_cp=12_000_000,
            provisoes_tecnicas_lp=95_000_000,
            emprestimos_lp=15_000_000,
            outras_obrigacoes_lp=8_000_000,
            capital_social=50_000_000,
            reservas_capital=10_000_000,
            reservas_lucros=18_000_000,
            ajustes_avaliacao=2_000_000,
            lucros_acumulados=5_000_000,
        ),
        dre=DRE(
            premios_emitidos=450_000_000,
            premios_cedidos_resseguro=382_500_000,  # 85% cedido!
            variacoes_provisoes_tecnicas=-15_000_000,
            premios_ganhos=52_500_000,
            sinistros_ocorridos=-31_500_000,
            custos_aquisicao=-15_750_000,
            outras_despesas_operacionais=-5_250_000,
            receitas_financeiras=8_000_000,
            despesas_financeiras=-2_000_000,
            despesas_administrativas=-12_000_000,
            despesas_tributarias=-3_000_000,
            resultado_operacional=-9_000_000,
            resultado_nao_operacional=500_000,
            irpj_csll=0,
        )
    )

    fronting_grupo = InformacoesGrupo(
        nome_grupo="Mega Insurance Group",
        rating_grupo="AA",  # Rating altíssimo do grupo
        agencia_rating="S&P",
        patrimonio_liquido_grupo=15_000_000_000,  # Grupo gigante
        carta_suporte_valor=200_000_000,
        garantia_explicita=True,
        premios_cedidos_grupo=350_000_000,  # Quase tudo para o grupo
        ativos_grupo=30_000_000,
        dividas_grupo=20_000_000,
        historico_aportes=150_000_000,
        anos_operacao_grupo=8
    )

    fronting_resseguro = InformacoesResseguro(
        premios_cedidos_total=382_500_000,  # 85%!
        sinistros_recuperados_resseguro=28_000_000,
        provisoes_ressegurador=250_000_000,
        retencao_maxima_risco=2_500_000,  # Apenas 2.5MM!
        retencao_maxima_evento=5_000_000,
        quota_parte_percentual=0.85,
        excesso_danos_valor=1_500_000,
        catastrofe_cobertura=300_000_000,  # Alta mas paga pelo grupo
        rating_medio_resseguradores="AA",
        concentracao_principal_ressegurador=0.92,  # 92% no grupo!
        ressegurador_grupo=True,
        creditos_resseguro_total=280_000_000,
        provisao_reducao_resseguro=10_000_000
    )

    seguradoras_fronting.append((fronting, fronting_grupo, fronting_resseguro))

    # ============================================================================
    # FILIAL GARANTIA LTDA. - Subsidiária brasileira de grupo europeu
    # ============================================================================
    filial = Seguradora(
        codigo_susep="22222",
        nome="Filial Garantia Ltda.",
        cnpj="22.222.222/0001-22",
        grupo_economico="European Insurance SE",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=25_000_000,
        patrimonio_liquido_ajustado=65_000_000,
        balanco=BalancoPatrimonial(
            disponibilidades=8_000_000,
            aplicacoes_financeiras_cp=35_000_000,
            premios_a_receber=95_000_000,
            creditos_operacionais=18_000_000,
            outros_creditos_cp=5_000_000,
            aplicacoes_financeiras_lp=28_000_000,
            investimentos=10_000_000,
            imobilizado=4_000_000,
            intangivel=2_000_000,
            outros_ativos_lp=1_500_000,
            provisoes_tecnicas_cp=98_000_000,
            debitos_operacionais=22_000_000,
            depositos_terceiros=10_000_000,
            emprestimos_cp=8_000_000,
            outras_obrigacoes_cp=9_000_000,
            provisoes_tecnicas_lp=55_000_000,
            emprestimos_lp=12_000_000,
            outras_obrigacoes_lp=5_000_000,
            capital_social=40_000_000,
            reservas_capital=8_000_000,
            reservas_lucros=12_000_000,
            ajustes_avaliacao=1_500_000,
            lucros_acumulados=3_500_000,
        ),
        dre=DRE(
            premios_emitidos=280_000_000,
            premios_cedidos_resseguro=210_000_000,  # 75% cedido
            variacoes_provisoes_tecnicas=-10_000_000,
            premios_ganhos=60_000_000,
            sinistros_ocorridos=-33_000_000,
            custos_aquisicao=-12_000_000,
            outras_despesas_operacionais=-6_000_000,
            receitas_financeiras=6_000_000,
            despesas_financeiras=-1_500_000,
            despesas_administrativas=-9_000_000,
            despesas_tributarias=-2_500_000,
            resultado_operacional=2_000_000,
            resultado_nao_operacional=300_000,
            irpj_csll=-800_000,
        )
    )

    filial_grupo = InformacoesGrupo(
        nome_grupo="European Insurance SE",
        rating_grupo="A+",
        agencia_rating="Fitch",
        patrimonio_liquido_grupo=8_000_000_000,
        carta_suporte_valor=100_000_000,
        garantia_explicita=True,
        premios_cedidos_grupo=195_000_000,
        ativos_grupo=25_000_000,
        dividas_grupo=15_000_000,
        historico_aportes=80_000_000,
        anos_operacao_grupo=12
    )

    filial_resseguro = InformacoesResseguro(
        premios_cedidos_total=210_000_000,  # 75%
        sinistros_recuperados_resseguro=25_000_000,
        provisoes_ressegurador=140_000_000,
        retencao_maxima_risco=3_500_000,  # Muito baixa
        retencao_maxima_evento=7_000_000,
        quota_parte_percentual=0.75,
        excesso_danos_valor=2_500_000,
        catastrofe_cobertura=180_000_000,
        rating_medio_resseguradores="A+",
        concentracao_principal_ressegurador=0.85,
        ressegurador_grupo=True,
        creditos_resseguro_total=160_000_000,
        provisao_reducao_resseguro=6_000_000
    )

    seguradoras_fronting.append((filial, filial_grupo, filial_resseguro))

    # ============================================================================
    # MINI GARANTIAS S.A. - Pequena seguradora com capital insuficiente
    # ============================================================================
    mini = Seguradora(
        codigo_susep="33333",
        nome="Mini Garantias S.A.",
        cnpj="33.333.333/0001-33",
        grupo_economico="Grupo Mini",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=20_000_000,
        patrimonio_liquido_ajustado=35_000_000,
        balanco=BalancoPatrimonial(
            disponibilidades=5_000_000,
            aplicacoes_financeiras_cp=22_000_000,
            premios_a_receber=28_000_000,
            creditos_operacionais=8_000_000,
            outros_creditos_cp=3_000_000,
            aplicacoes_financeiras_lp=18_000_000,
            investimentos=5_000_000,
            imobilizado=2_500_000,
            intangivel=1_500_000,
            outros_ativos_lp=1_000_000,
            provisoes_tecnicas_cp=42_000_000,
            debitos_operacionais=12_000_000,
            depositos_terceiros=6_000_000,
            emprestimos_cp=5_000_000,
            outras_obrigacoes_cp=4_000_000,
            provisoes_tecnicas_lp=25_000_000,
            emprestimos_lp=8_000_000,
            outras_obrigacoes_lp=3_000_000,
            capital_social=25_000_000,
            reservas_capital=5_000_000,
            reservas_lucros=5_000_000,
            ajustes_avaliacao=500_000,
            lucros_acumulados=-500_000,
        ),
        dre=DRE(
            premios_emitidos=85_000_000,
            premios_cedidos_resseguro=51_000_000,  # 60% cedido
            variacoes_provisoes_tecnicas=-4_000_000,
            premios_ganhos=30_000_000,
            sinistros_ocorridos=-21_000_000,  # 70% sinistralidade
            custos_aquisicao=-6_000_000,
            outras_despesas_operacionais=-3_000_000,
            receitas_financeiras=3_500_000,
            despesas_financeiras=-1_200_000,
            despesas_administrativas=-5_000_000,
            despesas_tributarias=-1_500_000,
            resultado_operacional=-4_200_000,
            resultado_nao_operacional=-200_000,
            irpj_csll=0,
        )
    )

    mini_grupo = InformacoesGrupo(
        nome_grupo="Grupo Mini",
        rating_grupo="BBB",  # Rating do grupo
        agencia_rating="AM Best",
        patrimonio_liquido_grupo=200_000_000,
        carta_suporte_valor=25_000_000,
        garantia_explicita=True,
        premios_cedidos_grupo=30_000_000,
        ativos_grupo=12_000_000,
        dividas_grupo=8_000_000,
        historico_aportes=40_000_000,
        anos_operacao_grupo=6
    )

    mini_resseguro = InformacoesResseguro(
        premios_cedidos_total=51_000_000,  # 60%
        sinistros_recuperados_resseguro=12_500_000,
        provisoes_ressegurador=38_000_000,
        retencao_maxima_risco=1_750_000,  # Apenas 1.75MM!
        retencao_maxima_evento=3_500_000,
        quota_parte_percentual=0.60,
        excesso_danos_valor=1_000_000,
        catastrofe_cobertura=25_000_000,
        rating_medio_resseguradores="BBB+",
        concentracao_principal_ressegurador=0.65,
        ressegurador_grupo=True,
        creditos_resseguro_total=42_000_000,
        provisao_reducao_resseguro=2_500_000
    )

    seguradoras_fronting.append((mini, mini_grupo, mini_resseguro))

    return seguradoras_fronting


def get_limites_referencia() -> dict:
    """
    Retorna os limites de referência para análise

    Returns:
        Dicionário com limites e suas descrições
    """
    return {
        'limite_capacidade_minima': {
            'valor': 50_000_000,
            'descricao': 'Capacidade mínima de retenção própria por risco',
            'unidade': 'BRL'
        },
        'limite_cessao_maxima': {
            'valor': 0.50,
            'descricao': 'Máximo aceitável de cessão ao resseguro',
            'unidade': '%'
        },
        'limite_concentracao_grupo': {
            'valor': 0.30,
            'descricao': 'Máximo de concentração de resseguro no grupo',
            'unidade': '%'
        },
        'limite_suficiencia_capital': {
            'valor': 1.50,
            'descricao': 'Mínimo de suficiência de capital isolada',
            'unidade': 'x'
        },
        'limite_gap_rating': {
            'valor': 2,
            'descricao': 'Máximo de notches de gap entre rating grupo e isolado',
            'unidade': 'notches'
        }
    }
