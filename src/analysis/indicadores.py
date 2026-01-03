"""
Analisador de Indicadores Financeiros para Seguradoras
Calcula e avalia indicadores de solvência, liquidez, rentabilidade e risco
"""

from typing import Tuple
from ..models.seguradora import Seguradora, IndicadoresFinanceiros


class AnalisadorIndicadores:
    """
    Classe responsável por calcular e analisar indicadores financeiros
    de seguradoras para avaliação de força financeira
    """

    # Pesos para cálculo do score de força financeira
    PESOS = {
        'solvencia': 0.25,
        'liquidez': 0.20,
        'rentabilidade': 0.20,
        'sinistralidade': 0.20,
        'estrutura': 0.15
    }

    # Limites para classificação de risco
    LIMITES_RATING = [
        (90, 'AAA'),   # Excepcional
        (80, 'AA'),    # Muito forte
        (70, 'A'),     # Forte
        (60, 'BBB'),   # Adequado
        (50, 'BB'),    # Menos vulnerável
        (40, 'B'),     # Mais vulnerável
        (30, 'CCC'),   # Atualmente vulnerável
        (20, 'CC'),    # Altamente vulnerável
        (10, 'C'),     # Em falência iminente
        (0, 'D'),      # Em inadimplência
    ]

    def calcular_indicadores(self, seguradora: Seguradora) -> IndicadoresFinanceiros:
        """
        Calcula todos os indicadores financeiros para uma seguradora

        Args:
            seguradora: Objeto Seguradora com balanço e DRE

        Returns:
            IndicadoresFinanceiros preenchidos
        """
        indicadores = IndicadoresFinanceiros(
            nome_seguradora=seguradora.nome,
            data_referencia=seguradora.data_balanco
        )

        balanco = seguradora.balanco
        dre = seguradora.dre

        # Indicadores de Solvência
        indicadores.indice_solvencia = self._calcular_indice_solvencia(balanco)
        indicadores.margem_solvencia = self._calcular_margem_solvencia(seguradora)
        indicadores.cobertura_provisoes = self._calcular_cobertura_provisoes(balanco)

        # Indicadores de Liquidez
        indicadores.liquidez_corrente = self._calcular_liquidez_corrente(balanco)
        indicadores.liquidez_seca = self._calcular_liquidez_seca(balanco)
        indicadores.liquidez_imediata = self._calcular_liquidez_imediata(balanco)

        # Indicadores de Rentabilidade
        indicadores.roe = self._calcular_roe(balanco, dre)
        indicadores.roa = self._calcular_roa(balanco, dre)
        indicadores.margem_liquida = self._calcular_margem_liquida(dre)
        indicadores.margem_operacional = self._calcular_margem_operacional(dre)

        # Indicadores de Sinistralidade
        indicadores.indice_sinistralidade = self._calcular_sinistralidade(dre)
        indicadores.indice_despesas = self._calcular_indice_despesas(dre)
        indicadores.indice_combinado = self._calcular_indice_combinado(dre)
        indicadores.indice_combinado_ampliado = self._calcular_combinado_ampliado(dre)

        # Indicadores de Estrutura
        indicadores.endividamento = self._calcular_endividamento(balanco)
        indicadores.imobilizacao_pl = self._calcular_imobilizacao_pl(balanco)
        indicadores.alavancagem = self._calcular_alavancagem(balanco, dre)

        # Cálculo do Score e Rating
        indicadores.score_forca_financeira = self._calcular_score_forca_financeira(indicadores)
        indicadores.classificacao_risco = self._determinar_rating(indicadores.score_forca_financeira)

        return indicadores

    def _safe_divide(self, numerador: float, denominador: float, default: float = 0.0) -> float:
        """Divisão segura evitando divisão por zero"""
        if denominador == 0:
            return default
        return numerador / denominador

    # ==================== INDICADORES DE SOLVÊNCIA ====================

    def _calcular_indice_solvencia(self, balanco) -> float:
        """
        Índice de Solvência = PL / Passivo Exigível
        Indica capacidade de pagar todas as obrigações
        """
        return self._safe_divide(
            balanco.patrimonio_liquido,
            balanco.passivo_exigivel
        )

    def _calcular_margem_solvencia(self, seguradora: Seguradora) -> float:
        """
        Margem de Solvência = PLA - CMR
        Patrimônio Líquido Ajustado - Capital Mínimo Requerido
        """
        pla = seguradora.patrimonio_liquido_ajustado
        cmr = seguradora.capital_minimo_requerido

        if pla == 0:
            pla = seguradora.balanco.patrimonio_liquido

        return pla - cmr

    def _calcular_cobertura_provisoes(self, balanco) -> float:
        """
        Cobertura de Provisões = Ativos Garantidores / Provisões Técnicas
        Ativos garantidores = Aplicações Financeiras + Disponibilidades
        """
        ativos_garantidores = (
            balanco.disponibilidades +
            balanco.aplicacoes_financeiras_cp +
            balanco.aplicacoes_financeiras_lp
        )
        return self._safe_divide(
            ativos_garantidores,
            balanco.provisoes_tecnicas_total
        )

    # ==================== INDICADORES DE LIQUIDEZ ====================

    def _calcular_liquidez_corrente(self, balanco) -> float:
        """
        Liquidez Corrente = Ativo Circulante / Passivo Circulante
        """
        return self._safe_divide(
            balanco.ativo_circulante,
            balanco.passivo_circulante
        )

    def _calcular_liquidez_seca(self, balanco) -> float:
        """
        Liquidez Seca = (AC - Prêmios a Receber) / PC
        Para seguradoras, prêmios a receber são equivalentes a estoques
        """
        return self._safe_divide(
            balanco.ativo_circulante - balanco.premios_a_receber,
            balanco.passivo_circulante
        )

    def _calcular_liquidez_imediata(self, balanco) -> float:
        """
        Liquidez Imediata = (Disponibilidades + Aplicações CP) / PC
        """
        ativos_liquidos = balanco.disponibilidades + balanco.aplicacoes_financeiras_cp
        return self._safe_divide(
            ativos_liquidos,
            balanco.passivo_circulante
        )

    # ==================== INDICADORES DE RENTABILIDADE ====================

    def _calcular_roe(self, balanco, dre) -> float:
        """
        ROE (Return on Equity) = Lucro Líquido / Patrimônio Líquido
        """
        return self._safe_divide(
            dre.lucro_liquido,
            balanco.patrimonio_liquido
        )

    def _calcular_roa(self, balanco, dre) -> float:
        """
        ROA (Return on Assets) = Lucro Líquido / Ativo Total
        """
        return self._safe_divide(
            dre.lucro_liquido,
            balanco.ativo_total
        )

    def _calcular_margem_liquida(self, dre) -> float:
        """
        Margem Líquida = Lucro Líquido / Prêmios Ganhos
        """
        return self._safe_divide(
            dre.lucro_liquido,
            dre.premios_ganhos
        )

    def _calcular_margem_operacional(self, dre) -> float:
        """
        Margem Operacional = Resultado Técnico / Prêmios Ganhos
        """
        return self._safe_divide(
            dre.resultado_tecnico,
            dre.premios_ganhos
        )

    # ==================== INDICADORES DE SINISTRALIDADE ====================

    def _calcular_sinistralidade(self, dre) -> float:
        """
        Índice de Sinistralidade = Sinistros Ocorridos / Prêmios Ganhos
        """
        return self._safe_divide(
            abs(dre.sinistros_ocorridos),
            dre.premios_ganhos
        )

    def _calcular_indice_despesas(self, dre) -> float:
        """
        Índice de Despesas = (Custos Aquisição + Desp. Adm) / Prêmios Ganhos
        """
        despesas = abs(dre.custos_aquisicao) + abs(dre.despesas_administrativas)
        return self._safe_divide(despesas, dre.premios_ganhos)

    def _calcular_indice_combinado(self, dre) -> float:
        """
        Índice Combinado = Sinistralidade + Índice de Despesas
        Se < 100%, a operação é lucrativa
        """
        sinistralidade = self._calcular_sinistralidade(dre)
        despesas = self._calcular_indice_despesas(dre)
        return sinistralidade + despesas

    def _calcular_combinado_ampliado(self, dre) -> float:
        """
        Índice Combinado Ampliado = Combinado - Resultado Financeiro/Prêmios
        Considera o impacto das receitas financeiras
        """
        combinado = self._calcular_indice_combinado(dre)
        resultado_fin_ratio = self._safe_divide(
            dre.resultado_financeiro,
            dre.premios_ganhos
        )
        return combinado - resultado_fin_ratio

    # ==================== INDICADORES DE ESTRUTURA ====================

    def _calcular_endividamento(self, balanco) -> float:
        """
        Endividamento = Passivo Exigível / Ativo Total
        """
        return self._safe_divide(
            balanco.passivo_exigivel,
            balanco.ativo_total
        )

    def _calcular_imobilizacao_pl(self, balanco) -> float:
        """
        Imobilização do PL = (Imobilizado + Intangível) / PL
        """
        imobilizado = balanco.imobilizado + balanco.intangivel
        return self._safe_divide(
            imobilizado,
            balanco.patrimonio_liquido
        )

    def _calcular_alavancagem(self, balanco, dre) -> float:
        """
        Alavancagem = Prêmios Emitidos / Patrimônio Líquido
        Mede exposição ao risco
        """
        return self._safe_divide(
            dre.premios_emitidos,
            balanco.patrimonio_liquido
        )

    # ==================== SCORE E RATING ====================

    def _calcular_score_forca_financeira(self, indicadores: IndicadoresFinanceiros) -> float:
        """
        Calcula o score de força financeira (0-100)
        Baseado em todos os indicadores com pesos definidos
        """
        # Score de Solvência (0-100)
        score_solvencia = self._pontuar_solvencia(indicadores)

        # Score de Liquidez (0-100)
        score_liquidez = self._pontuar_liquidez(indicadores)

        # Score de Rentabilidade (0-100)
        score_rentabilidade = self._pontuar_rentabilidade(indicadores)

        # Score de Sinistralidade (0-100)
        score_sinistralidade = self._pontuar_sinistralidade(indicadores)

        # Score de Estrutura (0-100)
        score_estrutura = self._pontuar_estrutura(indicadores)

        # Score final ponderado
        score_final = (
            score_solvencia * self.PESOS['solvencia'] +
            score_liquidez * self.PESOS['liquidez'] +
            score_rentabilidade * self.PESOS['rentabilidade'] +
            score_sinistralidade * self.PESOS['sinistralidade'] +
            score_estrutura * self.PESOS['estrutura']
        )

        return round(min(max(score_final, 0), 100), 2)

    def _pontuar_solvencia(self, indicadores: IndicadoresFinanceiros) -> float:
        """Pontua indicadores de solvência"""
        score = 0

        # Índice de Solvência (peso 40%)
        if indicadores.indice_solvencia >= 1.5:
            score += 40
        elif indicadores.indice_solvencia >= 1.0:
            score += 30
        elif indicadores.indice_solvencia >= 0.7:
            score += 20
        elif indicadores.indice_solvencia >= 0.5:
            score += 10

        # Cobertura de Provisões (peso 60%)
        if indicadores.cobertura_provisoes >= 1.2:
            score += 60
        elif indicadores.cobertura_provisoes >= 1.0:
            score += 45
        elif indicadores.cobertura_provisoes >= 0.9:
            score += 30
        elif indicadores.cobertura_provisoes >= 0.8:
            score += 15

        return score

    def _pontuar_liquidez(self, indicadores: IndicadoresFinanceiros) -> float:
        """Pontua indicadores de liquidez"""
        score = 0

        # Liquidez Corrente (peso 40%)
        if indicadores.liquidez_corrente >= 1.5:
            score += 40
        elif indicadores.liquidez_corrente >= 1.2:
            score += 30
        elif indicadores.liquidez_corrente >= 1.0:
            score += 20
        elif indicadores.liquidez_corrente >= 0.8:
            score += 10

        # Liquidez Imediata (peso 60%)
        if indicadores.liquidez_imediata >= 1.0:
            score += 60
        elif indicadores.liquidez_imediata >= 0.7:
            score += 45
        elif indicadores.liquidez_imediata >= 0.5:
            score += 30
        elif indicadores.liquidez_imediata >= 0.3:
            score += 15

        return score

    def _pontuar_rentabilidade(self, indicadores: IndicadoresFinanceiros) -> float:
        """Pontua indicadores de rentabilidade"""
        score = 0

        # ROE (peso 50%)
        if indicadores.roe >= 0.20:
            score += 50
        elif indicadores.roe >= 0.15:
            score += 40
        elif indicadores.roe >= 0.10:
            score += 30
        elif indicadores.roe >= 0.05:
            score += 20
        elif indicadores.roe >= 0:
            score += 10

        # Margem Líquida (peso 50%)
        if indicadores.margem_liquida >= 0.15:
            score += 50
        elif indicadores.margem_liquida >= 0.10:
            score += 40
        elif indicadores.margem_liquida >= 0.05:
            score += 30
        elif indicadores.margem_liquida >= 0:
            score += 20

        return score

    def _pontuar_sinistralidade(self, indicadores: IndicadoresFinanceiros) -> float:
        """Pontua indicadores de sinistralidade (quanto menor, melhor)"""
        score = 0

        # Índice de Sinistralidade (peso 50%)
        if indicadores.indice_sinistralidade <= 0.50:
            score += 50
        elif indicadores.indice_sinistralidade <= 0.60:
            score += 40
        elif indicadores.indice_sinistralidade <= 0.70:
            score += 30
        elif indicadores.indice_sinistralidade <= 0.80:
            score += 20
        elif indicadores.indice_sinistralidade <= 0.90:
            score += 10

        # Índice Combinado (peso 50%)
        if indicadores.indice_combinado <= 0.90:
            score += 50
        elif indicadores.indice_combinado <= 0.95:
            score += 40
        elif indicadores.indice_combinado <= 1.00:
            score += 30
        elif indicadores.indice_combinado <= 1.05:
            score += 20
        elif indicadores.indice_combinado <= 1.10:
            score += 10

        return score

    def _pontuar_estrutura(self, indicadores: IndicadoresFinanceiros) -> float:
        """Pontua indicadores de estrutura"""
        score = 0

        # Endividamento (peso 50%) - quanto menor, melhor
        if indicadores.endividamento <= 0.50:
            score += 50
        elif indicadores.endividamento <= 0.60:
            score += 40
        elif indicadores.endividamento <= 0.70:
            score += 30
        elif indicadores.endividamento <= 0.80:
            score += 20
        elif indicadores.endividamento <= 0.90:
            score += 10

        # Alavancagem (peso 50%) - moderada é ideal
        if 1.0 <= indicadores.alavancagem <= 3.0:
            score += 50
        elif 0.5 <= indicadores.alavancagem <= 4.0:
            score += 40
        elif 0.3 <= indicadores.alavancagem <= 5.0:
            score += 30
        elif indicadores.alavancagem <= 6.0:
            score += 20
        elif indicadores.alavancagem <= 8.0:
            score += 10

        return score

    def _determinar_rating(self, score: float) -> str:
        """Determina o rating baseado no score"""
        for limite, rating in self.LIMITES_RATING:
            if score >= limite:
                return rating
        return 'D'

    def analisar_pontos_fortes_fracos(
        self,
        indicadores: IndicadoresFinanceiros
    ) -> Tuple[list, list]:
        """
        Analisa e retorna os pontos fortes e fracos da seguradora

        Returns:
            Tuple com (lista de pontos fortes, lista de pontos fracos)
        """
        pontos_fortes = []
        pontos_fracos = []

        # Análise de Solvência
        if indicadores.indice_solvencia >= 1.0:
            pontos_fortes.append(
                f"Boa solvência: índice de {indicadores.indice_solvencia:.2f}"
            )
        else:
            pontos_fracos.append(
                f"Solvência baixa: índice de {indicadores.indice_solvencia:.2f}"
            )

        # Análise de Cobertura
        if indicadores.cobertura_provisoes >= 1.0:
            pontos_fortes.append(
                f"Provisões bem cobertas: {indicadores.cobertura_provisoes:.2f}x"
            )
        else:
            pontos_fracos.append(
                f"Cobertura insuficiente de provisões: {indicadores.cobertura_provisoes:.2f}x"
            )

        # Análise de Liquidez
        if indicadores.liquidez_corrente >= 1.2:
            pontos_fortes.append(
                f"Boa liquidez corrente: {indicadores.liquidez_corrente:.2f}"
            )
        elif indicadores.liquidez_corrente < 1.0:
            pontos_fracos.append(
                f"Liquidez corrente preocupante: {indicadores.liquidez_corrente:.2f}"
            )

        # Análise de Rentabilidade
        if indicadores.roe >= 0.10:
            pontos_fortes.append(
                f"Rentabilidade atrativa: ROE de {indicadores.roe:.1%}"
            )
        elif indicadores.roe < 0:
            pontos_fracos.append(
                f"Prejuízo no exercício: ROE de {indicadores.roe:.1%}"
            )

        # Análise de Sinistralidade
        if indicadores.indice_sinistralidade <= 0.60:
            pontos_fortes.append(
                f"Baixa sinistralidade: {indicadores.indice_sinistralidade:.1%}"
            )
        elif indicadores.indice_sinistralidade > 0.80:
            pontos_fracos.append(
                f"Alta sinistralidade: {indicadores.indice_sinistralidade:.1%}"
            )

        # Análise de Índice Combinado
        if indicadores.indice_combinado <= 0.95:
            pontos_fortes.append(
                f"Operação eficiente: índice combinado de {indicadores.indice_combinado:.1%}"
            )
        elif indicadores.indice_combinado > 1.0:
            pontos_fracos.append(
                f"Operação deficitária: índice combinado de {indicadores.indice_combinado:.1%}"
            )

        # Análise de Endividamento
        if indicadores.endividamento <= 0.60:
            pontos_fortes.append(
                f"Baixo endividamento: {indicadores.endividamento:.1%}"
            )
        elif indicadores.endividamento > 0.80:
            pontos_fracos.append(
                f"Alto endividamento: {indicadores.endividamento:.1%}"
            )

        return pontos_fortes, pontos_fracos
