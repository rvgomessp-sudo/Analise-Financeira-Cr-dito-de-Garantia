"""
Modelos de Estrutura Societária para Seguradoras Brasileiras

CONCEITOS FUNDAMENTAIS:
=======================

1. MATRIZ vs FILIAL (mesma pessoa jurídica):
   - MATRIZ: Sede principal onde está o CNPJ raiz
   - FILIAL: Estabelecimento secundário com mesmo CNPJ raiz mas sufixo diferente
   - Exemplo: Junto Seguros matriz (PR) e filial (SP) são a mesma empresa

2. CONTROLADORA vs SUBSIDIÁRIA (pessoas jurídicas distintas):
   - CONTROLADORA: Empresa que detém controle acionário de outra
   - SUBSIDIÁRIA: Empresa controlada por outra (CNPJ diferente)
   - Exemplo: Zurich Insurance Group (Suíça) controla Zurich Brasil Seguros

3. GRUPO ECONÔMICO/SEGURADOR:
   - Conjunto de empresas sob controle comum
   - Para seguradoras: NÃO inclui resseguradoras na avaliação de força
   - O rating do GRUPO pode ser emprestado para subsidiárias

IMPORTANTE: Este módulo trata EXCLUSIVAMENTE de seguradoras.
A análise de resseguro é feita em módulo separado (forca_isolada.py).
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import date
from enum import Enum


class TipoEntidade(Enum):
    """Tipo de entidade dentro da estrutura societária"""

    # Entidade Principal
    MATRIZ = "Matriz"
    CONTROLADORA = "Controladora"
    HOLDING = "Holding"

    # Entidade Secundária
    FILIAL = "Filial"
    SUBSIDIARIA = "Subsidiária"
    CONTROLADA = "Controlada"
    COLIGADA = "Coligada"

    # Entidade Internacional
    MATRIZ_INTERNACIONAL = "Matriz Internacional"
    SUBSIDIARIA_BRASILEIRA = "Subsidiária Brasileira"


class TipoControle(Enum):
    """Tipo de controle societário"""

    CONTROLE_TOTAL = "Controle Total (>50%)"
    CONTROLE_COMPARTILHADO = "Controle Compartilhado"
    INFLUENCIA_SIGNIFICATIVA = "Influência Significativa (20-50%)"
    PARTICIPACAO_MINORITARIA = "Participação Minoritária (<20%)"
    SEM_VINCULO = "Sem Vínculo Societário"


class OrigemCapital(Enum):
    """Origem do capital da seguradora"""

    NACIONAL_PRIVADO = "Capital Nacional Privado"
    NACIONAL_PUBLICO = "Capital Nacional Público"
    ESTRANGEIRO = "Capital Estrangeiro"
    MISTO = "Capital Misto"


class TipoRating(Enum):
    """Origem do rating da seguradora"""

    RATING_PROPRIO = "Rating Próprio (força isolada)"
    RATING_GRUPO = "Rating do Grupo (emprestado)"
    RATING_CONTROLADORA = "Rating da Controladora"
    SEM_RATING = "Sem Rating Formal"


@dataclass
class ControladoraInternacional:
    """
    Representa a controladora internacional de uma subsidiária brasileira

    Exemplo: Zurich Insurance Group é a controladora internacional
    da Zurich Brasil Seguros S.A.
    """

    # Identificação
    nome: str = ""
    pais_sede: str = ""
    codigo_identificacao: str = ""  # LEI, SWIFT ou outro identificador

    # Rating
    rating: str = ""
    agencia_rating: str = ""  # S&P, Fitch, Moody's, AM Best
    data_rating: Optional[date] = None
    outlook: str = ""  # Stable, Positive, Negative

    # Dados Financeiros (em USD ou EUR para internacionais)
    patrimonio_liquido_usd: float = 0.0
    ativo_total_usd: float = 0.0
    premios_emitidos_usd: float = 0.0
    lucro_liquido_usd: float = 0.0

    # Conversão para BRL
    patrimonio_liquido_brl: float = 0.0
    ativo_total_brl: float = 0.0
    premios_emitidos_brl: float = 0.0
    lucro_liquido_brl: float = 0.0
    taxa_cambio_usada: float = 0.0

    # Histórico
    anos_operacao: int = 0
    paises_atuacao: int = 0

    # Suporte à subsidiária
    carta_suporte: bool = False
    valor_carta_suporte_brl: float = 0.0
    garantia_explicita: bool = False


@dataclass
class VinculoSocietario:
    """
    Representa o vínculo entre duas entidades

    Define claramente a relação: quem controla quem,
    qual o percentual, e como isso afeta o rating.
    """

    # Entidade controladora
    nome_controladora: str = ""
    cnpj_controladora: str = ""
    tipo_controladora: TipoEntidade = TipoEntidade.CONTROLADORA

    # Entidade controlada
    nome_controlada: str = ""
    cnpj_controlada: str = ""
    tipo_controlada: TipoEntidade = TipoEntidade.SUBSIDIARIA

    # Caracterização do vínculo
    percentual_participacao: float = 0.0
    tipo_controle: TipoControle = TipoControle.CONTROLE_TOTAL
    data_inicio_controle: Optional[date] = None

    # Impacto no rating
    rating_emprestado: bool = False  # Se subsidiária usa rating do grupo
    notches_diferenca: int = 0  # Diferença entre rating próprio e grupo

    # Suporte financeiro
    ha_carta_suporte: bool = False
    valor_suporte_brl: float = 0.0
    historico_aportes_brl: float = 0.0


@dataclass
class FilialRegional:
    """
    Representa uma filial (mesmo CNPJ raiz) em outra localidade

    Exemplo: Junto Seguros tem matriz no PR e filial em SP.
    São a MESMA empresa jurídica, apenas estabelecimentos diferentes.
    """

    # Identificação
    nome_filial: str = ""
    cnpj_filial: str = ""  # CNPJ com sufixo diferente da matriz
    uf: str = ""
    cidade: str = ""
    tipo: str = "Filial"  # Filial, Agência, Escritório

    # Status
    ativa: bool = True
    data_abertura: Optional[date] = None

    # Operações (se disponível)
    premios_emitidos_brl: float = 0.0
    participacao_total: float = 0.0  # % do total da empresa


@dataclass
class GrupoSegurador:
    """
    Representa um Grupo Segurador/Econômico

    CONCEITO CRÍTICO:
    ================
    O grupo segurador é a ESTRUTURA SOCIETÁRIA da seguradora.
    NÃO inclui resseguradoras na composição do rating da seguradora.

    Exemplos:
    - Zurich Insurance Group: grupo global que controla Zurich Brasil
    - Junto Seguros: seguradora independente (não faz parte de grupo maior)
      mas pode ter relação com resseguradora para SUPORTE OPERACIONAL

    O rating do grupo pode ser "emprestado" às subsidiárias, mas isso
    deve ser claramente identificado como RATING_GRUPO vs RATING_PROPRIO.
    """

    # Identificação do Grupo
    nome_grupo: str = ""
    pais_sede: str = ""
    tipo_grupo: str = ""  # Internacional, Nacional, Regional

    # Rating do Grupo
    rating_grupo: str = ""
    agencia_rating: str = ""
    data_rating: Optional[date] = None

    # Composição do Grupo (apenas seguradoras, não resseguradoras)
    controladora: Optional[ControladoraInternacional] = None
    subsidiarias_brasil: List[str] = field(default_factory=list)
    total_empresas_grupo: int = 0

    # Dados Consolidados do Grupo
    patrimonio_liquido_consolidado_brl: float = 0.0
    ativo_total_consolidado_brl: float = 0.0
    premios_emitidos_consolidado_brl: float = 0.0

    # Força do Grupo
    anos_mercado: int = 0
    paises_atuacao: int = 0
    posicao_ranking_global: int = 0

    # Características
    origem_capital: OrigemCapital = OrigemCapital.ESTRANGEIRO
    tem_suporte_explicito: bool = False


@dataclass
class IndicadoresFinanceirosBRL:
    """
    Indicadores financeiros em BRL para comparação direta

    Todos os valores em Reais (R$) para facilitar comparação
    entre seguradoras brasileiras.
    """

    # Referência
    data_referencia: Optional[date] = None
    fonte_dados: str = ""  # SUSEP, Demonstrações Financeiras, etc.

    # Balanço Patrimonial
    ativo_total: float = 0.0
    ativo_circulante: float = 0.0
    disponibilidades: float = 0.0
    aplicacoes_financeiras: float = 0.0
    patrimonio_liquido: float = 0.0
    capital_social: float = 0.0
    provisoes_tecnicas: float = 0.0

    # DRE
    premios_emitidos: float = 0.0
    premios_ganhos: float = 0.0
    premios_retidos: float = 0.0
    sinistros_ocorridos: float = 0.0
    resultado_financeiro: float = 0.0
    lucro_liquido: float = 0.0

    # Indicadores Chave
    indice_sinistralidade: float = 0.0
    indice_combinado: float = 0.0
    liquidez_corrente: float = 0.0
    indice_solvencia: float = 0.0
    roe: float = 0.0
    roa: float = 0.0

    # Regulatórios
    margem_solvencia: float = 0.0
    capital_minimo_requerido: float = 0.0
    patrimonio_liquido_ajustado: float = 0.0
    suficiencia_pla: float = 0.0  # PLA / CMR


@dataclass
class SeguradoraBrasileira:
    """
    Modelo completo de uma seguradora brasileira com estrutura societária

    Este modelo integra:
    - Identificação completa (SUSEP, CNPJ)
    - Estrutura societária (matriz/filial, controladora/subsidiária)
    - Vínculo com grupo econômico
    - Indicadores financeiros em BRL
    - Rating próprio vs rating de grupo
    """

    # ============ IDENTIFICAÇÃO BÁSICA ============

    codigo_susep: str = ""
    nome_oficial: str = ""  # Razão social
    nome_fantasia: str = ""
    cnpj: str = ""

    # Localização da matriz
    uf_matriz: str = ""
    cidade_matriz: str = ""
    endereco_matriz: str = ""

    # Datas importantes
    data_constituicao: Optional[date] = None
    data_autorizacao_susep: Optional[date] = None

    # ============ ESTRUTURA SOCIETÁRIA ============

    # Tipo desta entidade
    tipo_entidade: TipoEntidade = TipoEntidade.MATRIZ

    # Se é subsidiária de empresa estrangeira
    eh_subsidiaria_estrangeira: bool = False
    controladora_internacional: Optional[ControladoraInternacional] = None

    # Se faz parte de grupo nacional
    grupo_economico: Optional[GrupoSegurador] = None

    # Vínculo societário (se aplicável)
    vinculo: Optional[VinculoSocietario] = None

    # Filiais (se for matriz)
    filiais: List[FilialRegional] = field(default_factory=list)

    # ============ RATING E CLASSIFICAÇÃO ============

    # Rating declarado/publicado
    rating_declarado: str = ""
    agencia_rating: str = ""
    data_rating: Optional[date] = None

    # Origem do rating
    tipo_rating: TipoRating = TipoRating.RATING_PROPRIO

    # Rating calculado (força isolada)
    rating_calculado: str = ""
    score_forca_isolada: float = 0.0

    # Gap entre rating declarado e calculado
    gap_rating: int = 0  # Em notches
    rating_inflado: bool = False

    # ============ DADOS FINANCEIROS BRL ============

    indicadores: IndicadoresFinanceirosBRL = field(
        default_factory=IndicadoresFinanceirosBRL
    )

    # Histórico de exercícios
    historico_indicadores: Dict[int, IndicadoresFinanceirosBRL] = field(
        default_factory=dict
    )

    # ============ CAPACIDADE E LIMITES ============

    # Capacidade de retenção
    limite_retencao_risco: float = 0.0
    limite_retencao_evento: float = 0.0

    # Referência de R$ 50 milhões
    atende_limite_50mm: bool = False
    margem_sobre_50mm: float = 0.0

    # ============ SEGURANÇA DA APÓLICE ============

    # Avaliação de segurança
    nota_seguranca_apolice: str = ""  # A+, A, A-, B+, B, B-, C
    parecer_seguranca: str = ""

    # Fatores de segurança
    fatores_positivos: List[str] = field(default_factory=list)
    fatores_atencao: List[str] = field(default_factory=list)
    fatores_risco: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validações e inicializações após criação"""
        self._validar_estrutura()
        self._calcular_gap_rating()

    def _validar_estrutura(self):
        """Valida consistência da estrutura societária"""
        if self.eh_subsidiaria_estrangeira and not self.controladora_internacional:
            # Warning: subsidiária sem controladora definida
            pass

        if self.tipo_entidade == TipoEntidade.FILIAL and self.filiais:
            # Warning: filial não deveria ter filiais
            pass

    def _calcular_gap_rating(self):
        """Calcula gap entre rating declarado e calculado"""
        if self.rating_declarado and self.rating_calculado:
            # Implementar lógica de cálculo de notches
            escala = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-',
                     'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-',
                     'B+', 'B', 'B-', 'CCC', 'CC', 'C', 'D']

            try:
                pos_declarado = escala.index(self.rating_declarado)
                pos_calculado = escala.index(self.rating_calculado)
                self.gap_rating = pos_calculado - pos_declarado
                self.rating_inflado = self.gap_rating > 0
            except ValueError:
                pass

    def eh_matriz(self) -> bool:
        """Verifica se é matriz (sede principal)"""
        return self.tipo_entidade in [TipoEntidade.MATRIZ, TipoEntidade.CONTROLADORA]

    def eh_subsidiaria(self) -> bool:
        """Verifica se é subsidiária de outra empresa"""
        return self.tipo_entidade in [
            TipoEntidade.SUBSIDIARIA,
            TipoEntidade.CONTROLADA,
            TipoEntidade.SUBSIDIARIA_BRASILEIRA
        ]

    def tem_suporte_grupo(self) -> bool:
        """Verifica se tem suporte de grupo econômico"""
        if self.grupo_economico:
            return self.grupo_economico.tem_suporte_explicito
        if self.controladora_internacional:
            return self.controladora_internacional.garantia_explicita
        return False

    def obter_rating_efetivo(self) -> str:
        """
        Retorna o rating efetivo considerando a estrutura

        Se é subsidiária com suporte de grupo, pode usar rating do grupo.
        Caso contrário, usa rating próprio (força isolada).
        """
        if self.tipo_rating == TipoRating.RATING_GRUPO:
            if self.grupo_economico:
                return self.grupo_economico.rating_grupo
            if self.controladora_internacional:
                return self.controladora_internacional.rating

        return self.rating_declarado or self.rating_calculado

    def gerar_resumo_estrutura(self) -> str:
        """Gera resumo da estrutura societária"""
        linhas = []
        linhas.append(f"{'='*60}")
        linhas.append(f"ESTRUTURA SOCIETÁRIA: {self.nome_oficial}")
        linhas.append(f"{'='*60}")

        # Tipo de entidade
        linhas.append(f"\nTipo: {self.tipo_entidade.value}")
        linhas.append(f"CNPJ: {self.cnpj}")
        linhas.append(f"Código SUSEP: {self.codigo_susep}")
        linhas.append(f"Sede: {self.cidade_matriz}/{self.uf_matriz}")

        # Estrutura societária
        if self.eh_subsidiaria_estrangeira and self.controladora_internacional:
            linhas.append(f"\n--- CONTROLADORA INTERNACIONAL ---")
            linhas.append(f"Nome: {self.controladora_internacional.nome}")
            linhas.append(f"País: {self.controladora_internacional.pais_sede}")
            linhas.append(f"Rating: {self.controladora_internacional.rating} ({self.controladora_internacional.agencia_rating})")
            linhas.append(f"Patrimônio (BRL): R$ {self.controladora_internacional.patrimonio_liquido_brl:,.2f}")

        if self.grupo_economico:
            linhas.append(f"\n--- GRUPO ECONÔMICO ---")
            linhas.append(f"Nome: {self.grupo_economico.nome_grupo}")
            linhas.append(f"Rating Grupo: {self.grupo_economico.rating_grupo}")
            linhas.append(f"PL Consolidado: R$ {self.grupo_economico.patrimonio_liquido_consolidado_brl:,.2f}")

        if self.filiais:
            linhas.append(f"\n--- FILIAIS ({len(self.filiais)}) ---")
            for filial in self.filiais:
                linhas.append(f"  • {filial.nome_filial} ({filial.cidade}/{filial.uf})")

        # Rating
        linhas.append(f"\n--- RATING ---")
        linhas.append(f"Rating Declarado: {self.rating_declarado}")
        linhas.append(f"Tipo do Rating: {self.tipo_rating.value}")
        linhas.append(f"Rating Calculado (Força Isolada): {self.rating_calculado}")
        if self.gap_rating:
            linhas.append(f"Gap: {self.gap_rating} notches {'(INFLADO!)' if self.rating_inflado else ''}")

        return "\n".join(linhas)


