"""
Segurança, LGPD & Propriedade Intelectual

Controle de acesso baseado em papéis (RBAC).
Gestão de consentimento LGPD e mascaramento de dados.
Controle de versão de estudos técnicos (PI).
"""

from src.crm.seguranca.controle_acesso import ControleAcesso, Perfil, Permissao
from src.crm.seguranca.lgpd import GestorLGPD

__all__ = ['ControleAcesso', 'Perfil', 'Permissao', 'GestorLGPD']
