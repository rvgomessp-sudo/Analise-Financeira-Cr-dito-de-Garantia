# -*- coding: utf-8 -*-
"""
Gerador de Notificações Jurídicas
=================================

Este módulo gera notificações formais sobre irregularidades
identificadas em processos licitatórios, incluindo:
- Notificação de Irregularidades
- Impugnação de Decisão
- Representação ao Órgão de Controle
- Parecer Jurídico
- Relatório de Análise

Autor: Sistema de Análise Jurídica
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime, timedelta
import textwrap

from .analisador_irregularidades import (
    Irregularidade, TipoIrregularidade, GravidadeIrregularidade
)
from .cruzamento_dados import ResultadoCruzamento, NivelConformidade
from .base_legal import BaseLegal14133, CategoriaLegal
from .referencias_tcu import ReferenciasTCU, TemaTCU


class TipoNotificacao(Enum):
    """Tipos de notificações geradas."""
    NOTIFICACAO_IRREGULARIDADE = "notificação_de_irregularidade"
    IMPUGNACAO = "impugnação"
    REPRESENTACAO = "representação"
    PARECER = "parecer_jurídico"
    RELATORIO = "relatório_de_análise"
    RECURSO = "recurso_administrativo"
    MANIFESTACAO = "manifestação"


@dataclass
class Destinatario:
    """Representa um destinatário da notificação."""
    nome: str
    cargo: str
    orgao: str
    endereco: str = ""
    email: str = ""


@dataclass
class Notificacao:
    """Representa uma notificação gerada."""
    tipo: TipoNotificacao
    numero: str
    data: datetime
    destinatarios: List[Destinatario]
    assunto: str
    processo: str
    objeto: str
    corpo: str
    fundamentacao_legal: List[str]
    fundamentacao_tcu: List[str]
    pedidos: List[str]
    anexos: List[str] = field(default_factory=list)
    prazo_resposta: int = 5  # dias úteis
    local: str = "Manaus/AM"

    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "tipo": self.tipo.value,
            "numero": self.numero,
            "data": self.data.isoformat(),
            "assunto": self.assunto,
            "processo": self.processo,
            "prazo_resposta": self.prazo_resposta,
        }


class GeradorNotificacao:
    """
    Gerador de notificações jurídicas para irregularidades em licitações.

    Gera documentos formais estruturados com:
    - Fundamentação legal (Lei 14.133/2021)
    - Fundamentação jurisprudencial (TCU)
    - Descrição das irregularidades
    - Pedidos e requerimentos
    """

    def __init__(self):
        self.base_legal = BaseLegal14133()
        self.referencias_tcu = ReferenciasTCU()
        self.contador_notificacoes = 0

    def _gerar_numero(self, tipo: TipoNotificacao) -> str:
        """Gera número sequencial para a notificação."""
        self.contador_notificacoes += 1
        prefixos = {
            TipoNotificacao.NOTIFICACAO_IRREGULARIDADE: "NI",
            TipoNotificacao.IMPUGNACAO: "IMP",
            TipoNotificacao.REPRESENTACAO: "REP",
            TipoNotificacao.PARECER: "PAR",
            TipoNotificacao.RELATORIO: "REL",
            TipoNotificacao.RECURSO: "REC",
            TipoNotificacao.MANIFESTACAO: "MAN",
        }
        prefixo = prefixos.get(tipo, "DOC")
        ano = datetime.now().year
        return f"{prefixo}-{ano}/{self.contador_notificacoes:04d}"

    def _formatar_data_extenso(self, data: datetime) -> str:
        """Formata data por extenso."""
        meses = [
            "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]
        return f"{data.day} de {meses[data.month]} de {data.year}"

    def _gerar_cabecalho(
        self,
        notificacao: Notificacao
    ) -> str:
        """Gera cabeçalho da notificação."""
        linhas = []
        linhas.append("=" * 70)
        linhas.append(f"{notificacao.tipo.value.upper()}")
        linhas.append(f"Nº {notificacao.numero}")
        linhas.append("=" * 70)
        linhas.append("")

        for dest in notificacao.destinatarios:
            linhas.append(f"AO(À) ILMO(A). SR(A). {dest.nome.upper()}")
            linhas.append(f"{dest.cargo}")
            linhas.append(f"{dest.orgao}")
            if dest.endereco:
                linhas.append(f"{dest.endereco}")
            linhas.append("")

        linhas.append(f"ASSUNTO: {notificacao.assunto}")
        linhas.append(f"PROCESSO: {notificacao.processo}")
        linhas.append(f"OBJETO: {notificacao.objeto}")
        linhas.append("")

        return "\n".join(linhas)

    def _gerar_preambulo(
        self,
        notificante: str,
        qualificacao: str,
        processo: str
    ) -> str:
        """Gera preâmbulo da notificação."""
        texto = f"""
{notificante}, {qualificacao}, vem, respeitosamente, à presença de
Vossa Senhoria, nos termos da Lei nº 14.133/2021 (Lei de Licitações
e Contratos Administrativos), apresentar a presente NOTIFICAÇÃO DE
IRREGULARIDADES referente ao processo licitatório {processo}, pelos
fatos e fundamentos a seguir expostos.
"""
        return texto.strip()

    def gerar_notificacao_irregularidades(
        self,
        resultado_cruzamento: ResultadoCruzamento,
        irregularidades: List[Irregularidade],
        destinatarios: List[Destinatario],
        notificante: str,
        qualificacao_notificante: str,
        dados_adicionais: Optional[Dict] = None
    ) -> Notificacao:
        """
        Gera notificação formal de irregularidades.

        Args:
            resultado_cruzamento: Resultado da análise de cruzamento
            irregularidades: Lista de irregularidades identificadas
            destinatarios: Lista de destinatários
            notificante: Nome do notificante
            qualificacao_notificante: Qualificação do notificante
            dados_adicionais: Dados adicionais opcionais

        Returns:
            Notificação gerada
        """
        dados_adicionais = dados_adicionais or {}

        # Coletar fundamentação
        fundamentacao_legal = set()
        fundamentacao_tcu = set()

        for irr in irregularidades:
            for fund in irr.fundamentacao_legal:
                fundamentacao_legal.add(f"{fund.dispositivo} - {fund.lei}")
            for fund in irr.fundamentacao_tcu:
                fundamentacao_tcu.add(fund)

        # Gerar corpo da notificação
        corpo_partes = []

        # I - DOS FATOS
        corpo_partes.append("\nI - DOS FATOS\n")
        corpo_partes.append("-" * 50)

        fatos = f"""
