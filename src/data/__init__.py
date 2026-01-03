"""Dados de exemplo e carregadores"""

from .dados_exemplo import carregar_dados_exemplo
from .dados_reais import (
    carregar_dados_reais,
    carregar_junto_seguros,
    carregar_zurich,
    get_ratings_info,
    get_financial_highlights
)

__all__ = [
    'carregar_dados_exemplo',
    'carregar_dados_reais',
    'carregar_junto_seguros',
    'carregar_zurich',
    'get_ratings_info',
    'get_financial_highlights'
]
