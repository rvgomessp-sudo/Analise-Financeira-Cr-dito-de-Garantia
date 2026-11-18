# -*- coding: utf-8 -*-
"""
Analisador de Irregularidades em Licitações
============================================

Este módulo implementa a análise automatizada de irregularidades
em processos licitatórios, com foco em:
- Omissão de documentos obrigatórios
- Seleção de garantias inadequadas
- Violação de princípios licitatórios
- Descarte de propostas com viés financeiro
- Risco regulatório e jurídico

Autor: Sistema de Análise Jurídica
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import json


class TipoIrregularidade(Enum):
    """Tipos de irregularidades identificáveis."""
    OMISSAO_DOCUMENTAL = "omissão_documental"
    GARANTIA_INADEQUADA = "garantia_inadequada"
    VIOLACAO_PRINCIPIO = "violação_de_princípio"
    DESCARTE_INDEVIDO = "descarte_indevido_proposta"
    VIES_FINANCEIRO = "viés_financeiro"
    RISCO_REGULATORIO = "risco_regulatório"
    FALTA_FUNDAMENTACAO = "falta_de_fundamentação"
    INABILITACAO_INDEVIDA = "inabilitação_indevida"
    HABILITACAO_INDEVIDA = "habilitação_indevida"
    PREJUIZO_COMPETITIVIDADE = "prejuízo_à_competitividade"
    LESAO_ERARIO = "lesão_ao_erário"
    RATING_DESCONSIDERADO = "rating_desconsiderado"


class GravidadeIrregularidade(Enum):
    """Níveis de gravidade das irregularidades."""
    BAIXA = "baixa"
    MEDIA = "média"
    ALTA = "alta"
    GRAVISSIMA = "gravíssima"


class StatusAnalise(Enum):
    """Status da análise."""
    PENDENTE = "pendente"
    EM_ANALISE = "em_análise"
    CONCLUIDA = "concluída"
    ARQUIVADA = "arquivada"


@dataclass
class FundamentacaoLegal:
    """Representa a fundamentação legal de uma irregularidade."""
    dispositivo: str
    lei: str
    texto: str
    aplicabilidade: str


@dataclass
class EvidenciaIrregularidade:
    """Representa uma evidência que suporta a irregularidade."""
    tipo: str  # documental, processual, comparativa, financeira
    descricao: str
    fonte: str
    data_identificacao: datetime = field(default_factory=datetime.now)
    anexos: List[str] = field(default_factory=list)


@dataclass
class Irregularidade:
    """Representa uma irregularidade identificada no certame."""
    id: str
    tipo: TipoIrregularidade
    gravidade: GravidadeIrregularidade
    titulo: str
    descricao: str
    fundamentacao_legal: List[FundamentacaoLegal]
    fundamentacao_tcu: List[str]
    evidencias: List[EvidenciaIrregularidade]
    impacto: str
    recomendacao: str
    responsaveis: List[str] = field(default_factory=list)
    data_identificacao: datetime = field(default_factory=datetime.now)
    prazo_manifestacao: int = 5  # dias úteis
    penalidades_aplicaveis: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Converte a irregularidade para dicionário."""
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "gravidade": self.gravidade.value,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "impacto": self.impacto,
            "recomendacao": self.recomendacao,
            "fundamentacao_legal": [
                {"dispositivo": f.dispositivo, "lei": f.lei, "texto": f.texto}
                for f in self.fundamentacao_legal
            ],
            "fundamentacao_tcu": self.fundamentacao_tcu,
            "evidencias": [
                {"tipo": e.tipo, "descricao": e.descricao, "fonte": e.fonte}
                for e in self.evidencias
            ],
            "responsaveis": self.responsaveis,
            "penalidades_aplicaveis": self.penalidades_aplicaveis,
        }


@dataclass
class DocumentoEdital:
    """Representa um documento exigido no edital."""
    nome: str
    obrigatorio: bool
    categoria: str  # habilitacao, qualificacao, tecnica, outros
    base_legal: str
    apresentado: bool = False
    valido: bool = False
    observacoes: str = ""


@dataclass
class DadosSeguradora:
    """Dados de uma seguradora para análise."""
    nome: str
    cnpj: str
    rating_sp: Optional[str] = None
    rating_moodys: Optional[str] = None
    rating_fitch: Optional[str] = None
    rating_am_best: Optional[str] = None
    patrimonio_liquido: float = 0.0
    indice_solvencia: float = 0.0
    proposta_valor: float = 0.0
    selecionada: bool = False


