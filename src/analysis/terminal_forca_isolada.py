"""
Interface de Terminal para Análise de Força Financeira Isolada

Módulo de apresentação visual da análise de força financeira isolada,
identificando fissuras e fragilidades de seguradoras que dependem
do rating do grupo econômico.
"""

import sys
import os
from typing import List, Optional

from ..models.seguradora import Seguradora
from ..models.forca_isolada import (
    IndicadoresForcaIsolada,
    InformacoesGrupo,
    InformacoesResseguro,
    NivelRisco,
    TipoFissura,
    RelatorioForcaIsolada
)
from .analisador_forca_isolada import AnalisadorForcaIsolada


# ============================================================================
# CORES E FORMATAÇÃO PARA TERMINAL
# ============================================================================
class Cores:
    """Códigos ANSI para cores no terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'

    PRETO = '\033[30m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    MAGENTA = '\033[35m'
    CIANO = '\033[36m'
    BRANCO = '\033[37m'

    BG_VERMELHO = '\033[41m'
    BG_VERDE = '\033[42m'
    BG_AMARELO = '\033[43m'
    BG_AZUL = '\033[44m'
    BG_MAGENTA = '\033[45m'

    CINZA = '\033[90m'
    VERMELHO_CLARO = '\033[91m'
    VERDE_CLARO = '\033[92m'
    AMARELO_CLARO = '\033[93m'
    AZUL_CLARO = '\033[94m'
    MAGENTA_CLARO = '\033[95m'
    CIANO_CLARO = '\033[96m'


def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa até o usuário pressionar Enter"""
    input(f"\n{Cores.CINZA}Pressione Enter para continuar...{Cores.RESET}")


def formatar_moeda(valor: float) -> str:
    """Formata valor como moeda brasileira"""
    if abs(valor) >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:.2f} Bi"
    elif abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.2f} Mi"
    elif abs(valor) >= 1_000:
        return f"R$ {valor/1_000:.2f} mil"
    else:
        return f"R$ {valor:.2f}"


def cor_nivel_risco(nivel: NivelRisco) -> str:
    """Retorna a cor apropriada para o nível de risco"""
    mapa = {
        NivelRisco.CRITICO: Cores.VERMELHO + Cores.BOLD,
        NivelRisco.ALTO: Cores.VERMELHO_CLARO,
        NivelRisco.MODERADO: Cores.AMARELO,
        NivelRisco.BAIXO: Cores.VERDE,
        NivelRisco.MINIMO: Cores.VERDE_CLARO
    }
    return mapa.get(nivel, Cores.BRANCO)


def cor_rating(rating: str) -> str:
    """Retorna a cor apropriada para o rating"""
    if rating in ['AAA', 'AA+', 'AA']:
        return Cores.VERDE_CLARO
    elif rating in ['AA-', 'A+', 'A']:
        return Cores.VERDE
    elif rating in ['A-', 'BBB+', 'BBB']:
        return Cores.AMARELO_CLARO
    elif rating in ['BBB-', 'BB+', 'BB']:
        return Cores.AMARELO
    elif rating in ['BB-', 'B+', 'B']:
        return Cores.VERMELHO_CLARO
    else:
        return Cores.VERMELHO


def cor_score(score: float) -> str:
    """Retorna a cor apropriada para o score"""
    if score >= 70:
        return Cores.VERDE_CLARO
    elif score >= 55:
        return Cores.VERDE
    elif score >= 40:
        return Cores.AMARELO_CLARO
    elif score >= 25:
        return Cores.AMARELO
    else:
        return Cores.VERMELHO


