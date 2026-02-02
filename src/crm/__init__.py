"""
CRM de Prospecção e Operações de Garantia

Sistema completo de CRM PJ-first para gestão de prospecção consultiva,
pipeline comercial, scoring, enriquecimento de dados e governança
de operações de seguro garantia.

Módulos:
    models       - Modelos de dados (Conta, Contato, Oportunidade, Atividade, Documento)
    pipeline     - Pipeline comercial com etapas e checklists
    scoring      - Scoring de Fit (conta) e Propensão (oportunidade)
    enriquecimento - Validação CNPJ, enriquecimento e deduplicação
    playbooks    - Playbooks de prospecção consultiva
    dashboards   - KPIs e dashboards executivos
    seguranca    - Controle de acesso (RBAC) e LGPD
    automacao    - Regras de automação e jobs agendados
    integracoes  - Orquestrador de integrações externas
    importador   - Importação de bases PGFN Marco Zero
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
    Atividade, TipoAtividade, StatusAtividade, Cadencia,
    EtapaCadencia,
)
from src.crm.models.documento import (
    Documento, TipoDocumento, VersaoDocumento,
)
from src.crm.pipeline.etapas import (
    EtapaPipeline, Pipeline, ChecklistItem,
)
from src.crm.pipeline.validador import ValidadorEtapa
from src.crm.scoring.score_fit import ScoreFit
from src.crm.scoring.score_propensao import ScorePropensao
from src.crm.enriquecimento.validador_cnpj import ValidadorCNPJ
from src.crm.enriquecimento.enriquecedor import Enriquecedor
from src.crm.enriquecimento.deduplicacao import Deduplicador
from src.crm.playbooks.playbook_editais import PlaybookEditais
from src.crm.playbooks.playbook_renovacao import PlaybookRenovacao
from src.crm.playbooks.playbook_contestacao import PlaybookContestacao
from src.crm.dashboards.kpis import MotorKPIs
from src.crm.dashboards.dashboard import DashboardExecutivo
from src.crm.seguranca.controle_acesso import ControleAcesso, Perfil, Permissao
from src.crm.seguranca.lgpd import GestorLGPD
from src.crm.automacao.regras import MotorRegras, Regra, TipoEvento
from src.crm.automacao.jobs import AgendadorJobs
from src.crm.integracoes.orquestrador import OrquestradorIntegracoes
from src.crm.importador.importador_bases import ImportadorBasesPGFN
from src.crm.importador.estatisticas import EstatisticasImportacao

__all__ = [
    # Models
    'Conta', 'PorteEmpresa', 'SituacaoCadastral', 'TipoEstabelecimento',
    'QuadroSocietario', 'IndicadoresFinanceiros', 'LimiteSeguradora',
    'Sinistro', 'CertidaoDocumento', 'SinalMercado',
    'DadosPGFN', 'TemperaturaLead',
    'Contato', 'AreaContato', 'NivelInfluencia', 'ConsentimentoLGPD',
    'Oportunidade', 'TipoGarantiaOportunidade', 'StatusSeguradora',
    'MatrizRisco', 'Contragarantia', 'EconomiaOperacao', 'EstudoTecnico',
    'Atividade', 'TipoAtividade', 'StatusAtividade', 'Cadencia', 'EtapaCadencia',
    'Documento', 'TipoDocumento', 'VersaoDocumento',
    # Pipeline
    'EtapaPipeline', 'Pipeline', 'ChecklistItem', 'ValidadorEtapa',
    # Scoring
    'ScoreFit', 'ScorePropensao',
    # Enriquecimento
    'ValidadorCNPJ', 'Enriquecedor', 'Deduplicador',
    # Playbooks
    'PlaybookEditais', 'PlaybookRenovacao', 'PlaybookContestacao',
    # Dashboards
    'MotorKPIs', 'DashboardExecutivo',
    # Segurança
    'ControleAcesso', 'Perfil', 'Permissao', 'GestorLGPD',
    # Automação
    'MotorRegras', 'Regra', 'TipoEvento', 'AgendadorJobs',
    # Integrações
    'OrquestradorIntegracoes',
    # Importador
    'ImportadorBasesPGFN', 'EstatisticasImportacao',
]
