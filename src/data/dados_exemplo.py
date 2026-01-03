"""
Dados de exemplo de seguradoras para demonstração do sistema
Valores fictícios baseados em padrões do mercado brasileiro
"""

from datetime import date
from typing import List

from ..models.seguradora import (
    Seguradora,
    BalancoPatrimonial,
    DRE
)


def carregar_dados_exemplo() -> List[Seguradora]:
    """
    Carrega dados de exemplo de seguradoras fictícias

    Returns:
        Lista de objetos Seguradora com dados financeiros
    """
    seguradoras = []

    # ============================================================================
    # SEGURADORA ALPHA GARANTIAS S.A. - Líder de mercado, excelente saúde financeira
    # ============================================================================
    alpha = Seguradora(
        codigo_susep="05355",
        nome="Alpha Garantias S.A.",
        cnpj="12.345.678/0001-90",
        grupo_economico="Grupo Alpha",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=150_000_000,
        patrimonio_liquido_ajustado=850_000_000,
        balanco=BalancoPatrimonial(
            # Ativo Circulante
            disponibilidades=120_000_000,
            aplicacoes_financeiras_cp=580_000_000,
            premios_a_receber=95_000_000,
            creditos_operacionais=45_000_000,
            outros_creditos_cp=25_000_000,
            # Ativo Não Circulante
            aplicacoes_financeiras_lp=420_000_000,
            investimentos=80_000_000,
            imobilizado=35_000_000,
            intangivel=15_000_000,
            outros_ativos_lp=10_000_000,
            # Passivo Circulante
            provisoes_tecnicas_cp=380_000_000,
            debitos_operacionais=55_000_000,
            depositos_terceiros=30_000_000,
            emprestimos_cp=0,
            outras_obrigacoes_cp=40_000_000,
            # Passivo Não Circulante
            provisoes_tecnicas_lp=220_000_000,
            emprestimos_lp=0,
            outras_obrigacoes_lp=20_000_000,
            # Patrimônio Líquido
            capital_social=400_000_000,
            reservas_capital=50_000_000,
            reservas_lucros=280_000_000,
            ajustes_avaliacao=15_000_000,
            lucros_acumulados=55_000_000,
        ),
        dre=DRE(
            premios_emitidos=750_000_000,
            premios_cedidos_resseguro=112_500_000,
            variacoes_provisoes_tecnicas=-25_000_000,
            premios_ganhos=612_500_000,
            sinistros_ocorridos=-275_625_000,  # 45% de sinistralidade
            custos_aquisicao=-91_875_000,
            outras_despesas_operacionais=-30_625_000,
            receitas_financeiras=95_000_000,
            despesas_financeiras=-8_000_000,
            despesas_administrativas=-85_000_000,
            despesas_tributarias=-18_000_000,
            resultado_operacional=198_375_000,
            resultado_nao_operacional=5_000_000,
            irpj_csll=-68_000_000,
        )
    )
    seguradoras.append(alpha)

    # ============================================================================
    # SEGURADORA BETA CRÉDITO S.A. - Boa performance, mercado consolidado
    # ============================================================================
    beta = Seguradora(
        codigo_susep="06123",
        nome="Beta Crédito S.A.",
        cnpj="23.456.789/0001-01",
        grupo_economico="Grupo Beta Financeiro",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=100_000_000,
        patrimonio_liquido_ajustado=520_000_000,
        balanco=BalancoPatrimonial(
            # Ativo Circulante
            disponibilidades=65_000_000,
            aplicacoes_financeiras_cp=320_000_000,
            premios_a_receber=72_000_000,
            creditos_operacionais=35_000_000,
            outros_creditos_cp=18_000_000,
            # Ativo Não Circulante
            aplicacoes_financeiras_lp=280_000_000,
            investimentos=45_000_000,
            imobilizado=28_000_000,
            intangivel=12_000_000,
            outros_ativos_lp=8_000_000,
            # Passivo Circulante
            provisoes_tecnicas_cp=245_000_000,
            debitos_operacionais=42_000_000,
            depositos_terceiros=22_000_000,
            emprestimos_cp=15_000_000,
            outras_obrigacoes_cp=28_000_000,
            # Passivo Não Circulante
            provisoes_tecnicas_lp=140_000_000,
            emprestimos_lp=25_000_000,
            outras_obrigacoes_lp=15_000_000,
            # Patrimônio Líquido
            capital_social=250_000_000,
            reservas_capital=35_000_000,
            reservas_lucros=180_000_000,
            ajustes_avaliacao=8_000_000,
            lucros_acumulados=35_000_000,
        ),
        dre=DRE(
            premios_emitidos=520_000_000,
            premios_cedidos_resseguro=78_000_000,
            variacoes_provisoes_tecnicas=-18_000_000,
            premios_ganhos=424_000_000,
            sinistros_ocorridos=-220_480_000,  # 52% de sinistralidade
            custos_aquisicao=-67_840_000,
            outras_despesas_operacionais=-21_200_000,
            receitas_financeiras=58_000_000,
            despesas_financeiras=-7_500_000,
            despesas_administrativas=-62_000_000,
            despesas_tributarias=-12_000_000,
            resultado_operacional=90_980_000,
            resultado_nao_operacional=2_500_000,
            irpj_csll=-31_000_000,
        )
    )
    seguradoras.append(beta)

    # ============================================================================
    # SEGURADORA GAMMA FIANÇA S.A. - Performance mediana, estável
    # ============================================================================
    gamma = Seguradora(
        codigo_susep="07890",
        nome="Gamma Fiança S.A.",
        cnpj="34.567.890/0001-12",
        grupo_economico="Grupo Gamma",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=80_000_000,
        patrimonio_liquido_ajustado=280_000_000,
        balanco=BalancoPatrimonial(
            # Ativo Circulante
            disponibilidades=35_000_000,
            aplicacoes_financeiras_cp=185_000_000,
            premios_a_receber=58_000_000,
            creditos_operacionais=28_000_000,
            outros_creditos_cp=14_000_000,
            # Ativo Não Circulante
            aplicacoes_financeiras_lp=145_000_000,
            investimentos=32_000_000,
            imobilizado=22_000_000,
            intangivel=8_000_000,
            outros_ativos_lp=5_000_000,
            # Passivo Circulante
            provisoes_tecnicas_cp=165_000_000,
            debitos_operacionais=35_000_000,
            depositos_terceiros=18_000_000,
            emprestimos_cp=20_000_000,
            outras_obrigacoes_cp=22_000_000,
            # Passivo Não Circulante
            provisoes_tecnicas_lp=95_000_000,
            emprestimos_lp=35_000_000,
            outras_obrigacoes_lp=12_000_000,
            # Patrimônio Líquido
            capital_social=150_000_000,
            reservas_capital=25_000_000,
            reservas_lucros=85_000_000,
            ajustes_avaliacao=5_000_000,
            lucros_acumulados=10_000_000,
        ),
        dre=DRE(
            premios_emitidos=320_000_000,
            premios_cedidos_resseguro=48_000_000,
            variacoes_provisoes_tecnicas=-12_000_000,
            premios_ganhos=260_000_000,
            sinistros_ocorridos=-156_000_000,  # 60% de sinistralidade
            custos_aquisicao=-46_800_000,
            outras_despesas_operacionais=-15_600_000,
            receitas_financeiras=32_000_000,
            despesas_financeiras=-6_000_000,
            despesas_administrativas=-42_000_000,
            despesas_tributarias=-8_000_000,
            resultado_operacional=17_600_000,
            resultado_nao_operacional=1_500_000,
            irpj_csll=-6_500_000,
        )
    )
    seguradoras.append(gamma)

    # ============================================================================
    # SEGURADORA DELTA SEGUROS S.A. - Em recuperação, alguns indicadores fracos
    # ============================================================================
    delta = Seguradora(
        codigo_susep="08456",
        nome="Delta Seguros S.A.",
        cnpj="45.678.901/0001-23",
        grupo_economico="Grupo Delta",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=60_000_000,
        patrimonio_liquido_ajustado=145_000_000,
        balanco=BalancoPatrimonial(
            # Ativo Circulante
            disponibilidades=18_000_000,
            aplicacoes_financeiras_cp=95_000_000,
            premios_a_receber=48_000_000,
            creditos_operacionais=22_000_000,
            outros_creditos_cp=12_000_000,
            # Ativo Não Circulante
            aplicacoes_financeiras_lp=78_000_000,
            investimentos=25_000_000,
            imobilizado=18_000_000,
            intangivel=6_000_000,
            outros_ativos_lp=4_000_000,
            # Passivo Circulante
            provisoes_tecnicas_cp=110_000_000,
            debitos_operacionais=32_000_000,
            depositos_terceiros=15_000_000,
            emprestimos_cp=25_000_000,
            outras_obrigacoes_cp=18_000_000,
            # Passivo Não Circulante
            provisoes_tecnicas_lp=65_000_000,
            emprestimos_lp=40_000_000,
            outras_obrigacoes_lp=10_000_000,
            # Patrimônio Líquido
            capital_social=100_000_000,
            reservas_capital=15_000_000,
            reservas_lucros=25_000_000,
            ajustes_avaliacao=2_000_000,
            lucros_acumulados=-4_000_000,
        ),
        dre=DRE(
            premios_emitidos=195_000_000,
            premios_cedidos_resseguro=29_250_000,
            variacoes_provisoes_tecnicas=-8_000_000,
            premios_ganhos=157_750_000,
            sinistros_ocorridos=-118_312_500,  # 75% de sinistralidade
            custos_aquisicao=-31_550_000,
            outras_despesas_operacionais=-12_620_000,
            receitas_financeiras=16_500_000,
            despesas_financeiras=-5_500_000,
            despesas_administrativas=-28_000_000,
            despesas_tributarias=-5_500_000,
            resultado_operacional=-27_232_500,
            resultado_nao_operacional=-500_000,
            irpj_csll=0,  # Prejuízo, sem IR
        )
    )
    seguradoras.append(delta)

    # ============================================================================
    # SEGURADORA EPSILON GARANTIA S.A. - Nova entrante, em crescimento
    # ============================================================================
    epsilon = Seguradora(
        codigo_susep="09012",
        nome="Epsilon Garantia S.A.",
        cnpj="56.789.012/0001-34",
        grupo_economico="Grupo Epsilon",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=50_000_000,
        patrimonio_liquido_ajustado=180_000_000,
        balanco=BalancoPatrimonial(
            # Ativo Circulante
            disponibilidades=42_000_000,
            aplicacoes_financeiras_cp=125_000_000,
            premios_a_receber=35_000_000,
            creditos_operacionais=18_000_000,
            outros_creditos_cp=10_000_000,
            # Ativo Não Circulante
            aplicacoes_financeiras_lp=95_000_000,
            investimentos=20_000_000,
            imobilizado=12_000_000,
            intangivel=5_000_000,
            outros_ativos_lp=3_000_000,
            # Passivo Circulante
            provisoes_tecnicas_cp=85_000_000,
            debitos_operacionais=22_000_000,
            depositos_terceiros=12_000_000,
            emprestimos_cp=8_000_000,
            outras_obrigacoes_cp=15_000_000,
            # Passivo Não Circulante
            provisoes_tecnicas_lp=52_000_000,
            emprestimos_lp=18_000_000,
            outras_obrigacoes_lp=8_000_000,
            # Patrimônio Líquido
            capital_social=120_000_000,
            reservas_capital=20_000_000,
            reservas_lucros=35_000_000,
            ajustes_avaliacao=3_000_000,
            lucros_acumulados=10_000_000,
        ),
        dre=DRE(
            premios_emitidos=165_000_000,
            premios_cedidos_resseguro=33_000_000,
            variacoes_provisoes_tecnicas=-6_000_000,
            premios_ganhos=126_000_000,
            sinistros_ocorridos=-63_000_000,  # 50% de sinistralidade
            custos_aquisicao=-25_200_000,
            outras_despesas_operacionais=-8_820_000,
            receitas_financeiras=21_000_000,
            despesas_financeiras=-3_200_000,
            despesas_administrativas=-22_000_000,
            despesas_tributarias=-4_500_000,
            resultado_operacional=20_280_000,
            resultado_nao_operacional=800_000,
            irpj_csll=-7_200_000,
        )
    )
    seguradoras.append(epsilon)

    # ============================================================================
    # SEGURADORA ZETA CRÉDITO GARANTIDO S.A. - Performance sólida
    # ============================================================================
    zeta = Seguradora(
        codigo_susep="10234",
        nome="Zeta Crédito Garantido S.A.",
        cnpj="67.890.123/0001-45",
        grupo_economico="Grupo Zeta Holdings",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=120_000_000,
        patrimonio_liquido_ajustado=680_000_000,
        balanco=BalancoPatrimonial(
            # Ativo Circulante
            disponibilidades=95_000_000,
            aplicacoes_financeiras_cp=420_000_000,
            premios_a_receber=85_000_000,
            creditos_operacionais=40_000_000,
            outros_creditos_cp=22_000_000,
            # Ativo Não Circulante
            aplicacoes_financeiras_lp=350_000_000,
            investimentos=65_000_000,
            imobilizado=30_000_000,
            intangivel=12_000_000,
            outros_ativos_lp=8_000_000,
            # Passivo Circulante
            provisoes_tecnicas_cp=320_000_000,
            debitos_operacionais=48_000_000,
            depositos_terceiros=25_000_000,
            emprestimos_cp=12_000_000,
            outras_obrigacoes_cp=35_000_000,
            # Passivo Não Circulante
            provisoes_tecnicas_lp=185_000_000,
            emprestimos_lp=28_000_000,
            outras_obrigacoes_lp=18_000_000,
            # Patrimônio Líquido
            capital_social=350_000_000,
            reservas_capital=45_000_000,
            reservas_lucros=220_000_000,
            ajustes_avaliacao=12_000_000,
            lucros_acumulados=40_000_000,
        ),
        dre=DRE(
            premios_emitidos=620_000_000,
            premios_cedidos_resseguro=93_000_000,
            variacoes_provisoes_tecnicas=-22_000_000,
            premios_ganhos=505_000_000,
            sinistros_ocorridos=-242_400_000,  # 48% de sinistralidade
            custos_aquisicao=-80_800_000,
            outras_despesas_operacionais=-25_250_000,
            receitas_financeiras=78_000_000,
            despesas_financeiras=-7_000_000,
            despesas_administrativas=-72_000_000,
            despesas_tributarias=-15_000_000,
            resultado_operacional=140_550_000,
            resultado_nao_operacional=4_000_000,
            irpj_csll=-49_000_000,
        )
    )
    seguradoras.append(zeta)

    return seguradoras


