"""
Automação - Regras e Jobs Agendados

Motor de regras com triggers e ações automáticas.
Agendador de jobs para enriquecimento, deduplicação e alertas.
"""

from src.crm.automacao.regras import MotorRegras, Regra, TipoEvento
from src.crm.automacao.jobs import AgendadorJobs

__all__ = ['MotorRegras', 'Regra', 'TipoEvento', 'AgendadorJobs']
