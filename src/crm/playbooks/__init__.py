"""
Playbooks de Prospecção Consultiva

Playbook A - Editais/Obras: trigger por CNAE/porte + sinal de edital
Playbook B - Renovação/Performance: trigger por marcos contratuais
Playbook C - Recusa Técnica / Contestação: trigger por recusa injustificada
"""

from src.crm.playbooks.playbook_editais import PlaybookEditais
from src.crm.playbooks.playbook_renovacao import PlaybookRenovacao
from src.crm.playbooks.playbook_contestacao import PlaybookContestacao

__all__ = ['PlaybookEditais', 'PlaybookRenovacao', 'PlaybookContestacao']
