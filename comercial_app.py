#!/usr/bin/env python3
"""
Aplicação de Terminal - Sistema Comercial de Operações

Interface interativa para:
- Qualificar operações
- Gerar propostas comerciais
- Acessar scripts de abordagem
- Gerenciar tomadores e operações

Modelo de Negócio:
- Diagnóstico sempre pago antecipadamente
- Fases independentes com valor próprio
- Nunca entregar sem pagamento
"""

import os
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict

# Importações do módulo comercial
from src.comercial.operacao import (
    Operacao, FaseOperacao, StatusFase, StatusOperacao,
    TipoOperacao, TipoGarantia, OrigemOperacao,
    criar_operacao_licitacao, criar_operacao_ma,
    criar_operacao_recuperacao_judicial
)
from src.comercial.tomador import (
    Tomador, HistoricoTomador, HistoricoOperacao,
    PorteTomador, SetorTomador, NivelContato, ClassificacaoRisco,
    criar_tomador_novo, criar_tomador_com_historico_calote
)
from src.comercial.qualificador import (
    QualificadorOperacao, AnaliseViabilidade,
    DecisaoOperacao, NivelComplexidade
)
from src.comercial.proposta import (
    GeradorProposta, PropostaComercial, TipoAbordagem
)


# ══════════════════════════════════════════════════════════════════════════════
# CORES E FORMATAÇÃO
# ══════════════════════════════════════════════════════════════════════════════

class Cores:
    """Códigos ANSI para cores no terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

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
    BG_VERMELHO = '\033[41m'
    BG_VERDE = '\033[42m'
    BG_AMARELO = '\033[43m'
    BG_AZUL = '\033[44m'

    @staticmethod
    def colorir(texto: str, cor: str) -> str:
        return f"{cor}{texto}{Cores.RESET}"


def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa e aguarda Enter"""
    input(f"\n{Cores.DIM}Pressione Enter para continuar...{Cores.RESET}")


def formatar_valor(valor: Decimal) -> str:
    """Formata valor monetário"""
    if valor >= 1_000_000_000:
        return f"R$ {valor/1_000_000_000:,.2f} Bi"
    elif valor >= 1_000_000:
        return f"R$ {valor/1_000_000:,.2f} Mi"
    elif valor >= 1_000:
        return f"R$ {valor/1_000:,.1f} mil"
    else:
        return f"R$ {valor:,.2f}"


def cor_classificacao(classificacao: ClassificacaoRisco) -> str:
    """Retorna cor para classificação de risco"""
    cores = {
        ClassificacaoRisco.VERDE: Cores.VERDE,
        ClassificacaoRisco.AMARELO: Cores.AMARELO,
        ClassificacaoRisco.LARANJA: Cores.AMARELO + Cores.BOLD,
        ClassificacaoRisco.VERMELHO: Cores.VERMELHO,
        ClassificacaoRisco.PRETO: Cores.VERMELHO + Cores.BOLD
    }
    return cores.get(classificacao, Cores.RESET)


def cor_decisao(decisao: DecisaoOperacao) -> str:
    """Retorna cor para decisão"""
    cores = {
        DecisaoOperacao.ENTRAR: Cores.VERDE,
        DecisaoOperacao.ENTRAR_COM_RESTRICOES: Cores.AMARELO,
        DecisaoOperacao.AVALIAR_MELHOR: Cores.CIANO,
        DecisaoOperacao.NAO_ENTRAR: Cores.VERMELHO,
        DecisaoOperacao.RECUSAR: Cores.VERMELHO + Cores.BOLD
    }
    return cores.get(decisao, Cores.RESET)


# ══════════════════════════════════════════════════════════════════════════════
# DADOS DE EXEMPLO
# ══════════════════════════════════════════════════════════════════════════════

