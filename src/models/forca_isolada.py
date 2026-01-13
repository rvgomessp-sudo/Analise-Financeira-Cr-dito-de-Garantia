"""
Modelos de dados para análise de Força Financeira Isolada de Resseguro
Identifica fragilidades de seguradoras que dependem do rating do grupo

METODOLOGIA: Avaliação da capacidade real de uma seguradora assumir riscos
por conta própria, sem considerar o suporte do grupo econômico ou resseguro.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date
from enum import Enum


class NivelRisco(Enum):
    """Níveis de risco para classificação de fragilidades"""
    CRITICO = "CRÍTICO"
    ALTO = "ALTO"
    MODERADO = "MODERADO"
    BAIXO = "BAIXO"
    MINIMO = "MÍNIMO"


class TipoFissura(Enum):
    """Tipos de fissuras/fragilidades identificadas"""
    DEPENDENCIA_RESSEGURO = "Dependência Excessiva de Resseguro"
    RATING_INFLADO = "Rating Inflado pelo Grupo"
    CAPACIDADE_INSUFICIENTE = "Capacidade Própria Insuficiente"
    CAPITAL_FRAGIL = "Capital Próprio Frágil"
    CONCENTRACAO_GRUPO = "Concentração em Operações do Grupo"
    LIQUIDEZ_DEPENDENTE = "Liquidez Dependente de Terceiros"
    PROVISAO_SUBDIMENSIONADA = "Provisões Subdimensionadas"
    RENTABILIDADE_ARTIFICIAL = "Rentabilidade Artificial"
    ALAVANCAGEM_EXCESSIVA = "Alavancagem Excessiva para Capital"
    EXPOSICAO_CATASTROFICA = "Exposição Catastrófica sem Cobertura"


@dataclass
class InformacoesGrupo:
    """Informações do grupo econômico para análise de dependência"""

    # Identificação do grupo
    nome_grupo: str = ""
    rating_grupo: str = ""  # Rating declarado do grupo (S&P, Fitch, AM Best)
    agencia_rating: str = ""  # S&P, Fitch, Moody's, AM Best

    # Patrimônio e suporte do grupo
    patrimonio_liquido_grupo: float = 0.0  # PL consolidado do grupo
    carta_suporte_valor: float = 0.0  # Valor de carta de suporte (se houver)
    garantia_explicita: bool = False  # Se há garantia explícita do grupo

    # Operações intercompany
    premios_cedidos_grupo: float = 0.0  # Prêmios cedidos para resseguradoras do grupo
    ativos_grupo: float = 0.0  # Ativos depositados em empresas do grupo
    dividas_grupo: float = 0.0  # Dívidas com empresas do grupo

    # Histórico de suporte
    historico_aportes: float = 0.0  # Total de aportes recebidos do grupo
    anos_operacao_grupo: int = 0


@dataclass
class InformacoesResseguro:
    """Informações detalhadas de cessão ao resseguro"""

    # Cessão total
    premios_cedidos_total: float = 0.0
    sinistros_recuperados_resseguro: float = 0.0
    provisoes_ressegurador: float = 0.0

    # Estrutura de resseguro
    retencao_maxima_risco: float = 0.0  # Limite máximo retido por risco
    retencao_maxima_evento: float = 0.0  # Limite máximo por evento

    # Tipo de contratos
    quota_parte_percentual: float = 0.0  # % cedido em quota parte
    excesso_danos_valor: float = 0.0  # Prioridade em XL
    catastrofe_cobertura: float = 0.0  # Cobertura Cat

    # Qualidade dos resseguradores
    rating_medio_resseguradores: str = ""  # Rating médio ponderado
    concentracao_principal_ressegurador: float = 0.0  # % no maior ressegurador
    ressegurador_grupo: bool = False  # Se resseguro é do mesmo grupo

    # Créditos de resseguro
    creditos_resseguro_total: float = 0.0
    provisao_reducao_resseguro: float = 0.0  # PRPC - Provisão Red Créditos Resseg


@dataclass
class LimitesCapacidade:
    """Limites de capacidade própria da seguradora"""

    # Limites regulatórios
    limite_retencao_susep: float = 0.0  # Limite SUSEP
    limite_operacional: float = 0.0  # Limite operacional interno

    # Limites calculados
    limite_por_risco_calculado: float = 0.0  # Máximo por risco individual
    limite_por_evento_calculado: float = 0.0  # Máximo por evento
    limite_agregado_calculado: float = 0.0  # Máximo agregado anual

    # Referência de 50 milhões
    LIMITE_REFERENCIA: float = 50_000_000  # R$ 50 milhões como referência
    atende_limite_referencia: bool = False
    margem_sobre_referencia: float = 0.0  # Quanto excede ou falta


@dataclass
class Fissura:
    """Representa uma fissura/fragilidade identificada"""

    tipo: TipoFissura = TipoFissura.CAPACIDADE_INSUFICIENTE
    nivel_risco: NivelRisco = NivelRisco.MODERADO
    descricao: str = ""
    valor_referencia: float = 0.0  # Valor que evidencia a fissura
    limite_aceitavel: float = 0.0  # Limite que deveria ser respeitado
    gap_percentual: float = 0.0  # Gap em % entre real e aceitável
    recomendacao: str = ""
    impacto_rating: int = 0  # Notches de impacto no rating (-1, -2, etc)


@dataclass
class IndicadoresForcaIsolada:
    """
    Indicadores de Força Financeira Isolada de Resseguro

    Esta classe contém todos os indicadores calculados para avaliar
    a real capacidade de uma seguradora assumir riscos por conta própria,
    identificando dependências de resseguro e rating de grupo.
    """

    # Identificação
    nome_seguradora: str = ""
    data_analise: Optional[date] = None

    # ========== INDICADORES DE DEPENDÊNCIA DE RESSEGURO ==========

    # Taxa de Cessão ao Resseguro
    taxa_cessao_resseguro: float = 0.0  # Prêmios Cedidos / Prêmios Emitidos

    # Índice de Retenção
    indice_retencao: float = 0.0  # Prêmios Retidos / Prêmios Emitidos

    # Dependência de Recuperação de Sinistros
    dependencia_recuperacao: float = 0.0  # Sinistros Recuperados / Sinistros Totais

    # Exposição Líquida ao Risco
    exposicao_liquida: float = 0.0  # (Prêmios Retidos - Sinistros Retidos) / PL

    # Concentração de Resseguro no Grupo
    concentracao_resseguro_grupo: float = 0.0  # Resseguro Grupo / Resseguro Total

    # ========== INDICADORES DE CAPACIDADE PRÓPRIA ==========

    # Patrimônio Líquido Real (sem ajustes de grupo)
    patrimonio_liquido_real: float = 0.0

    # Capital Próprio Efetivo
    capital_proprio_efetivo: float = 0.0  # PL - Ativos Intangíveis - Créditos Grupo

    # Capacidade Máxima de Retenção por Risco
    capacidade_retencao_risco: float = 0.0  # Baseado em % do Capital Próprio

    # Capacidade Máxima por Evento
    capacidade_retencao_evento: float = 0.0

    # Capacidade Agregada Anual
    capacidade_agregada_anual: float = 0.0

    # Índice de Capacidade vs Referência (50MM)
    indice_capacidade_50mm: float = 0.0  # Capacidade / 50.000.000

    # ========== INDICADORES DE RATING ISOLADO ==========

    # Score de Força Financeira Isolada (0-100)
    score_forca_isolada: float = 0.0

    # Rating Isolado Calculado
    rating_isolado: str = ""  # AAA, AA, A, BBB, BB, B, CCC, CC, C, D

    # Rating Declarado (do grupo)
    rating_declarado: str = ""

    # Gap de Rating (diferença em notches)
    gap_rating_notches: int = 0

    # Inflação de Rating (%)
    inflacao_rating: float = 0.0  # Quanto o rating está inflado

    # ========== INDICADORES DE SOLVÊNCIA ISOLADA ==========

    # Índice de Solvência Isolado
    indice_solvencia_isolado: float = 0.0  # PL Real / Passivo sem Grupo

    # Cobertura de Provisões Isolada
    cobertura_provisoes_isolada: float = 0.0  # Ativos Próprios / Provisões

    # Margem de Solvência Isolada
    margem_solvencia_isolada: float = 0.0  # PL Ajustado - CMR Isolado

    # Suficiência de Capital Isolada
    suficiencia_capital_isolada: float = 0.0  # Capital Efetivo / Capital Necessário

    # ========== INDICADORES DE LIQUIDEZ ISOLADA ==========

    # Liquidez sem Créditos de Grupo
    liquidez_isolada: float = 0.0  # Ativos Líquidos Próprios / Passivo CP

    # Dependência de Caixa do Grupo
    dependencia_caixa_grupo: float = 0.0  # Caixa Grupo / Caixa Total

    # ========== INDICADORES DE STRESS ==========

    # Impacto de Perda de Resseguro
    impacto_perda_resseguro: float = 0.0  # Quanto perderia se resseguro falhar

    # Capacidade de Absorção de Sinistros
    capacidade_absorcao_sinistros: float = 0.0  # Máximo sinistro absorvível

    # Resiliência a Eventos Catastróficos
    resiliencia_catastrofe: float = 0.0  # PL / Exposição Catastrófica

    # ========== CLASSIFICAÇÃO FINAL ==========

    # Classificação de Risco Isolado
    classificacao_risco_isolado: NivelRisco = NivelRisco.MODERADO

    # Lista de Fissuras Identificadas
    fissuras: List[Fissura] = field(default_factory=list)

    # Alertas Críticos
    alertas_criticos: List[str] = field(default_factory=list)

    # Recomendações
    recomendacoes: List[str] = field(default_factory=list)

    # Score de Vulnerabilidade (0-100, quanto maior mais vulnerável)
    score_vulnerabilidade: float = 0.0

    # Parecer Final
    parecer_final: str = ""


@dataclass
class SeguradoraComResseguro:
    """
    Extensão da classe Seguradora com informações de resseguro e grupo
    para análise de força financeira isolada
    """

    # Código da seguradora no sistema
    codigo_seguradora: str = ""
    nome_seguradora: str = ""

    # Informações do grupo
    info_grupo: InformacoesGrupo = field(default_factory=InformacoesGrupo)

    # Informações de resseguro
    info_resseguro: InformacoesResseguro = field(default_factory=InformacoesResseguro)

    # Limites de capacidade
    limites: LimitesCapacidade = field(default_factory=LimitesCapacidade)

    # Indicadores calculados
    indicadores_isolados: IndicadoresForcaIsolada = field(
        default_factory=IndicadoresForcaIsolada
    )

    # Maior Sinistro Individual Histórico
    maior_sinistro_historico: float = 0.0

    # Exposição Acumulada em Riscos > 50MM
    exposicao_riscos_grandes: float = 0.0

    # Quantidade de apólices > 50MM
    qtd_apolices_grandes: int = 0


@dataclass
class ComparacaoRating:
    """Comparação entre rating declarado e rating isolado calculado"""

    seguradora: str = ""
    rating_declarado: str = ""
    rating_grupo: str = ""
    rating_isolado_calculado: str = ""
    gap_notches: int = 0
    justificativa_gap: str = ""
    principais_fissuras: List[str] = field(default_factory=list)
    recomendacao_prudencial: str = ""


@dataclass
class RelatorioForcaIsolada:
    """Relatório completo de análise de força financeira isolada"""

    data_geracao: Optional[date] = None
    periodo_analise: str = ""

    # Resumo Executivo
    total_seguradoras_analisadas: int = 0
    seguradoras_risco_critico: int = 0
    seguradoras_rating_inflado: int = 0
    seguradoras_capacidade_insuficiente: int = 0

    # Análises individuais
    analises: List[IndicadoresForcaIsolada] = field(default_factory=list)

    # Comparações de rating
    comparacoes_rating: List[ComparacaoRating] = field(default_factory=list)

    # Ranking por vulnerabilidade
    ranking_vulnerabilidade: List[str] = field(default_factory=list)

    # Fissuras mais comuns no mercado
    fissuras_frequentes: List[tuple] = field(default_factory=list)  # (tipo, contagem)

    # Parecer geral do mercado
    parecer_mercado: str = ""
