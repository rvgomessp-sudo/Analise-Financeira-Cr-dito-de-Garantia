#!/usr/bin/env python3
"""
Aplicação Terminal Interativa - Análise Financeira de Seguradoras
Sistema de Análise de Força Financeira e Crédito de Garantia
"""

import sys
import os
from pathlib import Path
from typing import List, Optional

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.dados_exemplo import carregar_dados_exemplo
from src.analysis.indicadores import AnalisadorIndicadores
from src.analysis.comparador import ComparadorSeguradora
from src.models.seguradora import Seguradora


# ============================================================================
# CORES E FORMATAÇÃO PARA TERMINAL
# ============================================================================
class Cores:
    """Códigos ANSI para cores no terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

    # Cores de texto
    PRETO = '\033[30m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    MAGENTA = '\033[35m'
    CIANO = '\033[36m'
    BRANCO = '\033[37m'

    # Cores de fundo
    BG_PRETO = '\033[40m'
    BG_VERMELHO = '\033[41m'
    BG_VERDE = '\033[42m'
    BG_AMARELO = '\033[43m'
    BG_AZUL = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CIANO = '\033[46m'
    BG_BRANCO = '\033[47m'

    # Cores claras
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
    if score >= 80:
        return Cores.VERDE_CLARO
    elif score >= 65:
        return Cores.VERDE
    elif score >= 50:
        return Cores.AMARELO_CLARO
    elif score >= 35:
        return Cores.AMARELO
    else:
        return Cores.VERMELHO


# ============================================================================
# CLASSE PRINCIPAL DA APLICAÇÃO
# ============================================================================
class TerminalApp:
    """Aplicação interativa de terminal para análise de seguradoras"""

    def __init__(self):
        self.seguradoras: List[Seguradora] = []
        self.analisador = AnalisadorIndicadores()
        self.comparador = ComparadorSeguradora()
        self.dados_carregados = False

    def exibir_cabecalho(self, titulo: str = None):
        """Exibe o cabeçalho da aplicação"""
        limpar_tela()
        print(f"{Cores.BG_AZUL}{Cores.BRANCO}{Cores.BOLD}")
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "SISTEMA DE ANÁLISE FINANCEIRA - SEGURADORAS".center(78) + "║")
        print("║" + "Análise de Força Financeira e Crédito de Garantia".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝")
        print(Cores.RESET)

        if titulo:
            print(f"\n{Cores.CIANO_CLARO}{Cores.BOLD}» {titulo}{Cores.RESET}")
            print("─" * 80)

    def exibir_menu_principal(self):
        """Exibe o menu principal"""
        self.exibir_cabecalho()

        status = f"{Cores.VERDE}● Dados carregados ({len(self.seguradoras)} seguradoras){Cores.RESET}" if self.dados_carregados else f"{Cores.AMARELO}○ Dados não carregados{Cores.RESET}"
        print(f"\n  Status: {status}\n")

        print(f"  {Cores.BOLD}{Cores.CIANO}╔══════════════════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║                      MENU PRINCIPAL                          ║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}╠══════════════════════════════════════════════════════════════╣{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}                                                              {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[1]{Cores.RESET} Carregar Dados de Exemplo                            {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[2]{Cores.RESET} Listar Seguradoras                                   {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[3]{Cores.RESET} Ver Detalhes de uma Seguradora                       {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[4]{Cores.RESET} Ranking de Força Financeira                          {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[5]{Cores.RESET} Comparar Duas Seguradoras                            {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[6]{Cores.RESET} Estatísticas do Setor                                {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[7]{Cores.RESET} Análise de Indicadores por Categoria                 {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.AMARELO}[8]{Cores.RESET} Gerar Relatórios (HTML/Excel)                        {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}                                                              {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}   {Cores.VERMELHO}[0]{Cores.RESET} Sair                                                 {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}                                                              {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"  {Cores.BOLD}{Cores.CIANO}╚══════════════════════════════════════════════════════════════╝{Cores.RESET}")

        return input(f"\n  {Cores.BOLD}Digite sua opção: {Cores.RESET}").strip()

    def carregar_dados(self):
        """Carrega os dados de exemplo das seguradoras"""
        self.exibir_cabecalho("Carregando Dados")

        print(f"\n{Cores.AMARELO}⏳ Carregando dados de seguradoras...{Cores.RESET}")
        self.seguradoras = carregar_dados_exemplo()

        print(f"{Cores.AMARELO}⏳ Calculando indicadores financeiros...{Cores.RESET}")
        for seg in self.seguradoras:
            seg.indicadores = self.analisador.calcular_indicadores(seg)

        # Configura o comparador
        self.comparador = ComparadorSeguradora()
        self.comparador.adicionar_multiplas(self.seguradoras)

        self.dados_carregados = True

        print(f"\n{Cores.VERDE}✓ {len(self.seguradoras)} seguradoras carregadas com sucesso!{Cores.RESET}")
        print(f"\n{Cores.BOLD}Seguradoras disponíveis:{Cores.RESET}")

        for i, seg in enumerate(self.seguradoras, 1):
            cor = cor_rating(seg.indicadores.classificacao_risco)
            print(f"  {i}. {seg.nome}")
            print(f"     Score: {cor_score(seg.indicadores.score_forca_financeira)}{seg.indicadores.score_forca_financeira:.1f}{Cores.RESET} | "
                  f"Rating: {cor}{seg.indicadores.classificacao_risco}{Cores.RESET} | "
                  f"Ativo Total: {formatar_moeda(seg.balanco.ativo_total)}")

        pausar()

    def listar_seguradoras(self):
        """Lista todas as seguradoras carregadas"""
        if not self.dados_carregados:
            self.exibir_cabecalho("Listar Seguradoras")
            print(f"\n{Cores.VERMELHO}✗ Dados não carregados. Use a opção 1 primeiro.{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Lista de Seguradoras")

        # Cabeçalho da tabela
        print(f"\n{Cores.BOLD}{'#':<3} {'SEGURADORA':<30} {'SUSEP':<8} {'SCORE':<8} {'RATING':<8} {'ATIVO TOTAL':<15}{Cores.RESET}")
        print("─" * 80)

        for i, seg in enumerate(self.seguradoras, 1):
            cor = cor_rating(seg.indicadores.classificacao_risco)
            print(f"{i:<3} {seg.nome:<30} {seg.codigo_susep:<8} "
                  f"{cor_score(seg.indicadores.score_forca_financeira)}{seg.indicadores.score_forca_financeira:>6.1f}{Cores.RESET}  "
                  f"{cor}{seg.indicadores.classificacao_risco:<8}{Cores.RESET} "
                  f"{formatar_moeda(seg.balanco.ativo_total)}")

        print("─" * 80)
        print(f"\n{Cores.CINZA}Total: {len(self.seguradoras)} seguradoras{Cores.RESET}")

        pausar()

    def selecionar_seguradora(self, mensagem: str = "Selecione a seguradora") -> Optional[Seguradora]:
        """Permite ao usuário selecionar uma seguradora"""
        print(f"\n{Cores.BOLD}{mensagem}:{Cores.RESET}\n")

        for i, seg in enumerate(self.seguradoras, 1):
            print(f"  {Cores.AMARELO}[{i}]{Cores.RESET} {seg.nome}")

        print(f"  {Cores.CINZA}[0] Voltar{Cores.RESET}")

        try:
            opcao = int(input(f"\n  {Cores.BOLD}Digite o número: {Cores.RESET}").strip())
            if opcao == 0:
                return None
            if 1 <= opcao <= len(self.seguradoras):
                return self.seguradoras[opcao - 1]
        except ValueError:
            pass

        print(f"\n{Cores.VERMELHO}✗ Opção inválida!{Cores.RESET}")
        return None

    def ver_detalhes_seguradora(self):
        """Exibe detalhes completos de uma seguradora"""
        if not self.dados_carregados:
            self.exibir_cabecalho("Detalhes da Seguradora")
            print(f"\n{Cores.VERMELHO}✗ Dados não carregados. Use a opção 1 primeiro.{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Detalhes da Seguradora")

        seg = self.selecionar_seguradora()
        if not seg:
            return

        limpar_tela()
        self.exibir_cabecalho(f"Análise: {seg.nome}")

        ind = seg.indicadores
        cor = cor_rating(ind.classificacao_risco)

        # Informações gerais
        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ INFORMAÇÕES GERAIS ══════════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"  Nome: {Cores.BOLD}{seg.nome}{Cores.RESET}")
        print(f"  CNPJ: {seg.cnpj}")
        print(f"  Código SUSEP: {seg.codigo_susep}")
        print(f"  Grupo Econômico: {seg.grupo_economico}")
        print(f"  Exercício: {seg.ano_exercicio}")

        # Score e Rating
        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ AVALIAÇÃO FINANCEIRA ════════════════════════════════════════════════════╗{Cores.RESET}")

        score_bar = self._criar_barra_progresso(ind.score_forca_financeira, 100)
        print(f"  Score de Força Financeira: {cor_score(ind.score_forca_financeira)}{ind.score_forca_financeira:.1f}/100{Cores.RESET}")
        print(f"  {score_bar}")
        print(f"  Classificação de Risco: {cor}{Cores.BOLD}{ind.classificacao_risco}{Cores.RESET}")

        # Indicadores por categoria
        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ INDICADORES DE SOLVÊNCIA ════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"  Índice de Solvência:      {self._formatar_indicador(ind.indice_solvencia, tipo='ratio')}")
        print(f"  Cobertura de Provisões:   {self._formatar_indicador(ind.cobertura_provisoes, tipo='ratio')}")
        print(f"  Margem de Solvência:      {formatar_moeda(ind.margem_solvencia)}")

        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ INDICADORES DE LIQUIDEZ ═════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"  Liquidez Corrente:        {self._formatar_indicador(ind.liquidez_corrente, tipo='ratio')}")
        print(f"  Liquidez Seca:            {self._formatar_indicador(ind.liquidez_seca, tipo='ratio')}")
        print(f"  Liquidez Imediata:        {self._formatar_indicador(ind.liquidez_imediata, tipo='ratio')}")

        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ INDICADORES DE RENTABILIDADE ═══════════════════════════════════════════╗{Cores.RESET}")
        print(f"  ROE (Retorno s/ PL):      {self._formatar_indicador(ind.roe, tipo='percent')}")
        print(f"  ROA (Retorno s/ Ativos):  {self._formatar_indicador(ind.roa, tipo='percent')}")
        print(f"  Margem Líquida:           {self._formatar_indicador(ind.margem_liquida, tipo='percent')}")
        print(f"  Margem Operacional:       {self._formatar_indicador(ind.margem_operacional, tipo='percent')}")

        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ INDICADORES DE SINISTRALIDADE ══════════════════════════════════════════╗{Cores.RESET}")
        print(f"  Índice de Sinistralidade: {self._formatar_indicador(ind.indice_sinistralidade, tipo='percent', inverso=True)}")
        print(f"  Índice de Despesas:       {self._formatar_indicador(ind.indice_despesas, tipo='percent', inverso=True)}")
        print(f"  Índice Combinado:         {self._formatar_indicador(ind.indice_combinado, tipo='percent', inverso=True)}")
        print(f"  Índice Combinado Ampliado:{self._formatar_indicador(ind.indice_combinado_ampliado, tipo='percent', inverso=True)}")

        # Pontos fortes e fracos
        pontos_fortes, pontos_fracos = self.analisador.analisar_pontos_fortes_fracos(ind)

        print(f"\n{Cores.BOLD}{Cores.VERDE}╔══ PONTOS FORTES ══════════════════════════════════════════════════════════╗{Cores.RESET}")
        for ponto in pontos_fortes[:5]:
            print(f"  {Cores.VERDE}✓{Cores.RESET} {ponto}")

        print(f"\n{Cores.BOLD}{Cores.VERMELHO}╔══ PONTOS DE ATENÇÃO ══════════════════════════════════════════════════════╗{Cores.RESET}")
        for ponto in pontos_fracos[:5]:
            print(f"  {Cores.VERMELHO}✗{Cores.RESET} {ponto}")

        pausar()

    def _criar_barra_progresso(self, valor: float, maximo: float, largura: int = 40) -> str:
        """Cria uma barra de progresso visual"""
        percentual = min(valor / maximo, 1.0)
        preenchido = int(largura * percentual)
        vazio = largura - preenchido

        if percentual >= 0.8:
            cor = Cores.VERDE
        elif percentual >= 0.5:
            cor = Cores.AMARELO
        else:
            cor = Cores.VERMELHO

        return f"  [{cor}{'█' * preenchido}{Cores.CINZA}{'░' * vazio}{Cores.RESET}]"

    def _formatar_indicador(self, valor: float, tipo: str = 'ratio', inverso: bool = False) -> str:
        """Formata um indicador com cor apropriada"""
        if tipo == 'percent':
            texto = f"{valor:.1%}"
            # Para percentuais, bom depende se é inverso ou não
            if inverso:  # Menor é melhor (ex: sinistralidade)
                if valor <= 0.5:
                    cor = Cores.VERDE
                elif valor <= 0.8:
                    cor = Cores.AMARELO
                else:
                    cor = Cores.VERMELHO
            else:  # Maior é melhor (ex: ROE)
                if valor >= 0.15:
                    cor = Cores.VERDE
                elif valor >= 0.05:
                    cor = Cores.AMARELO
                else:
                    cor = Cores.VERMELHO
        else:  # ratio
            texto = f"{valor:.2f}"
            if valor >= 1.5:
                cor = Cores.VERDE
            elif valor >= 1.0:
                cor = Cores.AMARELO
            else:
                cor = Cores.VERMELHO

        return f"{cor}{texto}{Cores.RESET}"

    def exibir_ranking(self):
        """Exibe o ranking de força financeira"""
        if not self.dados_carregados:
            self.exibir_cabecalho("Ranking de Força Financeira")
            print(f"\n{Cores.VERMELHO}✗ Dados não carregados. Use a opção 1 primeiro.{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Ranking de Força Financeira")

        resultado = self.comparador.comparar()

        print(f"\n{Cores.BOLD}{Cores.AMARELO}🏆 RANKING GERAL DE FORÇA FINANCEIRA{Cores.RESET}\n")

        # Ordena por score
        ranking = sorted(self.seguradoras, key=lambda x: x.indicadores.score_forca_financeira, reverse=True)

        for pos, seg in enumerate(ranking, 1):
            ind = seg.indicadores
            cor = cor_rating(ind.classificacao_risco)

            # Medalhas para os 3 primeiros
            if pos == 1:
                medalha = f"{Cores.AMARELO}🥇{Cores.RESET}"
            elif pos == 2:
                medalha = f"{Cores.BRANCO}🥈{Cores.RESET}"
            elif pos == 3:
                medalha = f"{Cores.VERMELHO_CLARO}🥉{Cores.RESET}"
            else:
                medalha = f"  {pos}."

            barra = self._criar_barra_mini(ind.score_forca_financeira, 100)
            print(f"  {medalha} {seg.nome:<30} {barra} {cor_score(ind.score_forca_financeira)}{ind.score_forca_financeira:>5.1f}{Cores.RESET} "
                  f"[{cor}{ind.classificacao_risco}{Cores.RESET}]")

        # Menu de sub-rankings
        print(f"\n{Cores.BOLD}Ver ranking específico:{Cores.RESET}")
        print(f"  {Cores.AMARELO}[1]{Cores.RESET} Ranking de Solvência")
        print(f"  {Cores.AMARELO}[2]{Cores.RESET} Ranking de Liquidez")
        print(f"  {Cores.AMARELO}[3]{Cores.RESET} Ranking de Rentabilidade")
        print(f"  {Cores.AMARELO}[4]{Cores.RESET} Ranking de Sinistralidade")
        print(f"  {Cores.CINZA}[0] Voltar{Cores.RESET}")

        opcao = input(f"\n  {Cores.BOLD}Digite sua opção: {Cores.RESET}").strip()

        if opcao == '1':
            self._exibir_ranking_especifico('solvencia', 'Solvência', 'indice_solvencia')
        elif opcao == '2':
            self._exibir_ranking_especifico('liquidez', 'Liquidez', 'liquidez_corrente')
        elif opcao == '3':
            self._exibir_ranking_especifico('rentabilidade', 'Rentabilidade', 'roe')
        elif opcao == '4':
            self._exibir_ranking_especifico('sinistralidade', 'Sinistralidade', 'indice_sinistralidade', inverso=True)

    def _criar_barra_mini(self, valor: float, maximo: float) -> str:
        """Cria uma barra de progresso mini"""
        largura = 20
        percentual = min(valor / maximo, 1.0)
        preenchido = int(largura * percentual)

        if percentual >= 0.7:
            cor = Cores.VERDE
        elif percentual >= 0.4:
            cor = Cores.AMARELO
        else:
            cor = Cores.VERMELHO

        return f"{cor}{'▓' * preenchido}{Cores.CINZA}{'░' * (largura - preenchido)}{Cores.RESET}"

    def _exibir_ranking_especifico(self, categoria: str, titulo: str, atributo: str, inverso: bool = False):
        """Exibe um ranking específico por categoria"""
        limpar_tela()
        self.exibir_cabecalho(f"Ranking de {titulo}")

        # Ordena pelo atributo específico
        ranking = sorted(self.seguradoras,
                        key=lambda x: getattr(x.indicadores, atributo),
                        reverse=not inverso)

        print(f"\n{Cores.BOLD}{'Pos':<5} {'SEGURADORA':<30} {titulo.upper():<15} {'SCORE':<10}{Cores.RESET}")
        print("─" * 65)

        for pos, seg in enumerate(ranking, 1):
            ind = seg.indicadores
            valor = getattr(ind, atributo)

            if atributo in ['roe', 'roa', 'margem_liquida', 'indice_sinistralidade', 'indice_combinado']:
                valor_fmt = f"{valor:.1%}"
            else:
                valor_fmt = f"{valor:.2f}"

            print(f"{pos:<5} {seg.nome:<30} {valor_fmt:<15} {cor_score(ind.score_forca_financeira)}{ind.score_forca_financeira:.1f}{Cores.RESET}")

        pausar()

    def comparar_seguradoras(self):
        """Compara duas seguradoras lado a lado"""
        if not self.dados_carregados:
            self.exibir_cabecalho("Comparar Seguradoras")
            print(f"\n{Cores.VERMELHO}✗ Dados não carregados. Use a opção 1 primeiro.{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Comparar Seguradoras")

        seg1 = self.selecionar_seguradora("Selecione a PRIMEIRA seguradora")
        if not seg1:
            return

        seg2 = self.selecionar_seguradora("Selecione a SEGUNDA seguradora")
        if not seg2:
            return

        limpar_tela()
        self.exibir_cabecalho("Comparação Lado a Lado")

        comparacao = self.comparador.comparar_duas_seguradoras(seg1, seg2)

        # Cabeçalho da comparação
        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══════════════════════════════════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"{Cores.BOLD}{Cores.CIANO}║{Cores.RESET}  {seg1.nome:^35} {Cores.AMARELO}VS{Cores.RESET} {seg2.nome:^35}  {Cores.BOLD}{Cores.CIANO}║{Cores.RESET}")
        print(f"{Cores.BOLD}{Cores.CIANO}╚══════════════════════════════════════════════════════════════════════════════╝{Cores.RESET}")

        ind1 = seg1.indicadores
        ind2 = seg2.indicadores

        # Resultado geral
        vencedor = comparacao['vencedor_geral']
        print(f"\n{Cores.BOLD}🏆 VENCEDOR GERAL: {Cores.VERDE_CLARO}{vencedor}{Cores.RESET}")
        print(f"   Diferença de Score: {comparacao['diferenca_score']:.1f} pontos")

        # Tabela comparativa
        print(f"\n{Cores.BOLD}{'INDICADOR':<30} {'SEGURADORA 1':>18} {'SEGURADORA 2':>18} {'MELHOR':>10}{Cores.RESET}")
        print("─" * 80)

        comparativos = [
            ("Score Financeiro", ind1.score_forca_financeira, ind2.score_forca_financeira, False),
            ("Rating", ind1.classificacao_risco, ind2.classificacao_risco, None),
            ("Índice de Solvência", ind1.indice_solvencia, ind2.indice_solvencia, False),
            ("Liquidez Corrente", ind1.liquidez_corrente, ind2.liquidez_corrente, False),
            ("ROE", ind1.roe, ind2.roe, False),
            ("ROA", ind1.roa, ind2.roa, False),
            ("Margem Líquida", ind1.margem_liquida, ind2.margem_liquida, False),
            ("Sinistralidade", ind1.indice_sinistralidade, ind2.indice_sinistralidade, True),
            ("Índice Combinado", ind1.indice_combinado, ind2.indice_combinado, True),
        ]

        for nome, val1, val2, menor_melhor in comparativos:
            if isinstance(val1, str):
                fmt1 = val1
                fmt2 = val2
                melhor = "─"
            elif nome in ["ROE", "ROA", "Margem Líquida", "Sinistralidade", "Índice Combinado"]:
                fmt1 = f"{val1:.1%}"
                fmt2 = f"{val2:.1%}"
                if menor_melhor:
                    melhor = "◀" if val1 < val2 else ("▶" if val2 < val1 else "═")
                else:
                    melhor = "◀" if val1 > val2 else ("▶" if val2 > val1 else "═")
            else:
                fmt1 = f"{val1:.2f}"
                fmt2 = f"{val2:.2f}"
                if menor_melhor:
                    melhor = "◀" if val1 < val2 else ("▶" if val2 < val1 else "═")
                else:
                    melhor = "◀" if val1 > val2 else ("▶" if val2 > val1 else "═")

            if melhor == "◀":
                cor_melhor = Cores.VERDE
            elif melhor == "▶":
                cor_melhor = Cores.VERDE
            else:
                cor_melhor = Cores.AMARELO

            print(f"{nome:<30} {fmt1:>18} {fmt2:>18} {cor_melhor}{melhor:>10}{Cores.RESET}")

        # Vitórias por categoria
        print(f"\n{Cores.BOLD}Vitórias por Categoria:{Cores.RESET}")
        vitorias = comparacao.get('vitorias_por_categoria', {})
        for cat, vencedor_cat in vitorias.items():
            cor = Cores.VERDE if vencedor_cat == seg1.nome else Cores.AZUL_CLARO
            print(f"  • {cat}: {cor}{vencedor_cat}{Cores.RESET}")

        pausar()

    def estatisticas_setor(self):
        """Exibe estatísticas gerais do setor"""
        if not self.dados_carregados:
            self.exibir_cabecalho("Estatísticas do Setor")
            print(f"\n{Cores.VERMELHO}✗ Dados não carregados. Use a opção 1 primeiro.{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Estatísticas do Setor")

        resultado = self.comparador.comparar()
        stats = resultado.estatisticas_setor

        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ ESTATÍSTICAS GERAIS ═════════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"  Total de Seguradoras Analisadas: {Cores.BOLD}{stats['total_seguradoras']}{Cores.RESET}")

        # Totais financeiros
        total_ativos = sum(seg.balanco.ativo_total for seg in self.seguradoras)
        total_pl = sum(seg.balanco.patrimonio_liquido for seg in self.seguradoras)
        total_premios = sum(seg.dre.premios_emitidos for seg in self.seguradoras)

        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ TOTAIS DO SETOR ═════════════════════════════════════════════════════════╗{Cores.RESET}")
        print(f"  Ativo Total:              {formatar_moeda(total_ativos)}")
        print(f"  Patrimônio Líquido:       {formatar_moeda(total_pl)}")
        print(f"  Prêmios Emitidos:         {formatar_moeda(total_premios)}")

        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ MÉDIAS DO SETOR ═════════════════════════════════════════════════════════╗{Cores.RESET}")
        medias = stats['media']
        print(f"  Score Médio:              {medias['score_forca_financeira']:.1f}")
        print(f"  Índice Solvência Médio:   {medias['indice_solvencia']:.2f}")
        print(f"  Liquidez Corrente Média:  {medias['liquidez_corrente']:.2f}")
        print(f"  ROE Médio:                {medias['roe']:.1%}")
        print(f"  Sinistralidade Média:     {medias['indice_sinistralidade']:.1%}")

        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ DESTAQUES ═══════════════════════════════════════════════════════════════╗{Cores.RESET}")
        melhor = stats['melhor']
        pior = stats['pior']
        print(f"  {Cores.VERDE}★ Melhor Avaliação:{Cores.RESET}  {melhor['seguradora']} (Score: {melhor['score']:.1f})")
        print(f"  {Cores.VERMELHO}✗ Pior Avaliação:{Cores.RESET}    {pior['seguradora']} (Score: {pior['score']:.1f})")

        # Distribuição de ratings
        print(f"\n{Cores.BOLD}{Cores.CIANO}╔══ DISTRIBUIÇÃO DE RATINGS ═════════════════════════════════════════════════╗{Cores.RESET}")
        ratings_count = {}
        for seg in self.seguradoras:
            rating = seg.indicadores.classificacao_risco
            ratings_count[rating] = ratings_count.get(rating, 0) + 1

        for rating, count in sorted(ratings_count.items()):
            barra = "█" * (count * 5)
            print(f"  {cor_rating(rating)}{rating:<5}{Cores.RESET} {barra} ({count})")

        pausar()

    def analise_por_categoria(self):
        """Exibe análise detalhada por categoria de indicadores"""
        if not self.dados_carregados:
            self.exibir_cabecalho("Análise por Categoria")
            print(f"\n{Cores.VERMELHO}✗ Dados não carregados. Use a opção 1 primeiro.{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Análise de Indicadores por Categoria")

        print(f"\n{Cores.BOLD}Selecione a categoria:{Cores.RESET}")
        print(f"  {Cores.AMARELO}[1]{Cores.RESET} Solvência")
        print(f"  {Cores.AMARELO}[2]{Cores.RESET} Liquidez")
        print(f"  {Cores.AMARELO}[3]{Cores.RESET} Rentabilidade")
        print(f"  {Cores.AMARELO}[4]{Cores.RESET} Sinistralidade")
        print(f"  {Cores.AMARELO}[5]{Cores.RESET} Estrutura de Capital")
        print(f"  {Cores.CINZA}[0] Voltar{Cores.RESET}")

        opcao = input(f"\n  {Cores.BOLD}Digite sua opção: {Cores.RESET}").strip()

        if opcao == '1':
            self._exibir_categoria('Solvência', [
                ('indice_solvencia', 'Índice de Solvência', False),
                ('cobertura_provisoes', 'Cobertura de Provisões', False),
                ('margem_solvencia', 'Margem de Solvência (R$)', False),
            ])
        elif opcao == '2':
            self._exibir_categoria('Liquidez', [
                ('liquidez_corrente', 'Liquidez Corrente', False),
                ('liquidez_seca', 'Liquidez Seca', False),
                ('liquidez_imediata', 'Liquidez Imediata', False),
            ])
        elif opcao == '3':
            self._exibir_categoria('Rentabilidade', [
                ('roe', 'ROE', False, 'percent'),
                ('roa', 'ROA', False, 'percent'),
                ('margem_liquida', 'Margem Líquida', False, 'percent'),
                ('margem_operacional', 'Margem Operacional', False, 'percent'),
            ])
        elif opcao == '4':
            self._exibir_categoria('Sinistralidade', [
                ('indice_sinistralidade', 'Índice de Sinistralidade', True, 'percent'),
                ('indice_despesas', 'Índice de Despesas', True, 'percent'),
                ('indice_combinado', 'Índice Combinado', True, 'percent'),
                ('indice_combinado_ampliado', 'Índice Combinado Ampliado', True, 'percent'),
            ])
        elif opcao == '5':
            self._exibir_categoria('Estrutura de Capital', [
                ('alavancagem', 'Alavancagem', True),
                ('imobilizacao_pl', 'Imobilização do PL', True),
                ('indice_leverage', 'Índice de Leverage', True),
            ])

    def _exibir_categoria(self, titulo: str, indicadores: list):
        """Exibe detalhes de uma categoria específica"""
        limpar_tela()
        self.exibir_cabecalho(f"Análise de {titulo}")

        for attr, nome, menor_melhor, *fmt in indicadores:
            formato = fmt[0] if fmt else 'ratio'

            print(f"\n{Cores.BOLD}{Cores.CIANO}▸ {nome}{Cores.RESET}")
            print("─" * 60)

            # Ordena seguradoras pelo indicador
            ranking = sorted(self.seguradoras,
                           key=lambda x: getattr(x.indicadores, attr),
                           reverse=not menor_melhor)

            for pos, seg in enumerate(ranking, 1):
                valor = getattr(seg.indicadores, attr)

                if formato == 'percent':
                    valor_fmt = f"{valor:.1%}"
                elif attr == 'margem_solvencia':
                    valor_fmt = formatar_moeda(valor)
                else:
                    valor_fmt = f"{valor:.2f}"

                # Determina a cor baseado na posição
                if pos <= 2:
                    cor = Cores.VERDE
                elif pos >= len(self.seguradoras) - 1:
                    cor = Cores.VERMELHO
                else:
                    cor = Cores.AMARELO

                print(f"  {pos}. {seg.nome:<30} {cor}{valor_fmt:>15}{Cores.RESET}")

        pausar()

    def gerar_relatorios(self):
        """Gera relatórios em HTML e Excel"""
        if not self.dados_carregados:
            self.exibir_cabecalho("Gerar Relatórios")
            print(f"\n{Cores.VERMELHO}✗ Dados não carregados. Use a opção 1 primeiro.{Cores.RESET}")
            pausar()
            return

        self.exibir_cabecalho("Gerar Relatórios")

        print(f"\n{Cores.BOLD}Selecione o formato:{Cores.RESET}")
        print(f"  {Cores.AMARELO}[1]{Cores.RESET} HTML (Relatório Web)")
        print(f"  {Cores.AMARELO}[2]{Cores.RESET} Excel (Planilha)")
        print(f"  {Cores.AMARELO}[3]{Cores.RESET} Ambos")
        print(f"  {Cores.CINZA}[0] Voltar{Cores.RESET}")

        opcao = input(f"\n  {Cores.BOLD}Digite sua opção: {Cores.RESET}").strip()

        if opcao == '0':
            return

        formatos = []
        if opcao == '1':
            formatos = ['html']
        elif opcao == '2':
            formatos = ['excel']
        elif opcao == '3':
            formatos = ['html', 'excel']
        else:
            print(f"\n{Cores.VERMELHO}✗ Opção inválida!{Cores.RESET}")
            pausar()
            return

        try:
            from src.reports.gerador_relatorios import GeradorRelatorios

            print(f"\n{Cores.AMARELO}⏳ Gerando relatórios...{Cores.RESET}")

            gerador = GeradorRelatorios(output_dir="output")
            gerador.carregar_seguradoras(self.seguradoras)

            arquivos = gerador.gerar_relatorio_completo(
                nome_arquivo="relatorio_comparativo_seguradoras",
                formatos=formatos
            )

            print(f"\n{Cores.VERDE}✓ Relatórios gerados com sucesso!{Cores.RESET}")
            print(f"\n{Cores.BOLD}Arquivos gerados:{Cores.RESET}")
            for formato, caminho in arquivos.items():
                print(f"  📁 {formato.upper()}: {caminho}")

        except Exception as e:
            print(f"\n{Cores.VERMELHO}✗ Erro ao gerar relatórios: {e}{Cores.RESET}")

        pausar()

    def executar(self):
        """Loop principal da aplicação"""
        while True:
            opcao = self.exibir_menu_principal()

            if opcao == '1':
                self.carregar_dados()
            elif opcao == '2':
                self.listar_seguradoras()
            elif opcao == '3':
                self.ver_detalhes_seguradora()
            elif opcao == '4':
                self.exibir_ranking()
            elif opcao == '5':
                self.comparar_seguradoras()
            elif opcao == '6':
                self.estatisticas_setor()
            elif opcao == '7':
                self.analise_por_categoria()
            elif opcao == '8':
                self.gerar_relatorios()
            elif opcao == '0':
                limpar_tela()
                print(f"\n{Cores.CIANO}{Cores.BOLD}Obrigado por usar o Sistema de Análise Financeira!{Cores.RESET}")
                print(f"{Cores.CINZA}Até a próxima.{Cores.RESET}\n")
                break
            else:
                print(f"\n{Cores.VERMELHO}✗ Opção inválida! Tente novamente.{Cores.RESET}")
                pausar()


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================
if __name__ == "__main__":
    try:
        app = TerminalApp()
        app.executar()
    except KeyboardInterrupt:
        print(f"\n\n{Cores.AMARELO}Operação cancelada pelo usuário.{Cores.RESET}\n")
        sys.exit(0)