@dataclass
class AnaliseEdital:
    """Resultado da análise de um edital."""
    numero_processo: str
    objeto: str
    valor_estimado: float
    modalidade: str
    orgao: str
    documentos_exigidos: List[DocumentoEdital] = field(default_factory=list)
    garantias_previstas: Dict[str, Any] = field(default_factory=dict)
    criterio_julgamento: str = ""
    observacoes: List[str] = field(default_factory=list)


class AnalisadorIrregularidades:
    """
    Analisador de irregularidades em processos licitatórios.

    Realiza análise automatizada de:
    - Omissão de documentos obrigatórios
    - Adequação de garantias contratuais
    - Conformidade com a Lei 14.133/2021
    - Observância às orientações do TCU
    - Rating e solidez de seguradoras
    """

    def __init__(self):
        self.irregularidades: List[Irregularidade] = []
        self.analises: Dict[str, AnaliseEdital] = {}
        self.contador_irregularidades = 0
        self._inicializar_templates()

    def _inicializar_templates(self):
        """Inicializa templates de irregularidades comuns."""

        self.templates_irregularidades = {
            # Template: Omissão de documentos
            TipoIrregularidade.OMISSAO_DOCUMENTAL: {
                "titulo_base": "Omissão de Documento Obrigatório",
                "fundamentacao_legal": [
                    FundamentacaoLegal(
                        dispositivo="Art. 63, inciso I",
                        lei="Lei 14.133/2021",
                        texto="""Serão exigidas dos licitantes a habilitação
                        jurídica e a regularidade fiscal, social e trabalhista.""",
                        aplicabilidade="Obrigatoriedade de apresentação documental"
                    ),
                    FundamentacaoLegal(
                        dispositivo="Art. 155, inciso IV",
                        lei="Lei 14.133/2021",
                        texto="""Deixar de entregar a documentação exigida
                        para o certame.""",
                        aplicabilidade="Infração administrativa por omissão"
                    ),
                ],
                "fundamentacao_tcu": [
                    "Acórdão 1793/2011-Plenário: Inabilitação por omissão documental",
                ],
                "penalidades": [
                    "Inabilitação do licitante",
                    "Possível impedimento de licitar (Art. 156, III)",
                ],
            },

            # Template: Garantia inadequada
            TipoIrregularidade.GARANTIA_INADEQUADA: {
                "titulo_base": "Garantia Contratual Inadequada",
                "fundamentacao_legal": [
                    FundamentacaoLegal(
                        dispositivo="Art. 96",
                        lei="Lei 14.133/2021",
                        texto="""Poderá ser exigida prestação de garantia
                        nas contratações de obras, serviços e fornecimentos.""",
                        aplicabilidade="Obrigatoriedade de garantia robusta"
                    ),
                    FundamentacaoLegal(
                        dispositivo="Art. 97, §1º",
                        lei="Lei 14.133/2021",
                        texto="""Em contratações de grande vulto, poderá ser
                        exigido seguro-garantia em percentual de até 30%.""",
                        aplicabilidade="Dimensionamento de garantias"
                    ),
                ],
                "fundamentacao_tcu": [
                    "Acórdão 2745/2017-Plenário: Proporcionalidade das garantias",
                    "Acórdão 3089/2020-Plenário: Rating mínimo de seguradoras",
                ],
                "penalidades": [
                    "Nulidade da decisão de seleção",
                    "Responsabilização do gestor",
                ],
            },

            # Template: Viés financeiro
            TipoIrregularidade.VIES_FINANCEIRO: {
                "titulo_base": "Seleção com Viés Financeiro em Detrimento da Segurança",
                "fundamentacao_legal": [
                    FundamentacaoLegal(
                        dispositivo="Art. 11, inciso I",
                        lei="Lei 14.133/2021",
                        texto="""Assegurar a seleção da proposta apta a gerar
                        o resultado de contratação mais vantajoso para a
                        Administração Pública.""",
                        aplicabilidade="Vantajosidade real, não apenas menor preço"
                    ),
                    FundamentacaoLegal(
                        dispositivo="Art. 5º",
                        lei="Lei 14.133/2021",
                        texto="""Observância dos princípios da economicidade,
                        eficiência e interesse público.""",
                        aplicabilidade="Princípios norteadores"
                    ),
                ],
                "fundamentacao_tcu": [
                    "Acórdão 2656/2019-Plenário: Vantajosidade não é menor preço",
                    "Acórdão 2891/2021-Plenário: Descarte de melhor rating por custo",
                ],
                "penalidades": [
                    "Anulação da decisão",
                    "Responsabilização por prejuízo ao erário",
                ],
            },

            # Template: Rating desconsiderado
            TipoIrregularidade.RATING_DESCONSIDERADO: {
                "titulo_base": "Desconsideração de Rating de Solidez Financeira",
                "fundamentacao_legal": [
                    FundamentacaoLegal(
                        dispositivo="Art. 11, parágrafo único",
                        lei="Lei 14.133/2021",
                        texto="""A alta administração é responsável pela
                        governança das contratações e deve implementar
                        processos de gestão de riscos.""",
                        aplicabilidade="Gestão de riscos obrigatória"
                    ),
                    FundamentacaoLegal(
                        dispositivo="Art. 99, §1º",
                        lei="Lei 14.133/2021",
                        texto="""A seguradora deverá firmar o contrato,
                        prestando as informações exigidas.""",
                        aplicabilidade="Verificação de capacidade da seguradora"
                    ),
                ],
                "fundamentacao_tcu": [
                    "Acórdão 2622/2015-Plenário: Solidez financeira da seguradora",
                    "Acórdão 3089/2020-Plenário: Rating mínimo recomendado",
                    "Acórdão 2891/2021-Plenário: Vedação ao descarte por custo",
                ],
                "penalidades": [
                    "Nulidade da contratação",
                    "Responsabilização por exposição do erário ao risco",
                ],
            },

            # Template: Risco regulatório
            TipoIrregularidade.RISCO_REGULATORIO: {
                "titulo_base": "Exposição a Risco Regulatório e Jurídico",
                "fundamentacao_legal": [
                    FundamentacaoLegal(
                        dispositivo="Art. 11, parágrafo único",
                        lei="Lei 14.133/2021",
                        texto="""Implementar processos e estruturas de
                        gestão de riscos e controles internos.""",
                        aplicabilidade="Obrigação de gestão de riscos"
                    ),
                    FundamentacaoLegal(
                        dispositivo="Art. 18, §1º, XIII",
                        lei="Lei 14.133/2021",
                        texto="""Posicionamento conclusivo sobre a adequação
                        da contratação para atendimento da necessidade.""",
                        aplicabilidade="Análise de adequação obrigatória"
                    ),
                ],
                "fundamentacao_tcu": [
                    "Acórdão 2328/2018-Plenário: Gestão de riscos obrigatória",
                    "Acórdão 1521/2016-Plenário: Fundamentação de decisões",
                ],
                "penalidades": [
                    "Responsabilização pessoal do gestor",
                    "Glosa de valores em caso de dano",
                ],
            },

            # Template: Lesão ao erário
            TipoIrregularidade.LESAO_ERARIO: {
                "titulo_base": "Potencial Lesão ao Erário Público",
                "fundamentacao_legal": [
                    FundamentacaoLegal(
                        dispositivo="Art. 11, inciso III",
                        lei="Lei 14.133/2021",
                        texto="""Evitar contratações com sobrepreço ou
                        superfaturamento na execução dos contratos.""",
                        aplicabilidade="Proteção ao erário"
                    ),
                ],
                "fundamentacao_tcu": [
                    "Acórdão 2656/2019-Plenário: Custo total da contratação",
                ],
                "penalidades": [
                    "Ressarcimento ao erário",
                    "Multa proporcional ao dano",
                    "Declaração de inidoneidade",
                ],
            },
        }

    def _gerar_id_irregularidade(self) -> str:
        """Gera ID único para irregularidade."""
        self.contador_irregularidades += 1
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"IRR-{timestamp}-{self.contador_irregularidades:04d}"

    def analisar_omissao_documental(
        self,
        documentos: List[DocumentoEdital],
        licitante: str
    ) -> List[Irregularidade]:
        """
        Analisa omissão de documentos obrigatórios.

        Args:
            documentos: Lista de documentos exigidos com status de apresentação
            licitante: Nome/identificação do licitante

        Returns:
            Lista de irregularidades identificadas
        """
        irregularidades = []
        template = self.templates_irregularidades[TipoIrregularidade.OMISSAO_DOCUMENTAL]

        documentos_omitidos = [
            doc for doc in documentos
            if doc.obrigatorio and not doc.apresentado
        ]

        for doc in documentos_omitidos:
            irr = Irregularidade(
                id=self._gerar_id_irregularidade(),
                tipo=TipoIrregularidade.OMISSAO_DOCUMENTAL,
                gravidade=GravidadeIrregularidade.ALTA,
                titulo=f"{template['titulo_base']}: {doc.nome}",
                descricao=f"""O licitante {licitante} deixou de apresentar
                o documento obrigatório "{doc.nome}", exigido na categoria
                "{doc.categoria}" do edital, com base legal em {doc.base_legal}.
                Esta omissão configura descumprimento das exigências do
                instrumento convocatório e deve resultar em inabilitação.""",
                fundamentacao_legal=template["fundamentacao_legal"].copy(),
                fundamentacao_tcu=template["fundamentacao_tcu"].copy(),
                evidencias=[
                    EvidenciaIrregularidade(
                        tipo="documental",
                        descricao=f"Ausência do documento {doc.nome}",
                        fonte="Análise do envelope de habilitação",
                    )
                ],
                impacto="""Impossibilidade de verificação da capacidade do
                licitante. Risco de contratação de empresa sem qualificação
                comprovada.""",
                recomendacao=f"""INABILITAR o licitante {licitante} em
                razão da omissão documental, nos termos do art. 63 e 155,
                IV da Lei 14.133/2021.""",
                responsaveis=[licitante],
                penalidades_aplicaveis=template["penalidades"].copy(),
            )
            irregularidades.append(irr)

        return irregularidades

    def analisar_selecao_garantia(
        self,
        seguradoras: List[DadosSeguradora],
        valor_contrato: float,
        criterio_utilizado: str = "menor_preco"
    ) -> List[Irregularidade]:
        """
        Analisa a seleção de garantia com foco em viés financeiro.

        Args:
            seguradoras: Lista de seguradoras com seus dados
            valor_contrato: Valor estimado do contrato
            criterio_utilizado: Critério de seleção utilizado

        Returns:
            Lista de irregularidades identificadas
        """
        irregularidades = []

        # Identificar seguradora selecionada
        selecionada = next(
            (s for s in seguradoras if s.selecionada),
            None
        )

        if not selecionada:
            return irregularidades

        # Mapear ratings para scores
        rating_scores = {
            "AAA": 100, "AA+": 95, "AA": 90, "AA-": 85,
            "A+": 80, "A": 75, "A-": 70,
            "BBB+": 65, "BBB": 60, "BBB-": 55,
            "BB+": 50, "BB": 45, "BB-": 40,
            "B+": 35, "B": 30, "B-": 25,
            "CCC": 20, "CC": 15, "C": 10, "D": 5,
            None: 0
        }

        def get_melhor_rating(seg: DadosSeguradora) -> Tuple[str, int]:
            """Retorna o melhor rating da seguradora."""
            ratings = [
                seg.rating_sp, seg.rating_moodys,
                seg.rating_fitch, seg.rating_am_best
            ]
            melhor = None
            melhor_score = 0
            for r in ratings:
                if r and rating_scores.get(r, 0) > melhor_score:
                    melhor = r
                    melhor_score = rating_scores[r]
            return (melhor, melhor_score)

        rating_selecionada, score_selecionada = get_melhor_rating(selecionada)

        # Verificar se existe seguradora com melhor rating preterida
        for seg in seguradoras:
            if seg.selecionada:
                continue

            rating_outra, score_outra = get_melhor_rating(seg)

            # Se existe seguradora com rating significativamente melhor
            if score_outra > score_selecionada + 10:
                diferenca_preco = (
                    (selecionada.proposta_valor - seg.proposta_valor)
                    / seg.proposta_valor * 100
                    if seg.proposta_valor > 0 else 0
                )

                # Irregularidade: Descarte de melhor rating por custo
                template_rating = self.templates_irregularidades[
                    TipoIrregularidade.RATING_DESCONSIDERADO
                ]

                irr_rating = Irregularidade(
                    id=self._gerar_id_irregularidade(),
                    tipo=TipoIrregularidade.RATING_DESCONSIDERADO,
                    gravidade=GravidadeIrregularidade.GRAVISSIMA,
                    titulo=f"Descarte de Seguradora {seg.nome} com Rating Superior",
                    descricao=f"""Foi selecionada a seguradora {selecionada.nome}
                    com rating {rating_selecionada} (score {score_selecionada}),
                    preterindo a seguradora {seg.nome} que possui rating
                    {rating_outra} (score {score_outra}), significativamente
                    superior.

                    A diferença de preço entre as propostas foi de
                    {abs(diferenca_preco):.2f}%, porém a economia nominal
                    não compensa o risco adicional assumido pela escolha
                    de seguradora com menor solidez financeira.

                    Conforme estudo de rating previamente elaborado, a
                    seguradora {seg.nome} apresenta maior solidez para
                    honrar eventual sinistro, protegendo o interesse público.""",
                    fundamentacao_legal=template_rating["fundamentacao_legal"].copy(),
                    fundamentacao_tcu=template_rating["fundamentacao_tcu"].copy(),
                    evidencias=[
                        EvidenciaIrregularidade(
                            tipo="financeira",
                            descricao=f"Rating {seg.nome}: {rating_outra}",
                            fonte="Agências de classificação de risco",
                        ),
                        EvidenciaIrregularidade(
                            tipo="financeira",
                            descricao=f"Rating {selecionada.nome}: {rating_selecionada}",
                            fonte="Agências de classificação de risco",
                        ),
                        EvidenciaIrregularidade(
                            tipo="comparativa",
                            descricao=f"Diferença de preço: {diferenca_preco:.2f}%",
                            fonte="Análise de propostas",
                        ),
                    ],
                    impacto=f"""Exposição do Estado ao risco de inadimplemento
                    da seguradora em caso de sinistro. Em um contrato de
                    R$ {valor_contrato:,.2f}, o risco potencial é significativo
                    e desproporcional à economia obtida.""",
                    recomendacao=f"""ANULAR a decisão de seleção e
                    RECONSIDERAR a proposta da seguradora {seg.nome},
                    que apresenta rating superior e maior capacidade de
                    honrar eventual sinistro.""",
                    responsaveis=["Comissão de Licitação", "Autoridade Competente"],
                    penalidades_aplicaveis=template_rating["penalidades"].copy(),
                )
                irregularidades.append(irr_rating)

                # Irregularidade: Viés financeiro
                template_vies = self.templates_irregularidades[
                    TipoIrregularidade.VIES_FINANCEIRO
                ]

                irr_vies = Irregularidade(
                    id=self._gerar_id_irregularidade(),
                    tipo=TipoIrregularidade.VIES_FINANCEIRO,
                    gravidade=GravidadeIrregularidade.ALTA,
                    titulo="Seleção de Garantia com Viés de Menor Custo",
                    descricao=f"""A seleção da seguradora {selecionada.nome}
                    foi baseada exclusivamente no critério de menor preço,
                    desconsiderando a análise de solidez financeira e
                    rating das proponentes.

                    O critério de "{criterio_utilizado}" não é adequado para
                    seleção de garantias contratuais, onde a capacidade de
                    pagamento do garantidor é essencial para proteção do
                    interesse público.

                    A vantajosidade real deve considerar o custo total,
                    incluindo os riscos de inadimplemento da garantia.""",
                    fundamentacao_legal=template_vies["fundamentacao_legal"].copy(),
                    fundamentacao_tcu=template_vies["fundamentacao_tcu"].copy(),
                    evidencias=[
                        EvidenciaIrregularidade(
                            tipo="processual",
                            descricao=f"Critério utilizado: {criterio_utilizado}",
                            fonte="Ata de julgamento",
                        ),
                    ],
                    impacto="""Violação do princípio da vantajosidade.
                    A economia nominal pode resultar em prejuízo real
                    em caso de necessidade de acionamento da garantia.""",
                    recomendacao="""REVISAR os critérios de seleção de
                    seguradoras para garantias contratuais, incluindo
                    requisitos de rating mínimo.""",
                    responsaveis=["Comissão de Licitação"],
                    penalidades_aplicaveis=template_vies["penalidades"].copy(),
                )
                irregularidades.append(irr_vies)

        # Verificar se rating da selecionada é abaixo do grau de investimento
        if score_selecionada < 55:  # Abaixo de BBB-
            template_risco = self.templates_irregularidades[
                TipoIrregularidade.RISCO_REGULATORIO
            ]

            irr_risco = Irregularidade(
                id=self._gerar_id_irregularidade(),
                tipo=TipoIrregularidade.RISCO_REGULATORIO,
                gravidade=GravidadeIrregularidade.GRAVISSIMA,
                titulo="Aceitação de Seguradora Abaixo do Grau de Investimento",
                descricao=f"""A seguradora selecionada {selecionada.nome}
                possui rating {rating_selecionada} (score {score_selecionada}),
                que está ABAIXO do grau de investimento (mínimo BBB-).

                Seguradoras abaixo do grau de investimento apresentam
                risco elevado de inadimplemento, o que expõe o Estado
                a prejuízos significativos em caso de sinistro.

                Conforme orientação do TCU (Acórdão 3089/2020-Plenário),
                em contratações de vulto deve-se exigir rating mínimo
                de grau de investimento para seguradoras.""",
                fundamentacao_legal=template_risco["fundamentacao_legal"].copy(),
                fundamentacao_tcu=[
                    "Acórdão 3089/2020-Plenário: Rating mínimo recomendado",
                    "Acórdão 2622/2015-Plenário: Solidez financeira",
                ],
                evidencias=[
                    EvidenciaIrregularidade(
                        tipo="financeira",
                        descricao=f"Rating abaixo do grau de investimento",
                        fonte="Análise de rating",
                    ),
                ],
                impacto=f"""Exposição do Estado a risco ELEVADO de
                inadimplemento da garantia. Valor em risco:
                R$ {valor_contrato:,.2f}.""",
                recomendacao="""REJEITAR a garantia oferecida e exigir
                substituição por seguradora com rating mínimo de
                grau de investimento (BBB- ou superior).""",
                responsaveis=["Autoridade Competente", "Gestor do Contrato"],
                penalidades_aplicaveis=template_risco["penalidades"].copy(),
            )
            irregularidades.append(irr_risco)

        return irregularidades

    def analisar_risco_decisao(
        self,
        decisao: str,
        responsavel: str,
        fundamentacao: str,
        valor_envolvido: float
    ) -> List[Irregularidade]:
        """
        Analisa o risco regulatório e jurídico de uma decisão.

        Args:
            decisao: Descrição da decisão tomada
            responsavel: Responsável pela decisão
            fundamentacao: Fundamentação apresentada
            valor_envolvido: Valor envolvido na decisão

        Returns:
            Lista de irregularidades identificadas
        """
        irregularidades = []
        template = self.templates_irregularidades[TipoIrregularidade.RISCO_REGULATORIO]

        # Verificar se há fundamentação adequada
        if not fundamentacao or len(fundamentacao) < 100:
            irr = Irregularidade(
                id=self._gerar_id_irregularidade(),
                tipo=TipoIrregularidade.FALTA_FUNDAMENTACAO,
                gravidade=GravidadeIrregularidade.ALTA,
                titulo="Decisão sem Fundamentação Adequada",
                descricao=f"""A decisão "{decisao}" foi tomada pelo
                responsável {responsavel} sem fundamentação adequada
                nos autos do processo.

                Decisões administrativas, especialmente as que envolvem
                discricionariedade e valores significativos
                (R$ {valor_envolvido:,.2f}), devem ser motivadas
                expressamente, com demonstração dos fundamentos de fato
                e de direito que as embasam.

                Fundamentação apresentada: "{fundamentacao[:200]}..."
                """,
                fundamentacao_legal=[
                    FundamentacaoLegal(
                        dispositivo="Art. 50",
                        lei="Lei 9.784/1999",
                        texto="""Os atos administrativos deverão ser
                        motivados, com indicação dos fatos e dos
                        fundamentos jurídicos.""",
                        aplicabilidade="Obrigação de motivação"
                    ),
                ] + template["fundamentacao_legal"],
                fundamentacao_tcu=[
                    "Acórdão 1521/2016-Plenário: Fundamentação de decisões",
                ],
                evidencias=[
                    EvidenciaIrregularidade(
                        tipo="processual",
                        descricao="Ausência de fundamentação nos autos",
                        fonte="Análise do processo administrativo",
                    ),
                ],
                impacto="""Nulidade potencial da decisão por vício de
                motivação. Responsabilização do agente público.""",
                recomendacao=f"""INTIMAR o responsável {responsavel} para
                apresentar fundamentação adequada da decisão no prazo
                de 5 dias úteis, sob pena de anulação do ato.""",
                responsaveis=[responsavel],
                penalidades_aplicaveis=[
                    "Anulação do ato",
                    "Responsabilização funcional",
                ],
            )
            irregularidades.append(irr)

        return irregularidades

    def gerar_relatorio_irregularidades(
        self,
        processo: str,
        objeto: str
    ) -> str:
        """
        Gera relatório consolidado das irregularidades identificadas.

        Args:
            processo: Número do processo
            objeto: Objeto da licitação

        Returns:
            Relatório formatado em texto
        """
        relatorio = []
        relatorio.append("=" * 70)
        relatorio.append("RELATÓRIO DE IRREGULARIDADES IDENTIFICADAS")
        relatorio.append("=" * 70)
        relatorio.append(f"\nProcesso: {processo}")
        relatorio.append(f"Objeto: {objeto}")
        relatorio.append(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        relatorio.append(f"Total de Irregularidades: {len(self.irregularidades)}")

        # Classificar por gravidade
        por_gravidade = {}
        for irr in self.irregularidades:
            grav = irr.gravidade.value
            if grav not in por_gravidade:
                por_gravidade[grav] = []
            por_gravidade[grav].append(irr)

        relatorio.append("\n" + "-" * 70)
        relatorio.append("RESUMO POR GRAVIDADE")
        relatorio.append("-" * 70)
        for grav, lista in por_gravidade.items():
            relatorio.append(f"  {grav.upper()}: {len(lista)} ocorrência(s)")

        relatorio.append("\n" + "=" * 70)
        relatorio.append("DETALHAMENTO DAS IRREGULARIDADES")
        relatorio.append("=" * 70)

        ordem_gravidade = ["gravíssima", "alta", "média", "baixa"]
        for grav in ordem_gravidade:
            if grav in por_gravidade:
                relatorio.append(f"\n{'#' * 60}")
                relatorio.append(f"GRAVIDADE: {grav.upper()}")
                relatorio.append(f"{'#' * 60}")

                for irr in por_gravidade[grav]:
                    relatorio.append(f"\n[{irr.id}] {irr.titulo}")
                    relatorio.append("-" * 50)
                    relatorio.append(f"Tipo: {irr.tipo.value}")
                    relatorio.append(f"\nDescrição:\n{irr.descricao}")
                    relatorio.append(f"\nImpacto:\n{irr.impacto}")
                    relatorio.append(f"\nRecomendação:\n{irr.recomendacao}")

                    relatorio.append("\nFundamentação Legal:")
                    for fund in irr.fundamentacao_legal:
                        relatorio.append(f"  - {fund.dispositivo} ({fund.lei})")

                    relatorio.append("\nFundamentação TCU:")
                    for fund in irr.fundamentacao_tcu:
                        relatorio.append(f"  - {fund}")

                    if irr.evidencias:
                        relatorio.append("\nEvidências:")
                        for ev in irr.evidencias:
                            relatorio.append(f"  - [{ev.tipo}] {ev.descricao}")

                    if irr.penalidades_aplicaveis:
                        relatorio.append("\nPenalidades Aplicáveis:")
                        for pen in irr.penalidades_aplicaveis:
                            relatorio.append(f"  - {pen}")

        return "\n".join(relatorio)

    def exportar_json(self) -> str:
        """Exporta irregularidades em formato JSON."""
        dados = {
            "data_geracao": datetime.now().isoformat(),
            "total_irregularidades": len(self.irregularidades),
            "irregularidades": [irr.to_dict() for irr in self.irregularidades]
        }
        return json.dumps(dados, ensure_ascii=False, indent=2)

    def adicionar_irregularidade(self, irregularidade: Irregularidade):
        """Adiciona uma irregularidade à lista."""
        self.irregularidades.append(irregularidade)

    def limpar_irregularidades(self):
        """Limpa a lista de irregularidades."""
        self.irregularidades = []
        self.contador_irregularidades = 0