1. Trata-se do Processo Licitatório {resultado_cruzamento.processo},
   cujo objeto é: {resultado_cruzamento.objeto}.

2. Em análise detalhada do certame, foram identificadas {len(irregularidades)}
   ({"uma" if len(irregularidades) == 1 else "várias"}) irregularidade(s) que
   comprometem a legalidade e regularidade do procedimento.

3. A análise realizada contemplou o cruzamento de dados entre o edital,
   a Lei 14.133/2021, as orientações do Tribunal de Contas da União (TCU)
   e estudos técnicos de rating de seguradoras.

4. O score de conformidade apurado foi de {resultado_cruzamento.score_conformidade:.1f}%,
   sendo classificado como "{resultado_cruzamento.conformidade_geral.value}".
"""
        corpo_partes.append(fatos)

        # II - DAS IRREGULARIDADES
        corpo_partes.append("\nII - DAS IRREGULARIDADES IDENTIFICADAS\n")
        corpo_partes.append("-" * 50)

        for i, irr in enumerate(irregularidades, 1):
            irr_texto = f"""
{i}. {irr.titulo}
   Gravidade: {irr.gravidade.value.upper()}
   Tipo: {irr.tipo.value}

   Descrição:
   {textwrap.fill(irr.descricao, width=65, initial_indent='   ', subsequent_indent='   ')}

   Impacto:
   {textwrap.fill(irr.impacto, width=65, initial_indent='   ', subsequent_indent='   ')}