@dataclass
class ComparacaoEstruturaSocietaria:
    """
    Comparação de estrutura societária entre seguradoras

    Útil para comparar Zurich Brasil vs Junto Seguros,
    evidenciando diferenças de estrutura e impacto no rating.
    """

    seguradoras: List[SeguradoraBrasileira] = field(default_factory=list)
    data_comparacao: Optional[date] = None

    def comparar_estrutura(self) -> Dict:
        """Compara estrutura societária das seguradoras"""
        resultado = {
            'seguradoras_internacionais': [],
            'seguradoras_nacionais': [],
            'com_suporte_grupo': [],
            'sem_suporte_grupo': [],
            'rating_proprio': [],
            'rating_emprestado': []
        }

        for seg in self.seguradoras:
            # Classificação por origem
            if seg.eh_subsidiaria_estrangeira:
                resultado['seguradoras_internacionais'].append(seg.nome_oficial)
            else:
                resultado['seguradoras_nacionais'].append(seg.nome_oficial)

            # Suporte de grupo
            if seg.tem_suporte_grupo():
                resultado['com_suporte_grupo'].append(seg.nome_oficial)
            else:
                resultado['sem_suporte_grupo'].append(seg.nome_oficial)

            # Tipo de rating
            if seg.tipo_rating == TipoRating.RATING_PROPRIO:
                resultado['rating_proprio'].append(seg.nome_oficial)
            else:
                resultado['rating_emprestado'].append(seg.nome_oficial)

        return resultado

    def comparar_indicadores_brl(self) -> Dict:
        """Compara indicadores financeiros em BRL"""
        comparacao = {}

        for seg in self.seguradoras:
            comparacao[seg.nome_oficial] = {
                'patrimonio_liquido': seg.indicadores.patrimonio_liquido,
                'ativo_total': seg.indicadores.ativo_total,
                'premios_emitidos': seg.indicadores.premios_emitidos,
                'lucro_liquido': seg.indicadores.lucro_liquido,
                'indice_solvencia': seg.indicadores.indice_solvencia,
                'roe': seg.indicadores.roe,
                'rating_declarado': seg.rating_declarado,
                'rating_calculado': seg.rating_calculado,
                'tipo_rating': seg.tipo_rating.value
            }

        return comparacao

    def gerar_tabela_comparativa(self) -> str:
        """Gera tabela comparativa formatada"""
        if not self.seguradoras:
            return "Nenhuma seguradora para comparar"

        # Cabeçalho
        linhas = []
        linhas.append("=" * 100)
        linhas.append("COMPARATIVO DE ESTRUTURA SOCIETÁRIA E INDICADORES (BRL)")
        linhas.append("=" * 100)

        # Tabela de estrutura
        linhas.append("\n📊 ESTRUTURA SOCIETÁRIA:")
        linhas.append("-" * 100)
        header = f"{'Seguradora':<30} {'Tipo':<20} {'Origem':<15} {'Suporte Grupo':<15}"
        linhas.append(header)
        linhas.append("-" * 100)

        for seg in self.seguradoras:
            origem = "Internacional" if seg.eh_subsidiaria_estrangeira else "Nacional"
            suporte = "Sim" if seg.tem_suporte_grupo() else "Não"
            linha = f"{seg.nome_fantasia:<30} {seg.tipo_entidade.value:<20} {origem:<15} {suporte:<15}"
            linhas.append(linha)

        # Tabela de indicadores
        linhas.append("\n💰 INDICADORES FINANCEIROS (R$):")
        linhas.append("-" * 100)
        header = f"{'Seguradora':<25} {'PL (MM)':<15} {'Ativo (MM)':<15} {'Prêmios (MM)':<15} {'Lucro (MM)':<15}"
        linhas.append(header)
        linhas.append("-" * 100)

        for seg in self.seguradoras:
            pl = seg.indicadores.patrimonio_liquido / 1_000_000
            at = seg.indicadores.ativo_total / 1_000_000
            pr = seg.indicadores.premios_emitidos / 1_000_000
            ll = seg.indicadores.lucro_liquido / 1_000_000
            linha = f"{seg.nome_fantasia:<25} {pl:>12,.1f} {at:>14,.1f} {pr:>14,.1f} {ll:>14,.1f}"
            linhas.append(linha)

        # Rating
        linhas.append("\n⭐ RATING E FORÇA FINANCEIRA:")
        linhas.append("-" * 100)
        header = f"{'Seguradora':<25} {'Rating Dec.':<12} {'Tipo Rating':<20} {'Rating Calc.':<12} {'Gap':<8}"
        linhas.append(header)
        linhas.append("-" * 100)

        for seg in self.seguradoras:
            gap_str = f"{seg.gap_rating:+d}" if seg.gap_rating else "0"
            linha = f"{seg.nome_fantasia:<25} {seg.rating_declarado:<12} {seg.tipo_rating.value:<20} {seg.rating_calculado:<12} {gap_str:<8}"
            linhas.append(linha)

        # Segurança da Apólice
        linhas.append("\n🛡️ SEGURANÇA DA APÓLICE:")
        linhas.append("-" * 100)
        for seg in self.seguradoras:
            linhas.append(f"\n{seg.nome_fantasia}:")
            linhas.append(f"  Nota de Segurança: {seg.nota_seguranca_apolice}")
            linhas.append(f"  Parecer: {seg.parecer_seguranca}")
            if seg.fatores_positivos:
                linhas.append(f"  ✅ Pontos Fortes: {', '.join(seg.fatores_positivos[:3])}")
            if seg.fatores_atencao:
                linhas.append(f"  ⚠️ Atenção: {', '.join(seg.fatores_atencao[:3])}")

        return "\n".join(linhas)