def carregar_dados_csv(filepath: str) -> List[Seguradora]:
    """
    Carrega dados de seguradoras a partir de um arquivo CSV

    Args:
        filepath: Caminho para o arquivo CSV

    Returns:
        Lista de objetos Seguradora
    """
    import pandas as pd

    df = pd.read_csv(filepath)
    seguradoras = []

    for _, row in df.iterrows():
        seguradora = Seguradora(
            codigo_susep=str(row.get('codigo_susep', '')),
            nome=str(row.get('nome', '')),
            cnpj=str(row.get('cnpj', '')),
            grupo_economico=str(row.get('grupo_economico', '')),
            ano_exercicio=int(row.get('ano_exercicio', 0)),
            balanco=BalancoPatrimonial(
                disponibilidades=float(row.get('disponibilidades', 0)),
                aplicacoes_financeiras_cp=float(row.get('aplicacoes_financeiras_cp', 0)),
                premios_a_receber=float(row.get('premios_a_receber', 0)),
                creditos_operacionais=float(row.get('creditos_operacionais', 0)),
                outros_creditos_cp=float(row.get('outros_creditos_cp', 0)),
                aplicacoes_financeiras_lp=float(row.get('aplicacoes_financeiras_lp', 0)),
                investimentos=float(row.get('investimentos', 0)),
                imobilizado=float(row.get('imobilizado', 0)),
                intangivel=float(row.get('intangivel', 0)),
                outros_ativos_lp=float(row.get('outros_ativos_lp', 0)),
                provisoes_tecnicas_cp=float(row.get('provisoes_tecnicas_cp', 0)),
                debitos_operacionais=float(row.get('debitos_operacionais', 0)),
                depositos_terceiros=float(row.get('depositos_terceiros', 0)),
                emprestimos_cp=float(row.get('emprestimos_cp', 0)),
                outras_obrigacoes_cp=float(row.get('outras_obrigacoes_cp', 0)),
                provisoes_tecnicas_lp=float(row.get('provisoes_tecnicas_lp', 0)),
                emprestimos_lp=float(row.get('emprestimos_lp', 0)),
                outras_obrigacoes_lp=float(row.get('outras_obrigacoes_lp', 0)),
                capital_social=float(row.get('capital_social', 0)),
                reservas_capital=float(row.get('reservas_capital', 0)),
                reservas_lucros=float(row.get('reservas_lucros', 0)),
                ajustes_avaliacao=float(row.get('ajustes_avaliacao', 0)),
                lucros_acumulados=float(row.get('lucros_acumulados', 0)),
            ),
            dre=DRE(
                premios_emitidos=float(row.get('premios_emitidos', 0)),
                premios_cedidos_resseguro=float(row.get('premios_cedidos_resseguro', 0)),
                variacoes_provisoes_tecnicas=float(row.get('variacoes_provisoes_tecnicas', 0)),
                premios_ganhos=float(row.get('premios_ganhos', 0)),
                sinistros_ocorridos=float(row.get('sinistros_ocorridos', 0)),
                custos_aquisicao=float(row.get('custos_aquisicao', 0)),
                outras_despesas_operacionais=float(row.get('outras_despesas_operacionais', 0)),
                receitas_financeiras=float(row.get('receitas_financeiras', 0)),
                despesas_financeiras=float(row.get('despesas_financeiras', 0)),
                despesas_administrativas=float(row.get('despesas_administrativas', 0)),
                despesas_tributarias=float(row.get('despesas_tributarias', 0)),
                resultado_operacional=float(row.get('resultado_operacional', 0)),
                resultado_nao_operacional=float(row.get('resultado_nao_operacional', 0)),
                irpj_csll=float(row.get('irpj_csll', 0)),
            ),
            capital_minimo_requerido=float(row.get('capital_minimo_requerido', 0)),
            patrimonio_liquido_ajustado=float(row.get('patrimonio_liquido_ajustado', 0)),
        )
        seguradoras.append(seguradora)

    return seguradoras