"""
            corpo_partes.append(irr_texto)

            if irr.evidencias:
                corpo_partes.append("   Evidências:")
                for ev in irr.evidencias:
                    corpo_partes.append(f"   - [{ev.tipo}] {ev.descricao}")
                corpo_partes.append("")

        # III - DO DIREITO
        corpo_partes.append("\nIII - DO DIREITO\n")
        corpo_partes.append("-" * 50)

        direito = f"""
As irregularidades apontadas encontram fundamento na seguinte base legal
e jurisprudencial:

A) FUNDAMENTAÇÃO NA LEI 14.133/2021:
"""
        corpo_partes.append(direito)

        for fund in sorted(fundamentacao_legal):
            corpo_partes.append(f"   - {fund}")

        corpo_partes.append("\nB) FUNDAMENTAÇÃO NA JURISPRUDÊNCIA DO TCU:")

        for fund in sorted(fundamentacao_tcu):
            corpo_partes.append(f"   - {fund}")

        # Adicionar análise de rating se houver
        if dados_adicionais.get("analise_rating"):
            corpo_partes.append("\nC) ANÁLISE DE RATING DE SEGURADORAS:")
            corpo_partes.append(f"   {dados_adicionais['analise_rating']}")

        # IV - DA VIOLAÇÃO AO INTERESSE PÚBLICO
        corpo_partes.append("\nIV - DA VIOLAÇÃO AO INTERESSE PÚBLICO\n")
        corpo_partes.append("-" * 50)

        interesse_publico = """
As irregularidades identificadas violam diretamente o interesse público
pelos seguintes motivos:

1. EXPOSIÇÃO DO ERÁRIO AO RISCO: A seleção de garantia com base
   exclusivamente no menor preço, desconsiderando a solidez financeira
   do garantidor, expõe o Estado ao risco de inadimplemento em caso
   de sinistro, podendo resultar em prejuízo incalculável aos cofres
   públicos.

2. VIOLAÇÃO DO PRINCÍPIO DA VANTAJOSIDADE: O critério de menor preço
   não representa a proposta mais vantajosa quando se trata de garantias
   contratuais. A vantajosidade real deve considerar o custo total,
   incluindo os riscos de inadimplemento.

3. DESCONSIDERAÇÃO DE ESTUDOS TÉCNICOS: A existência de estudo de
   rating que aponta seguradoras com maior solidez financeira, preteridas
   por opções de menor custo, demonstra tomada de decisão contrária às
   recomendações técnicas.

4. GOVERNANÇA E GESTÃO DE RISCOS: A ausência de critérios objetivos
   para seleção de garantidores com base em sua capacidade financeira
   configura falha na governança e gestão de riscos da contratação,
   contrariando o disposto no art. 11, parágrafo único, da Lei 14.133/2021.
"""
        corpo_partes.append(interesse_publico)

        # V - DOS PEDIDOS
        corpo_partes.append("\nV - DOS PEDIDOS\n")
        corpo_partes.append("-" * 50)

        pedidos = [
            """NOTIFICAÇÃO FORMAL das autoridades responsáveis pelo certame
            sobre as irregularidades identificadas;""",
            """SUSPENSÃO IMEDIATA do procedimento licitatório até que sejam
            sanadas as irregularidades apontadas;""",
            """REVISÃO dos critérios de seleção de seguradoras para garantias
            contratuais, incluindo requisitos de rating mínimo;""",
            """RECONSIDERAÇÃO das propostas de seguradoras com melhor rating,
            conforme estudo técnico previamente elaborado;""",
            """FUNDAMENTAÇÃO EXPRESSA de qualquer decisão que opte por
            garantidor de menor solidez financeira;""",
            """MANIFESTAÇÃO das autoridades responsáveis no prazo de 5 (cinco)
            dias úteis sobre as irregularidades apontadas;""",
            """ENCAMINHAMENTO de cópia desta notificação ao Tribunal de Contas
            do Estado para ciência e eventual apuração.""",
        ]

        for irr in irregularidades:
            if irr.recomendacao and irr.recomendacao not in pedidos:
                pedidos.append(irr.recomendacao)

        corpo_partes.append("Ante o exposto, REQUER-SE:\n")
        for i, pedido in enumerate(pedidos, 1):
            corpo_partes.append(f"{i}. {pedido}\n")

        # VI - ENCERRAMENTO
        corpo_partes.append("\nVI - ENCERRAMENTO\n")
        corpo_partes.append("-" * 50)

        data_atual = datetime.now()
        encerramento = f"""