def criar_dados_exemplo() -> tuple:
    """
    Cria dados de exemplo baseados nos casos reais mencionados.
    """

    tomadores = []
    operacoes = []

    # ─────────────────────────────────────────────────────────────────────────
    # TOMADOR 1: RH Multi (caso real - litígio)
    # ─────────────────────────────────────────────────────────────────────────
    rh_multi = criar_tomador_com_historico_calote(
        id="TOM001",
        razao_social="RH Multi Serviços Ltda",
        cnpj="12.345.678/0001-90",
        porte=PorteTomador.GRANDE,
        setor=SetorTomador.SERVICOS,
        valor_calote=Decimal('150000'),  # Valor do calote
        nome_fantasia="RH Multi",
        contato_nome="Maria CEO",
        contato_cargo="CEO",
        contato_nivel=NivelContato.CEO,
        contato_email="ceo@rhmulti.com.br"
    )
    rh_multi.corretores_conhecidos = ["Corretora Antiga ABC"]
    rh_multi.adicionar_red_flag(
        categoria="Comportamento",
        descricao="Usou estudos nossos para emitir com outro corretor",
        severidade=5,
        fonte="Caso real - litígio em andamento"
    )
    rh_multi.calcular_score_risco()
    tomadores.append(rh_multi)

    # ─────────────────────────────────────────────────────────────────────────
    # TOMADOR 2: Citra Telecom (caso real - calote R$ 300K)
    # ─────────────────────────────────────────────────────────────────────────
    citra = Tomador(
        id="TOM002",
        razao_social="Citra Telecomunicações S.A.",
        nome_fantasia="Citra Telecom",
        cnpj="23.456.789/0001-01",
        porte=PorteTomador.GRANDE,
        setor=SetorTomador.TELECOM,
        contato_nome="Ana Proprietária",
        contato_cargo="CEO / Proprietária",
        contato_nivel=NivelContato.SOCIO,
        contato_email="ana@citra.com.br"
    )
    # Histórico: pagou uma vez, caloteou na segunda
    citra.historico.adicionar_operacao(HistoricoOperacao(
        data=datetime(2023, 6, 1),
        tipo="Garantia Telecom",
        valor_operacao=Decimal('50000000'),
        valor_honorarios=Decimal('800000'),
        valor_pago=Decimal('800000'),
        valor_pendente=Decimal('0'),
        status="Concluída"
    ))
    citra.historico.adicionar_operacao(HistoricoOperacao(
        data=datetime(2024, 3, 1),
        tipo="Estudo Índice Penalidades",
        valor_operacao=Decimal('0'),  # Era só consultoria
        valor_honorarios=Decimal('300000'),
        valor_pago=Decimal('0'),
        valor_pendente=Decimal('300000'),
        status="Calote",
        observacoes="Usou estudos para dispensar seguros na Vivo e TIM"
    ))
    citra.adicionar_red_flag(
        categoria="Comportamento",
        descricao="Histórico positivo não garantiu pagamento posterior",
        severidade=4,
        fonte="Caso real"
    )
    citra.adicionar_red_flag(
        categoria="Uso Indevido",
        descricao="Usou estudos para finalidade diferente (dispensar seguros)",
        severidade=5,
        fonte="Caso real"
    )
    citra.verificar_red_flags_automaticos()
    citra.calcular_score_risco()
    tomadores.append(citra)

    # ─────────────────────────────────────────────────────────────────────────
    # TOMADOR 3: Empresa M&A (caso real - Gallagher)
    # ─────────────────────────────────────────────────────────────────────────
    empresa_ma = Tomador(
        id="TOM003",
        razao_social="Holding Investimentos S.A.",
        nome_fantasia="Holding Invest",
        cnpj="34.567.890/0001-12",
        porte=PorteTomador.GRANDE,
        setor=SetorTomador.FINANCEIRO,
        contato_nome="João Gerente",
        contato_cargo="Gerente Financeiro",
        contato_nivel=NivelContato.GERENCIA,
        contato_email="joao@holdinginvest.com.br"
    )
    empresa_ma.corretores_conhecidos = ["Gallagher"]
    empresa_ma.seguradoras_que_recusaram = ["Seguradora A", "Seguradora B"]
    empresa_ma.adicionar_red_flag(
        categoria="Terceiros",
        descricao="Gallagher já tentou por 90 dias sem sucesso",
        severidade=3,
        fonte="Informação do cliente"
    )
    empresa_ma.adicionar_red_flag(
        categoria="Relacionamento",
        descricao="Contato apenas na gerência, não no nível decisório",
        severidade=2,
        fonte="Análise de relacionamento"
    )
    empresa_ma.calcular_score_risco()
    tomadores.append(empresa_ma)

    # ─────────────────────────────────────────────────────────────────────────
    # TOMADOR 4: Empresa em RJ (prospecto novo)
    # ─────────────────────────────────────────────────────────────────────────
    empresa_rj = criar_tomador_novo(
        id="TOM004",
        razao_social="Construções Brasil S.A. - Em Recuperação Judicial",
        cnpj="45.678.901/0001-23",
        porte=PorteTomador.GRANDE,
        setor=SetorTomador.CONSTRUCAO,
        contato_nome="Carlos Diretor",
        contato_cargo="Diretor Financeiro",
        contato_email="carlos@construcoesbrasil.com.br",
        nome_fantasia="Construções Brasil",
        em_recuperacao_judicial=True,
        faturamento_anual=Decimal('2000000000')
    )
    empresa_rj.seguradoras_que_recusaram = [
        "Junto", "Pottencial", "Zurich", "Sura", "BMG"
    ]
    empresa_rj.verificar_red_flags_automaticos()
    empresa_rj.calcular_score_risco()
    tomadores.append(empresa_rj)

    # ─────────────────────────────────────────────────────────────────────────
    # TOMADOR 5: Partners (exemplo de cliente ideal)
    # ─────────────────────────────────────────────────────────────────────────
    partners = criar_tomador_novo(
        id="TOM005",
        razao_social="Partners Engenharia S.A.",
        cnpj="56.789.012/0001-34",
        porte=PorteTomador.GRANDE,
        setor=SetorTomador.INFRAESTRUTURA,
        contato_nome="Roberto CEO",
        contato_cargo="CEO",
        contato_email="roberto@partners.com.br",
        nome_fantasia="Partners",
        contato_nivel=NivelContato.CEO,
        faturamento_anual=Decimal('500000000')
    )
    # Sem histórico ruim, sem outros corretores
    partners.calcular_score_risco()
    tomadores.append(partners)

    # ─────────────────────────────────────────────────────────────────────────
    # OPERAÇÕES DE EXEMPLO
    # ─────────────────────────────────────────────────────────────────────────

    # Operação 1: RH Multi - Licitação R$ 1 Bi (caso real)
    op_rh = criar_operacao_licitacao(
        id="OP001",
        nome="Licitação Federal - Serviços RH",
        tomador_id=rh_multi.id,
        tomador_nome=rh_multi.razao_social,
        tomador_cnpj=rh_multi.cnpj,
        valor_garantia=Decimal('100000000'),  # 10% de 1 Bi
        valor_contrato=Decimal('1000000000'),
        data_licitacao=date.today() + timedelta(days=30),
        contato_nome=rh_multi.contato_nome,
        contato_cargo=rh_multi.contato_cargo,
        contato_email=rh_multi.contato_email,
        contato_telefone="",
        origem=OrigemOperacao.DEMANDA_PASSIVA,
        descricao="Licitação federal para prestação de serviços de RH. "
                  "Tomador sem limite no mercado. Caso complexo."
    )
    operacoes.append(op_rh)

    # Operação 2: Empresa M&A - Garantia Financeira R$ 15M
    op_ma = criar_operacao_ma(
        id="OP002",
        nome="M&A - Garantia de Pagamento",
        tomador_id=empresa_ma.id,
        tomador_nome=empresa_ma.razao_social,
        tomador_cnpj=empresa_ma.cnpj,
        valor_garantia=Decimal('15000000'),
        valor_transacao=Decimal('150000000'),
        contato_nome=empresa_ma.contato_nome,
        contato_cargo=empresa_ma.contato_cargo,
        contato_email=empresa_ma.contato_email,
        contato_telefone="",
        origem=OrigemOperacao.DEMANDA_PASSIVA,
        descricao="Garantia financeira para operação de M&A. "
                  "Gallagher tentou por 90 dias sem sucesso."
    )
    op_ma.ja_tentou_outros_corretores = True
    op_ma.corretores_anteriores = ["Gallagher"]
    operacoes.append(op_ma)

    # Operação 3: Empresa RJ - Licitação Estadual
    op_rj = criar_operacao_recuperacao_judicial(
        id="OP003",
        nome="Licitação Estadual - Infraestrutura",
        tomador_id=empresa_rj.id,
        tomador_nome=empresa_rj.razao_social,
        tomador_cnpj=empresa_rj.cnpj,
        valor_garantia=Decimal('50000000'),
        valor_contrato=Decimal('500000000'),
        contato_nome=empresa_rj.contato_nome,
        contato_cargo=empresa_rj.contato_cargo,
        contato_email=empresa_rj.contato_email,
        contato_telefone="",
        origem=OrigemOperacao.PROSPECCAO_ATIVA,
        descricao="Empresa em RJ participando de licitação estadual. "
                  "Recusada por 5 seguradoras. Complexidade extrema."
    )
    operacoes.append(op_rj)

    # Operação 4: Partners - Licitação (cliente ideal)
    op_partners = criar_operacao_licitacao(
        id="OP004",
        nome="Licitação Municipal - Infraestrutura",
        tomador_id=partners.id,
        tomador_nome=partners.razao_social,
        tomador_cnpj=partners.cnpj,
        valor_garantia=Decimal('20000000'),
        valor_contrato=Decimal('200000000'),
        data_licitacao=date.today() + timedelta(days=45),
        contato_nome=partners.contato_nome,
        contato_cargo=partners.contato_cargo,
        contato_email=partners.contato_email,
        contato_telefone="",
        origem=OrigemOperacao.DEMANDA_PASSIVA,
        descricao="Licitação municipal de infraestrutura. "
                  "Cliente com bom perfil, sem histórico negativo."
    )
    operacoes.append(op_partners)

    return tomadores, operacoes


