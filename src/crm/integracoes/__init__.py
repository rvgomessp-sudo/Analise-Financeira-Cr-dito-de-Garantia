"""
Integrações

Orquestrador de integrações externas:
    - Dados externos (enriquecimento, editais, notícias)
    - E-mail/Calendário (sync bidirecional)
    - Documentos (SharePoint/OneDrive)
    - Automação (Power Automate/Workflows)
    - BI (Power BI)
    - Assinatura/Propostas (eSignature)
"""

from src.crm.integracoes.orquestrador import OrquestradorIntegracoes

__all__ = ['OrquestradorIntegracoes']
