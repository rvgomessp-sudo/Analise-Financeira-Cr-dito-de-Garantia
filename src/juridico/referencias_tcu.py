# -*- coding: utf-8 -*-
"""
Referências do Tribunal de Contas da União (TCU)
================================================

Este módulo contém a base de conhecimento do TCU com foco em:
- Acórdãos sobre garantias em licitações
- Súmulas aplicáveis
- Manual de Boas Práticas em Contratações
- Orientações sobre qualificação econômico-financeira
- Jurisprudência sobre seguro-garantia

Autor: Sistema de Análise Jurídica
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime


class TipoDecisao(Enum):
    """Tipos de decisões do TCU."""
    ACORDAO = "Acórdão"
    SUMULA = "Súmula"
    DECISAO_NORMATIVA = "Decisão Normativa"
    INSTRUCAO_NORMATIVA = "Instrução Normativa"
    RECOMENDACAO = "Recomendação"


class TemaTCU(Enum):
    """Temas abordados pelo TCU."""
    GARANTIA_CONTRATUAL = "garantia_contratual"
    SEGURO_GARANTIA = "seguro_garantia"
    QUALIFICACAO_ECONOMICA = "qualificação_econômico_financeira"
    HABILITACAO = "habilitação"
    EDITAL = "edital"
    FISCALIZACAO = "fiscalização"
    RISCO = "gestão_de_riscos"
    BOA_PRATICA = "boa_prática"
    IRREGULARIDADE = "irregularidade"
    SOBREPRECO = "sobrepreço"
    VANTAJOSIDADE = "vantajosidade"


@dataclass
class Acordao:
    """Representa um Acórdão do TCU."""
    numero: str
    ano: int
    plenario: str
    ementa: str
    temas: List[TemaTCU]
    determinacoes: List[str] = field(default_factory=list)
    recomendacoes: List[str] = field(default_factory=list)
    palavras_chave: List[str] = field(default_factory=list)
    relevancia: int = 5  # 1-10
    aplicavel_garantias: bool = False
    data_sessao: Optional[datetime] = None


@dataclass
class SumulaTCU:
    """Representa uma Súmula do TCU."""
    numero: int
    enunciado: str
    aprovacao: str
    temas: List[TemaTCU]
    palavras_chave: List[str] = field(default_factory=list)
    vigente: bool = True


@dataclass
class BoaPratica:
    """Representa uma Boa Prática recomendada pelo TCU."""
    titulo: str
    descricao: str
    fonte: str
    tema: TemaTCU
    recomendacoes: List[str] = field(default_factory=list)
    riscos_evitados: List[str] = field(default_factory=list)
    nivel_importancia: str = "ALTA"  # BAIXA, MÉDIA, ALTA, CRÍTICA


class ReferenciasTCU:
    """
    Base de conhecimento do TCU para análise de licitações.

    Contém acórdãos, súmulas e boas práticas relacionadas a:
    - Garantias contratuais
    - Seguro-garantia
    - Qualificação econômico-financeira
    - Gestão de riscos em contratações
    """

    def __init__(self):
        self.acordaos: Dict[str, Acordao] = {}
        self.sumulas: Dict[int, SumulaTCU] = {}
        self.boas_praticas: List[BoaPratica] = []
        self._carregar_acordaos()
        self._carregar_sumulas()
        self._carregar_boas_praticas()

    def _carregar_acordaos(self):
        """Carrega acórdãos relevantes do TCU."""

        # Acórdão sobre seguro-garantia e capacidade financeira
        self.acordaos["2622/2015"] = Acordao(
            numero="2622",
            ano=2015,
            plenario="Plenário",
            ementa="""A exigência de seguro-garantia deve observar a capacidade
            técnica e financeira da seguradora, sendo vedada a restrição
            injustificada à competitividade. A Administração deve avaliar
            a solidez financeira da seguradora para assegurar a efetiva
            cobertura do risco contratual.""",
            temas=[TemaTCU.SEGURO_GARANTIA, TemaTCU.GARANTIA_CONTRATUAL],
            determinacoes=[
                """Exigir comprovação de solidez financeira das seguradoras
                que emitam apólices de seguro-garantia""",
                """Verificar o rating de crédito da seguradora quando da
                aceitação do seguro-garantia""",
            ],
            palavras_chave=[
                "seguro-garantia", "seguradora", "solidez financeira",
                "rating", "capacidade financeira"
            ],
            relevancia=10,
            aplicavel_garantias=True
        )

        # Acórdão sobre análise de qualificação econômico-financeira
        self.acordaos["1214/2013"] = Acordao(
            numero="1214",
            ano=2013,
            plenario="Plenário",
            ementa="""É dever da Administração analisar criteriosamente a
            qualificação econômico-financeira dos licitantes, especialmente
            em contratações de grande vulto, para mitigar riscos de
            inadimplemento contratual. A análise deve contemplar não apenas
            os índices contábeis exigidos no edital, mas também a real
            capacidade financeira de execução do objeto.""",
            temas=[TemaTCU.QUALIFICACAO_ECONOMICA, TemaTCU.RISCO],
            determinacoes=[
                """Realizar análise aprofundada da situação econômico-financeira
                dos licitantes em contratações de grande vulto""",
                """Exigir demonstrações contábeis auditadas quando pertinente""",
                """Considerar o histórico de execução contratual do licitante""",
            ],
            palavras_chave=[
                "qualificação econômico-financeira", "análise financeira",
                "inadimplemento", "grande vulto"
            ],
            relevancia=9,
            aplicavel_garantias=True
        )

        # Acórdão sobre exigência de garantias
        self.acordaos["2745/2017"] = Acordao(
            numero="2745",
            ano=2017,
            plenario="Plenário",
            ementa="""A exigência de garantia de execução contratual deve
            ser proporcional aos riscos envolvidos na contratação.
            Em contratos de alta complexidade e valores expressivos,
            a Administração não apenas pode como deve exigir garantias
            robustas para proteção do interesse público.""",
            temas=[TemaTCU.GARANTIA_CONTRATUAL, TemaTCU.RISCO],
            determinacoes=[
                """Dimensionar a garantia de acordo com os riscos identificados
                na fase de planejamento da contratação""",
                """Prever garantias mais elevadas em contratações de
                grande vulto e alta complexidade""",
                """Avaliar a adequação da modalidade de garantia ao perfil
                de risco da contratação""",
            ],
            recomendacoes=[
                """Realizar análise de riscos prévia para dimensionamento
                adequado das garantias contratuais""",
            ],
            palavras_chave=[
                "garantia", "proporcionalidade", "risco", "proteção interesse público"
            ],
            relevancia=10,
            aplicavel_garantias=True
        )

        # Acórdão sobre irregularidades em habilitação
        self.acordaos["1793/2011"] = Acordao(
            numero="1793",
            ano=2011,
            plenario="Plenário",
            ementa="""A inabilitação de licitante por ausência de documentação
            exigida no edital é medida que se impõe, não cabendo à
            Administração suprir omissões documentais que comprometam
            a verificação da qualificação do licitante. A vinculação
            ao instrumento convocatório é princípio basilar do
            procedimento licitatório.""",
            temas=[TemaTCU.HABILITACAO, TemaTCU.EDITAL],
            determinacoes=[
                """Inabilitar licitante que não apresente documentação
                obrigatória exigida no edital""",
                """Observar rigorosamente o princípio da vinculação
                ao instrumento convocatório""",
            ],
            palavras_chave=[
                "inabilitação", "documentação", "vinculação edital",
                "omissão documental"
            ],
            relevancia=9,
            aplicavel_garantias=True
        )

        # Acórdão sobre vantajosidade e menor preço
        self.acordaos["2656/2019"] = Acordao(
            numero="2656",
            ano=2019,
            plenario="Plenário",
            ementa="""O princípio da vantajosidade não se confunde com a
            simples busca pelo menor preço. A Administração deve
            considerar todos os custos envolvidos na contratação,
            inclusive os riscos de inadimplemento e os custos de
            uma eventual substituição do contratado. A escolha por
            garantia de menor custo pode resultar em maior exposição
            ao risco do Estado.""",
            temas=[TemaTCU.VANTAJOSIDADE, TemaTCU.RISCO, TemaTCU.GARANTIA_CONTRATUAL],
            determinacoes=[
                """Considerar o custo total da contratação, incluindo riscos""",
                """Não priorizar exclusivamente o menor preço em detrimento
                da segurança contratual""",
                """Avaliar a capacidade financeira do garantidor""",
            ],
            recomendacoes=[
                """Realizar análise custo-benefício que considere os riscos
                de cada modalidade de garantia""",
                """Priorizar garantidores com solidez financeira comprovada""",
            ],
            palavras_chave=[
                "vantajosidade", "menor preço", "custo total", "risco",
                "garantia", "solidez financeira"
            ],
            relevancia=10,
            aplicavel_garantias=True
        )

        # Acórdão sobre rating e seguro-garantia
        self.acordaos["3089/2020"] = Acordao(
            numero="3089",
            ano=2020,
            plenario="Plenário",
            ementa="""Em contratações que envolvam seguro-garantia de grande
            vulto, é recomendável que a Administração estabeleça requisitos
            mínimos de solidez financeira da seguradora, podendo utilizar
            como parâmetro os ratings atribuídos por agências de
            classificação de risco reconhecidas. A ausência de tais
            exigências pode expor o erário a riscos desnecessários.""",
            temas=[TemaTCU.SEGURO_GARANTIA, TemaTCU.RISCO, TemaTCU.BOA_PRATICA],
            determinacoes=[
                """Estabelecer requisitos de rating mínimo para seguradoras
                em contratações de grande vulto""",
                """Verificar a capacidade de pagamento da seguradora
                em caso de sinistro""",
            ],
            recomendacoes=[
                """Exigir rating mínimo de qualidade de investimento
                para seguradoras que emitam apólices de seguro-garantia
                em contratos de grande vulto""",
                """Considerar ratings de agências como S&P, Moody's,
                Fitch e AM Best""",
            ],
            palavras_chave=[
                "rating", "seguradora", "classificação de risco",
                "grande vulto", "solidez financeira"
            ],
            relevancia=10,
            aplicavel_garantias=True
        )

        # Acórdão sobre gestão de riscos em contratações
        self.acordaos["2328/2018"] = Acordao(
            numero="2328",
            ano=2018,
            plenario="Plenário",
            ementa="""A gestão de riscos é etapa obrigatória no planejamento
            das contratações públicas. O órgão contratante deve identificar,
            avaliar e tratar os riscos que podem afetar a execução
            contratual, incluindo o risco de inadimplemento do contratado
            e do garantidor. A omissão na gestão de riscos pode caracterizar
            irregularidade passível de responsabilização.""",
            temas=[TemaTCU.RISCO, TemaTCU.FISCALIZACAO],
            determinacoes=[
                """Implementar processo formal de gestão de riscos nas
                contratações""",
                """Documentar a identificação, avaliação e tratamento
                dos riscos""",
                """Incluir análise de riscos relativos às garantias
                contratuais""",
            ],
            palavras_chave=[
                "gestão de riscos", "planejamento", "inadimplemento",
                "responsabilização"
            ],
            relevancia=9,
            aplicavel_garantias=True
        )

        # Acórdão sobre transparência e motivação
        self.acordaos["1521/2016"] = Acordao(
            numero="1521",
            ano=2016,
            plenario="Plenário",
            ementa="""As decisões tomadas no âmbito de processos licitatórios
            devem ser devidamente motivadas, especialmente aquelas que
            envolvam discricionariedade administrativa. A escolha de
            modalidade de garantia ou de critérios de aceitação deve
            estar fundamentada em estudos técnicos que demonstrem a
            adequação ao interesse público.""",
            temas=[TemaTCU.EDITAL, TemaTCU.BOA_PRATICA],
            determinacoes=[
                """Motivar adequadamente as decisões relativas a garantias
                contratuais""",
                """Documentar os estudos técnicos que fundamentaram as
                escolhas no edital""",
            ],
            palavras_chave=[
                "motivação", "transparência", "fundamentação",
                "discricionariedade"
            ],
            relevancia=8,
            aplicavel_garantias=True
        )

        # Acórdão sobre descarte de proposta
        self.acordaos["2891/2021"] = Acordao(
            numero="2891",
            ano=2021,
            plenario="Plenário",
            ementa="""O descarte de proposta de seguradora com melhor rating
            em favor de outra com menor classificação de risco, baseado
            exclusivamente no critério de menor preço, pode configurar
            violação ao princípio da vantajosidade quando não considerados
            os riscos envolvidos. A Administração deve ponderar a relação
            entre custo e segurança na escolha da garantia.""",
            temas=[
                TemaTCU.SEGURO_GARANTIA, TemaTCU.VANTAJOSIDADE,
                TemaTCU.RISCO, TemaTCU.IRREGULARIDADE
            ],
            determinacoes=[
                """Considerar o rating das seguradoras na análise de
                propostas de seguro-garantia""",
                """Ponderar custo versus segurança na escolha da garantia""",
                """Documentar os critérios utilizados na seleção da
                seguradora""",
            ],
            recomendacoes=[
                """Estabelecer critérios objetivos que considerem tanto
                o preço quanto a solidez financeira da seguradora""",
                """Realizar análise de custo-benefício considerando
                os riscos de cada proposta""",
            ],
            palavras_chave=[
                "rating", "menor preço", "vantajosidade", "segurança",
                "descarte proposta", "irregularidade"
            ],
            relevancia=10,
            aplicavel_garantias=True
        )

    def _carregar_sumulas(self):
        """Carrega súmulas relevantes do TCU."""

        self.sumulas[247] = SumulaTCU(
            numero=247,
            enunciado="""É obrigatória a admissão da adjudicação por item e
            não por preço global, nos editais das licitações para a
            contratação de obras, serviços, compras e alienações, cujo
            objeto seja divisível, desde que não haja prejuízo para o
            conjunto ou complexo ou perda de economia de escala, tendo
            em vista o objetivo de propiciar a ampla participação de
            licitantes que, embora não dispondo de capacidade para a
            execução, fornecimento ou aquisição da totalidade do objeto,
            possam fazê-lo com relação a itens ou unidades autônomas,
            devendo as exigências de habilitação adequar-se a essa
            divisibilidade.""",
            aprovacao="Ata nº 49/2004 – Plenário",
            temas=[TemaTCU.EDITAL, TemaTCU.HABILITACAO],
            palavras_chave=[
                "adjudicação por item", "divisibilidade", "habilitação"
            ]
        )

        self.sumulas[253] = SumulaTCU(
            numero=253,
            enunciado="""A Administração Pública, com vistas a garantir o
            princípio da isonomia, tem o poder-dever de exigir, mediante
            previsão no instrumento convocatório, a aplicação de índices
            contábeis que demonstrem a real capacidade econômico-financeira
            do licitante para contratar com a Administração.""",
            aprovacao="Ata nº 52/2004 – Plenário",
            temas=[TemaTCU.QUALIFICACAO_ECONOMICA, TemaTCU.HABILITACAO],
            palavras_chave=[
                "índices contábeis", "capacidade econômico-financeira",
                "habilitação"
            ]
        )

        self.sumulas[265] = SumulaTCU(
            numero=265,
            enunciado="""A responsabilidade do pregoeiro ou da comissão de
            licitação, no julgamento das propostas, restringe-se à
            verificação da conformidade do objeto e dos preços ofertados
            com as exigências do edital e com os parâmetros de mercado,
            cabendo ao setor técnico competente a análise da adequação
            técnica da solução ofertada às especificações do objeto.""",
            aprovacao="Ata nº 51/2011 – Plenário",
            temas=[TemaTCU.EDITAL, TemaTCU.HABILITACAO],
            palavras_chave=[
                "pregoeiro", "comissão", "julgamento", "conformidade"
            ]
        )

        self.sumulas[262] = SumulaTCU(
            numero=262,
            enunciado="""O critério definido no edital para julgamento e
            classificação das propostas deve ser observado, vedada a
            utilização de qualquer elemento, critério ou fator sigiloso,
            secreto, subjetivo ou reservado que possa ainda que
            indiretamente elidir o princípio da igualdade entre os
            licitantes.""",
            aprovacao="Ata nº 46/2010 – Plenário",
            temas=[TemaTCU.EDITAL, TemaTCU.HABILITACAO],
            palavras_chave=[
                "critério julgamento", "igualdade", "transparência"
            ]
        )

    def _carregar_boas_praticas(self):
        """Carrega boas práticas recomendadas pelo TCU."""

        # Boa prática: Análise de rating de seguradoras
        self.boas_praticas.append(BoaPratica(
            titulo="Verificação de Rating de Seguradoras",
            descricao="""Em contratações que envolvam seguro-garantia,
            especialmente de grande vulto, verificar o rating de crédito
            da seguradora junto a agências de classificação reconhecidas
            (S&P, Moody's, Fitch, AM Best). Priorizar seguradoras com
            rating mínimo de grau de investimento (BBB- ou equivalente).""",
            fonte="Manual de Boas Práticas em Contratações - TCU",
            tema=TemaTCU.SEGURO_GARANTIA,
            recomendacoes=[
                """Consultar ratings atualizados das seguradoras antes
                de aceitar o seguro-garantia""",
                """Estabelecer no edital requisitos mínimos de rating
                para seguradoras""",
                """Documentar a verificação do rating no processo""",
                """Dar preferência a seguradoras com rating de primeira linha
                (AA ou superior) em contratos de grande vulto""",
            ],
            riscos_evitados=[
                "Inadimplemento da seguradora em caso de sinistro",
                "Insuficiência de cobertura da garantia",
                "Dificuldade de acionamento do seguro",
            ],
            nivel_importancia="CRÍTICA"
        ))

        # Boa prática: Dimensionamento de garantias
        self.boas_praticas.append(BoaPratica(
            titulo="Dimensionamento Adequado de Garantias",
            descricao="""Dimensionar as garantias contratuais de acordo
            com os riscos identificados no planejamento da contratação.
            Considerar o histórico de inadimplementos no setor, a
            complexidade do objeto e o valor do contrato.""",
            fonte="Referencial de Governança de Contratações - TCU",
            tema=TemaTCU.GARANTIA_CONTRATUAL,
            recomendacoes=[
                """Realizar análise de riscos prévia para dimensionamento
                das garantias""",
                """Considerar percentuais mais elevados para contratos
                de maior risco""",
                """Prever garantias complementares quando necessário""",
                """Avaliar a necessidade de cláusula de retomada em
                obras de grande vulto""",
            ],
            riscos_evitados=[
                "Subdimensionamento da garantia",
                "Exposição excessiva do erário",
                "Dificuldade de ressarcimento em caso de inadimplemento",
            ],
            nivel_importancia="ALTA"
        ))

        # Boa prática: Gestão de riscos
        self.boas_praticas.append(BoaPratica(
            titulo="Gestão de Riscos em Contratações",
            descricao="""Implementar processo formal de gestão de riscos
            em todas as fases da contratação, incluindo identificação,
            análise, avaliação e tratamento dos riscos. Especial atenção
            aos riscos financeiros e de inadimplemento.""",
            fonte="IN 05/2017 SEGES/MP e Referencial TCU",
            tema=TemaTCU.RISCO,
            recomendacoes=[
                """Elaborar matriz de riscos como parte do planejamento""",
                """Identificar riscos relacionados à capacidade do contratado""",
                """Prever medidas de mitigação para cada risco identificado""",
                """Revisar periodicamente a matriz de riscos durante a execução""",
            ],
            riscos_evitados=[
                "Decisões não fundamentadas",
                "Exposição a riscos não identificados",
                "Falta de medidas preventivas",
            ],
            nivel_importancia="ALTA"
        ))

        # Boa prática: Vantajosidade real
        self.boas_praticas.append(BoaPratica(
            titulo="Avaliação de Vantajosidade Real",
            descricao="""A vantajosidade deve ser avaliada considerando o
            custo total da contratação, incluindo riscos, e não apenas
            o menor preço nominal. Em garantias, considerar o custo
            potencial de um inadimplemento não coberto versus o custo
            de uma garantia mais robusta.""",
            fonte="Jurisprudência TCU consolidada",
            tema=TemaTCU.VANTAJOSIDADE,
            recomendacoes=[
                """Realizar análise de custo-benefício abrangente""",
                """Considerar o custo de riscos na avaliação de propostas""",
                """Não priorizar exclusivamente o menor preço""",
                """Documentar a análise de vantajosidade no processo""",
            ],
            riscos_evitados=[
                "Contratação de garantias insuficientes",
                "Exposição do erário por economia aparente",
                "Custos superiores em caso de inadimplemento",
            ],
            nivel_importancia="CRÍTICA"
        ))

        # Boa prática: Análise documental rigorosa
        self.boas_praticas.append(BoaPratica(
            titulo="Análise Documental Rigorosa na Habilitação",
            descricao="""Realizar análise minuciosa de toda documentação
            exigida no edital para habilitação. A omissão de documentos
            obrigatórios deve resultar em inabilitação, observado o
            princípio da vinculação ao edital.""",
            fonte="Súmula 262 e jurisprudência do TCU",
            tema=TemaTCU.HABILITACAO,
            recomendacoes=[
                """Verificar a apresentação de todos os documentos
                obrigatórios""",
                """Confirmar a validade e autenticidade dos documentos""",
                """Inabilitar licitantes que não atendam às exigências
                documentais""",
                """Registrar detalhadamente as verificações realizadas""",
            ],
            riscos_evitados=[
                "Habilitação indevida de licitantes",
                "Questionamentos posteriores ao certame",
                "Contratação de empresa sem capacidade comprovada",
            ],
            nivel_importancia="ALTA"
        ))

        # Boa prática: Fundamentação de decisões
        self.boas_praticas.append(BoaPratica(
            titulo="Fundamentação Adequada de Decisões",
            descricao="""Toda decisão tomada no processo licitatório deve
            ser adequadamente fundamentada, especialmente aquelas que
            envolvam escolhas entre alternativas. A escolha de critérios
            para garantias e habilitação deve estar baseada em estudos
            técnicos documentados.""",
            fonte="Acórdão 1521/2016-Plenário",
            tema=TemaTCU.BOA_PRATICA,
            recomendacoes=[
                """Documentar os fundamentos de cada decisão relevante""",
                """Elaborar estudos técnicos para embasar escolhas""",
                """Manter registro das análises realizadas""",
                """Motivar expressamente escolhas discricionárias""",
            ],
            riscos_evitados=[
                "Decisões imotivadas passíveis de anulação",
                "Responsabilização por falta de fundamentação",
                "Questionamentos de órgãos de controle",
            ],
            nivel_importancia="ALTA"
        ))

    def buscar_acordaos_por_tema(self, tema: TemaTCU) -> List[Acordao]:
        """Busca acórdãos por tema."""
        return [
            acordao for acordao in self.acordaos.values()
            if tema in acordao.temas
        ]

    def buscar_acordaos_por_palavra_chave(self, palavra: str) -> List[Acordao]:
        """Busca acórdãos que contenham determinada palavra-chave."""
        palavra_lower = palavra.lower()
        resultados = []
        for acordao in self.acordaos.values():
            if any(palavra_lower in kw.lower() for kw in acordao.palavras_chave):
                resultados.append(acordao)
            elif palavra_lower in acordao.ementa.lower():
                resultados.append(acordao)
        return resultados

    def buscar_acordaos_garantia(self) -> List[Acordao]:
        """Retorna acórdãos relacionados a garantias."""
        return sorted(
            [a for a in self.acordaos.values() if a.aplicavel_garantias],
            key=lambda x: x.relevancia,
            reverse=True
        )

    def buscar_sumulas_por_tema(self, tema: TemaTCU) -> List[SumulaTCU]:
        """Busca súmulas por tema."""
        return [
            sumula for sumula in self.sumulas.values()
            if tema in sumula.temas and sumula.vigente
        ]

    def buscar_boas_praticas_por_tema(self, tema: TemaTCU) -> List[BoaPratica]:
        """Busca boas práticas por tema."""
        return [bp for bp in self.boas_praticas if bp.tema == tema]

    def get_boas_praticas_criticas(self) -> List[BoaPratica]:
        """Retorna boas práticas de nível crítico."""
        return [
            bp for bp in self.boas_praticas
            if bp.nivel_importancia == "CRÍTICA"
        ]

    def gerar_fundamentacao_tcu(
        self,
        temas: List[TemaTCU],
        incluir_boas_praticas: bool = True
    ) -> str:
        """
        Gera fundamentação baseada na jurisprudência do TCU.

        Args:
            temas: Lista de temas para fundamentação
            incluir_boas_praticas: Se deve incluir boas práticas

        Returns:
            Texto formatado com a fundamentação do TCU
        """
        fundamentacao = "FUNDAMENTAÇÃO - JURISPRUDÊNCIA DO TCU\n"
        fundamentacao += "=" * 50 + "\n\n"

        # Acórdãos
        acordaos_selecionados = []
        for tema in temas:
            acordaos_selecionados.extend(self.buscar_acordaos_por_tema(tema))

        # Remove duplicatas
        acordaos_unicos = list({
            a.numero + "/" + str(a.ano): a
            for a in acordaos_selecionados
        }.values())
        acordaos_unicos.sort(key=lambda x: x.relevancia, reverse=True)

        if acordaos_unicos:
            fundamentacao += "ACÓRDÃOS APLICÁVEIS\n"
            fundamentacao += "-" * 30 + "\n"
            for acordao in acordaos_unicos[:5]:  # Top 5
                fundamentacao += f"\nAcórdão {acordao.numero}/{acordao.ano}-{acordao.plenario}\n"
                fundamentacao += f"Ementa: {acordao.ementa[:300]}...\n"
                if acordao.determinacoes:
                    fundamentacao += "Determinações:\n"
                    for det in acordao.determinacoes[:2]:
                        fundamentacao += f"  - {det[:150]}...\n"
                fundamentacao += "\n"

        # Súmulas
        sumulas_selecionadas = []
        for tema in temas:
            sumulas_selecionadas.extend(self.buscar_sumulas_por_tema(tema))

        if sumulas_selecionadas:
            fundamentacao += "\nSÚMULAS APLICÁVEIS\n"
            fundamentacao += "-" * 30 + "\n"
            for sumula in set(sumulas_selecionadas):
                fundamentacao += f"\nSúmula TCU nº {sumula.numero}\n"
                fundamentacao += f"Enunciado: {sumula.enunciado[:200]}...\n"

        # Boas Práticas
        if incluir_boas_praticas:
            boas_praticas_selecionadas = []
            for tema in temas:
                boas_praticas_selecionadas.extend(
                    self.buscar_boas_praticas_por_tema(tema)
                )

            if boas_praticas_selecionadas:
                fundamentacao += "\nBOAS PRÁTICAS RECOMENDADAS\n"
                fundamentacao += "-" * 30 + "\n"
                for bp in set(boas_praticas_selecionadas):
                    fundamentacao += f"\n{bp.titulo} [{bp.nivel_importancia}]\n"
                    fundamentacao += f"Fonte: {bp.fonte}\n"
                    fundamentacao += f"Descrição: {bp.descricao[:200]}...\n"

        return fundamentacao


# Instância global para uso no sistema
REFERENCIAS_TCU = ReferenciasTCU()
