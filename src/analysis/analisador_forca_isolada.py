"""
Analisador de Força Financeira Isolada de Resseguro

METODOLOGIA:
Este módulo implementa a análise de força financeira isolada para identificar
seguradoras que dependem excessivamente do rating do grupo econômico ou de
resseguro para sustentar suas operações.

OBJETIVO:
Identificar "fissuras" e fragilidades de seguradoras que:
1. Usam rating do grupo como se fosse próprio
2. Não teriam capacidade isolada de assumir riscos > R$ 50 milhões
3. Dependem excessivamente de resseguro para operar
4. Teriam rating significativamente inferior se avaliadas isoladamente

REFERÊNCIA: R$ 50 milhões como limite de capacidade própria mínima aceitável
"""

from typing import List, Tuple, Optional
from datetime import date

from ..models.seguradora import Seguradora, BalancoPatrimonial, DRE
from ..models.forca_isolada import (
    IndicadoresForcaIsolada,
    InformacoesGrupo,
    InformacoesResseguro,
    LimitesCapacidade,
    SeguradoraComResseguro,
    Fissura,
    TipoFissura,
    NivelRisco,
    ComparacaoRating,
    RelatorioForcaIsolada
)


class AnalisadorForcaIsolada:
    """
    Analisador de Força Financeira Isolada de Resseguro

    Calcula indicadores que revelam a real capacidade de uma seguradora
    operar de forma independente, sem depender do grupo ou resseguro.
    """

    # Limite de referência para capacidade própria (R$ 50 milhões)
    LIMITE_REFERENCIA = 50_000_000

    # Mapeamento de ratings para valores numéricos (para cálculo de gap)
    RATING_NUMERICO = {
        'AAA': 10, 'AA+': 9, 'AA': 8, 'AA-': 7,
        'A+': 6, 'A': 5, 'A-': 4,
        'BBB+': 3, 'BBB': 2, 'BBB-': 1,
        'BB+': 0, 'BB': -1, 'BB-': -2,
        'B+': -3, 'B': -4, 'B-': -5,
        'CCC': -6, 'CC': -7, 'C': -8, 'D': -9
    }

    # Limites para classificação de risco de dependência de resseguro
    LIMITES_DEPENDENCIA = {
        'critico': 0.70,     # > 70% cedido = crítico
        'alto': 0.50,        # > 50% cedido = alto
        'moderado': 0.30,    # > 30% cedido = moderado
        'baixo': 0.15,       # > 15% cedido = baixo
    }

    # Limites para score de força isolada
    LIMITES_RATING_ISOLADO = [
        (90, 'AAA'),
        (85, 'AA+'),
        (80, 'AA'),
        (75, 'AA-'),
        (70, 'A+'),
        (65, 'A'),
        (60, 'A-'),
        (55, 'BBB+'),
        (50, 'BBB'),
        (45, 'BBB-'),
        (40, 'BB+'),
        (35, 'BB'),
        (30, 'BB-'),
        (25, 'B+'),
        (20, 'B'),
        (15, 'B-'),
        (10, 'CCC'),
        (5, 'CC'),
        (0, 'C'),
    ]

    # Pesos para score de força isolada
    PESOS_FORCA_ISOLADA = {
        'capacidade_propria': 0.25,      # Capacidade de retenção própria
        'independencia_resseguro': 0.20, # Independência de resseguro
        'capital_efetivo': 0.20,         # Capital próprio efetivo
        'solvencia_isolada': 0.15,       # Solvência sem suporte grupo
        'liquidez_isolada': 0.10,        # Liquidez sem dependência
        'resiliencia': 0.10              # Resiliência a eventos adversos
    }

    def __init__(self):
        """Inicializa o analisador"""
        self.data_analise = date.today()

    def analisar_seguradora(
        self,
        seguradora: Seguradora,
        info_grupo: Optional[InformacoesGrupo] = None,
        info_resseguro: Optional[InformacoesResseguro] = None
    ) -> IndicadoresForcaIsolada:
        """
        Realiza análise completa de força financeira isolada

        Args:
            seguradora: Objeto Seguradora com dados financeiros
            info_grupo: Informações do grupo econômico (opcional)
            info_resseguro: Informações de resseguro (opcional)

        Returns:
            IndicadoresForcaIsolada com todos os indicadores calculados
        """
        # Inicializa informações se não fornecidas
        if info_grupo is None:
            info_grupo = self._inferir_info_grupo(seguradora)

        if info_resseguro is None:
            info_resseguro = self._inferir_info_resseguro(seguradora)

        indicadores = IndicadoresForcaIsolada(
            nome_seguradora=seguradora.nome,
            data_analise=self.data_analise
        )

        # Calcula indicadores de dependência de resseguro
        self._calcular_indicadores_resseguro(indicadores, seguradora, info_resseguro)

        # Calcula indicadores de capacidade própria
        self._calcular_capacidade_propria(indicadores, seguradora, info_grupo)

        # Calcula indicadores de solvência isolada
        self._calcular_solvencia_isolada(indicadores, seguradora, info_grupo)

        # Calcula indicadores de liquidez isolada
        self._calcular_liquidez_isolada(indicadores, seguradora, info_grupo)

        # Calcula indicadores de stress e resiliência
        self._calcular_indicadores_stress(indicadores, seguradora, info_resseguro)

        # Calcula score de força isolada e rating
        self._calcular_score_forca_isolada(indicadores)

        # Determina rating isolado
        indicadores.rating_isolado = self._determinar_rating_isolado(
            indicadores.score_forca_isolada
        )

        # Calcula gap de rating
        indicadores.rating_declarado = info_grupo.rating_grupo
        indicadores.gap_rating_notches = self._calcular_gap_rating(
            indicadores.rating_declarado,
            indicadores.rating_isolado
        )

        # Calcula inflação de rating
        indicadores.inflacao_rating = self._calcular_inflacao_rating(
            indicadores.rating_declarado,
            indicadores.rating_isolado
        )

        # Identifica fissuras e fragilidades
        self._identificar_fissuras(indicadores, seguradora, info_grupo, info_resseguro)

        # Gera alertas críticos
        self._gerar_alertas_criticos(indicadores)

        # Gera recomendações
        self._gerar_recomendacoes(indicadores)

        # Define classificação de risco final
        indicadores.classificacao_risco_isolado = self._classificar_risco(indicadores)

        # Calcula score de vulnerabilidade
        indicadores.score_vulnerabilidade = self._calcular_score_vulnerabilidade(indicadores)

        # Gera parecer final
        indicadores.parecer_final = self._gerar_parecer_final(indicadores)

        return indicadores

    def _inferir_info_grupo(self, seguradora: Seguradora) -> InformacoesGrupo:
        """Infere informações do grupo a partir dos dados da seguradora"""
        info = InformacoesGrupo(
            nome_grupo=seguradora.grupo_economico,
            rating_grupo=seguradora.indicadores.classificacao_risco,
            patrimonio_liquido_grupo=seguradora.balanco.patrimonio_liquido * 2.5
        )
        return info

    def _inferir_info_resseguro(self, seguradora: Seguradora) -> InformacoesResseguro:
        """Infere informações de resseguro a partir do DRE"""
        info = InformacoesResseguro(
            premios_cedidos_total=abs(seguradora.dre.premios_cedidos_resseguro),
            sinistros_recuperados_resseguro=abs(seguradora.dre.sinistros_ocorridos) * 0.15,
            retencao_maxima_risco=seguradora.balanco.patrimonio_liquido * 0.05,
            quota_parte_percentual=abs(seguradora.dre.premios_cedidos_resseguro) /
                                   seguradora.dre.premios_emitidos if seguradora.dre.premios_emitidos > 0 else 0
        )
        return info

    def _calcular_indicadores_resseguro(
        self,
        indicadores: IndicadoresForcaIsolada,
        seguradora: Seguradora,
        info_resseguro: InformacoesResseguro
    ):
        """Calcula indicadores de dependência de resseguro"""
        dre = seguradora.dre

        # Taxa de Cessão ao Resseguro
        if dre.premios_emitidos > 0:
            indicadores.taxa_cessao_resseguro = (
                abs(dre.premios_cedidos_resseguro) / dre.premios_emitidos
            )
        else:
            indicadores.taxa_cessao_resseguro = 0

        # Índice de Retenção
        indicadores.indice_retencao = 1 - indicadores.taxa_cessao_resseguro

        # Dependência de Recuperação de Sinistros
        if abs(dre.sinistros_ocorridos) > 0:
            indicadores.dependencia_recuperacao = (
                info_resseguro.sinistros_recuperados_resseguro /
                abs(dre.sinistros_ocorridos)
            )
        else:
            indicadores.dependencia_recuperacao = 0

        # Exposição Líquida ao Risco
        premios_retidos = dre.premios_emitidos - abs(dre.premios_cedidos_resseguro)
        sinistros_retidos = abs(dre.sinistros_ocorridos) * (1 - indicadores.dependencia_recuperacao)

        if seguradora.balanco.patrimonio_liquido > 0:
            indicadores.exposicao_liquida = (
                (premios_retidos - sinistros_retidos) /
                seguradora.balanco.patrimonio_liquido
            )
        else:
            indicadores.exposicao_liquida = 0

        # Concentração de Resseguro no Grupo
        if info_resseguro.premios_cedidos_total > 0:
            indicadores.concentracao_resseguro_grupo = (
                info_resseguro.concentracao_principal_ressegurador
            )
        else:
            indicadores.concentracao_resseguro_grupo = 0

    def _calcular_capacidade_propria(
        self,
        indicadores: IndicadoresForcaIsolada,
        seguradora: Seguradora,
        info_grupo: InformacoesGrupo
    ):
        """Calcula indicadores de capacidade própria"""
        balanco = seguradora.balanco

        # Patrimônio Líquido Real
        indicadores.patrimonio_liquido_real = balanco.patrimonio_liquido

        # Capital Próprio Efetivo (deduzindo intangíveis e créditos do grupo)
        deducoes = (
            balanco.intangivel +
            info_grupo.ativos_grupo * 0.5 +  # Desconta 50% de ativos no grupo
            info_grupo.carta_suporte_valor * 0.7  # Desconta 70% de suporte implícito
        )
        indicadores.capital_proprio_efetivo = max(
            0,
            balanco.patrimonio_liquido - deducoes
        )

        # Capacidade Máxima de Retenção por Risco (5% do Capital Efetivo)
        indicadores.capacidade_retencao_risco = (
            indicadores.capital_proprio_efetivo * 0.05
        )

        # Capacidade Máxima por Evento (10% do Capital Efetivo)
        indicadores.capacidade_retencao_evento = (
            indicadores.capital_proprio_efetivo * 0.10
        )

        # Capacidade Agregada Anual (50% do Capital Efetivo)
        indicadores.capacidade_agregada_anual = (
            indicadores.capital_proprio_efetivo * 0.50
        )

        # Índice de Capacidade vs Referência (50MM)
        indicadores.indice_capacidade_50mm = (
            indicadores.capacidade_retencao_risco / self.LIMITE_REFERENCIA
        )

    def _calcular_solvencia_isolada(
        self,
        indicadores: IndicadoresForcaIsolada,
        seguradora: Seguradora,
        info_grupo: InformacoesGrupo
    ):
        """Calcula indicadores de solvência considerando operação isolada"""
        balanco = seguradora.balanco

        # Passivo sem suporte do grupo
        passivo_ajustado = (
            balanco.passivo_exigivel -
            info_grupo.dividas_grupo  # Remove dívidas intercompany
        )

        # Índice de Solvência Isolado
        if passivo_ajustado > 0:
            indicadores.indice_solvencia_isolado = (
                indicadores.capital_proprio_efetivo / passivo_ajustado
            )
        else:
            indicadores.indice_solvencia_isolado = 0

        # Ativos próprios (sem créditos do grupo)
        ativos_proprios = (
            balanco.disponibilidades +
            balanco.aplicacoes_financeiras_cp +
            balanco.aplicacoes_financeiras_lp -
            info_grupo.ativos_grupo
        )

        # Cobertura de Provisões Isolada
        if balanco.provisoes_tecnicas_total > 0:
            indicadores.cobertura_provisoes_isolada = (
                ativos_proprios / balanco.provisoes_tecnicas_total
            )
        else:
            indicadores.cobertura_provisoes_isolada = 0

        # Margem de Solvência Isolada
        indicadores.margem_solvencia_isolada = (
            indicadores.capital_proprio_efetivo -
            seguradora.capital_minimo_requerido
        )

        # Suficiência de Capital Isolada
        if seguradora.capital_minimo_requerido > 0:
            indicadores.suficiencia_capital_isolada = (
                indicadores.capital_proprio_efetivo /
                seguradora.capital_minimo_requerido
            )
        else:
            indicadores.suficiencia_capital_isolada = 0

    def _calcular_liquidez_isolada(
        self,
        indicadores: IndicadoresForcaIsolada,
        seguradora: Seguradora,
        info_grupo: InformacoesGrupo
    ):
        """Calcula indicadores de liquidez sem dependência do grupo"""
        balanco = seguradora.balanco

        # Ativos líquidos próprios
        ativos_liquidos_proprios = (
            balanco.disponibilidades +
            balanco.aplicacoes_financeiras_cp -
            info_grupo.ativos_grupo * 0.5
        )

        # Liquidez sem Créditos do Grupo
        if balanco.passivo_circulante > 0:
            indicadores.liquidez_isolada = (
                ativos_liquidos_proprios / balanco.passivo_circulante
            )
        else:
            indicadores.liquidez_isolada = 0

        # Dependência de Caixa do Grupo
        caixa_total = balanco.disponibilidades + balanco.aplicacoes_financeiras_cp
        if caixa_total > 0:
            indicadores.dependencia_caixa_grupo = (
                info_grupo.ativos_grupo / caixa_total
            )
        else:
            indicadores.dependencia_caixa_grupo = 0

    def _calcular_indicadores_stress(
        self,
        indicadores: IndicadoresForcaIsolada,
        seguradora: Seguradora,
        info_resseguro: InformacoesResseguro
    ):
        """Calcula indicadores de stress e resiliência"""

        # Impacto de Perda de Resseguro (se ressegurador falhar)
        creditos_resseguro = info_resseguro.creditos_resseguro_total
        pl = seguradora.balanco.patrimonio_liquido

        if pl > 0:
            indicadores.impacto_perda_resseguro = creditos_resseguro / pl
        else:
            indicadores.impacto_perda_resseguro = 0

        # Capacidade de Absorção de Sinistros
        # Máximo sinistro que pode absorver sem ficar insolvente
        indicadores.capacidade_absorcao_sinistros = (
            indicadores.capital_proprio_efetivo * 0.20  # 20% do capital
        )

        # Resiliência a Eventos Catastróficos
        exposicao_cat = info_resseguro.catastrofe_cobertura
        if exposicao_cat > 0:
            indicadores.resiliencia_catastrofe = (
                indicadores.capital_proprio_efetivo / exposicao_cat
            )
        else:
            # Se não tem cobertura Cat, assume exposição de 10% dos prêmios
            exposicao_estimada = seguradora.dre.premios_emitidos * 0.10
            if exposicao_estimada > 0:
                indicadores.resiliencia_catastrofe = (
                    indicadores.capital_proprio_efetivo / exposicao_estimada
                )
            else:
                indicadores.resiliencia_catastrofe = 0

    def _calcular_score_forca_isolada(self, indicadores: IndicadoresForcaIsolada):
        """Calcula o score de força financeira isolada (0-100)"""

        scores = {}

        # 1. Score de Capacidade Própria (0-100)
        if indicadores.indice_capacidade_50mm >= 1.0:
            scores['capacidade_propria'] = min(100, 60 + (indicadores.indice_capacidade_50mm - 1) * 40)
        else:
            scores['capacidade_propria'] = indicadores.indice_capacidade_50mm * 60

        # 2. Score de Independência de Resseguro (0-100)
        # Quanto maior a retenção, melhor (mas com limite)
        retencao = indicadores.indice_retencao
        if retencao >= 0.85:
            scores['independencia_resseguro'] = 100
        elif retencao >= 0.70:
            scores['independencia_resseguro'] = 80 + (retencao - 0.70) * 133
        elif retencao >= 0.50:
            scores['independencia_resseguro'] = 50 + (retencao - 0.50) * 150
        elif retencao >= 0.30:
            scores['independencia_resseguro'] = 20 + (retencao - 0.30) * 150
        else:
            scores['independencia_resseguro'] = retencao * 67

        # 3. Score de Capital Efetivo (0-100)
        suficiencia = indicadores.suficiencia_capital_isolada
        if suficiencia >= 3.0:
            scores['capital_efetivo'] = 100
        elif suficiencia >= 2.0:
            scores['capital_efetivo'] = 80 + (suficiencia - 2.0) * 20
        elif suficiencia >= 1.5:
            scores['capital_efetivo'] = 60 + (suficiencia - 1.5) * 40
        elif suficiencia >= 1.0:
            scores['capital_efetivo'] = 40 + (suficiencia - 1.0) * 40
        else:
            scores['capital_efetivo'] = suficiencia * 40

        # 4. Score de Solvência Isolada (0-100)
        solvencia = indicadores.indice_solvencia_isolado
        if solvencia >= 1.5:
            scores['solvencia_isolada'] = 100
        elif solvencia >= 1.0:
            scores['solvencia_isolada'] = 70 + (solvencia - 1.0) * 60
        elif solvencia >= 0.7:
            scores['solvencia_isolada'] = 40 + (solvencia - 0.7) * 100
        else:
            scores['solvencia_isolada'] = solvencia * 57

        # 5. Score de Liquidez Isolada (0-100)
        liquidez = indicadores.liquidez_isolada
        if liquidez >= 1.5:
            scores['liquidez_isolada'] = 100
        elif liquidez >= 1.2:
            scores['liquidez_isolada'] = 80 + (liquidez - 1.2) * 67
        elif liquidez >= 1.0:
            scores['liquidez_isolada'] = 60 + (liquidez - 1.0) * 100
        elif liquidez >= 0.8:
            scores['liquidez_isolada'] = 40 + (liquidez - 0.8) * 100
        else:
            scores['liquidez_isolada'] = liquidez * 50

        # 6. Score de Resiliência (0-100)
        # Baseado na capacidade de absorção e resiliência a catástrofes
        resiliencia = indicadores.resiliencia_catastrofe
        if resiliencia >= 2.0:
            scores['resiliencia'] = 100
        elif resiliencia >= 1.0:
            scores['resiliencia'] = 60 + (resiliencia - 1.0) * 40
        elif resiliencia >= 0.5:
            scores['resiliencia'] = 30 + (resiliencia - 0.5) * 60
        else:
            scores['resiliencia'] = resiliencia * 60

        # Score final ponderado
        indicadores.score_forca_isolada = sum(
            scores[key] * self.PESOS_FORCA_ISOLADA[key]
            for key in scores
        )

    def _determinar_rating_isolado(self, score: float) -> str:
        """Determina o rating isolado baseado no score"""
        for limite, rating in self.LIMITES_RATING_ISOLADO:
            if score >= limite:
                return rating
        return 'D'

    def _calcular_gap_rating(self, rating_declarado: str, rating_isolado: str) -> int:
        """Calcula a diferença em notches entre ratings"""
        valor_declarado = self.RATING_NUMERICO.get(rating_declarado, 0)
        valor_isolado = self.RATING_NUMERICO.get(rating_isolado, 0)
        return valor_declarado - valor_isolado

    def _calcular_inflacao_rating(self, rating_declarado: str, rating_isolado: str) -> float:
        """Calcula percentual de inflação do rating"""
        gap = self._calcular_gap_rating(rating_declarado, rating_isolado)
        if gap <= 0:
            return 0
        # Cada notch representa aproximadamente 10% de inflação
        return gap * 10.0

    def _identificar_fissuras(
        self,
        indicadores: IndicadoresForcaIsolada,
        seguradora: Seguradora,
        info_grupo: InformacoesGrupo,
        info_resseguro: InformacoesResseguro
    ):
        """Identifica todas as fissuras e fragilidades"""
        fissuras = []

        # 1. DEPENDÊNCIA EXCESSIVA DE RESSEGURO
        if indicadores.taxa_cessao_resseguro > self.LIMITES_DEPENDENCIA['critico']:
            fissuras.append(Fissura(
                tipo=TipoFissura.DEPENDENCIA_RESSEGURO,
                nivel_risco=NivelRisco.CRITICO,
                descricao=f"Cessão de {indicadores.taxa_cessao_resseguro:.1%} ao resseguro - "
                          f"seguradora opera como fronting",
                valor_referencia=indicadores.taxa_cessao_resseguro,
                limite_aceitavel=0.50,
                gap_percentual=(indicadores.taxa_cessao_resseguro - 0.50) / 0.50 * 100,
                recomendacao="Reduzir dependência de resseguro e aumentar retenção própria",
                impacto_rating=-3
            ))
        elif indicadores.taxa_cessao_resseguro > self.LIMITES_DEPENDENCIA['alto']:
            fissuras.append(Fissura(
                tipo=TipoFissura.DEPENDENCIA_RESSEGURO,
                nivel_risco=NivelRisco.ALTO,
                descricao=f"Alta cessão ao resseguro ({indicadores.taxa_cessao_resseguro:.1%})",
                valor_referencia=indicadores.taxa_cessao_resseguro,
                limite_aceitavel=0.30,
                gap_percentual=(indicadores.taxa_cessao_resseguro - 0.30) / 0.30 * 100,
                recomendacao="Avaliar capacidade de aumentar retenção",
                impacto_rating=-2
            ))

        # 2. RATING INFLADO PELO GRUPO
        if indicadores.gap_rating_notches >= 3:
            fissuras.append(Fissura(
                tipo=TipoFissura.RATING_INFLADO,
                nivel_risco=NivelRisco.CRITICO,
                descricao=f"Rating declarado ({indicadores.rating_declarado}) "
                          f"está {indicadores.gap_rating_notches} notches acima do rating isolado "
                          f"({indicadores.rating_isolado})",
                valor_referencia=indicadores.gap_rating_notches,
                limite_aceitavel=1,
                gap_percentual=indicadores.inflacao_rating,
                recomendacao="Rating individual deve ser divulgado separadamente",
                impacto_rating=-indicadores.gap_rating_notches
            ))
        elif indicadores.gap_rating_notches >= 2:
            fissuras.append(Fissura(
                tipo=TipoFissura.RATING_INFLADO,
                nivel_risco=NivelRisco.ALTO,
                descricao=f"Rating declarado inflado em {indicadores.gap_rating_notches} notches",
                valor_referencia=indicadores.gap_rating_notches,
                limite_aceitavel=1,
                gap_percentual=indicadores.inflacao_rating,
                recomendacao="Transparência sobre rating individual",
                impacto_rating=-indicadores.gap_rating_notches
            ))

        # 3. CAPACIDADE INSUFICIENTE PARA RISCOS > 50MM
        if indicadores.indice_capacidade_50mm < 1.0:
            nivel = NivelRisco.CRITICO if indicadores.indice_capacidade_50mm < 0.5 else NivelRisco.ALTO
            fissuras.append(Fissura(
                tipo=TipoFissura.CAPACIDADE_INSUFICIENTE,
                nivel_risco=nivel,
                descricao=f"Capacidade própria de R$ {indicadores.capacidade_retencao_risco/1e6:.1f}MM "
                          f"insuficiente para riscos de R$ 50MM",
                valor_referencia=indicadores.capacidade_retencao_risco,
                limite_aceitavel=self.LIMITE_REFERENCIA,
                gap_percentual=(1 - indicadores.indice_capacidade_50mm) * 100,
                recomendacao="Não deve assumir riscos acima de "
                            f"R$ {indicadores.capacidade_retencao_risco/1e6:.1f}MM por apólice",
                impacto_rating=-2
            ))

        # 4. CAPITAL PRÓPRIO FRÁGIL
        if indicadores.suficiencia_capital_isolada < 1.0:
            fissuras.append(Fissura(
                tipo=TipoFissura.CAPITAL_FRAGIL,
                nivel_risco=NivelRisco.CRITICO,
                descricao=f"Capital próprio efetivo insuficiente - "
                          f"suficiência de apenas {indicadores.suficiencia_capital_isolada:.1%}",
                valor_referencia=indicadores.capital_proprio_efetivo,
                limite_aceitavel=seguradora.capital_minimo_requerido,
                gap_percentual=(1 - indicadores.suficiencia_capital_isolada) * 100,
                recomendacao="Necessita aporte de capital urgente",
                impacto_rating=-4
            ))
        elif indicadores.suficiencia_capital_isolada < 1.5:
            fissuras.append(Fissura(
                tipo=TipoFissura.CAPITAL_FRAGIL,
                nivel_risco=NivelRisco.ALTO,
                descricao=f"Capital próprio com margem reduzida - "
                          f"suficiência de {indicadores.suficiencia_capital_isolada:.1%}",
                valor_referencia=indicadores.capital_proprio_efetivo,
                limite_aceitavel=seguradora.capital_minimo_requerido * 1.5,
                gap_percentual=(1.5 - indicadores.suficiencia_capital_isolada) / 1.5 * 100,
                recomendacao="Reforço de capital recomendado",
                impacto_rating=-2
            ))

        # 5. CONCENTRAÇÃO EM OPERAÇÕES DO GRUPO
        if indicadores.concentracao_resseguro_grupo > 0.50:
            fissuras.append(Fissura(
                tipo=TipoFissura.CONCENTRACAO_GRUPO,
                nivel_risco=NivelRisco.ALTO,
                descricao=f"Alta concentração de resseguro no próprio grupo "
                          f"({indicadores.concentracao_resseguro_grupo:.1%})",
                valor_referencia=indicadores.concentracao_resseguro_grupo,
                limite_aceitavel=0.30,
                gap_percentual=(indicadores.concentracao_resseguro_grupo - 0.30) / 0.30 * 100,
                recomendacao="Diversificar resseguro com parceiros externos ao grupo",
                impacto_rating=-1
            ))

        # 6. LIQUIDEZ DEPENDENTE DE TERCEIROS
        if indicadores.liquidez_isolada < 1.0:
            nivel = NivelRisco.CRITICO if indicadores.liquidez_isolada < 0.7 else NivelRisco.MODERADO
            fissuras.append(Fissura(
                tipo=TipoFissura.LIQUIDEZ_DEPENDENTE,
                nivel_risco=nivel,
                descricao=f"Liquidez isolada de apenas {indicadores.liquidez_isolada:.2f}x",
                valor_referencia=indicadores.liquidez_isolada,
                limite_aceitavel=1.0,
                gap_percentual=(1 - indicadores.liquidez_isolada) * 100,
                recomendacao="Aumentar ativos líquidos próprios",
                impacto_rating=-2 if nivel == NivelRisco.CRITICO else -1
            ))

        # 7. PROVISÕES SUBDIMENSIONADAS
        if indicadores.cobertura_provisoes_isolada < 1.0:
            fissuras.append(Fissura(
                tipo=TipoFissura.PROVISAO_SUBDIMENSIONADA,
                nivel_risco=NivelRisco.CRITICO,
                descricao=f"Cobertura de provisões isolada de apenas "
                          f"{indicadores.cobertura_provisoes_isolada:.1%}",
                valor_referencia=indicadores.cobertura_provisoes_isolada,
                limite_aceitavel=1.0,
                gap_percentual=(1 - indicadores.cobertura_provisoes_isolada) * 100,
                recomendacao="Insuficiência de ativos garantidores próprios",
                impacto_rating=-3
            ))

        # 8. ALAVANCAGEM EXCESSIVA
        alavancagem = seguradora.dre.premios_emitidos / indicadores.capital_proprio_efetivo \
            if indicadores.capital_proprio_efetivo > 0 else float('inf')

        if alavancagem > 6.0:
            fissuras.append(Fissura(
                tipo=TipoFissura.ALAVANCAGEM_EXCESSIVA,
                nivel_risco=NivelRisco.ALTO,
                descricao=f"Alavancagem de {alavancagem:.1f}x sobre capital efetivo",
                valor_referencia=alavancagem,
                limite_aceitavel=4.0,
                gap_percentual=(alavancagem - 4.0) / 4.0 * 100,
                recomendacao="Reduzir volume de prêmios ou aumentar capital",
                impacto_rating=-2
            ))

        # 9. EXPOSIÇÃO CATASTRÓFICA SEM COBERTURA ADEQUADA
        if indicadores.resiliencia_catastrofe < 0.5:
            fissuras.append(Fissura(
                tipo=TipoFissura.EXPOSICAO_CATASTROFICA,
                nivel_risco=NivelRisco.ALTO,
                descricao=f"Baixa resiliência a eventos catastróficos "
                          f"({indicadores.resiliencia_catastrofe:.2f}x)",
                valor_referencia=indicadores.resiliencia_catastrofe,
                limite_aceitavel=1.0,
                gap_percentual=(1 - indicadores.resiliencia_catastrofe) * 100,
                recomendacao="Aumentar cobertura catastrófica ou reduzir exposição",
                impacto_rating=-2
            ))

        indicadores.fissuras = fissuras

    def _gerar_alertas_criticos(self, indicadores: IndicadoresForcaIsolada):
        """Gera alertas críticos baseados nas fissuras identificadas"""
        alertas = []

        # Alertas baseados em fissuras críticas
        for fissura in indicadores.fissuras:
            if fissura.nivel_risco == NivelRisco.CRITICO:
                alertas.append(f"[CRÍTICO] {fissura.descricao}")

        # Alerta de capacidade vs 50MM
        if indicadores.indice_capacidade_50mm < 1.0:
            alertas.append(
                f"[ALERTA] NÃO PODE ASSUMIR RISCOS > R$ {indicadores.capacidade_retencao_risco/1e6:.1f}MM "
                f"(limite próprio sem resseguro)"
            )

        # Alerta de rating inflado
        if indicadores.gap_rating_notches >= 2:
            alertas.append(
                f"[ALERTA] Rating declarado ({indicadores.rating_declarado}) não reflete "
                f"força financeira isolada ({indicadores.rating_isolado})"
            )

        # Alerta de solvência
        if indicadores.margem_solvencia_isolada < 0:
            alertas.append(
                "[CRÍTICO] MARGEM DE SOLVÊNCIA ISOLADA NEGATIVA - "
                "Insuficiência de capital para operar sem suporte do grupo"
            )

        indicadores.alertas_criticos = alertas

    def _gerar_recomendacoes(self, indicadores: IndicadoresForcaIsolada):
        """Gera recomendações baseadas na análise"""
        recomendacoes = []

        # Recomendação sobre capacidade
        if indicadores.indice_capacidade_50mm < 1.0:
            limite_seguro = indicadores.capacidade_retencao_risco
            recomendacoes.append(
                f"Limitar retenção máxima por risco a R$ {limite_seguro/1e6:.1f} milhões"
            )

        # Recomendação sobre resseguro
        if indicadores.taxa_cessao_resseguro > 0.50:
            recomendacoes.append(
                "Desenvolver capacidade própria para reduzir dependência de resseguro"
            )

        # Recomendação sobre capital
        if indicadores.suficiencia_capital_isolada < 1.5:
            gap = indicadores.capital_proprio_efetivo * 1.5 - indicadores.capital_proprio_efetivo
            recomendacoes.append(
                f"Considerar aporte de capital de aproximadamente R$ {gap/1e6:.1f} milhões"
            )

        # Recomendação sobre transparência de rating
        if indicadores.gap_rating_notches >= 2:
            recomendacoes.append(
                "Divulgar rating individual separado do rating do grupo para maior transparência"
            )

        # Recomendação sobre diversificação
        if indicadores.concentracao_resseguro_grupo > 0.30:
            recomendacoes.append(
                "Diversificar programas de resseguro com parceiros externos ao grupo"
            )

        # Recomendação sobre liquidez
        if indicadores.liquidez_isolada < 1.0:
            recomendacoes.append(
                "Aumentar posição em ativos líquidos próprios (não dependentes do grupo)"
            )

        indicadores.recomendacoes = recomendacoes

    def _classificar_risco(self, indicadores: IndicadoresForcaIsolada) -> NivelRisco:
        """Classifica o nível de risco geral"""
        # Conta fissuras por nível
        criticas = sum(1 for f in indicadores.fissuras if f.nivel_risco == NivelRisco.CRITICO)
        altas = sum(1 for f in indicadores.fissuras if f.nivel_risco == NivelRisco.ALTO)

        if criticas >= 2 or indicadores.score_forca_isolada < 30:
            return NivelRisco.CRITICO
        elif criticas >= 1 or altas >= 2 or indicadores.score_forca_isolada < 45:
            return NivelRisco.ALTO
        elif altas >= 1 or indicadores.score_forca_isolada < 60:
            return NivelRisco.MODERADO
        elif indicadores.score_forca_isolada < 75:
            return NivelRisco.BAIXO
        else:
            return NivelRisco.MINIMO

    def _calcular_score_vulnerabilidade(self, indicadores: IndicadoresForcaIsolada) -> float:
        """Calcula score de vulnerabilidade (0-100, quanto maior mais vulnerável)"""
        # Inversão do score de força + penalidades por fissuras
        score_base = 100 - indicadores.score_forca_isolada

        # Adiciona penalidades por fissuras
        for fissura in indicadores.fissuras:
            if fissura.nivel_risco == NivelRisco.CRITICO:
                score_base += 10
            elif fissura.nivel_risco == NivelRisco.ALTO:
                score_base += 5
            elif fissura.nivel_risco == NivelRisco.MODERADO:
                score_base += 2

        return min(100, max(0, score_base))

    def _gerar_parecer_final(self, indicadores: IndicadoresForcaIsolada) -> str:
        """Gera parecer final sobre a força financeira isolada"""
        nome = indicadores.nome_seguradora
        score = indicadores.score_forca_isolada
        rating_decl = indicadores.rating_declarado
        rating_isol = indicadores.rating_isolado
        gap = indicadores.gap_rating_notches
        capacidade = indicadores.capacidade_retencao_risco / 1e6
        limite_ref = self.LIMITE_REFERENCIA / 1e6

        # Determina tom do parecer
        if indicadores.classificacao_risco_isolado == NivelRisco.CRITICO:
            tom = "PREOCUPANTE"
            conclusao = "NÃO RECOMENDADA para operações que exijam capacidade própria significativa"
        elif indicadores.classificacao_risco_isolado == NivelRisco.ALTO:
            tom = "VULNERÁVEL"
            conclusao = "Requer cautela e análise aprofundada antes de assumir riscos relevantes"
        elif indicadores.classificacao_risco_isolado == NivelRisco.MODERADO:
            tom = "ADEQUADA COM RESSALVAS"
            conclusao = "Pode operar dentro de limites conservadores"
        elif indicadores.classificacao_risco_isolado == NivelRisco.BAIXO:
            tom = "SATISFATÓRIA"
            conclusao = "Demonstra boa capacidade de operação independente"
        else:
            tom = "ROBUSTA"
            conclusao = "Excelente capacidade de operação isolada"

        parecer = f"""
========================================
PARECER DE FORÇA FINANCEIRA ISOLADA
========================================
Seguradora: {nome}
Data da Análise: {indicadores.data_analise}

CLASSIFICAÇÃO: {tom}
Score de Força Isolada: {score:.1f}/100
Nível de Risco: {indicadores.classificacao_risco_isolado.value}

COMPARAÇÃO DE RATING:
- Rating Declarado (Grupo): {rating_decl}
- Rating Isolado Calculado: {rating_isol}
- Gap de Rating: {gap} notches
- Inflação de Rating: {indicadores.inflacao_rating:.1f}%

CAPACIDADE PRÓPRIA:
- Capacidade por Risco: R$ {capacidade:.1f} milhões
- Referência (50MM): {'ATENDE' if capacidade >= limite_ref else 'NÃO ATENDE'}
- Índice de Capacidade: {indicadores.indice_capacidade_50mm:.2f}x

FISSURAS IDENTIFICADAS: {len(indicadores.fissuras)}
- Críticas: {sum(1 for f in indicadores.fissuras if f.nivel_risco == NivelRisco.CRITICO)}
- Altas: {sum(1 for f in indicadores.fissuras if f.nivel_risco == NivelRisco.ALTO)}
- Moderadas: {sum(1 for f in indicadores.fissuras if f.nivel_risco == NivelRisco.MODERADO)}

CONCLUSÃO: {conclusao}

ALERTAS: {len(indicadores.alertas_criticos)}
RECOMENDAÇÕES: {len(indicadores.recomendacoes)}
========================================
"""
        return parecer.strip()

    def gerar_comparacao_rating(
        self,
        indicadores: IndicadoresForcaIsolada
    ) -> ComparacaoRating:
        """Gera objeto de comparação de rating"""
        return ComparacaoRating(
            seguradora=indicadores.nome_seguradora,
            rating_declarado=indicadores.rating_declarado,
            rating_grupo=indicadores.rating_declarado,
            rating_isolado_calculado=indicadores.rating_isolado,
            gap_notches=indicadores.gap_rating_notches,
            justificativa_gap=self._justificar_gap(indicadores),
            principais_fissuras=[f.tipo.value for f in indicadores.fissuras[:3]],
            recomendacao_prudencial=indicadores.recomendacoes[0]
            if indicadores.recomendacoes else "Nenhuma recomendação específica"
        )

    def _justificar_gap(self, indicadores: IndicadoresForcaIsolada) -> str:
        """Gera justificativa para o gap de rating"""
        if indicadores.gap_rating_notches <= 0:
            return "Rating isolado compatível ou superior ao declarado"

        justificativas = []

        if indicadores.taxa_cessao_resseguro > 0.30:
            justificativas.append(
                f"dependência de resseguro ({indicadores.taxa_cessao_resseguro:.1%})"
            )

        if indicadores.suficiencia_capital_isolada < 1.5:
            justificativas.append(
                f"capital efetivo limitado ({indicadores.suficiencia_capital_isolada:.1%} de suficiência)"
            )

        if indicadores.indice_capacidade_50mm < 1.0:
            justificativas.append(
                f"capacidade própria insuficiente (R$ {indicadores.capacidade_retencao_risco/1e6:.1f}MM)"
            )

        if justificativas:
            return "Gap justificado por: " + "; ".join(justificativas)
        else:
            return "Gap não plenamente justificado por indicadores técnicos"

    def analisar_carteira(
        self,
        seguradoras: List[Seguradora],
        infos_grupo: Optional[List[InformacoesGrupo]] = None,
        infos_resseguro: Optional[List[InformacoesResseguro]] = None
    ) -> RelatorioForcaIsolada:
        """
        Analisa uma carteira completa de seguradoras

        Args:
            seguradoras: Lista de seguradoras
            infos_grupo: Lista de informações de grupo (opcional)
            infos_resseguro: Lista de informações de resseguro (opcional)

        Returns:
            RelatorioForcaIsolada com análise consolidada
        """
        relatorio = RelatorioForcaIsolada(
            data_geracao=self.data_analise,
            periodo_analise="2024"
        )

        analises = []
        comparacoes = []

        for i, seguradora in enumerate(seguradoras):
            info_grupo = infos_grupo[i] if infos_grupo and i < len(infos_grupo) else None
            info_resseguro = infos_resseguro[i] if infos_resseguro and i < len(infos_resseguro) else None

            indicadores = self.analisar_seguradora(seguradora, info_grupo, info_resseguro)
            analises.append(indicadores)
            comparacoes.append(self.gerar_comparacao_rating(indicadores))

        relatorio.analises = analises
        relatorio.comparacoes_rating = comparacoes
        relatorio.total_seguradoras_analisadas = len(seguradoras)

        # Contagens
        relatorio.seguradoras_risco_critico = sum(
            1 for a in analises if a.classificacao_risco_isolado == NivelRisco.CRITICO
        )
        relatorio.seguradoras_rating_inflado = sum(
            1 for a in analises if a.gap_rating_notches >= 2
        )
        relatorio.seguradoras_capacidade_insuficiente = sum(
            1 for a in analises if a.indice_capacidade_50mm < 1.0
        )

        # Ranking por vulnerabilidade
        ranking = sorted(analises, key=lambda x: x.score_vulnerabilidade, reverse=True)
        relatorio.ranking_vulnerabilidade = [a.nome_seguradora for a in ranking]

        # Fissuras frequentes
        todas_fissuras = []
        for a in analises:
            todas_fissuras.extend([f.tipo.value for f in a.fissuras])

        from collections import Counter
        contagem = Counter(todas_fissuras)
        relatorio.fissuras_frequentes = contagem.most_common()

        # Parecer de mercado
        relatorio.parecer_mercado = self._gerar_parecer_mercado(relatorio)

        return relatorio

    def _gerar_parecer_mercado(self, relatorio: RelatorioForcaIsolada) -> str:
        """Gera parecer geral sobre o mercado analisado"""
        total = relatorio.total_seguradoras_analisadas
        criticos = relatorio.seguradoras_risco_critico
        inflados = relatorio.seguradoras_rating_inflado
        insuficientes = relatorio.seguradoras_capacidade_insuficiente

        return f"""
PARECER DE MERCADO - FORÇA FINANCEIRA ISOLADA
==============================================

Total de Seguradoras Analisadas: {total}

ALERTAS DE MERCADO:
- Seguradoras em Risco Crítico: {criticos} ({criticos/total*100:.1f}%)
- Seguradoras com Rating Inflado: {inflados} ({inflados/total*100:.1f}%)
- Capacidade Insuficiente (<50MM): {insuficientes} ({insuficientes/total*100:.1f}%)

PRINCIPAIS FRAGILIDADES DO MERCADO:
{chr(10).join(f'- {f[0]}: {f[1]} ocorrências' for f in relatorio.fissuras_frequentes[:5])}

RECOMENDAÇÃO GERAL:
Credores e contrapartes devem solicitar rating individual (não consolidado)
e verificar capacidade de retenção própria antes de aceitar garantias
de seguradoras que operam sob umbrella de grupos econômicos.
"""