# ============================================================================
# CLASSE DE INTERFACE TERMINAL
# ============================================================================
class TerminalForcaIsolada:
    """Interface de terminal para análise de força financeira isolada"""

    LIMITE_REFERENCIA_50MM = 50_000_000

    def __init__(self):
        self.analisador = AnalisadorForcaIsolada()
        self.seguradoras: List[Seguradora] = []
        self.infos_grupo: List[InformacoesGrupo] = []
        self.infos_resseguro: List[InformacoesResseguro] = []
        self.resultados: List[IndicadoresForcaIsolada] = []
        self.relatorio: Optional[RelatorioForcaIsolada] = None

    def exibir_cabecalho(self, titulo: str = None):
        """Exibe o cabeçalho da análise de força isolada"""
        limpar_tela()
        print(f"{Cores.BG_MAGENTA}{Cores.BRANCO}{Cores.BOLD}")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "ANÁLISE DE FORÇA FINANCEIRA ISOLADA".center(78) + "║")
        print("║" + "Identificação de Fissuras e Fragilidades".center(78) + "║")
        print("║" + "Referência: Capacidade Própria > R$ 50 Milhões".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print(Cores.RESET)

        if titulo:
            print(f"\n{Cores.MAGENTA_CLARO}{Cores.BOLD}» {titulo}{Cores.RESET}")
            print("─" * 80)

    def exibir_menu_forca_isolada(self) -> str:
        """Exibe o menu de análise de força isolada"""
        self.exibir_cabecalho()

        status = f"{Cores.VERDE}● Análise realizada ({len(self.resultados)} seguradoras){Cores.RESET}" \
            if self.resultados else f"{Cores.AMARELO}○ Análise não realizada{Cores.RESET}"

        print(f"\n  Status: {status}\n")

        print(f"  {Cores.BOLD}{Cores.MAGENTA}╔══════════════════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║         ANÁLISE DE FORÇA FINANCEIRA ISOLADA                  ║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}╠══════════════════════════════════════════════════════════════╣{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}                                                              {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[1]{Cores.RESET} Executar Análise de Força Isolada                    {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[2]{Cores.RESET} Ver Ranking de Vulnerabilidade                       {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[3]{Cores.RESET} Análise Detalhada por Seguradora                     {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[4]{Cores.RESET} Comparação Rating Grupo vs Isolado                   {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[5]{Cores.RESET} Mapa de Fissuras e Fragilidades                      {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[6]{Cores.RESET} Análise de Capacidade (Ref: 50MM)                    {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[7]{Cores.RESET} Relatório de Alertas Críticos                        {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.AMARELO}[8]{Cores.RESET} Análise de Seguradoras Fronting                      {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}                                                              {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}   {Cores.VERMELHO}[0]{Cores.RESET} Voltar ao Menu Principal                            {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}                                                              {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.MAGENTA}╚══════════════════════════════════════════════════════════════╝{Cores.RESET}")

        return input(f"\n  {Cores.BOLD}Digite sua opção: {Cores.RESET}").strip()

    def carregar_dados(
        self,
        seguradoras: List[Seguradora],
        infos_grupo: List[InformacoesGrupo] = None,
        infos_resseguro: List[InformacoesResseguro] = None
    ):
        """Carrega os dados para análise"""
        self.seguradoras = seguradoras
        self.infos_grupo = infos_grupo or []
        self.infos_resseguro = infos_resseguro or []

    def executar_analise(self):
        """Executa a análise de força financeira isolada"""
        self.exibir_cabecalho("Executando Análise de Força Financeira Isolada")

        if not self.seguradoras:
            print(f"\n{Cores.VERMELHO}✗ Nenhuma seguradora carregada!{Cores.RESET}")
            pausar()
            return

        print(f"\n{Cores.AMARELO}⏳ Analisando {len(self.seguradoras)} seguradoras...{Cores.RESET}\n")

        self.resultados = []
        for i, seg in enumerate(self.seguradoras):
            info_grupo = self.infos_grupo[i] if i < len(self.infos_grupo) else None
            info_resseguro = self.infos_resseguro[i] if i < len(self.infos_resseguro) else None

            print(f"  Analisando: {seg.nome}...")

            resultado = self.analisador.analisar_seguradora(
                seg, info_grupo, info_resseguro
            )
            self.resultados.append(resultado)

            # Exibe resumo rápido
            cor = cor_nivel_risco(resultado.classificacao_risco_isolado)
            status = "✓" if resultado.indice_capacidade_50mm >= 1 else "✗"
            status_cor = Cores.VERDE if resultado.indice_capacidade_50mm >= 1 else Cores.VERMELHO

            print(f"    {status_cor}{status}{Cores.RESET} Score Isolado: {cor_score(resultado.score_forca_isolada)}{resultado.score_forca_isolada:.1f}{Cores.RESET} | "
                  f"Rating: {cor_rating(resultado.rating_isolado)}{resultado.rating_isolado}{Cores.RESET} | "
                  f"Risco: {cor}{resultado.classificacao_risco_isolado.value}{Cores.RESET}")

        # Gera relatório consolidado
        self.relatorio = self.analisador.analisar_carteira(
            self.seguradoras, self.infos_grupo, self.infos_resseguro
        )

        print(f"\n{Cores.VERDE}✓ Análise concluída!{Cores.RESET}")

        # Resumo
        print(f"\n{Cores.BOLD}{Cores.CIANO}═══ RESUMO DA ANÁLISE ═══{Cores.RESET}")
        print(f"  Total Analisadas:           {self.relatorio.total_seguradoras_analisadas}")
        print(f"  {Cores.VERMELHO}Risco Crítico:{Cores.RESET}              {self.relatorio.seguradoras_risco_critico}")
        print(f"  {Cores.AMARELO}Rating Inflado:{Cores.RESET}             {self.relatorio.seguradoras_rating_inflado}")
        print(f"  {Cores.VERMELHO_CLARO}Capacidade < 50MM:{Cores.RESET}          {self.relatorio.seguradoras_capacidade_insuficiente}")

        pausar()

    def exibir_ranking_vulnerabilidade(self):
        """Exibe ranking de vulnerabilidade"""
        if not self.resultados:
            self.exibir_cabecalho("Ranking de Vulnerabilidade")
            print(f"\n{Cores.VERMELHO}✗ Execute a análise primeiro (opção 1).{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Ranking de Vulnerabilidade")

        print(f"\n{Cores.BOLD}{Cores.VERMELHO}⚠ RANKING DE VULNERABILIDADE{Cores.RESET}")
        print(f"{Cores.CINZA}(Quanto maior o score, mais vulnerável){Cores.RESET}\n")

        # Ordena por vulnerabilidade (maior primeiro)
        ranking = sorted(self.resultados, key=lambda x: x.score_vulnerabilidade, reverse=True)

        print(f"{Cores.BOLD}{'#':<3} {'SEGURADORA':<28} {'VULN':<8} {'SCORE':<8} {'RATING':<8} {'RISCO':<12} {'FISSURAS':<8}{Cores.RESET}")
        print("─" * 85)

        for pos, res in enumerate(ranking, 1):
            # Ícones de alerta
            if res.score_vulnerabilidade >= 70:
                icone = f"{Cores.VERMELHO}⚠⚠⚠{Cores.RESET}"
            elif res.score_vulnerabilidade >= 50:
                icone = f"{Cores.VERMELHO_CLARO}⚠⚠{Cores.RESET}"
            elif res.score_vulnerabilidade >= 30:
                icone = f"{Cores.AMARELO}⚠{Cores.RESET}"
            else:
                icone = f"{Cores.VERDE}✓{Cores.RESET}"

            cor_risco = cor_nivel_risco(res.classificacao_risco_isolado)

            print(f"{pos:<3} {res.nome_seguradora:<28} "
                  f"{cor_score(100-res.score_vulnerabilidade)}{res.score_vulnerabilidade:>5.1f}{Cores.RESET}   "
                  f"{cor_score(res.score_forca_isolada)}{res.score_forca_isolada:>5.1f}{Cores.RESET}   "
                  f"{cor_rating(res.rating_isolado)}{res.rating_isolado:<8}{Cores.RESET} "
                  f"{cor_risco}{res.classificacao_risco_isolado.value:<12}{Cores.RESET} "
                  f"{len(res.fissuras):<8} {icone}")

        print("─" * 85)

        pausar()

    def exibir_analise_detalhada(self):
        """Exibe análise detalhada de uma seguradora"""
        if not self.resultados:
            self.exibir_cabecalho("Análise Detalhada")
            print(f"\n{Cores.VERMELHO}✗ Execute a análise primeiro (opção 1).{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Análise Detalhada por Seguradora")

        # Seleção de seguradora
        print(f"\n{Cores.BOLD}Selecione a seguradora:{Cores.RESET}\n")
        for i, res in enumerate(self.resultados, 1):
            cor = cor_nivel_risco(res.classificacao_risco_isolado)
            print(f"  {Cores.AMARELO}[{i}]{Cores.RESET} {res.nome_seguradora} "
                  f"({cor}{res.classificacao_risco_isolado.value}{Cores.RESET})")

        print(f"  {Cores.CINZA}[0] Voltar{Cores.RESET}")

        try:
            opcao = int(input(f"\n  {Cores.BOLD}Digite o número: {Cores.RESET}").strip())
            if opcao == 0:
                return
            if 1 <= opcao <= len(self.resultados):
                self._exibir_parecer_completo(self.resultados[opcao - 1])
        except ValueError:
            print(f"\n{Cores.VERMELHO}✗ Opção inválida!{Cores.RESET}")
            pausar()

    def _exibir_parecer_completo(self, resultado: IndicadoresForcaIsolada):
        """Exibe parecer completo de uma seguradora"""
        limpar_tela()
        self.exibir_cabecalho(f"Parecer: {resultado.nome_seguradora}")

        cor_risco = cor_nivel_risco(resultado.classificacao_risco_isolado)

        # Cabeçalho do parecer
        print(f"\n{Cores.BOLD}{Cores.MAGENTA}╔══════════════════════════════════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"{Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}        PARECER DE FORÇA FINANCEIRA ISOLADA DE RESSEGURO                     {Cores.BOLD}{Cores.MAGENTA}║{Cores.RESET}")
        print(f"{Cores.BOLD}{Cores.MAGENTA}╚══════════════════════════════════════════════════════════════════════════════╝{Cores.RESET}")

        # Classificação geral
        print(f"\n{Cores.BOLD}▸ CLASSIFICAÇÃO GERAL{Cores.RESET}")
        print("─" * 60)
        print(f"  Seguradora:               {Cores.BOLD}{resultado.nome_seguradora}{Cores.RESET}")
        print(f"  Nível de Risco Isolado:   {cor_risco}{Cores.BOLD}{resultado.classificacao_risco_isolado.value}{Cores.RESET}")
        print(f"  Score de Força Isolada:   {cor_score(resultado.score_forca_isolada)}{resultado.score_forca_isolada:.1f}/100{Cores.RESET}")
        print(f"  Score de Vulnerabilidade: {cor_score(100-resultado.score_vulnerabilidade)}{resultado.score_vulnerabilidade:.1f}/100{Cores.RESET}")

        # Comparação de Rating
        print(f"\n{Cores.BOLD}▸ COMPARAÇÃO DE RATING{Cores.RESET}")
        print("─" * 60)
        gap_cor = Cores.VERMELHO if resultado.gap_rating_notches >= 2 else (
            Cores.AMARELO if resultado.gap_rating_notches >= 1 else Cores.VERDE
        )
        print(f"  Rating Declarado (Grupo): {cor_rating(resultado.rating_declarado)}{resultado.rating_declarado}{Cores.RESET}")
        print(f"  Rating Isolado Calculado: {cor_rating(resultado.rating_isolado)}{resultado.rating_isolado}{Cores.RESET}")
        print(f"  Gap de Rating:            {gap_cor}{resultado.gap_rating_notches} notches{Cores.RESET}")
        print(f"  Inflação de Rating:       {gap_cor}{resultado.inflacao_rating:.1f}%{Cores.RESET}")

        # Indicadores de Capacidade
        print(f"\n{Cores.BOLD}▸ CAPACIDADE PRÓPRIA{Cores.RESET}")
        print("─" * 60)
        cap_cor = Cores.VERDE if resultado.indice_capacidade_50mm >= 1 else Cores.VERMELHO
        cap_status = "ATENDE" if resultado.indice_capacidade_50mm >= 1 else "NÃO ATENDE"
        print(f"  Capital Próprio Efetivo:  {formatar_moeda(resultado.capital_proprio_efetivo)}")
        print(f"  Capacidade por Risco:     {formatar_moeda(resultado.capacidade_retencao_risco)}")
        print(f"  Capacidade por Evento:    {formatar_moeda(resultado.capacidade_retencao_evento)}")
        print(f"  Índice vs 50MM:           {cap_cor}{resultado.indice_capacidade_50mm:.2f}x ({cap_status}){Cores.RESET}")

        # Indicadores de Dependência
        print(f"\n{Cores.BOLD}▸ DEPENDÊNCIA DE RESSEGURO{Cores.RESET}")
        print("─" * 60)
        cessao_cor = Cores.VERMELHO if resultado.taxa_cessao_resseguro > 0.5 else (
            Cores.AMARELO if resultado.taxa_cessao_resseguro > 0.3 else Cores.VERDE
        )
        print(f"  Taxa de Cessão:           {cessao_cor}{resultado.taxa_cessao_resseguro:.1%}{Cores.RESET}")
        print(f"  Índice de Retenção:       {1-resultado.taxa_cessao_resseguro:.1%}")
        print(f"  Dep. Recuperação Sinistros: {resultado.dependencia_recuperacao:.1%}")

        # Indicadores de Solvência Isolada
        print(f"\n{Cores.BOLD}▸ SOLVÊNCIA ISOLADA{Cores.RESET}")
        print("─" * 60)
        solv_cor = Cores.VERDE if resultado.indice_solvencia_isolado >= 1 else Cores.VERMELHO
        print(f"  Índice Solvência Isolado: {solv_cor}{resultado.indice_solvencia_isolado:.2f}{Cores.RESET}")
        print(f"  Cobertura Provisões:      {resultado.cobertura_provisoes_isolada:.2f}x")
        print(f"  Margem Solvência:         {formatar_moeda(resultado.margem_solvencia_isolada)}")
        print(f"  Suficiência Capital:      {resultado.suficiencia_capital_isolada:.1%}")

        # Fissuras Identificadas
        if resultado.fissuras:
            print(f"\n{Cores.BOLD}{Cores.VERMELHO}▸ FISSURAS E FRAGILIDADES IDENTIFICADAS ({len(resultado.fissuras)}){Cores.RESET}")
            print("─" * 60)

            for fissura in resultado.fissuras:
                cor_fissura = cor_nivel_risco(fissura.nivel_risco)
                print(f"\n  {cor_fissura}● {fissura.tipo.value}{Cores.RESET}")
                print(f"    Nível: {cor_fissura}{fissura.nivel_risco.value}{Cores.RESET}")
                print(f"    {fissura.descricao}")
                print(f"    {Cores.CINZA}Recomendação: {fissura.recomendacao}{Cores.RESET}")

        # Alertas Críticos
        if resultado.alertas_criticos:
            print(f"\n{Cores.BOLD}{Cores.VERMELHO}{Cores.BLINK}▸ ALERTAS CRÍTICOS{Cores.RESET}")
            print("─" * 60)
            for alerta in resultado.alertas_criticos:
                print(f"  {Cores.VERMELHO}⚠ {alerta}{Cores.RESET}")

        # Recomendações
        if resultado.recomendacoes:
            print(f"\n{Cores.BOLD}{Cores.CIANO}▸ RECOMENDAÇÕES{Cores.RESET}")
            print("─" * 60)
            for rec in resultado.recomendacoes:
                print(f"  {Cores.CIANO}→{Cores.RESET} {rec}")

        pausar()

    def exibir_comparacao_ratings(self):
        """Exibe comparação de ratings (grupo vs isolado)"""
        if not self.resultados:
            self.exibir_cabecalho("Comparação de Ratings")
            print(f"\n{Cores.VERMELHO}✗ Execute a análise primeiro (opção 1).{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Comparação: Rating Grupo vs Rating Isolado")

        print(f"\n{Cores.BOLD}{Cores.AMARELO}⚖ ANÁLISE DE INFLAÇÃO DE RATING{Cores.RESET}")
        print(f"{Cores.CINZA}Rating declarado (grupo) versus rating calculado isoladamente{Cores.RESET}\n")

        print(f"{Cores.BOLD}{'SEGURADORA':<30} {'GRUPO':<8} {'ISOLADO':<8} {'GAP':<6} {'INFLAÇÃO':<10} {'STATUS':<15}{Cores.RESET}")
        print("─" * 90)

        # Ordena por gap de rating (maior primeiro)
        ranking = sorted(self.resultados, key=lambda x: x.gap_rating_notches, reverse=True)

        for res in ranking:
            gap = res.gap_rating_notches

            if gap >= 3:
                status = f"{Cores.VERMELHO}MUITO INFLADO{Cores.RESET}"
                simbolo = "⚠⚠⚠"
            elif gap >= 2:
                status = f"{Cores.VERMELHO_CLARO}INFLADO{Cores.RESET}"
                simbolo = "⚠⚠"
            elif gap >= 1:
                status = f"{Cores.AMARELO}LEVEMENTE{Cores.RESET}"
                simbolo = "⚠"
            else:
                status = f"{Cores.VERDE}COMPATÍVEL{Cores.RESET}"
                simbolo = "✓"

            print(f"{res.nome_seguradora:<30} "
                  f"{cor_rating(res.rating_declarado)}{res.rating_declarado:<8}{Cores.RESET} "
                  f"{cor_rating(res.rating_isolado)}{res.rating_isolado:<8}{Cores.RESET} "
                  f"{gap:<6} "
                  f"{res.inflacao_rating:>5.1f}%     "
                  f"{status} {simbolo}")

        print("─" * 90)

        # Estatísticas
        total_inflados = sum(1 for r in self.resultados if r.gap_rating_notches >= 2)
        media_gap = sum(r.gap_rating_notches for r in self.resultados) / len(self.resultados)

        print(f"\n{Cores.BOLD}Resumo:{Cores.RESET}")
        print(f"  Seguradoras com Rating Inflado (gap >= 2): {Cores.VERMELHO}{total_inflados}{Cores.RESET}")
        print(f"  Gap Médio de Rating: {media_gap:.1f} notches")

        pausar()

    def exibir_mapa_fissuras(self):
        """Exibe mapa consolidado de fissuras"""
        if not self.resultados:
            self.exibir_cabecalho("Mapa de Fissuras")
            print(f"\n{Cores.VERMELHO}✗ Execute a análise primeiro (opção 1).{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Mapa de Fissuras e Fragilidades")

        print(f"\n{Cores.BOLD}{Cores.VERMELHO}🔍 MAPEAMENTO DE FISSURAS DO MERCADO{Cores.RESET}\n")

        # Consolida todas as fissuras
        todas_fissuras = {}
        for res in self.resultados:
            for fissura in res.fissuras:
                tipo = fissura.tipo.value
                if tipo not in todas_fissuras:
                    todas_fissuras[tipo] = {'count': 0, 'seguradoras': [], 'nivel_max': NivelRisco.MINIMO}
                todas_fissuras[tipo]['count'] += 1
                todas_fissuras[tipo]['seguradoras'].append(res.nome_seguradora)
                if list(NivelRisco).index(fissura.nivel_risco) < list(NivelRisco).index(todas_fissuras[tipo]['nivel_max']):
                    todas_fissuras[tipo]['nivel_max'] = fissura.nivel_risco

        # Ordena por frequência
        fissuras_ordenadas = sorted(todas_fissuras.items(), key=lambda x: x[1]['count'], reverse=True)

        print(f"{Cores.BOLD}{'TIPO DE FISSURA':<45} {'QTD':<6} {'NÍVEL MÁX':<15} {'SEGURADORAS':<30}{Cores.RESET}")
        print("─" * 100)

        for tipo, dados in fissuras_ordenadas:
            cor = cor_nivel_risco(dados['nivel_max'])
            barra = "█" * dados['count']
            seguradoras_str = ", ".join(dados['seguradoras'][:2])
            if len(dados['seguradoras']) > 2:
                seguradoras_str += f" (+{len(dados['seguradoras'])-2})"

            print(f"{tipo:<45} {dados['count']:<6} {cor}{dados['nivel_max'].value:<15}{Cores.RESET} {seguradoras_str}")

        print("─" * 100)

        # Matriz de fissuras por seguradora
        print(f"\n{Cores.BOLD}▸ MATRIZ DE FISSURAS POR SEGURADORA{Cores.RESET}\n")

        for res in self.resultados:
            criticas = sum(1 for f in res.fissuras if f.nivel_risco == NivelRisco.CRITICO)
            altas = sum(1 for f in res.fissuras if f.nivel_risco == NivelRisco.ALTO)

            if criticas > 0:
                icone = f"{Cores.VERMELHO}●{Cores.RESET}"
            elif altas > 0:
                icone = f"{Cores.AMARELO}●{Cores.RESET}"
            elif res.fissuras:
                icone = f"{Cores.VERDE_CLARO}●{Cores.RESET}"
            else:
                icone = f"{Cores.VERDE}✓{Cores.RESET}"

            print(f"  {icone} {res.nome_seguradora:<30} "
                  f"[{Cores.VERMELHO}{criticas} críticas{Cores.RESET}, "
                  f"{Cores.AMARELO}{altas} altas{Cores.RESET}, "
                  f"total: {len(res.fissuras)}]")

        pausar()

    def exibir_analise_capacidade_50mm(self):
        """Exibe análise de capacidade em relação ao limite de 50MM"""
        if not self.resultados:
            self.exibir_cabecalho("Análise de Capacidade (50MM)")
            print(f"\n{Cores.VERMELHO}✗ Execute a análise primeiro (opção 1).{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Análise de Capacidade - Referência R$ 50 Milhões")

        print(f"\n{Cores.BOLD}{Cores.CIANO}📊 CAPACIDADE PRÓPRIA vs LIMITE DE R$ 50 MILHÕES{Cores.RESET}")
        print(f"{Cores.CINZA}Avalia se a seguradora pode assumir riscos de R$ 50MM por conta própria{Cores.RESET}\n")

        print(f"{Cores.BOLD}{'SEGURADORA':<28} {'CAP. RISCO':<14} {'CAP. EVENTO':<14} {'ÍNDICE':<10} {'STATUS':<20}{Cores.RESET}")
        print("─" * 95)

        # Ordena por capacidade (maior primeiro)
        ranking = sorted(self.resultados, key=lambda x: x.capacidade_retencao_risco, reverse=True)

        atendem = 0
        nao_atendem = 0

        for res in ranking:
            cap_risco = res.capacidade_retencao_risco
            cap_evento = res.capacidade_retencao_evento
            indice = res.indice_capacidade_50mm

            if indice >= 1.5:
                status = f"{Cores.VERDE_CLARO}EXCELENTE{Cores.RESET}"
                atendem += 1
            elif indice >= 1.0:
                status = f"{Cores.VERDE}ADEQUADA{Cores.RESET}"
                atendem += 1
            elif indice >= 0.5:
                status = f"{Cores.AMARELO}LIMITADA{Cores.RESET}"
                nao_atendem += 1
            else:
                status = f"{Cores.VERMELHO}INSUFICIENTE{Cores.RESET}"
                nao_atendem += 1

            # Barra visual
            barra_len = min(int(indice * 10), 20)
            cor_barra = Cores.VERDE if indice >= 1 else Cores.VERMELHO
            barra = f"{cor_barra}{'█' * barra_len}{Cores.CINZA}{'░' * (10 - barra_len)}{Cores.RESET}"

            print(f"{res.nome_seguradora:<28} "
                  f"{formatar_moeda(cap_risco):<14} "
                  f"{formatar_moeda(cap_evento):<14} "
                  f"{indice:>5.2f}x    "
                  f"{status}")
            print(f"{'':>28} {barra}")

        print("─" * 95)

        print(f"\n{Cores.BOLD}Resumo:{Cores.RESET}")
        print(f"  {Cores.VERDE}Atendem (capacidade >= 50MM):{Cores.RESET}     {atendem} seguradoras")
        print(f"  {Cores.VERMELHO}Não Atendem (capacidade < 50MM):{Cores.RESET} {nao_atendem} seguradoras")

        print(f"\n{Cores.BOLD}Recomendação:{Cores.RESET}")
        if nao_atendem > 0:
            print(f"  {Cores.AMARELO}⚠ {nao_atendem} seguradora(s) não devem assumir riscos individuais > R$ 50MM{Cores.RESET}")
            print(f"    sem resseguro proporcional ou suporte do grupo.")

        pausar()

    def exibir_alertas_criticos(self):
        """Exibe relatório consolidado de alertas críticos"""
        if not self.resultados:
            self.exibir_cabecalho("Alertas Críticos")
            print(f"\n{Cores.VERMELHO}✗ Execute a análise primeiro (opção 1).{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Relatório de Alertas Críticos")

        print(f"\n{Cores.BOLD}{Cores.VERMELHO}🚨 ALERTAS CRÍTICOS - AÇÃO IMEDIATA RECOMENDADA{Cores.RESET}\n")

        total_alertas = 0

        for res in self.resultados:
            if res.alertas_criticos:
                cor = cor_nivel_risco(res.classificacao_risco_isolado)
                print(f"\n{Cores.BOLD}{cor}▸ {res.nome_seguradora}{Cores.RESET}")
                print("─" * 60)

                for alerta in res.alertas_criticos:
                    print(f"  {Cores.VERMELHO}⚠{Cores.RESET} {alerta}")
                    total_alertas += 1

        if total_alertas == 0:
            print(f"  {Cores.VERDE}✓ Nenhum alerta crítico identificado.{Cores.RESET}")
        else:
            print(f"\n{'─' * 60}")
            print(f"{Cores.BOLD}Total de Alertas Críticos: {Cores.VERMELHO}{total_alertas}{Cores.RESET}")

        pausar()

    def exibir_seguradoras_fronting(self):
        """Exibe análise de seguradoras que operam como fronting"""
        if not self.resultados:
            self.exibir_cabecalho("Análise de Fronting")
            print(f"\n{Cores.VERMELHO}✗ Execute a análise primeiro (opção 1).{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Identificação de Seguradoras Fronting")

        print(f"\n{Cores.BOLD}{Cores.AMARELO}🔎 ANÁLISE DE OPERAÇÕES FRONTING{Cores.RESET}")
        print(f"{Cores.CINZA}Seguradoras com alta cessão ao resseguro (>50%) e baixa retenção própria{Cores.RESET}\n")

        # Identifica frontings (cessão > 50%)
        frontings = [r for r in self.resultados if r.taxa_cessao_resseguro > 0.50]

        if not frontings:
            print(f"  {Cores.VERDE}✓ Nenhuma seguradora identificada como fronting (cessão > 50%).{Cores.RESET}")
            pausar()
            return

        print(f"{Cores.BOLD}{'SEGURADORA':<30} {'CESSÃO':<10} {'RETENÇÃO':<12} {'CAP. RISCO':<14} {'ALERTA':<20}{Cores.RESET}")
        print("─" * 95)

        # Ordena por taxa de cessão (maior primeiro)
        frontings = sorted(frontings, key=lambda x: x.taxa_cessao_resseguro, reverse=True)

        for res in frontings:
            if res.taxa_cessao_resseguro >= 0.70:
                alerta = f"{Cores.VERMELHO}FRONTING PURO{Cores.RESET}"
            else:
                alerta = f"{Cores.AMARELO}FRONTING PARCIAL{Cores.RESET}"

            print(f"{res.nome_seguradora:<30} "
                  f"{Cores.VERMELHO_CLARO}{res.taxa_cessao_resseguro:>7.1%}{Cores.RESET}   "
                  f"{res.indice_retencao:>7.1%}     "
                  f"{formatar_moeda(res.capacidade_retencao_risco):<14} "
                  f"{alerta}")

        print("─" * 95)

        print(f"\n{Cores.BOLD}Características de Fronting:{Cores.RESET}")
        print(f"  • Alta cessão ao resseguro (geralmente do próprio grupo)")
        print(f"  • Baixa capacidade de retenção própria")
        print(f"  • Rating sustentado pelo grupo, não por mérito próprio")
        print(f"  • Risco de descontinuidade se grupo retirar suporte")

        print(f"\n{Cores.BOLD}Recomendação:{Cores.RESET}")
        print(f"  {Cores.AMARELO}⚠ Verificar rating INDIVIDUAL destas seguradoras antes de aceitar{Cores.RESET}")
        print(f"    garantias para riscos relevantes.")

        pausar()

    def executar(
        self,
        seguradoras: List[Seguradora],
        infos_grupo: List[InformacoesGrupo] = None,
        infos_resseguro: List[InformacoesResseguro] = None
    ):
        """Loop principal do módulo de força isolada"""
        self.carregar_dados(seguradoras, infos_grupo, infos_resseguro)

        while True:
            opcao = self.exibir_menu_forca_isolada()

            if opcao == '1':
                self.executar_analise()
            elif opcao == '2':
                self.exibir_ranking_vulnerabilidade()
            elif opcao == '3':
                self.exibir_analise_detalhada()
            elif opcao == '4':
                self.exibir_comparacao_ratings()
            elif opcao == '5':
                self.exibir_mapa_fissuras()
            elif opcao == '6':
                self.exibir_analise_capacidade_50mm()
            elif opcao == '7':
                self.exibir_alertas_criticos()
            elif opcao == '8':
                self.exibir_seguradoras_fronting()
            elif opcao == '0':
                break
            else:
                print(f"\n{Cores.VERMELHO}✗ Opção inválida!{Cores.RESET}")
                pausar()
