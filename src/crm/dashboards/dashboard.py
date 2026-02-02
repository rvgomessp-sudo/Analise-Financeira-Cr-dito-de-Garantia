"""
Dashboard Executivo

Gera dashboard com 6 gráficos + semáforos + 5 insights automáticos.
Versão executiva para C-level atualizada diariamente.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from decimal import Decimal

from src.crm.models.conta import Conta
from src.crm.models.oportunidade import (
    Oportunidade, EtapaOportunidade, TipoGarantiaOportunidade,
)
from src.crm.models.atividade import Atividade
from src.crm.dashboards.kpis import MotorKPIs, KPI


@dataclass
class Insight:
    """Insight automático gerado pelo dashboard"""
    titulo: str
    descricao: str
    tipo: str  # positivo, atencao, critico, informativo
    prioridade: int  # 1-5 (5 = mais importante)
    acao_sugerida: str = ""
    data_geracao: datetime = field(default_factory=datetime.now)


@dataclass
class GraficoDashboard:
    """Dados para um gráfico do dashboard"""
    titulo: str
    tipo: str  # barra, pizza, linha, funil, gauge, tabela
    dados: Dict = field(default_factory=dict)
    descricao: str = ""


@dataclass
class DashboardData:
    """Dados completos do dashboard executivo"""
    titulo: str = "Dashboard Executivo - CRM Garantias"
    data_geracao: datetime = field(default_factory=datetime.now)
    periodo: str = ""
    semaforo_geral: str = "amarelo"  # verde, amarelo, vermelho

    kpis_destaque: List[KPI] = field(default_factory=list)
    graficos: List[GraficoDashboard] = field(default_factory=list)
    insights: List[Insight] = field(default_factory=list)
    semaforos: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            'titulo': self.titulo,
            'data_geracao': self.data_geracao.isoformat(),
            'periodo': self.periodo,
            'semaforo_geral': self.semaforo_geral,
            'kpis_destaque': [k.to_dict() for k in self.kpis_destaque],
            'graficos': [
                {'titulo': g.titulo, 'tipo': g.tipo, 'dados': g.dados}
                for g in self.graficos
            ],
            'insights': [
                {
                    'titulo': i.titulo,
                    'descricao': i.descricao,
                    'tipo': i.tipo,
                    'prioridade': i.prioridade,
                    'acao_sugerida': i.acao_sugerida,
                }
                for i in self.insights
            ],
            'semaforos': self.semaforos,
        }


class DashboardExecutivo:
    """
    Gerador de Dashboard Executivo.

    Versão C-level: 6 gráficos + semáforos + 5 insights automáticos por semana.
    Atualizado diariamente.
    """

    def __init__(self):
        self.motor_kpis = MotorKPIs()

    def gerar(
        self,
        contas: List[Conta],
        oportunidades: List[Oportunidade],
        atividades: List[Atividade] = None,
        periodo_dias: int = 30,
    ) -> DashboardData:
        """Gera dashboard executivo completo"""
        dashboard = DashboardData(
            periodo=f"Últimos {periodo_dias} dias",
        )

        # Calcular KPIs
        todos_kpis = self.motor_kpis.calcular_todos(
            contas, oportunidades, atividades, periodo_dias
        )

        # KPIs destaque (top 6)
        dashboard.kpis_destaque = self._selecionar_kpis_destaque(todos_kpis)

        # Gráficos
        dashboard.graficos = self._gerar_graficos(contas, oportunidades)

        # Semáforos
        dashboard.semaforos = self._calcular_semaforos(todos_kpis)

        # Insights automáticos
        dashboard.insights = self._gerar_insights(
            contas, oportunidades, todos_kpis
        )

        # Semáforo geral
        dashboard.semaforo_geral = self._semaforo_geral(dashboard.semaforos)

        return dashboard

    def _selecionar_kpis_destaque(self, todos_kpis: Dict[str, List[KPI]]) -> List[KPI]:
        """Seleciona os 6 KPIs mais relevantes"""
        destaque = []
        nomes_destaque = [
            "Oportunidades Abertas",
            "Valor Total Pipeline",
            "Win Rate",
            "Contas Enriquecidas (CNPJ/CNAE/Porte)",
            "Completude Média (Contas)",
            "Comissão Total",
        ]

        todos = []
        for lista in todos_kpis.values():
            todos.extend(lista)

        for nome in nomes_destaque:
            for kpi in todos:
                if kpi.nome == nome:
                    destaque.append(kpi)
                    break

        return destaque[:6]

    def _gerar_graficos(self, contas: List[Conta],
                         oportunidades: List[Oportunidade]) -> List[GraficoDashboard]:
        """Gera dados para os 6 gráficos do dashboard"""
        graficos = []

        # 1. Funil do Pipeline
        funil = {}
        abertas = [o for o in oportunidades if o.aberta]
        for op in abertas:
            etapa = op.etapa.value
            funil[etapa] = funil.get(etapa, 0) + 1

        graficos.append(GraficoDashboard(
            titulo="Funil do Pipeline",
            tipo="funil",
            dados={'etapas': funil},
            descricao="Distribuição de oportunidades por etapa",
        ))

        # 2. Pipeline por Tipo de Garantia
        por_tipo = {}
        for op in abertas:
            tipo = op.tipo_garantia.value
            if tipo not in por_tipo:
                por_tipo[tipo] = {'count': 0, 'valor': 0}
            por_tipo[tipo]['count'] += 1
            if op.valor_garantia:
                por_tipo[tipo]['valor'] += float(op.valor_garantia)

        graficos.append(GraficoDashboard(
            titulo="Pipeline por Tipo de Garantia",
            tipo="barra",
            dados={'tipos': por_tipo},
            descricao="Volume e valor por tipo de garantia",
        ))

        # 3. Contas por Porte / Fit
        por_porte = {}
        for conta in contas:
            porte = conta.porte.value
            por_porte[porte] = por_porte.get(porte, 0) + 1

        graficos.append(GraficoDashboard(
            titulo="Contas por Porte",
            tipo="pizza",
            dados={'portes': por_porte},
            descricao="Distribuição de contas por porte empresarial",
        ))

        # 4. Qualidade de Dados
        faixas = {'Excelente (>80%)': 0, 'Bom (60-80%)': 0, 'Regular (40-60%)': 0, 'Ruim (<40%)': 0}
        for conta in contas:
            pct = conta.percentual_completude
            if pct > 80:
                faixas['Excelente (>80%)'] += 1
            elif pct > 60:
                faixas['Bom (60-80%)'] += 1
            elif pct > 40:
                faixas['Regular (40-60%)'] += 1
            else:
                faixas['Ruim (<40%)'] += 1

        graficos.append(GraficoDashboard(
            titulo="Qualidade de Dados (Contas)",
            tipo="barra",
            dados={'faixas': faixas},
            descricao="Completude dos dados por faixa",
        ))

        # 5. Recusas vs Aprovações
        status_seg = {'Aprovadas': 0, 'Recusadas': 0, 'Em Análise': 0, 'Em Contestação': 0}
        for op in oportunidades:
            for seg in op.seguradoras:
                if seg.status.value == 'Aprovada':
                    status_seg['Aprovadas'] += 1
                elif seg.status.value == 'Recusada':
                    status_seg['Recusadas'] += 1
                elif seg.status.value == 'Em Análise':
                    status_seg['Em Análise'] += 1
                elif seg.status.value == 'Em Contestação':
                    status_seg['Em Contestação'] += 1

        graficos.append(GraficoDashboard(
            titulo="Status Seguradoras",
            tipo="pizza",
            dados={'status': status_seg},
            descricao="Distribuição de respostas das seguradoras",
        ))

        # 6. Semáforos de Risco do Pipeline
        semaforos_risco = {'verde': 0, 'amarelo': 0, 'vermelho': 0, 'sem_avaliacao': 0}
        for op in abertas:
            if op.matriz_risco:
                s = op.matriz_risco.semaforo_geral
                semaforos_risco[s] = semaforos_risco.get(s, 0) + 1
            else:
                semaforos_risco['sem_avaliacao'] += 1

        graficos.append(GraficoDashboard(
            titulo="Semáforos de Risco",
            tipo="gauge",
            dados={'semaforos': semaforos_risco},
            descricao="Distribuição de risco das oportunidades abertas",
        ))

        return graficos

    def _calcular_semaforos(self, todos_kpis: Dict[str, List[KPI]]) -> Dict[str, str]:
        """Calcula semáforos por área"""
        semaforos = {}

        for categoria, kpis in todos_kpis.items():
            vermelhos = sum(1 for k in kpis if k.semaforo == "vermelho")
            amarelos = sum(1 for k in kpis if k.semaforo == "amarelo")

            if vermelhos > 0:
                semaforos[categoria] = "vermelho"
            elif amarelos > 0:
                semaforos[categoria] = "amarelo"
            else:
                semaforos[categoria] = "verde"

        return semaforos

    def _semaforo_geral(self, semaforos: Dict[str, str]) -> str:
        """Calcula semáforo geral do CRM"""
        if any(s == "vermelho" for s in semaforos.values()):
            return "vermelho"
        if any(s == "amarelo" for s in semaforos.values()):
            return "amarelo"
        return "verde"

    def _gerar_insights(
        self,
        contas: List[Conta],
        oportunidades: List[Oportunidade],
        todos_kpis: Dict[str, List[KPI]],
    ) -> List[Insight]:
        """Gera até 5 insights automáticos"""
        insights = []

        # Insight 1: Oportunidades travadas
        abertas = [o for o in oportunidades if o.aberta]
        travadas = [o for o in abertas if o.dias_no_pipeline > 45]
        if travadas:
            insights.append(Insight(
                titulo=f"{len(travadas)} oportunidades travadas (>45 dias)",
                descricao=(
                    f"Existem {len(travadas)} oportunidades no pipeline há mais de 45 dias. "
                    f"Isso pode indicar gargalos no processo ou oportunidades abandonadas."
                ),
                tipo="atencao",
                prioridade=4,
                acao_sugerida="Revisar cada oportunidade travada e decidir: avançar, abortar ou redesenhar.",
            ))

        # Insight 2: Contas sem enriquecimento
        nao_enriquecidas = [c for c in contas if not c.dados_verificados]
        if len(nao_enriquecidas) > len(contas) * 0.3:
            insights.append(Insight(
                titulo=f"{len(nao_enriquecidas)} contas sem dados enriquecidos",
                descricao=(
                    f"{len(nao_enriquecidas)} de {len(contas)} contas não têm dados verificados. "
                    f"Meta KR1: 80% de contas com CNPJ validado e CNAE/porte enriquecidos."
                ),
                tipo="critico",
                prioridade=5,
                acao_sugerida="Executar job de enriquecimento em lote para contas pendentes.",
            ))

        # Insight 3: Recusas sem contestação
        recusas_sem_contestacao = 0
        for op in oportunidades:
            for seg in op.seguradoras:
                if seg.status.value == 'Recusada' and not seg.oficio_contestacao:
                    recusas_sem_contestacao += 1
        if recusas_sem_contestacao > 0:
            insights.append(Insight(
                titulo=f"{recusas_sem_contestacao} recusa(s) sem contestação",
                descricao=(
                    f"Existem {recusas_sem_contestacao} recusas de seguradoras sem contestação registrada. "
                    f"Recusas genéricas podem ser revertidas com argumentação técnica."
                ),
                tipo="atencao",
                prioridade=3,
                acao_sugerida="Analisar recusas via Playbook C (Contestação) e protocolar ofícios.",
            ))

        # Insight 4: Pipeline concentrado
        if abertas:
            etapa_contagem = {}
            for op in abertas:
                etapa_contagem[op.etapa.value] = etapa_contagem.get(op.etapa.value, 0) + 1
            etapa_mais_cheia = max(etapa_contagem, key=etapa_contagem.get)
            pct_concentrada = etapa_contagem[etapa_mais_cheia] / len(abertas) * 100
            if pct_concentrada > 50:
                insights.append(Insight(
                    titulo=f"Pipeline concentrado: {pct_concentrada:.0f}% em '{etapa_mais_cheia}'",
                    descricao=(
                        f"Mais da metade das oportunidades está na etapa '{etapa_mais_cheia}'. "
                        f"Isso indica um gargalo que precisa de ação."
                    ),
                    tipo="atencao",
                    prioridade=4,
                    acao_sugerida=f"Investigar gargalo na etapa '{etapa_mais_cheia}' e destravar oportunidades.",
                ))

        # Insight 5: Oportunidades de alto valor sem risco mapeado
        alto_valor_sem_risco = [
            o for o in abertas
            if o.valor_garantia and float(o.valor_garantia) > 1000000
            and not o.tem_matriz_risco
        ]
        if alto_valor_sem_risco:
            insights.append(Insight(
                titulo=f"{len(alto_valor_sem_risco)} oportunidade(s) >R$1M sem matriz de risco",
                descricao=(
                    f"Existem oportunidades de alto valor (>R$1M) sem matriz de risco elaborada. "
                    f"KR2 Obj 2: 100% das oportunidades devem ter risco e contragarantias."
                ),
                tipo="critico",
                prioridade=5,
                acao_sugerida="Priorizar elaboração de matriz de risco para estas oportunidades.",
            ))

        # Ordena por prioridade e limita a 5
        insights.sort(key=lambda i: i.prioridade, reverse=True)
        return insights[:5]

    def gerar_resumo_texto(self, dashboard: DashboardData) -> str:
        """Gera resumo executivo em texto"""
        linhas = []
        linhas.append(f"{'='*60}")
        linhas.append(f"  DASHBOARD EXECUTIVO - CRM GARANTIAS")
        linhas.append(f"  {dashboard.data_geracao.strftime('%d/%m/%Y %H:%M')} | {dashboard.periodo}")
        linhas.append(f"  Semáforo Geral: {dashboard.semaforo_geral.upper()}")
        linhas.append(f"{'='*60}")

        # KPIs destaque
        linhas.append(f"\n--- KPIs Destaque ---")
        for kpi in dashboard.kpis_destaque:
            meta_str = f" (meta: {kpi.meta}{kpi.unidade})" if kpi.meta else ""
            linhas.append(f"  [{kpi.semaforo[0].upper()}] {kpi.nome}: {kpi.valor} {kpi.unidade}{meta_str}")

        # Semáforos por área
        linhas.append(f"\n--- Semáforos por Área ---")
        for area, semaforo in dashboard.semaforos.items():
            linhas.append(f"  [{semaforo[0].upper()}] {area}")

        # Insights
        linhas.append(f"\n--- Insights ({len(dashboard.insights)}) ---")
        for i, insight in enumerate(dashboard.insights, 1):
            icone = {'positivo': '+', 'atencao': '!', 'critico': 'X', 'informativo': 'i'}
            linhas.append(f"  [{icone.get(insight.tipo, '?')}] {i}. {insight.titulo}")
            if insight.acao_sugerida:
                linhas.append(f"      -> {insight.acao_sugerida}")

        linhas.append(f"\n{'='*60}")
        return "\n".join(linhas)
