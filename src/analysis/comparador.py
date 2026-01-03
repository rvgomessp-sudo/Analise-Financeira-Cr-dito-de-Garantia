"""
Comparador de Força Financeira entre Seguradoras
Permite análise comparativa e ranking de seguradoras
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import pandas as pd
from ..models.seguradora import Seguradora, IndicadoresFinanceiros
from .indicadores import AnalisadorIndicadores


@dataclass
class ResultadoComparacao:
    """Resultado da comparação entre seguradoras"""
    ranking_geral: pd.DataFrame
    ranking_solvencia: pd.DataFrame
    ranking_liquidez: pd.DataFrame
    ranking_rentabilidade: pd.DataFrame
    ranking_sinistralidade: pd.DataFrame
    estatisticas_setor: Dict
    matriz_comparativa: pd.DataFrame


class ComparadorSeguradora:
    """
    Classe para comparar a força financeira entre múltiplas seguradoras
    """

    def __init__(self):
        self.analisador = AnalisadorIndicadores()
        self.seguradoras: List[Seguradora] = []
        self.indicadores_calculados: Dict[str, IndicadoresFinanceiros] = {}

    def adicionar_seguradora(self, seguradora: Seguradora) -> None:
        """
        Adiciona uma seguradora para comparação

        Args:
            seguradora: Objeto Seguradora com dados financeiros
        """
        self.seguradoras.append(seguradora)

        # Calcula indicadores se ainda não foram calculados
        indicadores = self.analisador.calcular_indicadores(seguradora)
        seguradora.indicadores = indicadores
        self.indicadores_calculados[seguradora.nome] = indicadores

    def adicionar_multiplas(self, seguradoras: List[Seguradora]) -> None:
        """Adiciona múltiplas seguradoras para comparação"""
        for seg in seguradoras:
            self.adicionar_seguradora(seg)

    def comparar(self) -> ResultadoComparacao:
        """
        Realiza a comparação completa entre todas as seguradoras

        Returns:
            ResultadoComparacao com todos os rankings e estatísticas
        """
        if len(self.seguradoras) < 2:
            raise ValueError("É necessário pelo menos 2 seguradoras para comparação")

        # Gera DataFrame com todos os indicadores
        df = self._gerar_dataframe_indicadores()

        # Rankings por categoria
        ranking_geral = self._gerar_ranking_geral(df)
        ranking_solvencia = self._gerar_ranking_solvencia(df)
        ranking_liquidez = self._gerar_ranking_liquidez(df)
        ranking_rentabilidade = self._gerar_ranking_rentabilidade(df)
        ranking_sinistralidade = self._gerar_ranking_sinistralidade(df)

        # Estatísticas do setor
        estatisticas = self._calcular_estatisticas_setor(df)

        # Matriz comparativa
        matriz = self._gerar_matriz_comparativa(df)

        return ResultadoComparacao(
            ranking_geral=ranking_geral,
            ranking_solvencia=ranking_solvencia,
            ranking_liquidez=ranking_liquidez,
            ranking_rentabilidade=ranking_rentabilidade,
            ranking_sinistralidade=ranking_sinistralidade,
            estatisticas_setor=estatisticas,
            matriz_comparativa=matriz
        )

    def _gerar_dataframe_indicadores(self) -> pd.DataFrame:
        """Gera DataFrame com todos os indicadores de todas as seguradoras"""
        dados = []

        for seg in self.seguradoras:
            ind = seg.indicadores
            dados.append({
                'Seguradora': seg.nome,
                'Código SUSEP': seg.codigo_susep,
                'Grupo Econômico': seg.grupo_economico,
                'Ano': seg.ano_exercicio,

                # Tamanho
                'Ativo Total (R$ MM)': seg.balanco.ativo_total / 1_000_000,
                'PL (R$ MM)': seg.balanco.patrimonio_liquido / 1_000_000,
                'Prêmios (R$ MM)': seg.dre.premios_emitidos / 1_000_000,
                'Lucro (R$ MM)': seg.dre.lucro_liquido / 1_000_000,

                # Solvência
                'Índice Solvência': ind.indice_solvencia,
                'Cobertura Provisões': ind.cobertura_provisoes,
                'Margem Solvência (R$ MM)': ind.margem_solvencia / 1_000_000,

                # Liquidez
                'Liquidez Corrente': ind.liquidez_corrente,
                'Liquidez Seca': ind.liquidez_seca,
                'Liquidez Imediata': ind.liquidez_imediata,

                # Rentabilidade
                'ROE (%)': ind.roe * 100,
                'ROA (%)': ind.roa * 100,
                'Margem Líquida (%)': ind.margem_liquida * 100,
                'Margem Operacional (%)': ind.margem_operacional * 100,

                # Sinistralidade
                'Sinistralidade (%)': ind.indice_sinistralidade * 100,
                'Índice Despesas (%)': ind.indice_despesas * 100,
                'Índice Combinado (%)': ind.indice_combinado * 100,
                'Combinado Ampliado (%)': ind.indice_combinado_ampliado * 100,

                # Estrutura
                'Endividamento (%)': ind.endividamento * 100,
                'Imobilização PL (%)': ind.imobilizacao_pl * 100,
                'Alavancagem': ind.alavancagem,

                # Score e Rating
                'Score Força Financeira': ind.score_forca_financeira,
                'Rating': ind.classificacao_risco
            })

        return pd.DataFrame(dados)

    def _gerar_ranking_geral(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera ranking geral baseado no score de força financeira"""
        ranking = df[['Seguradora', 'Score Força Financeira', 'Rating',
                      'Ativo Total (R$ MM)', 'PL (R$ MM)', 'Prêmios (R$ MM)']].copy()
        ranking = ranking.sort_values('Score Força Financeira', ascending=False)
        ranking['Posição'] = range(1, len(ranking) + 1)
        ranking = ranking[['Posição', 'Seguradora', 'Score Força Financeira',
                           'Rating', 'Ativo Total (R$ MM)', 'PL (R$ MM)', 'Prêmios (R$ MM)']]
        return ranking.reset_index(drop=True)

    def _gerar_ranking_solvencia(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera ranking de solvência"""
        ranking = df[['Seguradora', 'Índice Solvência', 'Cobertura Provisões',
                      'Margem Solvência (R$ MM)']].copy()
        ranking['Score Solvência'] = (
            (ranking['Índice Solvência'] / ranking['Índice Solvência'].max()) * 50 +
            (ranking['Cobertura Provisões'] / ranking['Cobertura Provisões'].max()) * 50
        )
        ranking = ranking.sort_values('Score Solvência', ascending=False)
        ranking['Posição'] = range(1, len(ranking) + 1)
        return ranking[['Posição', 'Seguradora', 'Índice Solvência',
                        'Cobertura Provisões', 'Margem Solvência (R$ MM)', 'Score Solvência']].reset_index(drop=True)

    def _gerar_ranking_liquidez(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera ranking de liquidez"""
        ranking = df[['Seguradora', 'Liquidez Corrente', 'Liquidez Seca',
                      'Liquidez Imediata']].copy()
        ranking['Score Liquidez'] = (
            (ranking['Liquidez Corrente'] / ranking['Liquidez Corrente'].max()) * 33.33 +
            (ranking['Liquidez Seca'] / ranking['Liquidez Seca'].max()) * 33.33 +
            (ranking['Liquidez Imediata'] / ranking['Liquidez Imediata'].max()) * 33.34
        )
        ranking = ranking.sort_values('Score Liquidez', ascending=False)
        ranking['Posição'] = range(1, len(ranking) + 1)
        return ranking[['Posição', 'Seguradora', 'Liquidez Corrente',
                        'Liquidez Seca', 'Liquidez Imediata', 'Score Liquidez']].reset_index(drop=True)

    def _gerar_ranking_rentabilidade(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera ranking de rentabilidade"""
        ranking = df[['Seguradora', 'ROE (%)', 'ROA (%)',
                      'Margem Líquida (%)', 'Lucro (R$ MM)']].copy()
        # Normaliza considerando valores negativos
        roe_norm = (ranking['ROE (%)'] - ranking['ROE (%)'].min()) / \
                   (ranking['ROE (%)'].max() - ranking['ROE (%)'].min() + 0.0001)
        ml_norm = (ranking['Margem Líquida (%)'] - ranking['Margem Líquida (%)'].min()) / \
                  (ranking['Margem Líquida (%)'].max() - ranking['Margem Líquida (%)'].min() + 0.0001)

        ranking['Score Rentabilidade'] = (roe_norm * 50 + ml_norm * 50) * 100
        ranking = ranking.sort_values('Score Rentabilidade', ascending=False)
        ranking['Posição'] = range(1, len(ranking) + 1)
        return ranking[['Posição', 'Seguradora', 'ROE (%)', 'ROA (%)',
                        'Margem Líquida (%)', 'Lucro (R$ MM)', 'Score Rentabilidade']].reset_index(drop=True)

    def _gerar_ranking_sinistralidade(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera ranking de sinistralidade (menor é melhor)"""
        ranking = df[['Seguradora', 'Sinistralidade (%)', 'Índice Despesas (%)',
                      'Índice Combinado (%)']].copy()
        # Inverte a pontuação (menor sinistralidade = maior score)
        max_sind = ranking['Sinistralidade (%)'].max()
        max_comb = ranking['Índice Combinado (%)'].max()

        ranking['Score Sinistralidade'] = (
            ((max_sind - ranking['Sinistralidade (%)']) / max_sind) * 50 +
            ((max_comb - ranking['Índice Combinado (%)']) / max_comb) * 50
        ) * 100

        ranking = ranking.sort_values('Score Sinistralidade', ascending=False)
        ranking['Posição'] = range(1, len(ranking) + 1)
        return ranking[['Posição', 'Seguradora', 'Sinistralidade (%)',
                        'Índice Despesas (%)', 'Índice Combinado (%)', 'Score Sinistralidade']].reset_index(drop=True)

    def _calcular_estatisticas_setor(self, df: pd.DataFrame) -> Dict:
        """Calcula estatísticas agregadas do setor"""
        return {
            'total_seguradoras': len(df),
            'ativo_total_setor': df['Ativo Total (R$ MM)'].sum(),
            'pl_total_setor': df['PL (R$ MM)'].sum(),
            'premios_total_setor': df['Prêmios (R$ MM)'].sum(),
            'lucro_total_setor': df['Lucro (R$ MM)'].sum(),

            'media': {
                'score_forca_financeira': df['Score Força Financeira'].mean(),
                'indice_solvencia': df['Índice Solvência'].mean(),
                'liquidez_corrente': df['Liquidez Corrente'].mean(),
                'roe': df['ROE (%)'].mean(),
                'sinistralidade': df['Sinistralidade (%)'].mean(),
                'indice_combinado': df['Índice Combinado (%)'].mean(),
            },

            'mediana': {
                'score_forca_financeira': df['Score Força Financeira'].median(),
                'indice_solvencia': df['Índice Solvência'].median(),
                'liquidez_corrente': df['Liquidez Corrente'].median(),
                'roe': df['ROE (%)'].median(),
                'sinistralidade': df['Sinistralidade (%)'].median(),
                'indice_combinado': df['Índice Combinado (%)'].median(),
            },

            'desvio_padrao': {
                'score_forca_financeira': df['Score Força Financeira'].std(),
                'indice_solvencia': df['Índice Solvência'].std(),
                'liquidez_corrente': df['Liquidez Corrente'].std(),
                'roe': df['ROE (%)'].std(),
                'sinistralidade': df['Sinistralidade (%)'].std(),
            },

            'melhor': {
                'seguradora': df.loc[df['Score Força Financeira'].idxmax(), 'Seguradora'],
                'score': df['Score Força Financeira'].max(),
                'rating': df.loc[df['Score Força Financeira'].idxmax(), 'Rating'],
            },

            'pior': {
                'seguradora': df.loc[df['Score Força Financeira'].idxmin(), 'Seguradora'],
                'score': df['Score Força Financeira'].min(),
                'rating': df.loc[df['Score Força Financeira'].idxmin(), 'Rating'],
            },

            'distribuicao_rating': df['Rating'].value_counts().to_dict(),
        }

    def _gerar_matriz_comparativa(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera matriz comparativa com indicadores-chave"""
        indicadores_chave = [
            'Seguradora', 'Rating', 'Score Força Financeira',
            'Índice Solvência', 'Liquidez Corrente', 'ROE (%)',
            'Sinistralidade (%)', 'Índice Combinado (%)', 'Endividamento (%)'
        ]

        matriz = df[indicadores_chave].copy()
        matriz = matriz.sort_values('Score Força Financeira', ascending=False)
        return matriz.reset_index(drop=True)

    def comparar_duas_seguradoras(
        self,
        seguradora_a: Seguradora,
        seguradora_b: Seguradora
    ) -> Dict:
        """
        Comparação detalhada entre duas seguradoras específicas

        Args:
            seguradora_a: Primeira seguradora
            seguradora_b: Segunda seguradora

        Returns:
            Dicionário com comparação detalhada
        """
        ind_a = seguradora_a.indicadores
        ind_b = seguradora_b.indicadores

        comparacao = {
            'seguradora_a': seguradora_a.nome,
            'seguradora_b': seguradora_b.nome,
            'vencedor_geral': seguradora_a.nome if ind_a.score_forca_financeira > ind_b.score_forca_financeira else seguradora_b.nome,
            'diferenca_score': abs(ind_a.score_forca_financeira - ind_b.score_forca_financeira),

            'comparativo': {
                'tamanho': {
                    'ativo_total': {
                        seguradora_a.nome: seguradora_a.balanco.ativo_total,
                        seguradora_b.nome: seguradora_b.balanco.ativo_total,
                        'maior': seguradora_a.nome if seguradora_a.balanco.ativo_total > seguradora_b.balanco.ativo_total else seguradora_b.nome
                    },
                    'patrimonio_liquido': {
                        seguradora_a.nome: seguradora_a.balanco.patrimonio_liquido,
                        seguradora_b.nome: seguradora_b.balanco.patrimonio_liquido,
                        'maior': seguradora_a.nome if seguradora_a.balanco.patrimonio_liquido > seguradora_b.balanco.patrimonio_liquido else seguradora_b.nome
                    }
                },

                'solvencia': {
                    'indice': {
                        seguradora_a.nome: ind_a.indice_solvencia,
                        seguradora_b.nome: ind_b.indice_solvencia,
                        'melhor': seguradora_a.nome if ind_a.indice_solvencia > ind_b.indice_solvencia else seguradora_b.nome
                    },
                    'cobertura_provisoes': {
                        seguradora_a.nome: ind_a.cobertura_provisoes,
                        seguradora_b.nome: ind_b.cobertura_provisoes,
                        'melhor': seguradora_a.nome if ind_a.cobertura_provisoes > ind_b.cobertura_provisoes else seguradora_b.nome
                    }
                },

                'liquidez': {
                    'corrente': {
                        seguradora_a.nome: ind_a.liquidez_corrente,
                        seguradora_b.nome: ind_b.liquidez_corrente,
                        'melhor': seguradora_a.nome if ind_a.liquidez_corrente > ind_b.liquidez_corrente else seguradora_b.nome
                    },
                    'imediata': {
                        seguradora_a.nome: ind_a.liquidez_imediata,
                        seguradora_b.nome: ind_b.liquidez_imediata,
                        'melhor': seguradora_a.nome if ind_a.liquidez_imediata > ind_b.liquidez_imediata else seguradora_b.nome
                    }
                },

                'rentabilidade': {
                    'roe': {
                        seguradora_a.nome: ind_a.roe,
                        seguradora_b.nome: ind_b.roe,
                        'melhor': seguradora_a.nome if ind_a.roe > ind_b.roe else seguradora_b.nome
                    },
                    'margem_liquida': {
                        seguradora_a.nome: ind_a.margem_liquida,
                        seguradora_b.nome: ind_b.margem_liquida,
                        'melhor': seguradora_a.nome if ind_a.margem_liquida > ind_b.margem_liquida else seguradora_b.nome
                    }
                },

                'sinistralidade': {
                    'indice': {
                        seguradora_a.nome: ind_a.indice_sinistralidade,
                        seguradora_b.nome: ind_b.indice_sinistralidade,
                        'melhor': seguradora_a.nome if ind_a.indice_sinistralidade < ind_b.indice_sinistralidade else seguradora_b.nome
                    },
                    'combinado': {
                        seguradora_a.nome: ind_a.indice_combinado,
                        seguradora_b.nome: ind_b.indice_combinado,
                        'melhor': seguradora_a.nome if ind_a.indice_combinado < ind_b.indice_combinado else seguradora_b.nome
                    }
                },

                'rating': {
                    seguradora_a.nome: ind_a.classificacao_risco,
                    seguradora_b.nome: ind_b.classificacao_risco,
                },

                'score_forca_financeira': {
                    seguradora_a.nome: ind_a.score_forca_financeira,
                    seguradora_b.nome: ind_b.score_forca_financeira,
                }
            }
        }

        return comparacao

    def gerar_resumo_executivo(self) -> str:
        """Gera um resumo executivo textual da comparação"""
        if len(self.seguradoras) < 2:
            return "É necessário pelo menos 2 seguradoras para gerar o resumo."

        resultado = self.comparar()
        stats = resultado.estatisticas_setor

        resumo = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RESUMO EXECUTIVO - ANÁLISE COMPARATIVA                   ║
║                        FORÇA FINANCEIRA DE SEGURADORAS                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 VISÃO GERAL DO SETOR ANALISADO
────────────────────────────────────────────────────────────────────────────────
• Total de Seguradoras Analisadas: {stats['total_seguradoras']}
• Ativo Total do Setor: R$ {stats['ativo_total_setor']:,.2f} milhões
• Patrimônio Líquido Total: R$ {stats['pl_total_setor']:,.2f} milhões
• Prêmios Emitidos Total: R$ {stats['premios_total_setor']:,.2f} milhões
• Lucro Líquido Total: R$ {stats['lucro_total_setor']:,.2f} milhões

🏆 RANKING DE FORÇA FINANCEIRA
────────────────────────────────────────────────────────────────────────────────
"""
        # Top 3 seguradoras
        ranking = resultado.ranking_geral.head(3)
        for _, row in ranking.iterrows():
            resumo += f"  {int(row['Posição'])}º - {row['Seguradora']}: Score {row['Score Força Financeira']:.1f} (Rating {row['Rating']})\n"

        resumo += f"""
📈 ESTATÍSTICAS MÉDIAS DO SETOR
────────────────────────────────────────────────────────────────────────────────
• Score Médio de Força Financeira: {stats['media']['score_forca_financeira']:.1f}
• Índice de Solvência Médio: {stats['media']['indice_solvencia']:.2f}
• Liquidez Corrente Média: {stats['media']['liquidez_corrente']:.2f}
• ROE Médio: {stats['media']['roe']:.1f}%
• Sinistralidade Média: {stats['media']['sinistralidade']:.1f}%
• Índice Combinado Médio: {stats['media']['indice_combinado']:.1f}%

🎯 DISTRIBUIÇÃO DE RATINGS
────────────────────────────────────────────────────────────────────────────────
"""
        for rating, count in sorted(stats['distribuicao_rating'].items()):
            resumo += f"  • {rating}: {count} seguradora(s)\n"

        resumo += f"""
✅ MELHOR SEGURADORA
────────────────────────────────────────────────────────────────────────────────
  {stats['melhor']['seguradora']}
  Score: {stats['melhor']['score']:.1f} | Rating: {stats['melhor']['rating']}

⚠️ SEGURADORA COM MENOR SCORE
────────────────────────────────────────────────────────────────────────────────
  {stats['pior']['seguradora']}
  Score: {stats['pior']['score']:.1f} | Rating: {stats['pior']['rating']}

══════════════════════════════════════════════════════════════════════════════
"""
        return resumo