Nesses termos, pede deferimento.

{dados_adicionais.get('local', 'Manaus/AM')}, {self._formatar_data_extenso(data_atual)}.



_________________________________________
{notificante}
{qualificacao_notificante}
"""
        corpo_partes.append(encerramento)

        # Montar notificação
        notificacao = Notificacao(
            tipo=TipoNotificacao.NOTIFICACAO_IRREGULARIDADE,
            numero=self._gerar_numero(TipoNotificacao.NOTIFICACAO_IRREGULARIDADE),
            data=data_atual,
            destinatarios=destinatarios,
            assunto=f"NOTIFICAÇÃO DE IRREGULARIDADES - {resultado_cruzamento.processo}",
            processo=resultado_cruzamento.processo,
            objeto=resultado_cruzamento.objeto,
            corpo="\n".join(corpo_partes),
            fundamentacao_legal=list(fundamentacao_legal),
            fundamentacao_tcu=list(fundamentacao_tcu),
            pedidos=pedidos,
            local=dados_adicionais.get('local', 'Manaus/AM'),
        )

        return notificacao

    def gerar_representacao_tce(
        self,
        resultado_cruzamento: ResultadoCruzamento,
        irregularidades: List[Irregularidade],
        representante: str,
        qualificacao_representante: str,
        dados_adicionais: Optional[Dict] = None
    ) -> Notificacao:
        """
        Gera representação ao Tribunal de Contas do Estado.

        Args:
            resultado_cruzamento: Resultado da análise
            irregularidades: Lista de irregularidades
            representante: Nome do representante
            qualificacao_representante: Qualificação
            dados_adicionais: Dados adicionais

        Returns:
            Representação gerada
        """
        dados_adicionais = dados_adicionais or {}
        data_atual = datetime.now()

        # Destinatário padrão: TCE-AM
        destinatarios = [
            Destinatario(
                nome="Conselheiro Presidente",
                cargo="Presidente do Tribunal de Contas do Estado",
                orgao="TRIBUNAL DE CONTAS DO ESTADO DO AMAZONAS - TCE/AM",
            )
        ]

        # Fundamentação
        fundamentacao_legal = set()
        fundamentacao_tcu = set()

        for irr in irregularidades:
            for fund in irr.fundamentacao_legal:
                fundamentacao_legal.add(f"{fund.dispositivo} - {fund.lei}")
            for fund in irr.fundamentacao_tcu:
                fundamentacao_tcu.add(fund)

        # Corpo da representação
        corpo_partes = []

        corpo_partes.append(f"""
EXCELENTÍSSIMO SENHOR CONSELHEIRO PRESIDENTE DO TRIBUNAL DE CONTAS
DO ESTADO DO AMAZONAS

REPRESENTAÇÃO Nº {self._gerar_numero(TipoNotificacao.REPRESENTACAO)}

Processo de Origem: {resultado_cruzamento.processo}
Órgão: {dados_adicionais.get('orgao', 'SEAP')}
Objeto: {resultado_cruzamento.objeto}
""")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("I - DO REPRESENTANTE\n")

        corpo_partes.append(f"""
{representante}, {qualificacao_representante}, no uso das prerrogativas
legais, vem, respeitosamente, à presença de Vossa Excelência, com
fundamento no art. 74, §2º da Constituição Federal, c/c art. 113 da
Lei 14.133/2021, apresentar a presente REPRESENTAÇÃO em face de
irregularidades identificadas no certame licitatório em epígrafe.
""")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("II - DO OBJETO DA REPRESENTAÇÃO\n")

        corpo_partes.append(f"""
