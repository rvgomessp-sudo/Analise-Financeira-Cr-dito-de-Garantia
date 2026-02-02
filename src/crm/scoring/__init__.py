"""
Scoring & Priorização

Score de Fit (Conta): avalia adequação da conta ao ICP.
Score de Propensão (Oportunidade): avalia probabilidade de fechamento.
Semáforos de risco para priorização de esforços.
"""

from src.crm.scoring.score_fit import ScoreFit
from src.crm.scoring.score_propensao import ScorePropensao

__all__ = ['ScoreFit', 'ScorePropensao']
