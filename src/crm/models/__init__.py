"""
Modelos de Dados CRM (PJ-first)

Chave primária do negócio: CNPJ (com status e data de atualização).
Regra: Conta (PJ) é o centro; Contato (decisor/área) se relaciona à conta;
Oportunidade amarra contrato/objeto, risco, seguradora e fluxo.
"""

from src.crm.models.conta import (
    Conta, PorteEmpresa, SituacaoCadastral, TipoEstabelecimento,
    QuadroSocietario, IndicadoresFinanceiros, LimiteSeguradora,
    Sinistro, CertidaoDocumento, SinalMercado,
    DadosPGFN, TemperaturaLead,
)
from src.crm.models.contato import (
    Contato, AreaContato, NivelInfluencia, ConsentimentoLGPD,
)
from src.crm.models.oportunidade import (
    Oportunidade, TipoGarantiaOportunidade, StatusSeguradora,
    MatrizRisco, Contragarantia, EconomiaOperacao, EstudoTecnico,
)
from src.crm.models.atividade import (
    Atividade, TipoAtividade, StatusAtividade, Cadencia, EtapaCadencia,
)
from src.crm.models.documento import (
    Documento, TipoDocumento, VersaoDocumento,
)

__all__ = [
    'Conta', 'PorteEmpresa', 'SituacaoCadastral', 'TipoEstabelecimento',
    'QuadroSocietario', 'IndicadoresFinanceiros', 'LimiteSeguradora',
    'Sinistro', 'CertidaoDocumento', 'SinalMercado',
    'DadosPGFN', 'TemperaturaLead',
    'Contato', 'AreaContato', 'NivelInfluencia', 'ConsentimentoLGPD',
    'Oportunidade', 'TipoGarantiaOportunidade', 'StatusSeguradora',
    'MatrizRisco', 'Contragarantia', 'EconomiaOperacao', 'EstudoTecnico',
    'Atividade', 'TipoAtividade', 'StatusAtividade', 'Cadencia', 'EtapaCadencia',
    'Documento', 'TipoDocumento', 'VersaoDocumento',
]
