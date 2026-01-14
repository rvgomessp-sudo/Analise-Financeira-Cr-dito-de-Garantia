"""
Analisador de Estrutura Societária para Seguradoras

Este módulo implementa a análise completa de estrutura societária,
permitindo diferenciar claramente:

1. MATRIZ vs FILIAL (mesma pessoa jurídica)
2. CONTROLADORA vs SUBSIDIÁRIA (pessoas jurídicas distintas)
3. RATING PRÓPRIO vs RATING DE GRUPO

IMPORTANTE:
==========
- Este módulo analisa APENAS a estrutura societária das SEGURADORAS
- A análise de RESSEGURO é feita em módulo separado (analisador_forca_isolada.py)
- O "grupo" aqui refere-se à ESTRUTURA SOCIETÁRIA, não à composição com resseguro

EXEMPLO DE USO:
==============
A Zurich Brasil é SUBSIDIÁRIA do Zurich Insurance Group (Suíça).
A Junto Seguros é MATRIZ nacional com FILIAIS em SP, RJ, MG.
São estruturas completamente diferentes que impactam o rating.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import date
from enum import Enum

from src.models.estrutura_societaria import (
    SeguradoraBrasileira,
    TipoEntidade,
    TipoRating,
    TipoControle,
    OrigemCapital,
    IndicadoresFinanceirosBRL,
    ComparacaoEstruturaSocietaria,
)


class ClassificacaoSeguranca(Enum):
    """Classificação de segurança da apólice"""
    MAXIMA = "Segurança Máxima"
    ALTA = "Alta Segurança"
    BOA = "Boa Segurança"
    ADEQUADA = "Segurança Adequada"
    ATENCAO = "Requer Atenção"
    RISCO = "Risco Elevado"


@dataclass
class AnaliseEstrutural:
    """Resultado da análise estrutural de uma seguradora"""

    # Identificação
    nome_seguradora: str = ""
    cnpj: str = ""
    data_analise: Optional[date] = None

    # Classificação Estrutural
    eh_subsidiaria_internacional: bool = False
    eh_matriz_nacional: bool = False
    eh_filial: bool = False
    pertence_grupo: bool = False

    # Rating
    rating_declarado: str = ""
    origem_rating: str = ""  # "Próprio" ou "Grupo"
    rating_isolado: str = ""
    gap_rating: int = 0
    rating_inflado: bool = False

    # Suporte de Grupo
    tem_suporte_grupo: bool = False
    patrimonio_grupo_brl: float = 0.0
    tipo_suporte: str = ""

    # Indicadores Chave
    patrimonio_liquido_brl: float = 0.0
    ativo_total_brl: float = 0.0
    premios_emitidos_brl: float = 0.0
    roe: float = 0.0

    # Segurança da Apólice
    classificacao_seguranca: ClassificacaoSeguranca = ClassificacaoSeguranca.ADEQUADA
    nota_seguranca: str = ""
    parecer: str = ""

    # Fatores
    fatores_positivos: List[str] = field(default_factory=list)
    fatores_atencao: List[str] = field(default_factory=list)
    fatores_risco: List[str] = field(default_factory=list)


@dataclass
class ComparacaoEstrutural:
    """Comparação estrutural entre duas ou mais seguradoras"""

    seguradoras_analisadas: List[str] = field(default_factory=list)
    data_comparacao: Optional[date] = None

    # Classificações
    subsidiarias_internacionais: List[str] = field(default_factory=list)
    matrizes_nacionais: List[str] = field(default_factory=list)
    com_rating_grupo: List[str] = field(default_factory=list)
    com_rating_proprio: List[str] = field(default_factory=list)

    # Rankings
    ranking_patrimonio: List[Tuple[str, float]] = field(default_factory=list)
    ranking_premios: List[Tuple[str, float]] = field(default_factory=list)
    ranking_roe: List[Tuple[str, float]] = field(default_factory=list)

    # Análises individuais
    analises: Dict[str, AnaliseEstrutural] = field(default_factory=dict)


class AnalisadorEstruturaSocietaria:
    """
    Analisador de Estrutura Societária para Seguradoras

    CONCEITOS FUNDAMENTAIS:
    ======================

    1. MATRIZ vs FILIAL (mesma pessoa jurídica):
       - MATRIZ: Sede principal onde está o CNPJ raiz
       - FILIAL: Estabelecimento secundário com sufixo diferente
       - São a MESMA empresa juridicamente

    2. CONTROLADORA vs SUBSIDIÁRIA (pessoas jurídicas distintas):
       - CONTROLADORA: Empresa que detém controle acionário de outra
       - SUBSIDIÁRIA: Empresa controlada (CNPJ totalmente diferente)
       - São EMPRESAS DIFERENTES

    3. RATING PRÓPRIO vs RATING DE GRUPO:
       - PRÓPRIO: Baseado na força financeira isolada da seguradora
       - GRUPO: "Emprestado" da controladora/grupo econômico

    IMPORTANTE:
    ==========
    - NÃO confundir GRUPO com RESSEGURO
    - O grupo é a estrutura SOCIETÁRIA (quem controla quem)
    - A análise de resseguro é SEPARADA (outro módulo)
    """

    # Escala de ratings para cálculo de gap
    ESCALA_RATING = [
        'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-',
        'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-',
        'B+', 'B', 'B-', 'CCC', 'CC', 'C', 'D'
    ]

    # Escala brasileira
    ESCALA_RATING_BR = [
        'brAAA', 'brAA+', 'brAA', 'brAA-', 'brA+', 'brA', 'brA-',
        'brBBB+', 'brBBB', 'brBBB-', 'brBB+', 'brBB', 'brBB-',
        'brB+', 'brB', 'brB-', 'brCCC', 'brCC', 'brC', 'brD'
    ]

    def __init__(self):
        """Inicializa o analisador"""
        self.seguradoras_analisadas: List[SeguradoraBrasileira] = []

    def analisar_seguradora(
        self,
        seguradora: SeguradoraBrasileira
    ) -> AnaliseEstrutural:
        """
        Analisa a estrutura societária de uma seguradora

        Args:
            seguradora: Instância de SeguradoraBrasileira

        Returns:
            AnaliseEstrutural com todos os detalhes
        """
        analise = AnaliseEstrutural(
            nome_seguradora=seguradora.nome_oficial,
            cnpj=seguradora.cnpj,
            data_analise=date.today(),
        )

        # Classificação Estrutural
        self._classificar_estrutura(seguradora, analise)

        # Análise de Rating
        self._analisar_rating(seguradora, analise)

        # Análise de Suporte de Grupo
        self._analisar_suporte_grupo(seguradora, analise)

        # Indicadores Financeiros
        self._extrair_indicadores(seguradora, analise)

        # Classificação de Segurança
        self._classificar_seguranca(seguradora, analise)

        # Registra seguradora analisada
        self.seguradoras_analisadas.append(seguradora)

        return analise

    def _classificar_estrutura(
        self,
        seguradora: SeguradoraBrasileira,
        analise: AnaliseEstrutural
    ) -> None:
        """Classifica a estrutura societária"""

        # Subsidiária Internacional
        if seguradora.eh_subsidiaria_estrangeira:
            analise.eh_subsidiaria_internacional = True
            analise.pertence_grupo = True

        # Matriz Nacional
        if seguradora.tipo_entidade in [
            TipoEntidade.MATRIZ,
            TipoEntidade.CONTROLADORA
        ]:
            analise.eh_matriz_nacional = True

        # Filial
        if seguradora.tipo_entidade == TipoEntidade.FILIAL:
            analise.eh_filial = True

        # Pertence a Grupo
        if seguradora.grupo_economico or seguradora.controladora_internacional:
            analise.pertence_grupo = True

    def _analisar_rating(
        self,
        seguradora: SeguradoraBrasileira,
        analise: AnaliseEstrutural
    ) -> None:
        """Analisa a origem e qualidade do rating"""

        analise.rating_declarado = seguradora.rating_declarado
        analise.rating_isolado = seguradora.rating_calculado

        # Determina origem do rating
        if seguradora.tipo_rating == TipoRating.RATING_PROPRIO:
            analise.origem_rating = "Próprio (Força Isolada)"
        elif seguradora.tipo_rating == TipoRating.RATING_GRUPO:
            analise.origem_rating = "Grupo (Emprestado)"
        elif seguradora.tipo_rating == TipoRating.RATING_CONTROLADORA:
            analise.origem_rating = "Controladora"
        else:
            analise.origem_rating = "Não Definido"

        # Calcula gap
        analise.gap_rating = seguradora.gap_rating
        analise.rating_inflado = seguradora.rating_inflado

    def _analisar_suporte_grupo(
        self,
        seguradora: SeguradoraBrasileira,
        analise: AnaliseEstrutural
    ) -> None:
        """Analisa o suporte de grupo econômico"""

        if seguradora.controladora_internacional:
            analise.tem_suporte_grupo = True
            analise.patrimonio_grupo_brl = (
                seguradora.controladora_internacional.patrimonio_liquido_brl
            )
            if seguradora.controladora_internacional.garantia_explicita:
                analise.tipo_suporte = "Garantia Explícita"
            elif seguradora.controladora_internacional.carta_suporte:
                analise.tipo_suporte = "Carta de Suporte"
            else:
                analise.tipo_suporte = "Suporte Implícito"

        elif seguradora.grupo_economico:
            if seguradora.grupo_economico.tem_suporte_explicito:
                analise.tem_suporte_grupo = True
                analise.patrimonio_grupo_brl = (
                    seguradora.grupo_economico.patrimonio_liquido_consolidado_brl
                )
                analise.tipo_suporte = "Suporte do Grupo"

    def _extrair_indicadores(
        self,
        seguradora: SeguradoraBrasileira,
        analise: AnaliseEstrutural
    ) -> None:
        """Extrai indicadores financeiros"""

        analise.patrimonio_liquido_brl = seguradora.indicadores.patrimonio_liquido
        analise.ativo_total_brl = seguradora.indicadores.ativo_total
        analise.premios_emitidos_brl = seguradora.indicadores.premios_emitidos
        analise.roe = seguradora.indicadores.roe

    def _classificar_seguranca(
        self,
        seguradora: SeguradoraBrasileira,
        analise: AnaliseEstrutural
    ) -> None:
        """Classifica o nível de segurança da apólice"""

        # Pontuação base
        pontos = 0

        # Rating (até 40 pontos)
        if seguradora.rating_declarado in ['AAA', 'brAAA']:
            pontos += 40
        elif seguradora.rating_declarado in ['AA+', 'AA', 'AA-', 'brAA+', 'brAA', 'brAA-']:
            pontos += 35
        elif seguradora.rating_declarado in ['A+', 'A', 'A-', 'brA+', 'brA', 'brA-']:
            pontos += 30
        elif seguradora.rating_declarado.startswith('BBB') or seguradora.rating_declarado.startswith('brBBB'):
            pontos += 25
        elif seguradora.rating_declarado.startswith('BB') or seguradora.rating_declarado.startswith('brBB'):
            pontos += 15
        else:
            pontos += 5

        # Suporte de Grupo (até 20 pontos)
        if analise.tem_suporte_grupo:
            if analise.patrimonio_grupo_brl > 100_000_000_000:  # > 100 bi
                pontos += 20
            elif analise.patrimonio_grupo_brl > 10_000_000_000:  # > 10 bi
                pontos += 15
            else:
                pontos += 10

        # Patrimônio Próprio (até 20 pontos)
        pl = seguradora.indicadores.patrimonio_liquido
        if pl > 1_000_000_000:  # > 1 bi
            pontos += 20
        elif pl > 500_000_000:  # > 500 mi
            pontos += 15
        elif pl > 200_000_000:  # > 200 mi
            pontos += 10
        else:
            pontos += 5

        # Indicadores Operacionais (até 20 pontos)
        if seguradora.indicadores.indice_solvencia > 0.5:
            pontos += 5
        if seguradora.indicadores.liquidez_corrente > 1.2:
            pontos += 5
        if seguradora.indicadores.roe > 15:
            pontos += 5
        if seguradora.indicadores.indice_sinistralidade < 50:
            pontos += 5

        # Penalização por rating inflado
        if analise.rating_inflado:
            pontos -= analise.gap_rating * 3

        # Classificação
        if pontos >= 90:
            analise.classificacao_seguranca = ClassificacaoSeguranca.MAXIMA
            analise.nota_seguranca = "A+"
        elif pontos >= 80:
            analise.classificacao_seguranca = ClassificacaoSeguranca.ALTA
            analise.nota_seguranca = "A"
        elif pontos >= 70:
            analise.classificacao_seguranca = ClassificacaoSeguranca.BOA
            analise.nota_seguranca = "A-"
        elif pontos >= 60:
            analise.classificacao_seguranca = ClassificacaoSeguranca.ADEQUADA
            analise.nota_seguranca = "B+"
        elif pontos >= 50:
            analise.classificacao_seguranca = ClassificacaoSeguranca.ATENCAO
            analise.nota_seguranca = "B"
        else:
            analise.classificacao_seguranca = ClassificacaoSeguranca.RISCO
            analise.nota_seguranca = "C"

        # Fatores
        analise.fatores_positivos = seguradora.fatores_positivos.copy()
        analise.fatores_atencao = seguradora.fatores_atencao.copy()
        analise.fatores_risco = seguradora.fatores_risco.copy()

        # Parecer
        analise.parecer = seguradora.parecer_seguranca

    def comparar_seguradoras(
        self,
        seguradoras: List[SeguradoraBrasileira]
    ) -> ComparacaoEstrutural:
        """
        Compara estrutura societária de múltiplas seguradoras

        Args:
            seguradoras: Lista de seguradoras para comparar

        Returns:
            ComparacaoEstrutural com análise comparativa
        """
        comparacao = ComparacaoEstrutural(
            data_comparacao=date.today(),
        )

        for seg in seguradoras:
            # Analisa individualmente
            analise = self.analisar_seguradora(seg)
            comparacao.analises[seg.nome_oficial] = analise
            comparacao.seguradoras_analisadas.append(seg.nome_oficial)

            # Classifica
            if analise.eh_subsidiaria_internacional:
                comparacao.subsidiarias_internacionais.append(seg.nome_oficial)
            else:
                comparacao.matrizes_nacionais.append(seg.nome_oficial)

            if analise.origem_rating == "Próprio (Força Isolada)":
                comparacao.com_rating_proprio.append(seg.nome_oficial)
            else:
                comparacao.com_rating_grupo.append(seg.nome_oficial)

        # Rankings
        comparacao.ranking_patrimonio = sorted(
            [(nome, a.patrimonio_liquido_brl) for nome, a in comparacao.analises.items()],
            key=lambda x: x[1],
            reverse=True
        )
        comparacao.ranking_premios = sorted(
            [(nome, a.premios_emitidos_brl) for nome, a in comparacao.analises.items()],
            key=lambda x: x[1],
            reverse=True
        )
        comparacao.ranking_roe = sorted(
            [(nome, a.roe) for nome, a in comparacao.analises.items()],
            key=lambda x: x[1],
            reverse=True
        )

        return comparacao

    def gerar_relatorio_comparativo(
        self,
        comparacao: ComparacaoEstrutural
    ) -> str:
        """
        Gera relatório comparativo formatado

        Args:
            comparacao: ComparacaoEstrutural com dados

        Returns:
            Relatório em texto formatado
        """
        linhas = []

        # Cabeçalho
        linhas.append("=" * 90)
        linhas.append("RELATÓRIO COMPARATIVO DE ESTRUTURA SOCIETÁRIA")
        linhas.append("=" * 90)
        linhas.append(f"Data: {comparacao.data_comparacao}")
        linhas.append(f"Seguradoras: {len(comparacao.seguradoras_analisadas)}")
        linhas.append("")

        # Classificação Estrutural
        linhas.append("-" * 90)
        linhas.append("CLASSIFICAÇÃO ESTRUTURAL")
        linhas.append("-" * 90)
        linhas.append("")

        linhas.append("📌 SUBSIDIÁRIAS DE GRUPOS INTERNACIONAIS:")
        if comparacao.subsidiarias_internacionais:
            for nome in comparacao.subsidiarias_internacionais:
                analise = comparacao.analises[nome]
                linhas.append(f"   • {nome}")
                linhas.append(f"     Rating: {analise.rating_declarado} ({analise.origem_rating})")
                linhas.append(f"     PL Grupo: R$ {analise.patrimonio_grupo_brl/1e9:,.1f} bilhões")
        else:
            linhas.append("   (nenhuma)")
        linhas.append("")

        linhas.append("📌 MATRIZES NACIONAIS (força própria):")
        if comparacao.matrizes_nacionais:
            for nome in comparacao.matrizes_nacionais:
                analise = comparacao.analises[nome]
                linhas.append(f"   • {nome}")
                linhas.append(f"     Rating: {analise.rating_declarado} ({analise.origem_rating})")
                linhas.append(f"     PL Próprio: R$ {analise.patrimonio_liquido_brl/1e6:,.1f} milhões")
        else:
            linhas.append("   (nenhuma)")
        linhas.append("")

        # Comparativo de Rating
        linhas.append("-" * 90)
        linhas.append("ANÁLISE DE RATING")
        linhas.append("-" * 90)
        linhas.append("")

        linhas.append("┌────────────────────────┬──────────────┬─────────────────────────┬──────────────┬─────────┐")
        linhas.append("│ Seguradora             │ Rating Decl. │ Origem                  │ Rating Isol. │ Gap     │")
        linhas.append("├────────────────────────┼──────────────┼─────────────────────────┼──────────────┼─────────┤")

        for nome, analise in comparacao.analises.items():
            nome_fmt = nome[:22] if len(nome) > 22 else nome
            gap_str = f"{analise.gap_rating:+d}" if analise.gap_rating else "0"
            linhas.append(
                f"│ {nome_fmt:<22} │ {analise.rating_declarado:<12} │ {analise.origem_rating:<23} │ {analise.rating_isolado:<12} │ {gap_str:<7} │"
            )

        linhas.append("└────────────────────────┴──────────────┴─────────────────────────┴──────────────┴─────────┘")
        linhas.append("")

        # Indicadores Financeiros
        linhas.append("-" * 90)
        linhas.append("INDICADORES FINANCEIROS (BRL)")
        linhas.append("-" * 90)
        linhas.append("")

        linhas.append("┌────────────────────────┬────────────────┬────────────────┬────────────────┬──────────┐")
        linhas.append("│ Seguradora             │ PL (milhões)   │ Ativo (milhões)│ Prêmios (mi)   │ ROE      │")
        linhas.append("├────────────────────────┼────────────────┼────────────────┼────────────────┼──────────┤")

        for nome, analise in comparacao.analises.items():
            nome_fmt = nome[:22] if len(nome) > 22 else nome
            pl = analise.patrimonio_liquido_brl / 1e6
            at = analise.ativo_total_brl / 1e6
            pr = analise.premios_emitidos_brl / 1e6
            roe = analise.roe
            linhas.append(
                f"│ {nome_fmt:<22} │ R$ {pl:>10,.1f} │ R$ {at:>10,.1f} │ R$ {pr:>10,.1f} │ {roe:>6.1f}% │"
            )

        linhas.append("└────────────────────────┴────────────────┴────────────────┴────────────────┴──────────┘")
        linhas.append("")

        # Segurança da Apólice
        linhas.append("-" * 90)
        linhas.append("SEGURANÇA DA APÓLICE")
        linhas.append("-" * 90)
        linhas.append("")

        for nome, analise in comparacao.analises.items():
            linhas.append(f">>> {nome}")
            linhas.append(f"    Classificação: {analise.classificacao_seguranca.value}")
            linhas.append(f"    Nota: {analise.nota_seguranca}")
            linhas.append(f"    Suporte de Grupo: {'Sim (' + analise.tipo_suporte + ')' if analise.tem_suporte_grupo else 'Não'}")
            linhas.append("")

            if analise.fatores_positivos:
                linhas.append("    ✅ Pontos Fortes:")
                for fator in analise.fatores_positivos[:3]:
                    linhas.append(f"       • {fator}")

            if analise.fatores_atencao:
                linhas.append("    ⚠️ Pontos de Atenção:")
                for fator in analise.fatores_atencao[:2]:
                    linhas.append(f"       • {fator}")

            linhas.append("")

        # Conclusão
        linhas.append("=" * 90)
        linhas.append("CONCLUSÃO")
        linhas.append("=" * 90)
        linhas.append("")

        if comparacao.subsidiarias_internacionais and comparacao.matrizes_nacionais:
            linhas.append("DIFERENÇAS IDENTIFICADAS:")
            linhas.append("")
            linhas.append("As seguradoras analisadas possuem estruturas societárias DISTINTAS:")
            linhas.append("")
            linhas.append(f"• SUBSIDIÁRIAS INTERNACIONAIS ({len(comparacao.subsidiarias_internacionais)}):")
            linhas.append("  - Rating tende a ser 'emprestado' do grupo controlador")
            linhas.append("  - Força isolada pode ser menor que o rating declarado")
            linhas.append("  - Segurança da apólice depende indiretamente do grupo")
            linhas.append("")
            linhas.append(f"• MATRIZES NACIONAIS ({len(comparacao.matrizes_nacionais)}):")
            linhas.append("  - Rating é baseado na força financeira PRÓPRIA")
            linhas.append("  - Não há gap entre rating declarado e isolado")
            linhas.append("  - Segurança da apólice depende da força própria")
            linhas.append("")

        linhas.append("AMBAS AS ESTRUTURAS PODEM SER SEGURAS PARA APÓLICES.")
        linhas.append("A diferença está na ORIGEM da segurança:")
        linhas.append("  • Subsidiárias: Suporte do grupo internacional")
        linhas.append("  • Matrizes Nacionais: Força financeira própria")
        linhas.append("")

        return "\n".join(linhas)

    def explicar_diferenca_matriz_filial_subsidiaria(self) -> str:
        """
        Retorna explicação detalhada sobre as diferenças conceituais

        MATRIZ vs FILIAL: Mesma empresa, locais diferentes
        CONTROLADORA vs SUBSIDIÁRIA: Empresas diferentes, mesmo grupo
        """
        return """
