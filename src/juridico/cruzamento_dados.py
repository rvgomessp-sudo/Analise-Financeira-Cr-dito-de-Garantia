# -*- coding: utf-8 -*-
"""
Motor de Cruzamento de Dados para Análise Jurídica
===================================================

Este módulo implementa o cruzamento de informações entre:
- Edital do certame
- Lei 14.133/2021
- Manual de Boas Práticas do TCU
- Estudos de rating de seguradoras
- Garantias de execução

Autor: Sistema de Análise Jurídica
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
from datetime import datetime
import json
import sys
import os

# Adicionar path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base_legal import BaseLegal14133, ArtigoLei, CategoriaLegal
from .referencias_tcu import ReferenciasTCU, TemaTCU, Acordao, BoaPratica
from .analisador_irregularidades import (
    AnalisadorIrregularidades, Irregularidade, TipoIrregularidade,
    GravidadeIrregularidade, DocumentoEdital, DadosSeguradora,
    FundamentacaoLegal, EvidenciaIrregularidade
)


class TipoCruzamento(Enum):
    """Tipos de cruzamento de dados."""
    EDITAL_LEI = "edital_vs_lei"
    EDITAL_TCU = "edital_vs_tcu"
    GARANTIA_RATING = "garantia_vs_rating"
    DOCUMENTACAO_HABILITACAO = "documentacao_habilitacao"
    RISCO_DECISAO = "risco_decisao"
    COMPLETO = "analise_completa"


class NivelConformidade(Enum):
    """Níveis de conformidade identificados."""
    CONFORME = "conforme"
    PARCIALMENTE_CONFORME = "parcialmente_conforme"
    NAO_CONFORME = "não_conforme"
    GRAVE_NAO_CONFORMIDADE = "grave_não_conformidade"


@dataclass
class ItemVerificacao:
    """Item de verificação no cruzamento."""
    id: str
    descricao: str
    requisito_legal: str
    situacao_encontrada: str
    conformidade: NivelConformidade
    evidencias: List[str] = field(default_factory=list)
    recomendacoes: List[str] = field(default_factory=list)


@dataclass
class ResultadoCruzamento:
    """Resultado de um cruzamento de dados."""
    tipo: TipoCruzamento
    data_analise: datetime
    processo: str
    objeto: str
    itens_verificados: List[ItemVerificacao]
    irregularidades_encontradas: List[Irregularidade]
    conformidade_geral: NivelConformidade
    score_conformidade: float  # 0-100
    resumo_executivo: str
    recomendacoes_gerais: List[str] = field(default_factory=list)
    observacoes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Converte para dicionário."""
        return {
            "tipo": self.tipo.value,
            "data_analise": self.data_analise.isoformat(),
            "processo": self.processo,
            "objeto": self.objeto,
            "conformidade_geral": self.conformidade_geral.value,
            "score_conformidade": self.score_conformidade,
            "resumo_executivo": self.resumo_executivo,
            "total_itens_verificados": len(self.itens_verificados),
            "total_irregularidades": len(self.irregularidades_encontradas),
            "recomendacoes_gerais": self.recomendacoes_gerais,
        }


@dataclass
class DadosEdital:
    """Dados extraídos do edital para análise."""
    numero: str
    processo: str
    objeto: str
    valor_estimado: float
    modalidade: str
    orgao: str
    setor: str = ""
    data_abertura: Optional[datetime] = None
    criterio_julgamento: str = "menor_preco"
    prazo_execucao: int = 0  # dias
    garantia_exigida: bool = False
    percentual_garantia: float = 0.0
    modalidade_garantia: str = ""
    documentos_habilitacao: List[DocumentoEdital] = field(default_factory=list)
    exigencias_qualificacao: List[str] = field(default_factory=list)
    seguradoras_propostas: List[DadosSeguradora] = field(default_factory=list)
    clausulas_relevantes: Dict[str, str] = field(default_factory=dict)


@dataclass
class DadosRating:
    """Dados de rating de seguradoras do estudo."""
    seguradoras: List[DadosSeguradora]
    data_estudo: datetime
    fonte: str
    metodologia: str = ""
    ranking_recomendado: List[str] = field(default_factory=list)
    observacoes: List[str] = field(default_factory=list)