A presente representação tem por objeto levar ao conhecimento dessa
Egrégia Corte de Contas as seguintes irregularidades identificadas
no Processo Licitatório {resultado_cruzamento.processo}:

Total de irregularidades: {len(irregularidades)}
Gravidade geral: {resultado_cruzamento.conformidade_geral.value.upper()}
Score de conformidade: {resultado_cruzamento.score_conformidade:.1f}%
""")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("III - DAS IRREGULARIDADES\n")

        # Classificar por gravidade
        gravisimas = [i for i in irregularidades
                      if i.gravidade == GravidadeIrregularidade.GRAVISSIMA]
        altas = [i for i in irregularidades
                 if i.gravidade == GravidadeIrregularidade.ALTA]

        if gravisimas:
            corpo_partes.append("\nIRREGULARIDADES GRAVÍSSIMAS:")
            for i, irr in enumerate(gravisimas, 1):
                corpo_partes.append(f"\n{i}. {irr.titulo}")
                corpo_partes.append(f"   {irr.descricao[:500]}...")

        if altas:
            corpo_partes.append("\nIRREGULARIDADES DE ALTA GRAVIDADE:")
            for i, irr in enumerate(altas, 1):
                corpo_partes.append(f"\n{i}. {irr.titulo}")
                corpo_partes.append(f"   {irr.descricao[:500]}...")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("IV - DA FUNDAMENTAÇÃO JURÍDICA\n")

        corpo_partes.append("A) Lei 14.133/2021:")
        for fund in sorted(fundamentacao_legal):
            corpo_partes.append(f"   - {fund}")

        corpo_partes.append("\nB) Jurisprudência do TCU:")
        for fund in sorted(fundamentacao_tcu):
            corpo_partes.append(f"   - {fund}")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("V - DO PEDIDO\n")

        corpo_partes.append("""
Ante o exposto, REQUER:

1. O RECEBIMENTO E AUTUAÇÃO da presente Representação;

2. A INSTAURAÇÃO DE PROCESSO DE FISCALIZAÇÃO para apuração das
   irregularidades apontadas;

3. A SUSPENSÃO CAUTELAR do procedimento licitatório até a conclusão
   da apuração, ante o risco de dano irreparável ao erário;

4. A CITAÇÃO dos responsáveis para apresentarem defesa;

5. A APLICAÇÃO DAS SANÇÕES CABÍVEIS aos responsáveis pelas
   irregularidades;

6. A DETERMINAÇÃO para que o órgão adote as medidas corretivas
   necessárias.

Termos em que,
Pede deferimento.
""")

        corpo_partes.append(f"""
{dados_adicionais.get('local', 'Manaus/AM')}, {self._formatar_data_extenso(data_atual)}.



_________________________________________
{representante}
{qualificacao_representante}
""")

        notificacao = Notificacao(
            tipo=TipoNotificacao.REPRESENTACAO,
            numero=self._gerar_numero(TipoNotificacao.REPRESENTACAO),
            data=data_atual,
            destinatarios=destinatarios,
            assunto=f"REPRESENTAÇÃO - {resultado_cruzamento.processo}",
            processo=resultado_cruzamento.processo,
            objeto=resultado_cruzamento.objeto,
            corpo="\n".join(corpo_partes),
            fundamentacao_legal=list(fundamentacao_legal),
            fundamentacao_tcu=list(fundamentacao_tcu),
            pedidos=[
                "Recebimento e autuação",
                "Instauração de processo de fiscalização",
                "Suspensão cautelar",
                "Citação dos responsáveis",
                "Aplicação de sanções",
            ],
            local=dados_adicionais.get('local', 'Manaus/AM'),
        )

        return notificacao

    def gerar_parecer_juridico(
        self,
        resultado_cruzamento: ResultadoCruzamento,
        irregularidades: List[Irregularidade],
        parecerista: str,
        cargo_parecerista: str,
        dados_adicionais: Optional[Dict] = None
    ) -> Notificacao:
        """
        Gera parecer jurídico sobre as irregularidades.

        Args:
            resultado_cruzamento: Resultado da análise
            irregularidades: Lista de irregularidades
            parecerista: Nome do parecerista
            cargo_parecerista: Cargo
            dados_adicionais: Dados adicionais

        Returns:
            Parecer gerado
        """
        dados_adicionais = dados_adicionais or {}
        data_atual = datetime.now()

        # Fundamentação
        fundamentacao_legal = set()
        fundamentacao_tcu = set()

        for irr in irregularidades:
            for fund in irr.fundamentacao_legal:
                fundamentacao_legal.add(f"{fund.dispositivo} - {fund.lei}")
            for fund in irr.fundamentacao_tcu:
                fundamentacao_tcu.add(fund)

        # Corpo do parecer
        corpo_partes = []

        corpo_partes.append(f"""
{'=' * 70}
PARECER JURÍDICO Nº {self._gerar_numero(TipoNotificacao.PARECER)}
{'=' * 70}

