"""Módulos de análise financeira"""

from .indicadores import AnalisadorIndicadores
from .comparador import ComparadorSeguradora
from .analisador_estrutura_societaria import (
    AnalisadorEstruturaSocietaria,
    AnaliseEstrutural,
    ComparacaoEstrutural,
    ClassificacaoSeguranca,
    analisar_e_comparar,
    criar_analisador,
)

__all__ = [
    'AnalisadorIndicadores', 'ComparadorSeguradora',
    'AnalisadorEstruturaSocietaria', 'AnaliseEstrutural',
    'ComparacaoEstrutural', 'ClassificacaoSeguranca',
    'analisar_e_comparar', 'criar_analisador',
]
