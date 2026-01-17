"""
Sistema de Captura de Editais com Exigência de Rating

Este módulo captura editais de licitações públicas que exigem rating/classificação
de risco para seguradoras, com ênfase no estado do Amazonas.

Funcionalidades:
- Captura de editais do PNCP (Portal Nacional de Contratações Públicas)
- Captura de editais do Portal de Compras do Amazonas
- Detecção automática de exigências de rating
- Geração de alertas e relatórios
"""

from .modelos import (
    Edital,
    ExigenciaRating,
    FonteEdital,
    ResultadoBusca,
    ConfiguracaoCaptura,
    TipoLicitacao,
    TipoGarantia,
    NivelRating,
    AgenciaRating,
    StatusEdital
)
from .detector_rating import DetectorRating
from .capturador_base import CapturadorBase, verificar_dependencias, instalar_dependencias
from .capturador_pncp import CapturadorPNCP
from .capturador_amazonas import CapturadorAmazonas
from .gestor_capturas import GestorCapturas

__all__ = [
    'Edital',
    'ExigenciaRating',
    'FonteEdital',
    'ResultadoBusca',
    'ConfiguracaoCaptura',
    'TipoLicitacao',
    'TipoGarantia',
    'NivelRating',
    'AgenciaRating',
    'StatusEdital',
    'DetectorRating',
    'CapturadorBase',
    'CapturadorPNCP',
    'CapturadorAmazonas',
    'GestorCapturas',
    'verificar_dependencias',
    'instalar_dependencias'
]