PROCESSO: {resultado_cruzamento.processo}
OBJETO: {resultado_cruzamento.objeto}
INTERESSADO: {dados_adicionais.get('interessado', 'Estado do Amazonas')}
ASSUNTO: Análise de Irregularidades em Certame Licitatório
""")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("I - RELATÓRIO\n")

        corpo_partes.append(f"""
Trata-se de análise jurídica do processo licitatório em referência,
especificamente quanto às irregularidades identificadas na fase de
habilitação e seleção de garantias contratuais.

Foi realizado cruzamento de dados entre:
- Edital do certame
- Lei 14.133/2021 (Nova Lei de Licitações)
- Jurisprudência e orientações do Tribunal de Contas da União
- Estudos técnicos de rating de seguradoras

RESULTADO DA ANÁLISE:
- Score de Conformidade: {resultado_cruzamento.score_conformidade:.1f}%
- Classificação: {resultado_cruzamento.conformidade_geral.value.upper()}
- Irregularidades Identificadas: {len(irregularidades)}
""")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("II - FUNDAMENTAÇÃO\n")

        corpo_partes.append("\n2.1. DA BASE LEGAL\n")
        for fund in sorted(fundamentacao_legal):
            corpo_partes.append(f"   - {fund}")

        corpo_partes.append("\n2.2. DA JURISPRUDÊNCIA DO TCU\n")
        for fund in sorted(fundamentacao_tcu):
            corpo_partes.append(f"   - {fund}")

        corpo_partes.append("\n2.3. DAS IRREGULARIDADES\n")

        for i, irr in enumerate(irregularidades, 1):
            corpo_partes.append(f"""
{i}. {irr.titulo}
   Gravidade: {irr.gravidade.value}
   Fundamentação: {', '.join(f.dispositivo for f in irr.fundamentacao_legal[:2])}
""")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("III - ANÁLISE JURÍDICA\n")

        corpo_partes.append("""
Após detida análise dos fatos e fundamentos, verifica-se que:

1. As irregularidades identificadas configuram violação direta a
   dispositivos da Lei 14.133/2021, especialmente no que tange à
   seleção de garantias contratuais e observância do princípio da
   vantajosidade.

2. O descarte de seguradora com rating superior em favor de outra
   com menor solidez financeira, baseado exclusivamente no critério
   de menor preço, contraria a jurisprudência consolidada do TCU
   (Acórdão 2891/2021-Plenário).

3. A ausência de critérios objetivos para avaliação da capacidade
   financeira das seguradoras expõe o Estado a riscos desnecessários,
   configurando falha na gestão de riscos (art. 11, parágrafo único,
   Lei 14.133/2021).

4. As evidências documentais demonstram que existia estudo técnico
   de rating disponível, que não foi adequadamente considerado na
   tomada de decisão.
""")

        corpo_partes.append("\n" + "=" * 70)
        corpo_partes.append("IV - CONCLUSÃO E RECOMENDAÇÕES\n")

        corpo_partes.append(f"""
Com base na análise realizada, OPINO pela:

1. CONSTATAÇÃO DAS IRREGULARIDADES apontadas, com classificação
   de gravidade "{resultado_cruzamento.conformidade_geral.value}";

