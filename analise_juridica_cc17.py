#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análise Jurídica - Certame CC17/2025 - CSC/SEAP Manaus
==================================================================

Aplicação interativa para análise de irregularidades no certame
licitatório CC17/2025 da SEAP Manaus, com cruzamento de dados entre:
- Edital do certame
- Lei 14.133/2021
- Manual de Boas Práticas do TCU
- Estudos de rating de seguradoras

Funcionalidades:
1. Cadastro de dados do edital
2. Cadastro de seguradoras e ratings
3. Análise de irregularidades
4. Cruzamento de dados
5. Geração de notificações jurídicas
6. Exportação de relatórios

Autor: Sistema de Análise Jurídica
Versão: 1.0.0
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Adicionar path para importações
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.juridico.base_legal import BaseLegal14133, CategoriaLegal
from src.juridico.referencias_tcu import ReferenciasTCU, TemaTCU
from src.juridico.analisador_irregularidades import (
    AnalisadorIrregularidades, DocumentoEdital, DadosSeguradora,
    TipoIrregularidade, GravidadeIrregularidade
)
from src.juridico.cruzamento_dados import (
    MotorCruzamento, DadosEdital, DadosRating, ResultadoCruzamento
)
from src.juridico.gerador_notificacao import (
    GeradorNotificacao, TipoNotificacao, Destinatario
)


