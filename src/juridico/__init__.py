# -*- coding: utf-8 -*-
"""
Módulo Jurídico para Análise de Licitações
==========================================

Este módulo contém ferramentas para análise jurídica de processos licitatórios,
cruzamento com a Lei 14.133/2021, referências do TCU e geração de notificações.

Autor: Sistema de Análise Jurídica
Versão: 1.0.0
"""

from .base_legal import BaseLegal14133, ArtigoLei, DispositivoLegal
from .referencias_tcu import ReferenciasTCU, Acordao, SumulaTCU
from .analisador_irregularidades import AnalisadorIrregularidades, Irregularidade
from .cruzamento_dados import MotorCruzamento, ResultadoCruzamento
from .gerador_notificacao import GeradorNotificacao, Notificacao

__all__ = [
    'BaseLegal14133',
    'ArtigoLei',
    'DispositivoLegal',
    'ReferenciasTCU',
    'Acordao',
    'SumulaTCU',
    'AnalisadorIrregularidades',
    'Irregularidade',
    'MotorCruzamento',
    'ResultadoCruzamento',
    'GeradorNotificacao',
    'Notificacao'
]