2. SUSPENSÃO DO PROCEDIMENTO até que sejam sanadas as irregularidades;

3. REVISÃO da decisão de seleção de garantia, com observância dos
   critérios de rating e solidez financeira;

4. NOTIFICAÇÃO dos responsáveis para ciência e manifestação;

5. ENCAMINHAMENTO de cópia ao órgão de controle para as providências
   cabíveis.

É o parecer.
""")

        corpo_partes.append(f"""
{dados_adicionais.get('local', 'Manaus/AM')}, {self._formatar_data_extenso(data_atual)}.



_________________________________________
{parecerista}
{cargo_parecerista}
OAB/AM nº {dados_adicionais.get('oab', 'XXXXX')}
""")

        notificacao = Notificacao(
            tipo=TipoNotificacao.PARECER,
            numero=self._gerar_numero(TipoNotificacao.PARECER),
            data=data_atual,
            destinatarios=[],
            assunto=f"PARECER JURÍDICO - {resultado_cruzamento.processo}",
            processo=resultado_cruzamento.processo,
            objeto=resultado_cruzamento.objeto,
            corpo="\n".join(corpo_partes),
            fundamentacao_legal=list(fundamentacao_legal),
            fundamentacao_tcu=list(fundamentacao_tcu),
            pedidos=[
                "Constatação das irregularidades",
                "Suspensão do procedimento",
                "Revisão da decisão",
                "Notificação dos responsáveis",
            ],
            local=dados_adicionais.get('local', 'Manaus/AM'),
        )

        return notificacao

    def formatar_notificacao(self, notificacao: Notificacao) -> str:
        """
        Formata a notificação para impressão/exportação.

        Args:
            notificacao: Notificação a ser formatada

        Returns:
            Texto formatado
        """
        texto = []

        # Cabeçalho
        texto.append(self._gerar_cabecalho(notificacao))

        # Corpo
        texto.append(notificacao.corpo)

        # Anexos
        if notificacao.anexos:
            texto.append("\n" + "=" * 70)
            texto.append("ANEXOS:")
            for i, anexo in enumerate(notificacao.anexos, 1):
                texto.append(f"  {i}. {anexo}")

        return "\n".join(texto)

    def exportar_notificacao_html(self, notificacao: Notificacao) -> str:
        """
        Exporta a notificação em formato HTML.

        Args:
            notificacao: Notificação a ser exportada

        Returns:
            HTML formatado
        """
        corpo_html = notificacao.corpo.replace("\n", "<br>\n")

        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{notificacao.assunto}</title>
    <style>
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.5;
            margin: 2cm;
            text-align: justify;
        }}
        h1 {{
            font-size: 14pt;
            text-align: center;
            margin-bottom: 20px;
        }}
        h2 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 20px;
        }}
        .cabecalho {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .numero {{
            font-weight: bold;
            font-size: 14pt;
        }}
        .destinatario {{
            margin-bottom: 20px;
        }}
        .corpo {{
            margin-top: 20px;
        }}
        .assinatura {{
            margin-top: 50px;
            text-align: center;
        }}
        .linha-assinatura {{
            border-top: 1px solid black;
            width: 300px;
            margin: 0 auto;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ccc;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="cabecalho">
        <h1>{notificacao.tipo.value.upper()}</h1>
        <p class="numero">Nº {notificacao.numero}</p>
    </div>

    <div class="destinatarios">
"""
        for dest in notificacao.destinatarios:
            html += f"""
        <div class="destinatario">
            <strong>AO(À) ILMO(A). SR(A). {dest.nome.upper()}</strong><br>
            {dest.cargo}<br>
            {dest.orgao}
        </div>
"""

        html += f"""
    </div>

    <p><strong>ASSUNTO:</strong> {notificacao.assunto}</p>
    <p><strong>PROCESSO:</strong> {notificacao.processo}</p>
    <p><strong>OBJETO:</strong> {notificacao.objeto}</p>

    <hr>

    <div class="corpo">
        {corpo_html}
    </div>

</body>
</html>
"""
        return html