class MotorCruzamento:
    """
    Motor de cruzamento de dados para análise jurídica de licitações.

    Realiza cruzamentos entre:
    - Edital x Lei 14.133/2021
    - Edital x Orientações do TCU
    - Garantias x Estudos de Rating
    - Documentação x Requisitos de Habilitação
    """

    def __init__(self):
        self.base_legal = BaseLegal14133()
        self.referencias_tcu = ReferenciasTCU()
        self.analisador = AnalisadorIrregularidades()
        self.resultados: List[ResultadoCruzamento] = []

    def cruzar_edital_lei(
        self,
        dados_edital: DadosEdital
    ) -> ResultadoCruzamento:
        """
        Cruza dados do edital com a Lei 14.133/2021.

        Args:
            dados_edital: Dados extraídos do edital

        Returns:
            Resultado do cruzamento
        """
        itens = []
        irregularidades = []

        # Verificação 1: Garantia de execução
        artigo_96 = self.base_legal.get_artigo(96)
        artigo_97 = self.base_legal.get_artigo(97)

        if dados_edital.valor_estimado > 200_000_000:  # Grande vulto
            # Verificar se exige garantia de até 30%
            item_garantia = ItemVerificacao(
                id="VER-001",
                descricao="Exigência de garantia para contratação de grande vulto",
                requisito_legal=f"Art. 97, §1º: Garantia de até 30% em contratações de grande vulto",
                situacao_encontrada=f"Garantia exigida: {dados_edital.garantia_exigida}, "
                                   f"Percentual: {dados_edital.percentual_garantia}%",
                conformidade=NivelConformidade.CONFORME
                if dados_edital.garantia_exigida and dados_edital.percentual_garantia >= 5
                else NivelConformidade.NAO_CONFORME,
            )

            if not dados_edital.garantia_exigida:
                item_garantia.conformidade = NivelConformidade.GRAVE_NAO_CONFORMIDADE
                item_garantia.recomendacoes.append(
                    "Exigir garantia de execução de no mínimo 5%, podendo chegar a 30%"
                )

            itens.append(item_garantia)

        # Verificação 2: Documentos de habilitação
        artigo_63 = self.base_legal.get_artigo(63)
        docs_obrigatorios = [
            "habilitação jurídica", "regularidade fiscal",
            "regularidade trabalhista", "qualificação técnica"
        ]

        docs_exigidos_nomes = [d.nome.lower() for d in dados_edital.documentos_habilitacao]
        docs_faltantes = []

        for doc in docs_obrigatorios:
            if not any(doc in nome for nome in docs_exigidos_nomes):
                docs_faltantes.append(doc)

        item_docs = ItemVerificacao(
            id="VER-002",
            descricao="Exigência de documentos obrigatórios de habilitação",
            requisito_legal="Art. 63: Documentos de habilitação jurídica, "
                           "regularidade fiscal, social e trabalhista",
            situacao_encontrada=f"Documentos exigidos: {len(dados_edital.documentos_habilitacao)}. "
                               f"Categorias cobertas.",
            conformidade=NivelConformidade.CONFORME
            if not docs_faltantes else NivelConformidade.PARCIALMENTE_CONFORME,
        )

        if docs_faltantes:
            item_docs.recomendacoes.append(
                f"Incluir exigência de: {', '.join(docs_faltantes)}"
            )

        itens.append(item_docs)

        # Verificação 3: Qualificação econômico-financeira
        artigo_67 = self.base_legal.get_artigo(67)

        exige_balanco = any(
            "balanço" in e.lower() or "demonstraç" in e.lower()
            for e in dados_edital.exigencias_qualificacao
        )

        item_qef = ItemVerificacao(
            id="VER-003",
            descricao="Qualificação econômico-financeira",
            requisito_legal="Art. 67: Balanço patrimonial e demonstrações contábeis",
            situacao_encontrada=f"Exige balanço: {exige_balanco}",
            conformidade=NivelConformidade.CONFORME if exige_balanco
            else NivelConformidade.PARCIALMENTE_CONFORME,
        )

        if not exige_balanco:
            item_qef.recomendacoes.append(
                "Exigir balanço patrimonial e demonstrações contábeis"
            )

        itens.append(item_qef)

        # Verificação 4: Critério de julgamento adequado
        artigo_25 = self.base_legal.get_artigo(25)

        criterios_validos = ["menor_preco", "maior_desconto", "tecnica_preco", "melhor_tecnica"]
        criterio_ok = dados_edital.criterio_julgamento.lower().replace(" ", "_") in criterios_validos

        item_criterio = ItemVerificacao(
            id="VER-004",
            descricao="Critério de julgamento das propostas",
            requisito_legal="Art. 25: Menor preço, maior desconto, técnica e preço, etc.",
            situacao_encontrada=f"Critério utilizado: {dados_edital.criterio_julgamento}",
            conformidade=NivelConformidade.CONFORME if criterio_ok
            else NivelConformidade.NAO_CONFORME,
        )

        itens.append(item_criterio)

        # Calcular conformidade geral
        conformes = sum(1 for i in itens if i.conformidade == NivelConformidade.CONFORME)
        parciais = sum(1 for i in itens if i.conformidade == NivelConformidade.PARCIALMENTE_CONFORME)
        nao_conformes = sum(1 for i in itens if i.conformidade == NivelConformidade.NAO_CONFORME)
        graves = sum(1 for i in itens if i.conformidade == NivelConformidade.GRAVE_NAO_CONFORMIDADE)

        score = (conformes * 100 + parciais * 50) / len(itens) if itens else 0

        if graves > 0:
            conformidade_geral = NivelConformidade.GRAVE_NAO_CONFORMIDADE
        elif nao_conformes > 0:
            conformidade_geral = NivelConformidade.NAO_CONFORME
        elif parciais > 0:
            conformidade_geral = NivelConformidade.PARCIALMENTE_CONFORME
        else:
            conformidade_geral = NivelConformidade.CONFORME

        resultado = ResultadoCruzamento(
            tipo=TipoCruzamento.EDITAL_LEI,
            data_analise=datetime.now(),
            processo=dados_edital.processo,
            objeto=dados_edital.objeto,
            itens_verificados=itens,
            irregularidades_encontradas=irregularidades,
            conformidade_geral=conformidade_geral,
            score_conformidade=score,
            resumo_executivo=f"Análise de conformidade do edital {dados_edital.numero} "
                            f"com a Lei 14.133/2021. Score: {score:.1f}%",
            recomendacoes_gerais=[
                rec for item in itens for rec in item.recomendacoes
            ],
        )

        self.resultados.append(resultado)
        return resultado

    def cruzar_garantia_rating(
        self,
        dados_edital: DadosEdital,
        dados_rating: DadosRating
    ) -> ResultadoCruzamento:
        """
        Cruza dados de garantia com estudos de rating.

        Args:
            dados_edital: Dados do edital
            dados_rating: Dados do estudo de rating

        Returns:
            Resultado do cruzamento
        """
        itens = []
        irregularidades = []

        # Mapear seguradoras do estudo para as propostas
        seguradoras_mapeadas = {}
        for seg_proposta in dados_edital.seguradoras_propostas:
            for seg_estudo in dados_rating.seguradoras:
                if (seg_proposta.nome.lower() in seg_estudo.nome.lower() or
                    seg_estudo.nome.lower() in seg_proposta.nome.lower()):
                    seguradoras_mapeadas[seg_proposta.nome] = seg_estudo

        # Verificação 1: Existência de estudo de rating
        item_estudo = ItemVerificacao(
            id="GAR-001",
            descricao="Existência de estudo de rating para análise de seguradoras",
            requisito_legal="TCU Acórdão 3089/2020: Verificação de rating recomendada",
            situacao_encontrada=f"Estudo de rating disponível: {dados_rating.fonte}",
            conformidade=NivelConformidade.CONFORME,
            evidencias=[f"Estudo datado de {dados_rating.data_estudo.strftime('%d/%m/%Y')}"],
        )
        itens.append(item_estudo)

        # Verificação 2: Análise da seguradora selecionada
        selecionada = next(
            (s for s in dados_edital.seguradoras_propostas if s.selecionada),
            None
        )

        if selecionada:
            # Buscar rating do estudo
            seg_estudo = seguradoras_mapeadas.get(selecionada.nome)

            if seg_estudo:
                melhor_rating = seg_estudo.rating_sp or seg_estudo.rating_moodys or \
                               seg_estudo.rating_fitch or seg_estudo.rating_am_best

                rating_scores = {
                    "AAA": 100, "AA+": 95, "AA": 90, "AA-": 85,
                    "A+": 80, "A": 75, "A-": 70,
                    "BBB+": 65, "BBB": 60, "BBB-": 55,
                    "BB+": 50, "BB": 45, "BB-": 40,
                    "B+": 35, "B": 30, "B-": 25,
                }

                score_rating = rating_scores.get(melhor_rating, 0)

                conformidade_rating = (
                    NivelConformidade.CONFORME if score_rating >= 70 else
                    NivelConformidade.PARCIALMENTE_CONFORME if score_rating >= 55 else
                    NivelConformidade.NAO_CONFORME if score_rating >= 40 else
                    NivelConformidade.GRAVE_NAO_CONFORMIDADE
                )

                item_rating = ItemVerificacao(
                    id="GAR-002",
                    descricao="Rating da seguradora selecionada",
                    requisito_legal="TCU: Rating mínimo de grau de investimento (BBB-)",
                    situacao_encontrada=f"Seguradora: {selecionada.nome}, Rating: {melhor_rating}",
                    conformidade=conformidade_rating,
                    evidencias=[
                        f"Rating S&P: {seg_estudo.rating_sp}",
                        f"Rating Moody's: {seg_estudo.rating_moodys}",
                        f"Rating Fitch: {seg_estudo.rating_fitch}",
                    ],
                )

                if score_rating < 55:
                    item_rating.recomendacoes.append(
                        "Exigir substituição por seguradora com rating de grau de investimento"
                    )

                itens.append(item_rating)

        # Verificação 3: Comparação com seguradoras preteridas
        melhores_ratings = []
        for seg in dados_edital.seguradoras_propostas:
            if seg.selecionada:
                continue

            seg_estudo = seguradoras_mapeadas.get(seg.nome)
            if seg_estudo:
                rating = seg_estudo.rating_sp or seg_estudo.rating_moodys
                if rating:
                    melhores_ratings.append((seg.nome, rating))

        if melhores_ratings and selecionada:
            seg_estudo_selecionada = seguradoras_mapeadas.get(selecionada.nome)
            rating_selecionada = None
            if seg_estudo_selecionada:
                rating_selecionada = seg_estudo_selecionada.rating_sp or \
                                    seg_estudo_selecionada.rating_moodys

            # Verificar se alguma preterida tem rating melhor
            for nome, rating in melhores_ratings:
                score_preterida = rating_scores.get(rating, 0)
                score_selecionada = rating_scores.get(rating_selecionada, 0)

                if score_preterida > score_selecionada + 10:
                    # Gerar irregularidade
                    irrs = self.analisador.analisar_selecao_garantia(
                        dados_edital.seguradoras_propostas,
                        dados_edital.valor_estimado,
                        dados_edital.criterio_julgamento
                    )
                    irregularidades.extend(irrs)

                    item_preterida = ItemVerificacao(
                        id=f"GAR-003",
                        descricao="Análise de seguradoras preteridas",
                        requisito_legal="TCU Acórdão 2891/2021: Vedação ao descarte "
                                       "de melhor rating por custo",
                        situacao_encontrada=f"Seguradora {nome} com rating {rating} foi "
                                           f"preterida em favor de {selecionada.nome}",
                        conformidade=NivelConformidade.GRAVE_NAO_CONFORMIDADE,
                        evidencias=[
                            f"Rating preterida: {rating}",
                            f"Rating selecionada: {rating_selecionada}",
                        ],
                        recomendacoes=[
                            f"Reconsiderar proposta de {nome}",
                            "Fundamentar adequadamente a escolha",
                        ],
                    )
                    itens.append(item_preterida)
                    break

        # Verificação 4: Conformidade com ranking recomendado
        if dados_rating.ranking_recomendado and selecionada:
            posicao = None
            for i, nome in enumerate(dados_rating.ranking_recomendado):
                if selecionada.nome.lower() in nome.lower():
                    posicao = i + 1
                    break

            if posicao:
                conformidade_ranking = (
                    NivelConformidade.CONFORME if posicao <= 2 else
                    NivelConformidade.PARCIALMENTE_CONFORME if posicao <= 4 else
                    NivelConformidade.NAO_CONFORME
                )

                item_ranking = ItemVerificacao(
                    id="GAR-004",
                    descricao="Posição no ranking recomendado pelo estudo",
                    requisito_legal="Estudo técnico de rating: Ranking de solidez",
                    situacao_encontrada=f"Seguradora selecionada ocupa {posicao}ª posição",
                    conformidade=conformidade_ranking,
                )

                if posicao > 2:
                    item_ranking.recomendacoes.append(
                        f"Considerar seguradoras melhor posicionadas: "
                        f"{', '.join(dados_rating.ranking_recomendado[:2])}"
                    )

                itens.append(item_ranking)

        # Calcular score
        conformes = sum(1 for i in itens if i.conformidade == NivelConformidade.CONFORME)
        score = (conformes * 100) / len(itens) if itens else 0

        # Determinar conformidade geral
        graves = any(i.conformidade == NivelConformidade.GRAVE_NAO_CONFORMIDADE for i in itens)
        nao_conformes = any(i.conformidade == NivelConformidade.NAO_CONFORME for i in itens)

        if graves:
            conformidade_geral = NivelConformidade.GRAVE_NAO_CONFORMIDADE
        elif nao_conformes:
            conformidade_geral = NivelConformidade.NAO_CONFORME
        elif any(i.conformidade == NivelConformidade.PARCIALMENTE_CONFORME for i in itens):
            conformidade_geral = NivelConformidade.PARCIALMENTE_CONFORME
        else:
            conformidade_geral = NivelConformidade.CONFORME

        resultado = ResultadoCruzamento(
            tipo=TipoCruzamento.GARANTIA_RATING,
            data_analise=datetime.now(),
            processo=dados_edital.processo,
            objeto=dados_edital.objeto,
            itens_verificados=itens,
            irregularidades_encontradas=irregularidades,
            conformidade_geral=conformidade_geral,
            score_conformidade=score,
            resumo_executivo=f"Cruzamento garantia x rating. "
                            f"Identificadas {len(irregularidades)} irregularidades. "
                            f"Score: {score:.1f}%",
            recomendacoes_gerais=[
                rec for item in itens for rec in item.recomendacoes
            ],
        )

        # Adicionar irregularidades ao analisador
        for irr in irregularidades:
            self.analisador.adicionar_irregularidade(irr)

        self.resultados.append(resultado)
        return resultado

    def cruzar_documentacao_habilitacao(
        self,
        dados_edital: DadosEdital,
        documentos_apresentados: Dict[str, List[DocumentoEdital]]
    ) -> ResultadoCruzamento:
        """
        Cruza documentação exigida com documentos apresentados.

        Args:
            dados_edital: Dados do edital
            documentos_apresentados: Dict de licitante -> documentos

        Returns:
            Resultado do cruzamento
        """
        itens = []
        irregularidades = []

        for licitante, docs in documentos_apresentados.items():
            # Verificar omissões
            docs_omitidos = [
                doc for doc in dados_edital.documentos_habilitacao
                if doc.obrigatorio and doc.nome not in [d.nome for d in docs]
            ]

            if docs_omitidos:
                # Gerar irregularidade por omissão
                irrs = self.analisador.analisar_omissao_documental(
                    dados_edital.documentos_habilitacao,
                    licitante
                )
                irregularidades.extend(irrs)

                item_omissao = ItemVerificacao(
                    id=f"HAB-{licitante[:3].upper()}",
                    descricao=f"Análise documental - {licitante}",
                    requisito_legal="Art. 63 e 155, IV da Lei 14.133/2021",
                    situacao_encontrada=f"Omitidos {len(docs_omitidos)} documentos obrigatórios",
                    conformidade=NivelConformidade.NAO_CONFORME,
                    evidencias=[f"Documento faltante: {d.nome}" for d in docs_omitidos],
                    recomendacoes=[
                        f"INABILITAR o licitante {licitante}",
                        "Registrar a omissão em ata",
                    ],
                )
                itens.append(item_omissao)
            else:
                item_ok = ItemVerificacao(
                    id=f"HAB-{licitante[:3].upper()}",
                    descricao=f"Análise documental - {licitante}",
                    requisito_legal="Art. 63 da Lei 14.133/2021",
                    situacao_encontrada="Todos os documentos obrigatórios apresentados",
                    conformidade=NivelConformidade.CONFORME,
                )
                itens.append(item_ok)

        # Calcular score
        conformes = sum(1 for i in itens if i.conformidade == NivelConformidade.CONFORME)
        score = (conformes * 100) / len(itens) if itens else 0

        resultado = ResultadoCruzamento(
            tipo=TipoCruzamento.DOCUMENTACAO_HABILITACAO,
            data_analise=datetime.now(),
            processo=dados_edital.processo,
            objeto=dados_edital.objeto,
            itens_verificados=itens,
            irregularidades_encontradas=irregularidades,
            conformidade_geral=(
                NivelConformidade.CONFORME if not irregularidades
                else NivelConformidade.NAO_CONFORME
            ),
            score_conformidade=score,
            resumo_executivo=f"Análise de habilitação: {len(itens)} licitantes, "
                            f"{len(irregularidades)} com omissões documentais.",
        )

        for irr in irregularidades:
            self.analisador.adicionar_irregularidade(irr)

        self.resultados.append(resultado)
        return resultado

    def executar_analise_completa(
        self,
        dados_edital: DadosEdital,
        dados_rating: Optional[DadosRating] = None,
        documentos_licitantes: Optional[Dict[str, List[DocumentoEdital]]] = None
    ) -> ResultadoCruzamento:
        """
        Executa análise completa do certame.

        Args:
            dados_edital: Dados do edital
            dados_rating: Dados de rating (opcional)
            documentos_licitantes: Documentos por licitante (opcional)

        Returns:
            Resultado consolidado
        """
        self.analisador.limpar_irregularidades()
        todos_itens = []
        todas_irregularidades = []
        recomendacoes = []

        # 1. Cruzamento Edital x Lei
        resultado_lei = self.cruzar_edital_lei(dados_edital)
        todos_itens.extend(resultado_lei.itens_verificados)
        todas_irregularidades.extend(resultado_lei.irregularidades_encontradas)
        recomendacoes.extend(resultado_lei.recomendacoes_gerais)

        # 2. Cruzamento Garantia x Rating
        if dados_rating:
            resultado_rating = self.cruzar_garantia_rating(dados_edital, dados_rating)
            todos_itens.extend(resultado_rating.itens_verificados)
            todas_irregularidades.extend(resultado_rating.irregularidades_encontradas)
            recomendacoes.extend(resultado_rating.recomendacoes_gerais)

        # 3. Cruzamento Documentação
        if documentos_licitantes:
            resultado_docs = self.cruzar_documentacao_habilitacao(
                dados_edital, documentos_licitantes
            )
            todos_itens.extend(resultado_docs.itens_verificados)
            todas_irregularidades.extend(resultado_docs.irregularidades_encontradas)
            recomendacoes.extend(resultado_docs.recomendacoes_gerais)

        # Consolidar irregularidades do analisador
        todas_irregularidades = self.analisador.irregularidades

        # Calcular conformidade geral
        conformes = sum(1 for i in todos_itens if i.conformidade == NivelConformidade.CONFORME)
        score = (conformes * 100) / len(todos_itens) if todos_itens else 0

        if any(i.conformidade == NivelConformidade.GRAVE_NAO_CONFORMIDADE for i in todos_itens):
            conformidade_geral = NivelConformidade.GRAVE_NAO_CONFORMIDADE
        elif any(i.conformidade == NivelConformidade.NAO_CONFORME for i in todos_itens):
            conformidade_geral = NivelConformidade.NAO_CONFORME
        elif any(i.conformidade == NivelConformidade.PARCIALMENTE_CONFORME for i in todos_itens):
            conformidade_geral = NivelConformidade.PARCIALMENTE_CONFORME
        else:
            conformidade_geral = NivelConformidade.CONFORME

        # Gerar resumo executivo
        resumo = f"""
ANÁLISE COMPLETA DO CERTAME {dados_edital.numero}
{'=' * 50}

Processo: {dados_edital.processo}
Objeto: {dados_edital.objeto}
Valor Estimado: R$ {dados_edital.valor_estimado:,.2f}
Órgão: {dados_edital.orgao}

RESULTADO DA ANÁLISE:
- Itens Verificados: {len(todos_itens)}
- Irregularidades Identificadas: {len(todas_irregularidades)}
- Score de Conformidade: {score:.1f}%
- Conformidade Geral: {conformidade_geral.value.upper()}

CLASSIFICAÇÃO DAS IRREGULARIDADES:
- Gravíssimas: {sum(1 for i in todas_irregularidades if i.gravidade == GravidadeIrregularidade.GRAVISSIMA)}
- Altas: {sum(1 for i in todas_irregularidades if i.gravidade == GravidadeIrregularidade.ALTA)}
- Médias: {sum(1 for i in todas_irregularidades if i.gravidade == GravidadeIrregularidade.MEDIA)}
- Baixas: {sum(1 for i in todas_irregularidades if i.gravidade == GravidadeIrregularidade.BAIXA)}
"""

        resultado_final = ResultadoCruzamento(
            tipo=TipoCruzamento.COMPLETO,
            data_analise=datetime.now(),
            processo=dados_edital.processo,
            objeto=dados_edital.objeto,
            itens_verificados=todos_itens,
            irregularidades_encontradas=todas_irregularidades,
            conformidade_geral=conformidade_geral,
            score_conformidade=score,
            resumo_executivo=resumo,
            recomendacoes_gerais=list(set(recomendacoes)),
        )

        return resultado_final

    def gerar_relatorio_cruzamento(
        self,
        resultado: ResultadoCruzamento
    ) -> str:
        """
        Gera relatório formatado do cruzamento.

        Args:
            resultado: Resultado do cruzamento

        Returns:
            Relatório em texto
        """
        linhas = []
        linhas.append("=" * 70)
        linhas.append("RELATÓRIO DE CRUZAMENTO DE DADOS")
        linhas.append("=" * 70)
        linhas.append(f"\nTipo: {resultado.tipo.value}")
        linhas.append(f"Data: {resultado.data_analise.strftime('%d/%m/%Y %H:%M')}")
        linhas.append(f"Processo: {resultado.processo}")
        linhas.append(f"Objeto: {resultado.objeto}")
        linhas.append(f"\nConformidade Geral: {resultado.conformidade_geral.value.upper()}")
        linhas.append(f"Score: {resultado.score_conformidade:.1f}%")

        linhas.append("\n" + "-" * 70)
        linhas.append("ITENS VERIFICADOS")
        linhas.append("-" * 70)

        for item in resultado.itens_verificados:
            linhas.append(f"\n[{item.id}] {item.descricao}")
            linhas.append(f"  Requisito: {item.requisito_legal}")
            linhas.append(f"  Situação: {item.situacao_encontrada}")
            linhas.append(f"  Conformidade: {item.conformidade.value}")
            if item.recomendacoes:
                linhas.append("  Recomendações:")
                for rec in item.recomendacoes:
                    linhas.append(f"    - {rec}")

        if resultado.irregularidades_encontradas:
            linhas.append("\n" + "=" * 70)
            linhas.append("IRREGULARIDADES IDENTIFICADAS")
            linhas.append("=" * 70)

            for irr in resultado.irregularidades_encontradas:
                linhas.append(f"\n[{irr.id}] {irr.titulo}")
                linhas.append(f"  Gravidade: {irr.gravidade.value.upper()}")
                linhas.append(f"  Tipo: {irr.tipo.value}")

        if resultado.recomendacoes_gerais:
            linhas.append("\n" + "-" * 70)
            linhas.append("RECOMENDAÇÕES GERAIS")
            linhas.append("-" * 70)
            for rec in resultado.recomendacoes_gerais:
                linhas.append(f"  - {rec}")

        return "\n".join(linhas)

    def exportar_resultados_json(self) -> str:
        """Exporta todos os resultados em JSON."""
        dados = {
            "data_exportacao": datetime.now().isoformat(),
            "total_analises": len(self.resultados),
            "resultados": [r.to_dict() for r in self.resultados]
        }
        return json.dumps(dados, ensure_ascii=False, indent=2)