# ══════════════════════════════════════════════════════════════════════════════
# APLICAÇÃO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

class AplicacaoComercial:
    """Aplicação interativa do sistema comercial"""

    def __init__(self):
        self.tomadores: List[Tomador] = []
        self.operacoes: List[Operacao] = []
        self.qualificador = QualificadorOperacao()
        self.gerador_proposta = GeradorProposta()

    def executar(self):
        """Loop principal da aplicação"""
        self._exibir_boas_vindas()

        while True:
            opcao = self._menu_principal()

            if opcao == '0':
                self._sair()
                break
            elif opcao == '1':
                self._carregar_dados_exemplo()
            elif opcao == '2':
                self._listar_tomadores()
            elif opcao == '3':
                self._listar_operacoes()
            elif opcao == '4':
                self._qualificar_operacao()
            elif opcao == '5':
                self._gerar_proposta()
            elif opcao == '6':
                self._ver_scripts_demanda_passiva()
            elif opcao == '7':
                self._ver_scripts_prospeccao_ativa()
            elif opcao == '8':
                self._analisar_tomador()
            elif opcao == '9':
                self._gerar_contrato()
            else:
                print(f"\n{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
                pausar()

    def _exibir_boas_vindas(self):
        """Exibe tela de boas-vindas"""
        limpar_tela()
        print(f"""
{Cores.CIANO}{Cores.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     SISTEMA COMERCIAL DE OPERAÇÕES - SEGURO GARANTIA                         ║
║                                                                              ║
║     Qualificação • Propostas • Scripts de Abordagem                          ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║     PRINCÍPIOS DO SISTEMA:                                                   ║
║                                                                              ║
║     1. Diagnóstico SEMPRE 100% antecipado                                    ║
║     2. Cada fase tem valor independente                                      ║
║     3. Nunca entregar sem pagamento                                          ║
║     4. Documentar tudo para proteção                                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Cores.RESET}
""")
        pausar()

    def _menu_principal(self) -> str:
        """Exibe menu principal e retorna opção"""
        limpar_tela()
        print(f"""
{Cores.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                           MENU PRINCIPAL                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣{Cores.RESET}
║                                                                              ║
║  {Cores.CIANO}[1]{Cores.RESET} Carregar Dados de Exemplo                                           ║
║                                                                              ║
║  {Cores.AMARELO}── CONSULTAS ──{Cores.RESET}                                                        ║
║  {Cores.CIANO}[2]{Cores.RESET} Listar Tomadores                                                    ║
║  {Cores.CIANO}[3]{Cores.RESET} Listar Operações                                                    ║
║  {Cores.CIANO}[8]{Cores.RESET} Analisar Tomador (Risco Comercial)                                  ║
║                                                                              ║
║  {Cores.VERDE}── QUALIFICAÇÃO ──{Cores.RESET}                                                      ║
║  {Cores.CIANO}[4]{Cores.RESET} Qualificar Operação (Entrar ou Não?)                                ║
║                                                                              ║
║  {Cores.MAGENTA}── COMERCIAL ──{Cores.RESET}                                                         ║
║  {Cores.CIANO}[5]{Cores.RESET} Gerar Proposta Comercial                                            ║
║  {Cores.CIANO}[6]{Cores.RESET} Scripts - Demanda Passiva                                           ║
║  {Cores.CIANO}[7]{Cores.RESET} Scripts - Prospecção Ativa                                          ║
║  {Cores.CIANO}[9]{Cores.RESET} Gerar Contrato de Fase                                              ║
║                                                                              ║
║  {Cores.VERMELHO}[0]{Cores.RESET} Sair                                                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
        return input(f"{Cores.BOLD}Escolha uma opção: {Cores.RESET}").strip()

    def _carregar_dados_exemplo(self):
        """Carrega dados de exemplo"""
        limpar_tela()
        print(f"\n{Cores.CIANO}Carregando dados de exemplo...{Cores.RESET}\n")

        self.tomadores, self.operacoes = criar_dados_exemplo()

        print(f"{Cores.VERDE}✓ {len(self.tomadores)} tomadores carregados{Cores.RESET}")
        print(f"{Cores.VERDE}✓ {len(self.operacoes)} operações carregadas{Cores.RESET}")

        print(f"\n{Cores.AMARELO}Tomadores incluídos (baseados em casos reais):{Cores.RESET}")
        for t in self.tomadores:
            cor = cor_classificacao(t.classificacao)
            print(f"  • {t.nome_fantasia} - {cor}{t.classificacao.value}{Cores.RESET}")

        pausar()

    def _listar_tomadores(self):
        """Lista todos os tomadores"""
        limpar_tela()

        if not self.tomadores:
            print(f"\n{Cores.AMARELO}Nenhum tomador carregado. Use opção [1] primeiro.{Cores.RESET}")
            pausar()
            return

        print(f"""
{Cores.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                           TOMADORES CADASTRADOS                              ║
╠══════════════════════════════════════════════════════════════════════════════╣{Cores.RESET}
""")

        for i, t in enumerate(self.tomadores):
            cor = cor_classificacao(t.classificacao)
            score = t.score_risco or 0

            # Indicadores
            flags = "🚩" * min(len([rf for rf in t.red_flags if rf.ativo]), 5)
            hist = f"📊 {t.historico.taxa_pagamento:.0f}%" if t.historico.total_operacoes > 0 else ""

            print(f"""║ [{i+1}] {t.nome_fantasia:<30} {cor}■ {t.classificacao.value:<20}{Cores.RESET}
║     CNPJ: {t.cnpj:<20} Score Risco: {score:.0f}/100
║     Contato: {t.contato_nome} ({t.contato_nivel.value})
║     {flags} {hist}
║""")

        print(f"╚══════════════════════════════════════════════════════════════════════════════╝")
        pausar()

    def _listar_operacoes(self):
        """Lista todas as operações"""
        limpar_tela()

        if not self.operacoes:
            print(f"\n{Cores.AMARELO}Nenhuma operação carregada. Use opção [1] primeiro.{Cores.RESET}")
            pausar()
            return

        print(f"""
{Cores.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                           OPERAÇÕES CADASTRADAS                              ║
╠══════════════════════════════════════════════════════════════════════════════╣{Cores.RESET}
""")

        for i, op in enumerate(self.operacoes):
            urgencia_cor = Cores.VERDE
            if op.urgencia == "CRÍTICA":
                urgencia_cor = Cores.VERMELHO
            elif op.urgencia == "ALTA":
                urgencia_cor = Cores.AMARELO

            print(f"""║ [{i+1}] {op.nome:<50}
║     Tomador: {op.tomador_nome[:40]:<40}
║     Tipo: {op.tipo_operacao.value:<30}
║     Garantia: {formatar_valor(op.valor_garantia):<20} Contrato: {formatar_valor(op.valor_contrato)}
║     Origem: {op.origem.value:<30}
║     Urgência: {urgencia_cor}{op.urgencia}{Cores.RESET}
║""")

        print(f"╚══════════════════════════════════════════════════════════════════════════════╝")
        pausar()

    def _selecionar_operacao(self) -> Optional[Operacao]:
        """Permite selecionar uma operação"""
        if not self.operacoes:
            print(f"\n{Cores.AMARELO}Nenhuma operação carregada.{Cores.RESET}")
            return None

        print(f"\n{Cores.BOLD}Operações disponíveis:{Cores.RESET}")
        for i, op in enumerate(self.operacoes):
            print(f"  [{i+1}] {op.nome} - {op.tomador_nome[:30]}")

        try:
            idx = int(input(f"\n{Cores.BOLD}Selecione a operação: {Cores.RESET}")) - 1
            if 0 <= idx < len(self.operacoes):
                return self.operacoes[idx]
        except ValueError:
            pass

        print(f"{Cores.VERMELHO}Seleção inválida.{Cores.RESET}")
        return None

    def _encontrar_tomador(self, tomador_id: str) -> Optional[Tomador]:
        """Encontra tomador pelo ID"""
        for t in self.tomadores:
            if t.id == tomador_id:
                return t
        return None

    def _qualificar_operacao(self):
        """Qualifica uma operação"""
        limpar_tela()
        print(f"\n{Cores.BOLD}═══ QUALIFICAR OPERAÇÃO ═══{Cores.RESET}\n")

        operacao = self._selecionar_operacao()
        if not operacao:
            pausar()
            return

        tomador = self._encontrar_tomador(operacao.tomador_id)
        if not tomador:
            print(f"{Cores.VERMELHO}Tomador não encontrado.{Cores.RESET}")
            pausar()
            return

        print(f"\n{Cores.CIANO}Analisando operação...{Cores.RESET}\n")

        analise = self.qualificador.qualificar(operacao, tomador)

        # Exibe resumo executivo
        print(self.qualificador.gerar_resumo_executivo(analise))

        # Exibe recomendações
        print(f"\n{Cores.BOLD}RECOMENDAÇÕES:{Cores.RESET}")
        for rec in analise.recomendacoes:
            print(f"  • {rec}")

        # Exibe estrutura de cobrança
        print(f"\n{Cores.BOLD}ESTRUTURA DE COBRANÇA RECOMENDADA:{Cores.RESET}")
        ec = analise.estrutura_cobranca
        print(f"  Diagnóstico: {formatar_valor(analise.valor_recomendado_diagnostico)}")
        print(f"  Condição: {ec['diagnostico']['condicao']}")

        pausar()

    def _gerar_proposta(self):
        """Gera proposta comercial"""
        limpar_tela()
        print(f"\n{Cores.BOLD}═══ GERAR PROPOSTA COMERCIAL ═══{Cores.RESET}\n")

        operacao = self._selecionar_operacao()
        if not operacao:
            pausar()
            return

        tomador = self._encontrar_tomador(operacao.tomador_id)
        if not tomador:
            print(f"{Cores.VERMELHO}Tomador não encontrado.{Cores.RESET}")
            pausar()
            return

        # Qualifica primeiro
        analise = self.qualificador.qualificar(operacao, tomador)

        # Gera proposta
        proposta = self.gerador_proposta.gerar_proposta(operacao, tomador, analise)

        limpar_tela()
        print(proposta.gerar_texto())

        # Opção de salvar
        salvar = input(f"\n{Cores.BOLD}Salvar proposta em arquivo? (s/n): {Cores.RESET}").strip().lower()
        if salvar == 's':
            nome_arquivo = f"proposta_{proposta.numero}.txt"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(proposta.gerar_texto())
            print(f"{Cores.VERDE}Proposta salva em: {nome_arquivo}{Cores.RESET}")

        pausar()

    def _ver_scripts_demanda_passiva(self):
        """Exibe scripts para demanda passiva"""
        limpar_tela()
        print(f"\n{Cores.BOLD}═══ SCRIPTS - DEMANDA PASSIVA ═══{Cores.RESET}\n")

        operacao = self._selecionar_operacao()
        if not operacao:
            pausar()
            return

        tomador = self._encontrar_tomador(operacao.tomador_id)
        if not tomador:
            print(f"{Cores.VERMELHO}Tomador não encontrado.{Cores.RESET}")
            pausar()
            return

        analise = self.qualificador.qualificar(operacao, tomador)
        scripts = self.gerador_proposta.script_demanda_passiva(operacao, tomador, analise)

        while True:
            limpar_tela()
            print(f"""
{Cores.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                    SCRIPTS - DEMANDA PASSIVA                                 ║
║                    (Cliente veio até nós)                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣{Cores.RESET}
║                                                                              ║
║  {Cores.CIANO}[1]{Cores.RESET} Resposta Inicial à Solicitação                                     ║
║  {Cores.CIANO}[2]{Cores.RESET} Objeção: "Muito Caro"                                              ║
║  {Cores.CIANO}[3]{Cores.RESET} Objeção: "Prefiro Pagar no Final"                                  ║
║  {Cores.CIANO}[4]{Cores.RESET} Fechamento com Urgência                                           ║
║                                                                              ║
║  {Cores.VERMELHO}[0]{Cores.RESET} Voltar                                                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
            opcao = input(f"{Cores.BOLD}Escolha o script: {Cores.RESET}").strip()

            if opcao == '0':
                break
            elif opcao == '1':
                limpar_tela()
                print(scripts['resposta_inicial'])
                pausar()
            elif opcao == '2':
                limpar_tela()
                print(scripts['objecao_preco'])
                pausar()
            elif opcao == '3':
                limpar_tela()
                print(scripts['objecao_pagar_final'])
                pausar()
            elif opcao == '4':
                limpar_tela()
                print(scripts['fechamento_urgencia'])
                pausar()

    def _ver_scripts_prospeccao_ativa(self):
        """Exibe scripts para prospecção ativa"""
        limpar_tela()
        print(f"\n{Cores.BOLD}═══ SCRIPTS - PROSPECÇÃO ATIVA ═══{Cores.RESET}\n")

        operacao = self._selecionar_operacao()
        if not operacao:
            pausar()
            return

        tomador = self._encontrar_tomador(operacao.tomador_id)
        if not tomador:
            print(f"{Cores.VERMELHO}Tomador não encontrado.{Cores.RESET}")
            pausar()
            return

        analise = self.qualificador.qualificar(operacao, tomador)
        scripts = self.gerador_proposta.script_prospeccao_ativa(operacao, tomador, analise)

        while True:
            limpar_tela()
            print(f"""
{Cores.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                    SCRIPTS - PROSPECÇÃO ATIVA                                ║
║                    (Nós buscamos o cliente)                                  ║
╠══════════════════════════════════════════════════════════════════════════════╣{Cores.RESET}
║                                                                              ║
║  {Cores.CIANO}[1]{Cores.RESET} Abordagem Inicial (Criar Problema)                                 ║
║  {Cores.CIANO}[2]{Cores.RESET} Reunião de Qualificação                                           ║
║  {Cores.CIANO}[3]{Cores.RESET} Follow-up (Sem Resposta)                                          ║
║  {Cores.CIANO}[4]{Cores.RESET} Conversão de Interesse em Venda                                   ║
║                                                                              ║
║  {Cores.VERMELHO}[0]{Cores.RESET} Voltar                                                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
            opcao = input(f"{Cores.BOLD}Escolha o script: {Cores.RESET}").strip()

            if opcao == '0':
                break
            elif opcao == '1':
                limpar_tela()
                print(scripts['abordagem_inicial'])
                pausar()
            elif opcao == '2':
                limpar_tela()
                print(scripts['reuniao_qualificacao'])
                pausar()
            elif opcao == '3':
                limpar_tela()
                print(scripts['followup_sem_resposta'])
                pausar()
            elif opcao == '4':
                limpar_tela()
                print(scripts['conversao_interesse'])
                pausar()

    def _analisar_tomador(self):
        """Analisa risco de um tomador específico"""
        limpar_tela()
        print(f"\n{Cores.BOLD}═══ ANÁLISE DE RISCO DO TOMADOR ═══{Cores.RESET}\n")

        if not self.tomadores:
            print(f"{Cores.AMARELO}Nenhum tomador carregado.{Cores.RESET}")
            pausar()
            return

        print(f"{Cores.BOLD}Tomadores disponíveis:{Cores.RESET}")
        for i, t in enumerate(self.tomadores):
            print(f"  [{i+1}] {t.nome_fantasia}")

        try:
            idx = int(input(f"\n{Cores.BOLD}Selecione o tomador: {Cores.RESET}")) - 1
            if 0 <= idx < len(self.tomadores):
                tomador = self.tomadores[idx]
            else:
                print(f"{Cores.VERMELHO}Seleção inválida.{Cores.RESET}")
                pausar()
                return
        except ValueError:
            print(f"{Cores.VERMELHO}Seleção inválida.{Cores.RESET}")
            pausar()
            return

        limpar_tela()
        cor = cor_classificacao(tomador.classificacao)

        print(f"""
{Cores.BOLD}╔══════════════════════════════════════════════════════════════════════════════╗
║                    ANÁLISE DE RISCO COMERCIAL                                ║
╠══════════════════════════════════════════════════════════════════════════════╣{Cores.RESET}
║ Tomador: {tomador.razao_social[:66]:<66} ║
║ CNPJ: {tomador.cnpj:<70} ║
║ Setor: {tomador.setor.value:<69} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║ {Cores.BOLD}CLASSIFICAÇÃO:{Cores.RESET} {cor}{tomador.classificacao.value:<45}{Cores.RESET}        ║
║ {Cores.BOLD}SCORE DE RISCO:{Cores.RESET} {tomador.score_risco or 0:.0f}/100 (maior = mais risco)                      ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ {Cores.BOLD}HISTÓRICO CONOSCO{Cores.RESET}                                                        ║
║ ├─ Total de operações: {tomador.historico.total_operacoes:<10}                                   ║
║ ├─ Total honorários: {formatar_valor(tomador.historico.total_honorarios):<15}                              ║
║ ├─ Total pago: {formatar_valor(tomador.historico.total_pago):<15}                                    ║
║ ├─ Taxa de pagamento: {tomador.historico.taxa_pagamento:.1f}%                                       ║
║ ├─ Teve calote: {'SIM ⚠️' if tomador.historico.teve_calote else 'Não':<15}                                     ║
║ └─ Em litígio: {'SIM 🚨' if tomador.historico.tem_litigio else 'Não':<15}                                      ║
║                                                                              ║
""")

        # Red Flags
        red_flags_ativos = [rf for rf in tomador.red_flags if rf.ativo]
        if red_flags_ativos:
            print(f"╠══════════════════════════════════════════════════════════════════════════════╣")
            print(f"║ {Cores.VERMELHO}{Cores.BOLD}RED FLAGS ({len(red_flags_ativos)}){Cores.RESET}                                                            ║")
            for rf in red_flags_ativos[:5]:
                sev = "🔴" * rf.severidade
                print(f"║ {sev} {rf.descricao[:60]:<60} ║")
            print(f"║                                                                              ║")

        # Recomendação de cobrança
        rec = tomador.recomendacao_estrutura_cobranca()
        print(f"""╠══════════════════════════════════════════════════════════════════════════════╣
║ {Cores.BOLD}RECOMENDAÇÃO DE COBRANÇA{Cores.RESET}                                                 ║
║                                                                              ║
║ Operar: {'✅ SIM' if rec['operar'] else '❌ NÃO RECOMENDADO':<68} ║
║ Antecipação mínima: {rec['percentual_antecipado']}%                                                  ║
║                                                                              ║
║ Estrutura sugerida:                                                          ║""")

        for fase in rec['estrutura_fases']:
            print(f"║   • {fase.get('fase', '')}: {fase.get('pagamento', ''):<50} ║")

        print(f"""║                                                                              ║
║ Alertas:                                                                     ║""")

        for alerta in rec['alertas'][:3]:
            print(f"║   ⚠️ {alerta[:68]:<68} ║")

        print(f"""║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

        pausar()

    def _gerar_contrato(self):
        """Gera contrato para fase específica"""
        limpar_tela()
        print(f"\n{Cores.BOLD}═══ GERAR CONTRATO DE FASE ═══{Cores.RESET}\n")

        operacao = self._selecionar_operacao()
        if not operacao:
            pausar()
            return

        tomador = self._encontrar_tomador(operacao.tomador_id)
        if not tomador:
            print(f"{Cores.VERMELHO}Tomador não encontrado.{Cores.RESET}")
            pausar()
            return

        print(f"\n{Cores.BOLD}Selecione a fase:{Cores.RESET}")
        print("  [1] Diagnóstico Técnico")
        print("  [2] Execução Técnica")
        print("  [3] Acompanhamento até Emissão")

        fase = input(f"\n{Cores.BOLD}Fase: {Cores.RESET}").strip()

        try:
            fase_num = int(fase)
            if fase_num not in [1, 2, 3]:
                raise ValueError()
        except ValueError:
            print(f"{Cores.VERMELHO}Fase inválida.{Cores.RESET}")
            pausar()
            return

        # Calcula valor baseado na análise
        analise = self.qualificador.qualificar(operacao, tomador)

        if fase_num == 1:
            valor = analise.valor_recomendado_diagnostico
        elif fase_num == 2:
            valor = analise.valor_recomendado_diagnostico * Decimal('2.5')
        else:
            valor = analise.valor_recomendado_diagnostico * Decimal('0.5')

        contrato = self.gerador_proposta.gerar_contrato_fase(
            fase_num, operacao, tomador, valor
        )

        limpar_tela()
        print(contrato)

        # Opção de salvar
        salvar = input(f"\n{Cores.BOLD}Salvar contrato em arquivo? (s/n): {Cores.RESET}").strip().lower()
        if salvar == 's':
            nome_arquivo = f"contrato_fase{fase_num}_{tomador.cnpj.replace('/', '_').replace('.', '_')}.txt"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(contrato)
            print(f"{Cores.VERDE}Contrato salvo em: {nome_arquivo}{Cores.RESET}")

        pausar()

    def _sair(self):
        """Encerra a aplicação"""
        limpar_tela()
        print(f"""
{Cores.CIANO}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     Obrigado por usar o Sistema Comercial!                                   ║
║                                                                              ║
║     Lembre-se:                                                               ║
║     • Diagnóstico SEMPRE 100% antecipado                                     ║
║     • Nunca entregar sem pagamento                                           ║
║     • Documentar tudo                                                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Cores.RESET}
""")


# ══════════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Função principal"""
    app = AplicacaoComercial()
    app.executar()


if __name__ == "__main__":
    main()
