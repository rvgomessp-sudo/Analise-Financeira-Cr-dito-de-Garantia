"""Dados de exemplo e carregadores"""

from .dados_exemplo import carregar_dados_exemplo
from .dados_estrutura_societaria import (
    criar_zurich_minas_brasil,
    criar_junto_seguros,
    criar_comparacao_zurich_junto,
    obter_dados_comparativos_brl,
    gerar_relatorio_diferenciacao,
    ZURICH_INSURANCE_GROUP,
    GRUPO_ZURICH_BRASIL,
)

__all__ = [
    'carregar_dados_exemplo',
    'criar_zurich_minas_brasil', 'criar_junto_seguros',
    'criar_comparacao_zurich_junto', 'obter_dados_comparativos_brl',
    'gerar_relatorio_diferenciacao',
    'ZURICH_INSURANCE_GROUP', 'GRUPO_ZURICH_BRASIL',
]