═══════════════════════════════════════════════════════════════════════════════════════════
                    DIFERENCIAÇÃO: MATRIZ, FILIAL E SUBSIDIÁRIA
═══════════════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        1. MATRIZ vs FILIAL (mesma empresa)                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  MATRIZ                          FILIAL                                                 │
│  ──────                          ──────                                                 │
│  • Sede principal                • Estabelecimento secundário                           │
│  • CNPJ raiz (8 dígitos)         • CNPJ com sufixo diferente                           │
│  • Onde a empresa foi fundada    • Pode estar em qualquer local                        │
│  • Centro de decisões            • Opera sob direção da matriz                         │
│                                                                                         │
│  EXEMPLO:                                                                               │
│  Junto Seguros S.A. (CNPJ 84.948.157/0001-33) → MATRIZ em Curitiba/PR                 │
│  Junto Seguros S.A. (CNPJ 84.948.157/0002-14) → FILIAL em São Paulo/SP                │
│                                                                                         │
│  São a MESMA EMPRESA juridicamente. Mesmo CNPJ raiz, sufixos diferentes.              │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                  2. CONTROLADORA vs SUBSIDIÁRIA (empresas diferentes)                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  CONTROLADORA                    SUBSIDIÁRIA                                            │
│  ────────────                    ───────────                                            │
│  • Empresa que controla outra    • Empresa controlada                                   │
│  • CNPJ completamente diferente  • CNPJ completamente diferente                         │
│  • Detém participação acionária  • Recebe investimento/controle                        │
│  • Pode dar suporte financeiro   • Pode usar rating do grupo                           │
│                                                                                         │
│  EXEMPLO:                                                                               │
│  Zurich Insurance Group (Suíça) → CONTROLADORA internacional                           │
│  Zurich Minas Brasil Seguros S.A. (CNPJ 17.197.385/0001-21) → SUBSIDIÁRIA brasileira  │
│                                                                                         │
│  São EMPRESAS DIFERENTES. CNPJs completamente distintos (e países diferentes).         │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              3. GRUPO ECONÔMICO/SEGURADOR                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  DEFINIÇÃO:                                                                             │
│  Conjunto de empresas sob controle comum ou influência significativa mútua.            │
│                                                                                         │
│  CARACTERÍSTICAS:                                                                       │
│  • Controladora + Subsidiárias + Coligadas                                              │
│  • Podem compartilhar gestão, recursos, marca                                           │
│  • O rating do GRUPO pode ser usado pelas subsidiárias                                  │
│                                                                                         │
│  ⚠️ IMPORTANTE:                                                                         │
│  • GRUPO refere-se à estrutura SOCIETÁRIA (quem controla quem)                         │
│  • NÃO confundir com RESSEGURO (que é operação de transferência de risco)              │
│  • A análise de resseguro é feita em módulo SEPARADO                                    │
│                                                                                         │
│  EXEMPLO DE GRUPO:                                                                      │
│  ┌────────────────────────────────────────────────┐                                    │
│  │        Zurich Insurance Group (Suíça)          │ ← CONTROLADORA                     │
│  │              Rating: AA (S&P/Fitch)            │                                    │
│  └────────────────────────────────────────────────┘                                    │
│                         │                                                               │
│          ┌──────────────┼──────────────┐                                               │
│          ▼              ▼              ▼                                                │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                                 │
│  │ Zurich Minas  │ │ Zurich        │ │ Zurich        │ ← SUBSIDIÁRIAS                  │
│  │ Brasil        │ │ Santander     │ │ Previdência   │                                 │
│  │ Rating: AA*   │ │ Brasil        │ │ Brasil        │                                 │
│  └───────────────┘ └───────────────┘ └───────────────┘                                 │
│                                                                                         │
│  * Rating AA é do GRUPO, não da força isolada da subsidiária                           │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           4. IMPACTO NO RATING DA APÓLICE                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  RATING PRÓPRIO (força isolada):                                                        │
│  • Baseado apenas nos números da seguradora                                             │
│  • Não depende de suporte externo                                                       │
│  • Exemplo: Junto Seguros (brAAA é rating próprio)                                      │
│                                                                                         │
│  RATING DE GRUPO (emprestado):                                                          │
│  • Subsidiária usa rating da controladora                                               │
│  • Depende do suporte do grupo                                                          │
│  • Exemplo: Zurich Brasil (AA é do grupo Zurich)                                        │
│                                                                                         │
│  GAP DE RATING:                                                                         │
│  • Diferença entre rating declarado e rating isolado                                    │
│  • Indica quanto o rating depende do suporte do grupo                                   │
│  • Gap > 0 significa rating "inflado" pelo grupo                                        │
│                                                                                         │
│  AMBOS PODEM SER SEGUROS, mas a fonte da segurança é diferente:                        │
│  • Subsidiárias: segurança vem do grupo                                                │
│  • Matrizes Nacionais: segurança vem da própria empresa                                │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════════
"""


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def criar_analisador() -> AnalisadorEstruturaSocietaria:
    """Cria instância do analisador"""
    return AnalisadorEstruturaSocietaria()


def analisar_e_comparar(
    seguradoras: List[SeguradoraBrasileira]
) -> Tuple[ComparacaoEstrutural, str]:
    """
    Analisa e compara lista de seguradoras

    Args:
        seguradoras: Lista de seguradoras

    Returns:
        Tupla com (ComparacaoEstrutural, relatório_texto)
    """
    analisador = criar_analisador()
    comparacao = analisador.comparar_seguradoras(seguradoras)
    relatorio = analisador.gerar_relatorio_comparativo(comparacao)
    return comparacao, relatorio
