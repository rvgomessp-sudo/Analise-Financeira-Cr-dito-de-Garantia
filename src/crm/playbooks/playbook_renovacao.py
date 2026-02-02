"""
Playbook B — Renovação/Performance

Trigger: Contratos com marcos a 90/60/30 dias.
Ação: Revisar performance, atualizar cronograma físico-financeiro,
      rodar reprecificação e mitigações (contragarantias),
      preparar renovação.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional

from src.crm.models.oportunidade import (
    Oportunidade, EtapaOportunidade,
)
from src.crm.models.atividade import (
    TipoAtividade, PrioridadeAtividade,
)


@dataclass
class AcaoRenovacao:
    """Ação de renovação gerada pelo playbook"""
    tipo: str
    descricao: str
    dados: Dict = field(default_factory=dict)
    prioridade: str = "media"
    dias_para_vencer: int = 0


@dataclass
class ResultadoRenovacao:
    """Resultado do playbook de renovação"""
    playbook: str = "Playbook B - Renovação/Performance"
    oportunidades_analisadas: int = 0
    alertas_90_dias: List[Dict] = field(default_factory=list)
    alertas_60_dias: List[Dict] = field(default_factory=list)
    alertas_30_dias: List[Dict] = field(default_factory=list)
    acoes_geradas: List[AcaoRenovacao] = field(default_factory=list)
    data_execucao: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'playbook': self.playbook,
            'analisadas': self.oportunidades_analisadas,
            'alertas': {
                '90_dias': len(self.alertas_90_dias),
                '60_dias': len(self.alertas_60_dias),
                '30_dias': len(self.alertas_30_dias),
            },
            'total_acoes': len(self.acoes_geradas),
        }


class PlaybookRenovacao:
    """
    Playbook B — Renovação/Performance

    Monitora oportunidades em pós-emissão e gera alertas
    quando marcos contratuais se aproximam.

    Marcos monitorados: 90, 60 e 30 dias antes do vencimento.
    """

    MARCOS_DIAS = [90, 60, 30]
    NOME = "Playbook B - Renovação/Performance"

    def executar(self, oportunidades: List[Oportunidade]) -> ResultadoRenovacao:
        """
        Analisa oportunidades e gera alertas e ações de renovação.

        Foco em oportunidades na etapa Pós-Emissão com data_fim_vigencia.
        """
        resultado = ResultadoRenovacao()
        hoje = date.today()

        oportunidades_monitoraveis = [
            op for op in oportunidades
            if op.etapa == EtapaOportunidade.POS_EMISSAO
            and op.data_fim_vigencia is not None
        ]

        resultado.oportunidades_analisadas = len(oportunidades_monitoraveis)

        for op in oportunidades_monitoraveis:
            dias_restantes = (op.data_fim_vigencia - hoje).days

            if dias_restantes < 0:
                # Já vencida
                resultado.alertas_30_dias.append({
                    'oportunidade_id': op.id,
                    'nome': op.nome,
                    'dias_vencido': abs(dias_restantes),
                    'urgencia': 'VENCIDA',
                })
                self._gerar_acoes_vencida(resultado, op, dias_restantes)

            elif dias_restantes <= 30:
                resultado.alertas_30_dias.append({
                    'oportunidade_id': op.id,
                    'nome': op.nome,
                    'dias_restantes': dias_restantes,
                    'urgencia': 'CRITICA',
                })
                self._gerar_acoes_30_dias(resultado, op, dias_restantes)

            elif dias_restantes <= 60:
                resultado.alertas_60_dias.append({
                    'oportunidade_id': op.id,
                    'nome': op.nome,
                    'dias_restantes': dias_restantes,
                    'urgencia': 'ALTA',
                })
                self._gerar_acoes_60_dias(resultado, op, dias_restantes)

            elif dias_restantes <= 90:
                resultado.alertas_90_dias.append({
                    'oportunidade_id': op.id,
                    'nome': op.nome,
                    'dias_restantes': dias_restantes,
                    'urgencia': 'MEDIA',
                })
                self._gerar_acoes_90_dias(resultado, op, dias_restantes)

        return resultado

    def _gerar_acoes_90_dias(self, resultado: ResultadoRenovacao,
                              op: Oportunidade, dias: int) -> None:
        """Ações para marco de 90 dias"""
        resultado.acoes_geradas.append(AcaoRenovacao(
            tipo="criar_atividade",
            descricao=f"Revisar performance do contrato - {op.nome}",
            dados={
                'tipo': TipoAtividade.ANALISE_INTERNA.value,
                'titulo': f"Revisão de performance 90d - {op.nome}",
                'descricao': (
                    "Revisão pré-renovação (90 dias):\n"
                    "1. Revisar cronograma físico-financeiro atual\n"
                    "2. Verificar cumprimento de marcos contratuais\n"
                    "3. Atualizar indicadores financeiros da conta\n"
                    "4. Avaliar necessidade de ajuste de valor/vigência\n"
                    "5. Preparar relatório de performance para seguradora"
                ),
                'oportunidade_id': op.id,
                'sla_horas': 168,  # 7 dias
            },
            prioridade="media",
            dias_para_vencer=dias,
        ))

    def _gerar_acoes_60_dias(self, resultado: ResultadoRenovacao,
                              op: Oportunidade, dias: int) -> None:
        """Ações para marco de 60 dias"""
        resultado.acoes_geradas.append(AcaoRenovacao(
            tipo="criar_atividade",
            descricao=f"Preparar reprecificação e mitigações - {op.nome}",
            dados={
                'tipo': TipoAtividade.TAREFA.value,
                'titulo': f"Reprecificação e renovação 60d - {op.nome}",
                'descricao': (
                    "Preparação para renovação (60 dias):\n"
                    "1. Rodar reprecificação (nova taxa, prêmio)\n"
                    "2. Avaliar contragarantias atuais\n"
                    "3. Propor novas mitigações se necessário\n"
                    "4. Submeter proposta de renovação à seguradora\n"
                    "5. Contatar cliente sobre renovação"
                ),
                'oportunidade_id': op.id,
                'prioridade': PrioridadeAtividade.ALTA.value,
                'sla_horas': 120,  # 5 dias
            },
            prioridade="alta",
            dias_para_vencer=dias,
        ))

        # Atividade de contato com cliente
        resultado.acoes_geradas.append(AcaoRenovacao(
            tipo="criar_atividade",
            descricao=f"Contatar cliente sobre renovação - {op.nome}",
            dados={
                'tipo': TipoAtividade.LIGACAO.value,
                'titulo': f"Contato renovação - {op.nome}",
                'descricao': (
                    "Contatar cliente para:\n"
                    "1. Informar sobre vencimento iminente\n"
                    "2. Coletar atualizações do contrato/obra\n"
                    "3. Verificar necessidade de ajustes\n"
                    "4. Alinhar cronograma de renovação"
                ),
                'oportunidade_id': op.id,
                'prioridade': PrioridadeAtividade.ALTA.value,
            },
            prioridade="alta",
            dias_para_vencer=dias,
        ))

    def _gerar_acoes_30_dias(self, resultado: ResultadoRenovacao,
                              op: Oportunidade, dias: int) -> None:
        """Ações para marco de 30 dias (urgente)"""
        resultado.acoes_geradas.append(AcaoRenovacao(
            tipo="criar_atividade",
            descricao=f"URGENTE: Formalizar renovação - {op.nome}",
            dados={
                'tipo': TipoAtividade.TAREFA.value,
                'titulo': f"URGENTE: Renovação 30d - {op.nome}",
                'descricao': (
                    "RENOVAÇÃO URGENTE (30 dias):\n"
                    "1. Confirmar aprovação da seguradora\n"
                    "2. Formalizar endosso/aditivo\n"
                    "3. Cobrar documentos pendentes do cliente\n"
                    "4. Garantir emissão antes do vencimento\n"
                    "5. Alertar diretoria se houver risco de gap de cobertura"
                ),
                'oportunidade_id': op.id,
                'prioridade': PrioridadeAtividade.CRITICA.value,
                'sla_horas': 48,
            },
            prioridade="critica",
            dias_para_vencer=dias,
        ))

        # Alerta para diretoria
        resultado.acoes_geradas.append(AcaoRenovacao(
            tipo="alerta",
            descricao=f"Alerta diretoria: Renovação em {dias} dias - {op.nome}",
            dados={
                'canal': 'teams',
                'destinatarios': ['diretoria', 'operacoes'],
                'mensagem': (
                    f"Apólice {op.nome} vence em {dias} dias. "
                    f"Valor: {op.valor_garantia}. "
                    f"Ação imediata necessária para evitar gap de cobertura."
                ),
                'oportunidade_id': op.id,
            },
            prioridade="critica",
            dias_para_vencer=dias,
        ))

    def _gerar_acoes_vencida(self, resultado: ResultadoRenovacao,
                              op: Oportunidade, dias: int) -> None:
        """Ações para apólice já vencida"""
        resultado.acoes_geradas.append(AcaoRenovacao(
            tipo="alerta",
            descricao=f"ALERTA: Apólice VENCIDA há {abs(dias)} dias - {op.nome}",
            dados={
                'canal': 'teams',
                'destinatarios': ['diretoria', 'operacoes', 'juridico'],
                'mensagem': (
                    f"ATENÇÃO: Apólice {op.nome} VENCIDA há {abs(dias)} dias. "
                    f"Risco de sinistro sem cobertura. "
                    f"Ação imediata do jurídico e diretoria necessária."
                ),
                'oportunidade_id': op.id,
                'urgencia': 'CRITICA',
            },
            prioridade="critica",
            dias_para_vencer=dias,
        ))

    def resumo_renovacoes(self, oportunidades: List[Oportunidade]) -> Dict:
        """Gera resumo executivo das renovações pendentes"""
        resultado = self.executar(oportunidades)
        return {
            'total_monitoradas': resultado.oportunidades_analisadas,
            'vencendo_90d': len(resultado.alertas_90_dias),
            'vencendo_60d': len(resultado.alertas_60_dias),
            'vencendo_30d': len(resultado.alertas_30_dias),
            'total_acoes_pendentes': len(resultado.acoes_geradas),
            'criticas': len([a for a in resultado.acoes_geradas if a.prioridade == "critica"]),
        }
