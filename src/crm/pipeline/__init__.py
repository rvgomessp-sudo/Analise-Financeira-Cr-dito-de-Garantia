"""
Pipeline Comercial de Garantias

8 etapas com checklists de campos obrigatórios para avançar.
Cada etapa tem "saídas" objetivas e validação de governança de dados.
"""

from src.crm.pipeline.etapas import EtapaPipeline, Pipeline, ChecklistItem
from src.crm.pipeline.validador import ValidadorEtapa

__all__ = ['EtapaPipeline', 'Pipeline', 'ChecklistItem', 'ValidadorEtapa']
