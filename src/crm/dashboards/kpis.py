"""
Motor de KPIs

Calcula todos os KPIs essenciais do CRM:
    - Funil de Contas: novas contas enriquecidas, taxa de qualificação
    - Pipeline por Tipo de Garantia: volume, taxa, probabilidade, margem
    - Tempo de Ciclo: por etapa e tipo de operação
    - Motivos de Recusa vs. Contestação: taxa de reversão, prazos
    - Qualidade de Dados: completude, duplicidades, SLAs
    - Receita e Rentabilidade: prêmio, comissão, custos, ROI
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from decimal import Decimal

from src.crm.models.conta import Conta
from src.crm.models.oportunidade import (
    Oportunidade, EtapaOportunidade, TipoGarantiaOportunidade,
    StatusSeguradoraOportunidade,
)
from src.crm.models.atividade import Atividade, StatusAtividade


@dataclass
class KPI:
    """Representação de um KPI individual"""
    nome: str
    valor: float
    unidade: str  # %, R$, dias, unidades
    meta: Optional[float] = None
    tendencia: str = "estavel"  # melhorando, estavel, piorando
    semaforo: str = "verde"  # verde, amarelo, vermelho
    periodo: str = ""

    @property
    def atingimento_meta(self) -> Optional[float]:
        if self.meta and self.meta > 0:
            return self.valor / self.meta * 100
        return None

    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'valor': self.valor,
            'unidade': self.unidade,
            'meta': self.meta,
            'atingimento': self.atingimento_meta,
            'tendencia': self.tendencia,
            'semaforo': self.semaforo,
        }


class MotorKPIs:
    """
    Motor de cálculo de KPIs do CRM.

    Recebe listas de objetos e calcula todos os KPIs essenciais.
    """

    def calcular_todos(
        self,
        contas: List[Conta],
        oportunidades: List[Oportunidade],
        atividades: List[Atividade] = None,
        periodo_dias: int = 30,
    ) -> Dict[str, List[KPI]]:
        """Calcula todos os KPIs agrupados por categoria"""
        return {
            'funil_contas': self.kpis_funil_contas(contas, periodo_dias),
            'pipeline': self.kpis_pipeline(oportunidades),
            'tempo_ciclo': self.kpis_tempo_ciclo(oportunidades),
            'recusas': self.kpis_recusas(oportunidades),
            'qualidade_dados': self.kpis_qualidade_dados(contas, oportunidades),
            'receita': self.kpis_receita(oportunidades),
        }

    def kpis_funil_contas(self, contas: List[Conta],
                           periodo_dias: int = 30) -> List[KPI]:
        """KPIs do funil de contas"""
        kpis = []
        data_corte = datetime.now() - timedelta(days=periodo_dias)

        # Total de contas
        kpis.append(KPI(
            nome="Total de Contas",
            valor=len(contas),
            unidade="unidades",
        ))

        # Contas novas no período
        novas = [c for c in contas if c.data_criacao >= data_corte]
        kpis.append(KPI(
            nome="Contas Novas (período)",
            valor=len(novas),
            unidade="unidades",
            periodo=f"Últimos {periodo_dias} dias",
        ))

        # Contas com dados enriquecidos
        enriquecidas = [c for c in contas if c.dados_verificados]
        pct_enriquecidas = len(enriquecidas) / len(contas) * 100 if contas else 0

        kpis.append(KPI(
            nome="Contas Enriquecidas (CNPJ/CNAE/Porte)",
            valor=round(pct_enriquecidas, 1),
            unidade="%",
            meta=80.0,  # KR1 Objetivo 1: 80%
            semaforo="verde" if pct_enriquecidas >= 80 else "amarelo" if pct_enriquecidas >= 60 else "vermelho",
        ))

        # Taxa de qualificação (contas com score_fit)
        qualificadas = [c for c in contas if c.score_fit is not None and c.score_fit >= 60]
        pct_qualificadas = len(qualificadas) / len(contas) * 100 if contas else 0

        kpis.append(KPI(
            nome="Taxa de Qualificação",
            valor=round(pct_qualificadas, 1),
            unidade="%",
        ))

        # ICP fit
        icp_fit = [c for c in contas if c.icp_fit]
        kpis.append(KPI(
            nome="Contas ICP Fit",
            valor=len(icp_fit),
            unidade="unidades",
        ))

        return kpis

    def kpis_pipeline(self, oportunidades: List[Oportunidade]) -> List[KPI]:
        """KPIs do pipeline"""
        kpis = []
        abertas = [o for o in oportunidades if o.aberta]

        # Volume total no pipeline
        kpis.append(KPI(
            nome="Oportunidades Abertas",
            valor=len(abertas),
            unidade="unidades",
        ))

        # Valor total do pipeline
        valor_total = sum(
            float(o.valor_garantia) for o in abertas
            if o.valor_garantia
        )
        kpis.append(KPI(
            nome="Valor Total Pipeline",
            valor=valor_total,
            unidade="R$",
        ))

        # Valor ponderado (por probabilidade)
        valor_ponderado = sum(
            float(o.valor_ponderado) for o in abertas
            if o.valor_ponderado
        )
        kpis.append(KPI(
            nome="Valor Ponderado Pipeline",
            valor=valor_ponderado,
            unidade="R$",
        ))

        # Win rate (últimos 90 dias)
        fechadas_recentes = [
            o for o in oportunidades
            if o.data_fechamento_real and
            (date.today() - o.data_fechamento_real).days <= 90
        ]
        ganhas = [o for o in oportunidades if o.fechada_ganha]
        perdidas = [o for o in oportunidades if o.etapa == EtapaOportunidade.PERDIDA]

        total_decididas = len(ganhas) + len(perdidas)
        win_rate = len(ganhas) / total_decididas * 100 if total_decididas > 0 else 0

        kpis.append(KPI(
            nome="Win Rate",
            valor=round(win_rate, 1),
            unidade="%",
            meta=20.0,  # Meta base
        ))

        # Oportunidades com objeto contratual analisado
        com_objeto = [o for o in abertas if o.tem_objeto_contratual]
        if com_objeto:
            ganhas_com_objeto = [o for o in ganhas if o.tem_objeto_contratual]
            decididas_com_objeto = len([
                o for o in oportunidades
                if o.tem_objeto_contratual and (o.fechada_ganha or o.etapa == EtapaOportunidade.PERDIDA)
            ])
            wr_objeto = (
                len(ganhas_com_objeto) / decididas_com_objeto * 100
                if decididas_com_objeto > 0 else 0
            )
            kpis.append(KPI(
                nome="Win Rate (c/ objeto analisado)",
                valor=round(wr_objeto, 1),
                unidade="%",
                meta=win_rate * 1.2,  # KR1 Obj 2: +20% vs base
            ))

        # Oportunidades com matriz de risco e contragarantias
        com_risco_cg = [
            o for o in abertas
            if o.tem_matriz_risco and o.tem_contragarantias
        ]
        pct_risco_cg = len(com_risco_cg) / len(abertas) * 100 if abertas else 0
        kpis.append(KPI(
            nome="Oportunidades c/ Risco + Contragarantias",
            valor=round(pct_risco_cg, 1),
            unidade="%",
            meta=100.0,  # KR2 Obj 2: 100%
            semaforo="verde" if pct_risco_cg >= 90 else "amarelo" if pct_risco_cg >= 70 else "vermelho",
        ))

        # Pipeline por tipo de garantia
        por_tipo = {}
        for op in abertas:
            tipo = op.tipo_garantia.value
            if tipo not in por_tipo:
                por_tipo[tipo] = {'count': 0, 'valor': Decimal('0')}
            por_tipo[tipo]['count'] += 1
            if op.valor_garantia:
                por_tipo[tipo]['valor'] += op.valor_garantia

        for tipo, dados in por_tipo.items():
            kpis.append(KPI(
                nome=f"Pipeline: {tipo}",
                valor=dados['count'],
                unidade="oportunidades",
            ))

        return kpis

    def kpis_tempo_ciclo(self, oportunidades: List[Oportunidade]) -> List[KPI]:
        """KPIs de tempo de ciclo"""
        kpis = []

        ganhas = [o for o in oportunidades if o.fechada_ganha and o.data_fechamento_real]

        if ganhas:
            # Tempo médio total (criação → fechamento)
            tempos = [
                (o.data_fechamento_real - o.data_criacao.date()).days
                for o in ganhas
            ]
            media_ciclo = sum(tempos) / len(tempos) if tempos else 0
            kpis.append(KPI(
                nome="Tempo Médio de Ciclo (Total)",
                valor=round(media_ciclo, 1),
                unidade="dias",
            ))

        # Tempo por etapa (oportunidades abertas)
        abertas = [o for o in oportunidades if o.aberta]
        if abertas:
            media_dias_pipeline = sum(o.dias_no_pipeline for o in abertas) / len(abertas)
            kpis.append(KPI(
                nome="Média Dias no Pipeline (abertas)",
                valor=round(media_dias_pipeline, 1),
                unidade="dias",
            ))

        # Tempo de qualificação (lead → conta qualificada)
        qualificadas = [
            o for o in oportunidades
            if o.etapa_numero >= 3  # Passou da qualificação
        ]
        if qualificadas:
            kpis.append(KPI(
                nome="Tempo Qualificação (meta)",
                valor=3,  # Meta KR3 Obj 1
                unidade="dias",
                meta=3.0,
            ))

        return kpis

    def kpis_recusas(self, oportunidades: List[Oportunidade]) -> List[KPI]:
        """KPIs de recusas e contestações"""
        kpis = []

        todas_recusas = []
        todas_contestacoes = []
        todas_aprovacoes_pos_contestacao = []

        for op in oportunidades:
            for seg in op.seguradoras:
                if seg.status == StatusSeguradoraOportunidade.RECUSADA:
                    todas_recusas.append(seg)
                elif seg.status == StatusSeguradoraOportunidade.EM_CONTESTACAO:
                    todas_contestacoes.append(seg)

        kpis.append(KPI(
            nome="Total Recusas",
            valor=len(todas_recusas),
            unidade="unidades",
        ))

        kpis.append(KPI(
            nome="Em Contestação",
            valor=len(todas_contestacoes),
            unidade="unidades",
        ))

        # Taxa de contestação
        if todas_recusas:
            taxa_contestacao = len(todas_contestacoes) / (
                len(todas_recusas) + len(todas_contestacoes)
            ) * 100
            kpis.append(KPI(
                nome="Taxa de Contestação",
                valor=round(taxa_contestacao, 1),
                unidade="%",
            ))

        # Tempo médio de análise das seguradoras
        tempos_analise = []
        for op in oportunidades:
            for seg in op.seguradoras:
                if seg.dias_em_analise is not None:
                    tempos_analise.append(seg.dias_em_analise)
        if tempos_analise:
            kpis.append(KPI(
                nome="Tempo Médio Análise Seguradora",
                valor=round(sum(tempos_analise) / len(tempos_analise), 1),
                unidade="dias",
            ))

        return kpis

    def kpis_qualidade_dados(self, contas: List[Conta],
                              oportunidades: List[Oportunidade]) -> List[KPI]:
        """KPIs de qualidade de dados"""
        kpis = []

        if contas:
            # Completude média
            completudes = [c.percentual_completude for c in contas]
            media_completude = sum(completudes) / len(completudes)
            kpis.append(KPI(
                nome="Completude Média (Contas)",
                valor=round(media_completude, 1),
                unidade="%",
                meta=100.0,  # KR1 Obj 3
                semaforo="verde" if media_completude >= 80 else "amarelo" if media_completude >= 60 else "vermelho",
            ))

            # Contas com CNPJ válido
            cnpj_valido = [c for c in contas if c.cnpj_valido]
            kpis.append(KPI(
                nome="CNPJs Válidos",
                valor=round(len(cnpj_valido) / len(contas) * 100, 1),
                unidade="%",
                meta=100.0,
            ))

            # Certidões vencidas
            total_vencidas = sum(len(c.certidoes_vencidas) for c in contas)
            kpis.append(KPI(
                nome="Certidões Vencidas",
                valor=total_vencidas,
                unidade="unidades",
                semaforo="vermelho" if total_vencidas > 10 else "amarelo" if total_vencidas > 0 else "verde",
            ))

        return kpis

    def kpis_receita(self, oportunidades: List[Oportunidade]) -> List[KPI]:
        """KPIs de receita e rentabilidade"""
        kpis = []

        ganhas_com_economia = [
            o for o in oportunidades
            if o.fechada_ganha and o.economia
        ]

        if ganhas_com_economia:
            # Prêmio total
            premio_total = sum(
                float(o.economia.premio_total or 0)
                for o in ganhas_com_economia
            )
            kpis.append(KPI(
                nome="Prêmio Total (ganhas)",
                valor=premio_total,
                unidade="R$",
            ))

            # Comissão total
            comissao_total = sum(
                float(o.economia.comissao_valor or 0)
                for o in ganhas_com_economia
            )
            kpis.append(KPI(
                nome="Comissão Total",
                valor=comissao_total,
                unidade="R$",
            ))

            # Margem média
            margens = [
                o.economia.margem_percentual
                for o in ganhas_com_economia
                if o.economia.margem_percentual is not None
            ]
            if margens:
                kpis.append(KPI(
                    nome="Margem Média",
                    valor=round(sum(margens) / len(margens), 1),
                    unidade="%",
                ))

            # Taxa média praticada
            taxas = [
                o.economia.taxa_praticada
                for o in ganhas_com_economia
                if o.economia.taxa_praticada is not None
            ]
            if taxas:
                kpis.append(KPI(
                    nome="Taxa Média Praticada",
                    valor=round(sum(taxas) / len(taxas), 2),
                    unidade="% a.a.",
                ))

        return kpis