# Cores para terminal
class Cores:
    HEADER = '\033[95m'
    AZUL = '\033[94m'
    CIANO = '\033[96m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    RESET = '\033[0m'
    NEGRITO = '\033[1m'
    SUBLINHADO = '\033[4m'


def limpar_tela():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    """Pausa para leitura."""
    input(f"\n{Cores.CIANO}Pressione ENTER para continuar...{Cores.RESET}")


def imprimir_cabecalho(titulo: str):
    """Imprime cabeçalho formatado."""
    limpar_tela()
    print(f"{Cores.NEGRITO}{Cores.AZUL}")
    print("=" * 70)
    print(f"  {titulo}")
    print("=" * 70)
    print(f"{Cores.RESET}")


def imprimir_secao(titulo: str):
    """Imprime título de seção."""
    print(f"\n{Cores.AMARELO}{Cores.NEGRITO}{titulo}{Cores.RESET}")
    print("-" * 50)


class AnalisadorCC17:
    """
    Analisador específico para o Certame CC17/2025 - CSC/SEAP Manaus.
    """

    def __init__(self):
        self.motor = MotorCruzamento()
        self.gerador = GeradorNotificacao()
        self.dados_edital: Optional[DadosEdital] = None
        self.dados_rating: Optional[DadosRating] = None
        self.resultado_analise: Optional[ResultadoCruzamento] = None

        # Pré-carregar dados do CC17/2025
        self._carregar_dados_cc17()

    def _carregar_dados_cc17(self):
        """Carrega dados pré-configurados do CC17/2025."""

        # Dados do Edital CC17/2025
        self.dados_edital = DadosEdital(
            numero="CC17/2025",
            processo="CC17/2025 - CSC",
            objeto="Contratação de Seguro-Garantia para obras e serviços "
                   "da Secretaria de Estado de Administração Penitenciária - SEAP/AM",
            valor_estimado=50_000_000.00,  # R$ 50 milhões (exemplo)
            modalidade="Concorrência",
            orgao="SEAP - Secretaria de Estado de Administração Penitenciária",
            setor="Centro de Serviços Compartilhados - CSC",
            data_abertura=datetime(2025, 1, 15),
            criterio_julgamento="menor_preco",
            prazo_execucao=365,
            garantia_exigida=True,
            percentual_garantia=5.0,
            modalidade_garantia="seguro-garantia",
            documentos_habilitacao=[
                DocumentoEdital(
                    nome="Certidão Negativa de Débitos Federais",
                    obrigatorio=True,
                    categoria="regularidade_fiscal",
                    base_legal="Art. 68, Lei 14.133/2021"
                ),
                DocumentoEdital(
                    nome="Certidão Negativa de Débitos Estaduais",
                    obrigatorio=True,
                    categoria="regularidade_fiscal",
                    base_legal="Art. 68, Lei 14.133/2021"
                ),
                DocumentoEdital(
                    nome="Certidão Negativa de Débitos Municipais",
                    obrigatorio=True,
                    categoria="regularidade_fiscal",
                    base_legal="Art. 68, Lei 14.133/2021"
                ),
                DocumentoEdital(
                    nome="Certidão de Regularidade do FGTS",
                    obrigatorio=True,
                    categoria="regularidade_fiscal",
                    base_legal="Art. 68, Lei 14.133/2021"
                ),
                DocumentoEdital(
                    nome="Certidão Negativa de Débitos Trabalhistas",
                    obrigatorio=True,
                    categoria="regularidade_trabalhista",
                    base_legal="Art. 68, Lei 14.133/2021"
                ),
                DocumentoEdital(
                    nome="Balanço Patrimonial",
                    obrigatorio=True,
                    categoria="qualificacao_economica",
                    base_legal="Art. 67, Lei 14.133/2021"
                ),
                DocumentoEdital(
                    nome="Demonstração de Resultado do Exercício",
                    obrigatorio=True,
                    categoria="qualificacao_economica",
                    base_legal="Art. 67, Lei 14.133/2021"
                ),
                DocumentoEdital(
                    nome="Comprovante de Rating da Seguradora",
                    obrigatorio=False,
                    categoria="qualificacao_economica",
                    base_legal="Acórdão TCU 3089/2020"
                ),
            ],
            exigencias_qualificacao=[
                "Balanço patrimonial e demonstrações contábeis",
                "Certidão negativa de falência",
                "Capital mínimo de 10% do valor da contratação",
            ],
        )

        # Dados de Rating das Seguradoras (baseado nos estudos do repositório)
        self.dados_rating = DadosRating(
            seguradoras=[
                DadosSeguradora(
                    nome="Zurich Seguros",
                    cnpj="17.197.385/0001-21",
                    rating_sp="AA",
                    rating_moodys="Aa3",
                    rating_fitch="AA-",
                    rating_am_best="A+",
                    patrimonio_liquido=5_000_000_000.00,
                    indice_solvencia=2.5,
                    proposta_valor=1_500_000.00,
                    selecionada=False,
                ),
                DadosSeguradora(
                    nome="Junto Seguros",
                    cnpj="68.652.478/0001-08",
                    rating_sp="BBB+",
                    rating_moodys="Baa1",
                    rating_fitch=None,
                    rating_am_best=None,
                    patrimonio_liquido=800_000_000.00,
                    indice_solvencia=1.8,
                    proposta_valor=1_200_000.00,
                    selecionada=True,  # Selecionada por menor preço
                ),
                DadosSeguradora(
                    nome="Swiss Re",
                    cnpj="29.487.627/0001-57",
                    rating_sp="AA-",
                    rating_moodys="Aa3",
                    rating_fitch="AA-",
                    rating_am_best="A+",
                    patrimonio_liquido=8_000_000_000.00,
                    indice_solvencia=3.0,
                    proposta_valor=1_650_000.00,
                    selecionada=False,
                ),
                DadosSeguradora(
                    nome="Allianz Seguros",
                    cnpj="61.573.796/0001-66",
                    rating_sp="AA",
                    rating_moodys="Aa2",
                    rating_fitch="AA",
                    rating_am_best="A+",
                    patrimonio_liquido=6_500_000_000.00,
                    indice_solvencia=2.8,
                    proposta_valor=1_580_000.00,
                    selecionada=False,
                ),
            ],
            data_estudo=datetime(2024, 12, 15),
            fonte="Análise de Solidez Financeira - Estudo de Rating 2024",
            metodologia="Análise de ratings S&P, Moody's, Fitch e AM Best",
            ranking_recomendado=[
                "Zurich Seguros",
                "Allianz Seguros",
                "Swiss Re",
                "Junto Seguros",
            ],
            observacoes=[
                "Zurich e Allianz apresentam ratings de primeira linha (AA)",
                "Swiss Re possui excelente solidez financeira",
                "Junto Seguros apresenta rating de grau de investimento, porém inferior",
            ],
        )

        # Adicionar seguradoras ao edital
        self.dados_edital.seguradoras_propostas = self.dados_rating.seguradoras

    def exibir_menu_principal(self):
        """Exibe menu principal."""
        while True:
            imprimir_cabecalho("SISTEMA DE ANÁLISE JURÍDICA - CC17/2025 - CSC/SEAP")

            print(f"""
{Cores.CIANO}Certame: {Cores.RESET}CC17/2025 - CSC
{Cores.CIANO}Órgão:   {Cores.RESET}SEAP - Secretaria de Estado de Administração Penitenciária
{Cores.CIANO}Objeto:  {Cores.RESET}Contratação de Seguro-Garantia
{Cores.CIANO}Valor:   {Cores.RESET}R$ {self.dados_edital.valor_estimado:,.2f}
""")

            print(f"{Cores.AMARELO}MENU PRINCIPAL{Cores.RESET}")
            print("-" * 40)
            print("1. Visualizar Dados do Edital")
            print("2. Visualizar Estudo de Rating")
            print("3. Consultar Base Legal (Lei 14.133/2021)")
            print("4. Consultar Jurisprudência TCU")
            print("5. Executar Análise Completa de Irregularidades")
            print("6. Gerar Notificação de Irregularidades")
            print("7. Gerar Representação ao TCE")
            print("8. Gerar Parecer Jurídico")
            print("9. Exportar Relatórios")
            print("0. Sair")

            opcao = input(f"\n{Cores.VERDE}Escolha uma opção: {Cores.RESET}")

            if opcao == "1":
                self.visualizar_dados_edital()
            elif opcao == "2":
                self.visualizar_estudo_rating()
            elif opcao == "3":
                self.consultar_base_legal()
            elif opcao == "4":
                self.consultar_tcu()
            elif opcao == "5":
                self.executar_analise_completa()
            elif opcao == "6":
                self.gerar_notificacao()
            elif opcao == "7":
                self.gerar_representacao()
            elif opcao == "8":
                self.gerar_parecer()
            elif opcao == "9":
                self.exportar_relatorios()
            elif opcao == "0":
                print(f"\n{Cores.VERDE}Encerrando sistema...{Cores.RESET}")
                break
            else:
                print(f"\n{Cores.VERMELHO}Opção inválida!{Cores.RESET}")
                pausar()

    def visualizar_dados_edital(self):
        """Exibe dados do edital."""
        imprimir_cabecalho("DADOS DO EDITAL - CC17/2025")

        edital = self.dados_edital

        print(f"""
{Cores.NEGRITO}INFORMAÇÕES GERAIS{Cores.RESET}
{"-" * 50}
Número:          {edital.numero}
Processo:        {edital.processo}
Modalidade:      {edital.modalidade}
Órgão:           {edital.orgao}
Setor:           {edital.setor}
Data Abertura:   {edital.data_abertura.strftime('%d/%m/%Y') if edital.data_abertura else 'N/A'}
Prazo Execução:  {edital.prazo_execucao} dias

{Cores.NEGRITO}OBJETO{Cores.RESET}
{"-" * 50}
{edital.objeto}

{Cores.NEGRITO}VALORES{Cores.RESET}
{"-" * 50}
Valor Estimado:      R$ {edital.valor_estimado:,.2f}
Garantia Exigida:    {'Sim' if edital.garantia_exigida else 'Não'}
Percentual:          {edital.percentual_garantia}%
Modalidade Garantia: {edital.modalidade_garantia}
Critério Julgamento: {edital.criterio_julgamento}
""")

        imprimir_secao("DOCUMENTOS DE HABILITAÇÃO EXIGIDOS")
        for i, doc in enumerate(edital.documentos_habilitacao, 1):
            obrig = f"{Cores.VERMELHO}[OBRIGATÓRIO]{Cores.RESET}" if doc.obrigatorio else "[Opcional]"
            print(f"  {i}. {doc.nome} {obrig}")
            print(f"     Base Legal: {doc.base_legal}")

        imprimir_secao("SEGURADORAS PARTICIPANTES")
        for seg in edital.seguradoras_propostas:
            sel = f"{Cores.VERDE}[SELECIONADA]{Cores.RESET}" if seg.selecionada else ""
            print(f"  - {seg.nome} {sel}")
            print(f"    Proposta: R$ {seg.proposta_valor:,.2f}")
            print(f"    Rating S&P: {seg.rating_sp or 'N/A'}")

        pausar()

    def visualizar_estudo_rating(self):
        """Exibe estudo de rating."""
        imprimir_cabecalho("ESTUDO DE RATING DE SEGURADORAS")

        rating = self.dados_rating

        print(f"""
{Cores.NEGRITO}INFORMAÇÕES DO ESTUDO{Cores.RESET}
{"-" * 50}
Fonte:       {rating.fonte}
Data:        {rating.data_estudo.strftime('%d/%m/%Y')}
Metodologia: {rating.metodologia}
""")

        imprimir_secao("RANKING DE SOLIDEZ FINANCEIRA")
        print(f"\n{Cores.NEGRITO}Ranking Recomendado (do mais sólido ao menos sólido):{Cores.RESET}\n")

        for i, nome in enumerate(rating.ranking_recomendado, 1):
            seg = next((s for s in rating.seguradoras if s.nome == nome), None)
            if seg:
                selecionada = f" {Cores.AMARELO}<<< PRETERIDA{Cores.RESET}" if not seg.selecionada else f" {Cores.VERDE}<<< SELECIONADA{Cores.RESET}"
                if seg.selecionada and i > 1:
                    selecionada = f" {Cores.VERMELHO}<<< SELECIONADA (NÃO É A MELHOR!){Cores.RESET}"

                print(f"  {i}º {seg.nome}{selecionada}")
                print(f"     Rating S&P: {seg.rating_sp or 'N/A'}")
                print(f"     Rating Moody's: {seg.rating_moodys or 'N/A'}")
                print(f"     Rating Fitch: {seg.rating_fitch or 'N/A'}")
                print(f"     Patrimônio Líquido: R$ {seg.patrimonio_liquido:,.2f}")
                print(f"     Índice de Solvência: {seg.indice_solvencia:.2f}")
                print(f"     Proposta: R$ {seg.proposta_valor:,.2f}")
                print()

        imprimir_secao("OBSERVAÇÕES DO ESTUDO")
        for obs in rating.observacoes:
            print(f"  - {obs}")

        imprimir_secao("ANÁLISE COMPARATIVA")
        selecionada = next((s for s in rating.seguradoras if s.selecionada), None)
        melhor = next((s for s in rating.seguradoras if s.nome == rating.ranking_recomendado[0]), None)

        if selecionada and melhor and selecionada != melhor:
            diferenca_preco = selecionada.proposta_valor - melhor.proposta_valor
            print(f"""
{Cores.VERMELHO}{Cores.NEGRITO}ALERTA DE IRREGULARIDADE{Cores.RESET}

A seguradora selecionada ({selecionada.nome}) NÃO é a mais sólida
financeiramente conforme o estudo de rating.

Seguradora Selecionada: {selecionada.nome}
  - Rating: {selecionada.rating_sp}
  - Proposta: R$ {selecionada.proposta_valor:,.2f}

Seguradora Recomendada (melhor rating): {melhor.nome}
  - Rating: {melhor.rating_sp}
  - Proposta: R$ {melhor.proposta_valor:,.2f}

Diferença de Preço: R$ {abs(diferenca_preco):,.2f}
Economia Percentual: {abs(diferenca_preco) / melhor.proposta_valor * 100:.2f}%

{Cores.AMARELO}CONCLUSÃO:{Cores.RESET} A economia de R$ {abs(diferenca_preco):,.2f}
não justifica o risco adicional de selecionar uma seguradora com
rating inferior. Em caso de sinistro, a capacidade de pagamento
da seguradora é fundamental para proteção do interesse público.
""")

        pausar()

    def consultar_base_legal(self):
        """Consulta base legal."""
        imprimir_cabecalho("BASE LEGAL - LEI 14.133/2021")

        base = self.motor.base_legal

        print(f"""
{Cores.NEGRITO}LEI Nº 14.133/2021{Cores.RESET}
Lei de Licitações e Contratos Administrativos

Selecione a categoria para consultar os artigos relevantes:

1. Garantias Contratuais
2. Habilitação
3. Qualificação Econômico-Financeira
4. Sanções
5. Princípios
6. Artigos sobre Seguro-Garantia
7. Voltar
""")

        opcao = input(f"{Cores.VERDE}Escolha: {Cores.RESET}")

        mapeamento = {
            "1": CategoriaLegal.GARANTIA,
            "2": CategoriaLegal.HABILITACAO,
            "3": CategoriaLegal.QUALIFICACAO_ECONOMICA,
            "4": CategoriaLegal.SANCAO,
            "5": CategoriaLegal.PRINCIPIO,
            "6": CategoriaLegal.SEGURO,
        }

        if opcao in mapeamento:
            categoria = mapeamento[opcao]
            artigos = base.buscar_por_categoria(categoria)

            imprimir_cabecalho(f"ARTIGOS - {categoria.value.upper()}")

            if not artigos:
                # Buscar artigos de garantia para seguro
                if opcao == "6":
                    artigos = base.buscar_artigos_garantia()

            for artigo in artigos:
                print(f"\n{Cores.NEGRITO}Art. {artigo.numero}{Cores.RESET}")
                print("-" * 50)
                # Truncar para exibição
                caput = artigo.caput[:500] + "..." if len(artigo.caput) > 500 else artigo.caput
                print(f"{caput}")

                if artigo.incisos:
                    print("\nIncisos:")
                    for num, texto in list(artigo.incisos.items())[:3]:
                        print(f"  {num} - {texto[:100]}...")

                if artigo.paragrafos:
                    print("\nParágrafos:")
                    for num, texto in list(artigo.paragrafos.items())[:2]:
                        print(f"  {num}: {texto[:100]}...")

                print(f"\nPalavras-chave: {', '.join(artigo.palavras_chave[:5])}")
                print(f"Relevância para garantias: {artigo.relevancia_garantia}/10")

        pausar()

    def consultar_tcu(self):
        """Consulta jurisprudência do TCU."""
        imprimir_cabecalho("JURISPRUDÊNCIA DO TCU")

        tcu = self.motor.referencias_tcu

        print("""
Selecione o tema para consultar:

1. Garantia Contratual
2. Seguro-Garantia
3. Qualificação Econômico-Financeira
4. Gestão de Riscos
5. Vantajosidade
6. Boas Práticas (nível CRÍTICO)
7. Voltar
""")

        opcao = input(f"{Cores.VERDE}Escolha: {Cores.RESET}")

        mapeamento = {
            "1": TemaTCU.GARANTIA_CONTRATUAL,
            "2": TemaTCU.SEGURO_GARANTIA,
            "3": TemaTCU.QUALIFICACAO_ECONOMICA,
            "4": TemaTCU.RISCO,
            "5": TemaTCU.VANTAJOSIDADE,
        }

        if opcao in mapeamento:
            tema = mapeamento[opcao]
            acordaos = tcu.buscar_acordaos_por_tema(tema)

            imprimir_cabecalho(f"ACÓRDÃOS TCU - {tema.value.upper()}")

            for acordao in acordaos:
                print(f"\n{Cores.NEGRITO}Acórdão {acordao.numero}/{acordao.ano}-{acordao.plenario}{Cores.RESET}")
                print("-" * 50)
                print(f"Ementa: {acordao.ementa[:400]}...")

                if acordao.determinacoes:
                    print(f"\n{Cores.AMARELO}Determinações:{Cores.RESET}")
                    for det in acordao.determinacoes[:2]:
                        print(f"  - {det[:100]}...")

                if acordao.recomendacoes:
                    print(f"\n{Cores.VERDE}Recomendações:{Cores.RESET}")
                    for rec in acordao.recomendacoes[:2]:
                        print(f"  - {rec[:100]}...")

                print(f"\nRelevância: {acordao.relevancia}/10")

        elif opcao == "6":
            boas_praticas = tcu.get_boas_praticas_criticas()

            imprimir_cabecalho("BOAS PRÁTICAS - NÍVEL CRÍTICO")

            for bp in boas_praticas:
                print(f"\n{Cores.NEGRITO}{bp.titulo}{Cores.RESET}")
                print(f"Fonte: {bp.fonte}")
                print("-" * 50)
                print(f"Descrição: {bp.descricao[:300]}...")

                print(f"\n{Cores.VERDE}Recomendações:{Cores.RESET}")
                for rec in bp.recomendacoes[:3]:
                    print(f"  - {rec[:80]}...")

                print(f"\n{Cores.VERMELHO}Riscos Evitados:{Cores.RESET}")
                for risco in bp.riscos_evitados:
                    print(f"  - {risco}")

        pausar()

    def executar_analise_completa(self):
        """Executa análise completa de irregularidades."""
        imprimir_cabecalho("ANÁLISE COMPLETA DE IRREGULARIDADES")

        print(f"""
{Cores.CIANO}Iniciando análise do certame CC17/2025...{Cores.RESET}

Etapas da análise:
1. Cruzamento Edital x Lei 14.133/2021
2. Cruzamento Garantias x Estudo de Rating
3. Análise de Documentação
4. Consolidação de Irregularidades
""")

        input(f"\n{Cores.VERDE}Pressione ENTER para iniciar...{Cores.RESET}")

        print(f"\n{Cores.AMARELO}Executando análise...{Cores.RESET}")

        # Executar análise
        self.resultado_analise = self.motor.executar_analise_completa(
            self.dados_edital,
            self.dados_rating,
            None  # Sem documentos de licitantes neste exemplo
        )

        # Exibir resultados
        imprimir_cabecalho("RESULTADO DA ANÁLISE")

        resultado = self.resultado_analise

        # Definir cor baseada na conformidade
        if resultado.conformidade_geral.value in ["grave_não_conformidade", "não_conforme"]:
            cor_status = Cores.VERMELHO
        elif resultado.conformidade_geral.value == "parcialmente_conforme":
            cor_status = Cores.AMARELO
        else:
            cor_status = Cores.VERDE

        print(f"""
{Cores.NEGRITO}RESUMO EXECUTIVO{Cores.RESET}
{"=" * 60}

Processo:        {resultado.processo}
Data Análise:    {resultado.data_analise.strftime('%d/%m/%Y %H:%M')}
Score:           {resultado.score_conformidade:.1f}%
Conformidade:    {cor_status}{resultado.conformidade_geral.value.upper()}{Cores.RESET}

Itens Verificados:       {len(resultado.itens_verificados)}
Irregularidades:         {len(resultado.irregularidades_encontradas)}
""")

        # Classificar irregularidades
        gravisimas = [i for i in resultado.irregularidades_encontradas
                      if i.gravidade == GravidadeIrregularidade.GRAVISSIMA]
        altas = [i for i in resultado.irregularidades_encontradas
                 if i.gravidade == GravidadeIrregularidade.ALTA]
        medias = [i for i in resultado.irregularidades_encontradas
                  if i.gravidade == GravidadeIrregularidade.MEDIA]

        print(f"""
{Cores.NEGRITO}CLASSIFICAÇÃO DAS IRREGULARIDADES{Cores.RESET}
{"-" * 40}
{Cores.VERMELHO}Gravíssimas: {len(gravisimas)}{Cores.RESET}
{Cores.AMARELO}Altas:       {len(altas)}{Cores.RESET}
Médias:      {len(medias)}
""")

        if gravisimas:
            imprimir_secao("IRREGULARIDADES GRAVÍSSIMAS")
            for irr in gravisimas:
                print(f"\n{Cores.VERMELHO}[{irr.id}] {irr.titulo}{Cores.RESET}")
                print(f"Tipo: {irr.tipo.value}")
                print(f"\nDescrição:")
                # Formatar descrição
                desc = irr.descricao.replace("\n", " ").strip()
                palavras = desc.split()
                linha = ""
                for palavra in palavras:
                    if len(linha) + len(palavra) > 70:
                        print(f"  {linha}")
                        linha = palavra
                    else:
                        linha = f"{linha} {palavra}" if linha else palavra
                if linha:
                    print(f"  {linha}")

        if altas:
            imprimir_secao("IRREGULARIDADES DE ALTA GRAVIDADE")
            for irr in altas:
                print(f"\n{Cores.AMARELO}[{irr.id}] {irr.titulo}{Cores.RESET}")
                print(f"Tipo: {irr.tipo.value}")

        imprimir_secao("RECOMENDAÇÕES")
        for i, rec in enumerate(resultado.recomendacoes_gerais[:5], 1):
            print(f"{i}. {rec}")

        pausar()

    def gerar_notificacao(self):
        """Gera notificação de irregularidades."""
        if not self.resultado_analise:
            print(f"\n{Cores.VERMELHO}Execute a análise primeiro (opção 5)!{Cores.RESET}")
            pausar()
            return

        imprimir_cabecalho("GERAÇÃO DE NOTIFICAÇÃO DE IRREGULARIDADES")

        # Coletar dados
        print("Informe os dados do notificante:\n")
        notificante = input("Nome do Notificante: ") or "EMPRESA INTERESSADA LTDA"
        qualificacao = input("Qualificação: ") or "empresa participante do certame, inscrita no CNPJ sob nº XX.XXX.XXX/0001-XX"

        print("\nInforme os dados do destinatário:\n")
        nome_dest = input("Nome do Destinatário: ") or "Presidente da Comissão de Licitação"
        cargo_dest = input("Cargo: ") or "Presidente da Comissão Permanente de Licitação"
        orgao_dest = input("Órgão: ") or "SEAP - Secretaria de Estado de Administração Penitenciária"

        destinatarios = [
            Destinatario(
                nome=nome_dest,
                cargo=cargo_dest,
                orgao=orgao_dest,
            )
        ]

        print(f"\n{Cores.AMARELO}Gerando notificação...{Cores.RESET}")

        notificacao = self.gerador.gerar_notificacao_irregularidades(
            resultado_cruzamento=self.resultado_analise,
            irregularidades=self.resultado_analise.irregularidades_encontradas,
            destinatarios=destinatarios,
            notificante=notificante,
            qualificacao_notificante=qualificacao,
            dados_adicionais={
                "local": "Manaus/AM",
                "analise_rating": "Conforme estudo de rating anexo, a seguradora Zurich "
                                  "apresenta rating AA (S&P), superior ao rating BBB+ da "
                                  "seguradora selecionada (Junto Seguros).",
            }
        )

        # Exibir prévia
        imprimir_cabecalho("PRÉVIA DA NOTIFICAÇÃO")
        texto = self.gerador.formatar_notificacao(notificacao)
        print(texto[:3000])
        print(f"\n{Cores.CIANO}[... documento continua ...]{Cores.RESET}")

        # Salvar
        salvar = input(f"\n{Cores.VERDE}Salvar notificação? (S/N): {Cores.RESET}").upper()
        if salvar == "S":
            filename = f"notificacao_cc17_2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(texto)
            print(f"\n{Cores.VERDE}Notificação salva em: {filename}{Cores.RESET}")

            # Salvar HTML também
            html = self.gerador.exportar_notificacao_html(notificacao)
            filename_html = filename.replace(".txt", ".html")
            with open(filename_html, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Versão HTML salva em: {filename_html}")

        pausar()

    def gerar_representacao(self):
        """Gera representação ao TCE."""
        if not self.resultado_analise:
            print(f"\n{Cores.VERMELHO}Execute a análise primeiro (opção 5)!{Cores.RESET}")
            pausar()
            return

        imprimir_cabecalho("GERAÇÃO DE REPRESENTAÇÃO AO TCE")

        print("Informe os dados do representante:\n")
        representante = input("Nome: ") or "EMPRESA INTERESSADA LTDA"
        qualificacao = input("Qualificação: ") or "empresa participante do certame"

        print(f"\n{Cores.AMARELO}Gerando representação...{Cores.RESET}")

        representacao = self.gerador.gerar_representacao_tce(
            resultado_cruzamento=self.resultado_analise,
            irregularidades=self.resultado_analise.irregularidades_encontradas,
            representante=representante,
            qualificacao_representante=qualificacao,
            dados_adicionais={
                "local": "Manaus/AM",
                "orgao": "SEAP/AM",
            }
        )

        # Exibir prévia
        imprimir_cabecalho("PRÉVIA DA REPRESENTAÇÃO")
        texto = self.gerador.formatar_notificacao(representacao)
        print(texto[:3000])
        print(f"\n{Cores.CIANO}[... documento continua ...]{Cores.RESET}")

        # Salvar
        salvar = input(f"\n{Cores.VERDE}Salvar representação? (S/N): {Cores.RESET}").upper()
        if salvar == "S":
            filename = f"representacao_tce_cc17_2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(texto)
            print(f"\n{Cores.VERDE}Representação salva em: {filename}{Cores.RESET}")

        pausar()

    def gerar_parecer(self):
        """Gera parecer jurídico."""
        if not self.resultado_analise:
            print(f"\n{Cores.VERMELHO}Execute a análise primeiro (opção 5)!{Cores.RESET}")
            pausar()
            return

        imprimir_cabecalho("GERAÇÃO DE PARECER JURÍDICO")

        print("Informe os dados do parecerista:\n")
        parecerista = input("Nome: ") or "Dr. Fulano de Tal"
        cargo = input("Cargo: ") or "Advogado"
        oab = input("OAB/AM nº: ") or "12345"

        print(f"\n{Cores.AMARELO}Gerando parecer...{Cores.RESET}")

        parecer = self.gerador.gerar_parecer_juridico(
            resultado_cruzamento=self.resultado_analise,
            irregularidades=self.resultado_analise.irregularidades_encontradas,
            parecerista=parecerista,
            cargo_parecerista=cargo,
            dados_adicionais={
                "local": "Manaus/AM",
                "oab": oab,
                "interessado": "Estado do Amazonas",
            }
        )

        # Exibir prévia
        imprimir_cabecalho("PRÉVIA DO PARECER")
        texto = self.gerador.formatar_notificacao(parecer)
        print(texto[:3000])
        print(f"\n{Cores.CIANO}[... documento continua ...]{Cores.RESET}")

        # Salvar
        salvar = input(f"\n{Cores.VERDE}Salvar parecer? (S/N): {Cores.RESET}").upper()
        if salvar == "S":
            filename = f"parecer_juridico_cc17_2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(texto)
            print(f"\n{Cores.VERDE}Parecer salvo em: {filename}{Cores.RESET}")

        pausar()

    def exportar_relatorios(self):
        """Exporta relatórios da análise."""
        if not self.resultado_analise:
            print(f"\n{Cores.VERMELHO}Execute a análise primeiro (opção 5)!{Cores.RESET}")
            pausar()
            return

        imprimir_cabecalho("EXPORTAÇÃO DE RELATÓRIOS")

        print("""
Selecione o formato de exportação:

1. Relatório de Irregularidades (TXT)
2. Relatório de Cruzamento (TXT)
3. Dados em JSON
4. Todos os relatórios
5. Voltar
""")

        opcao = input(f"{Cores.VERDE}Escolha: {Cores.RESET}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if opcao in ["1", "4"]:
            # Relatório de irregularidades
            relatorio = self.motor.analisador.gerar_relatorio_irregularidades(
                self.resultado_analise.processo,
                self.resultado_analise.objeto
            )
            filename = f"relatorio_irregularidades_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(relatorio)
            print(f"{Cores.VERDE}Salvo: {filename}{Cores.RESET}")

        if opcao in ["2", "4"]:
            # Relatório de cruzamento
            relatorio = self.motor.gerar_relatorio_cruzamento(self.resultado_analise)
            filename = f"relatorio_cruzamento_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(relatorio)
            print(f"{Cores.VERDE}Salvo: {filename}{Cores.RESET}")

        if opcao in ["3", "4"]:
            # JSON
            json_data = self.motor.exportar_resultados_json()
            filename = f"dados_analise_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json_data)
            print(f"{Cores.VERDE}Salvo: {filename}{Cores.RESET}")

        if opcao != "5":
            pausar()


def main():
    """Função principal."""
    try:
        analisador = AnalisadorCC17()
        analisador.exibir_menu_principal()
    except KeyboardInterrupt:
        print(f"\n\n{Cores.AMARELO}Operação cancelada pelo usuário.{Cores.RESET}")
    except Exception as e:
        print(f"\n{Cores.VERMELHO}Erro: {e}{Cores.RESET}")
        raise


if __name__ == "__main__":
    main()
