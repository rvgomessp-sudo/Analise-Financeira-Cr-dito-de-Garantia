"""
Orquestrador de Integrações

Gerencia conexões com sistemas externos:
    CRM no centro, com:
    - Dados externos → conectores/API (enriquecimento, editais, notícias)
    - E-mail/Calendário → sync bidirecional
    - Documentos → SharePoint/OneDrive com pastas por Conta/Oportunidade
    - Automação → Power Automate/Workflows nativos
    - BI → Power BI (dataset incremental)
    - Assinatura/Propostas → eSignature
    - Backoffice Financeiro → comissões/custos
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Callable


class StatusIntegracao(Enum):
    """Status de uma integração"""
    ATIVA = "Ativa"
    INATIVA = "Inativa"
    ERRO = "Erro"
    CONFIGURANDO = "Configurando"


class TipoIntegracao(Enum):
    """Tipo de integração"""
    API_REST = "API REST"
    WEBHOOK = "Webhook"
    CONECTOR_NATIVO = "Conector Nativo"
    POWER_AUTOMATE = "Power Automate"
    SYNC_BIDIRECIONAL = "Sync Bidirecional"
    EXPORT_BATCH = "Export Batch"


@dataclass
class ConfiguracaoIntegracao:
    """Configuração de uma integração"""
    id: str
    nome: str
    tipo: TipoIntegracao
    descricao: str
    endpoint: str = ""
    credenciais_ref: str = ""  # Referência ao cofre de credenciais
    headers: Dict = field(default_factory=dict)
    parametros: Dict = field(default_factory=dict)
    ativa: bool = False
    ultima_sincronizacao: Optional[datetime] = None
    frequencia_sync: str = ""  # diario, horario, tempo_real
    status: StatusIntegracao = StatusIntegracao.CONFIGURANDO


@dataclass
class LogIntegracao:
    """Log de execução de integração"""
    integracao_id: str
    acao: str
    sucesso: bool
    registros_processados: int = 0
    data: datetime = field(default_factory=datetime.now)
    detalhes: str = ""
    erro: str = ""


class OrquestradorIntegracoes:
    """
    Orquestrador central de integrações.

    Gerencia a configuração, execução e monitoramento de todas
    as integrações externas do CRM.

    Arquitetura (alto nível):
        CRM (centro) ← → Conectores ← → Sistemas Externos
    """

    def __init__(self):
        self.integracoes: Dict[str, ConfiguracaoIntegracao] = {}
        self.logs: List[LogIntegracao] = []
        self._callbacks: Dict[str, Callable] = {}
        self._registrar_integracoes_padrao()

    def _registrar_integracoes_padrao(self) -> None:
        """Registra integrações padrão do sistema"""

        # 1. Enriquecimento de dados (Receita Federal / APIs PJ)
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT001",
            nome="Enriquecimento PJ (API Receita/CNPJ)",
            tipo=TipoIntegracao.API_REST,
            descricao="Validação e enriquecimento de CNPJ, situação cadastral, "
                      "CNAE, porte, endereço, quadro societário",
            frequencia_sync="diario",
            parametros={
                'campos': ['razao_social', 'cnae', 'porte', 'situacao',
                           'endereco', 'socios', 'natureza_juridica'],
                'batch_size': 100,
            },
        ))

        # 2. Editais e contratos públicos (PNCP)
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT002",
            nome="Portal Nacional de Compras Públicas (PNCP)",
            tipo=TipoIntegracao.API_REST,
            descricao="Detecção de novas obras, contratos públicos e editais "
                      "que requerem garantia",
            frequencia_sync="diario",
            parametros={
                'filtros_cnae': ['41', '42', '43', '35', '49', '71'],
                'valor_minimo': 1000000,
                'tipos_garantia': ['seguro_garantia', 'fianca_bancaria'],
            },
        ))

        # 3. Notícias e mudanças societárias
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT003",
            nome="Monitoramento de Notícias e Mudanças",
            tipo=TipoIntegracao.API_REST,
            descricao="Monitoramento de notícias materiais, alterações societárias "
                      "e eventos relevantes das contas monitoradas",
            frequencia_sync="diario",
        ))

        # 4. E-mail / Calendário (Microsoft 365)
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT004",
            nome="E-mail e Calendário (Microsoft 365)",
            tipo=TipoIntegracao.SYNC_BIDIRECIONAL,
            descricao="Sincronização bidirecional de e-mails e eventos de calendário, "
                      "registrando atividades automaticamente",
            frequencia_sync="tempo_real",
            parametros={
                'sync_email': True,
                'sync_calendario': True,
                'logar_atividades': True,
            },
        ))

        # 5. Documentos (SharePoint/OneDrive)
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT005",
            nome="Repositório de Documentos (SharePoint/OneDrive)",
            tipo=TipoIntegracao.CONECTOR_NATIVO,
            descricao="Armazenamento de documentos com pastas por Conta/Oportunidade "
                      "e metadados automáticos",
            frequencia_sync="tempo_real",
            parametros={
                'estrutura_pastas': '{Conta}/{Oportunidade}/{TipoDocumento}',
                'metadados_automaticos': True,
                'controle_versao': True,
            },
        ))

        # 6. Automação (Power Automate)
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT006",
            nome="Automação (Power Automate)",
            tipo=TipoIntegracao.POWER_AUTOMATE,
            descricao="Fluxos de automação para enriquecimento, deduplicação, "
                      "tarefas e notificações (Teams)",
            frequencia_sync="tempo_real",
            parametros={
                'fluxos': [
                    'enriquecimento_conta',
                    'deduplicacao_semanal',
                    'alerta_renovacao',
                    'notificacao_recusa',
                    'tarefa_contestacao',
                ],
            },
        ))

        # 7. BI (Power BI)
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT007",
            nome="Business Intelligence (Power BI)",
            tipo=TipoIntegracao.EXPORT_BATCH,
            descricao="Dataset incremental para Power BI com dados do CRM "
                      "e logs de enriquecimento",
            frequencia_sync="diario",
            parametros={
                'datasets': [
                    'pipeline_oportunidades',
                    'funil_contas',
                    'kpis_comerciais',
                    'qualidade_dados',
                    'recusas_contestacoes',
                ],
                'tipo_refresh': 'incremental',
            },
        ))

        # 8. Assinatura eletrônica
        self.registrar_integracao(ConfiguracaoIntegracao(
            id="INT008",
            nome="Assinatura Eletrônica (eSignature)",
            tipo=TipoIntegracao.API_REST,
            descricao="Envio e rastreamento de documentos para assinatura eletrônica",
        ))

    def registrar_integracao(self, config: ConfiguracaoIntegracao) -> None:
        """Registra uma nova integração"""
        self.integracoes[config.id] = config

    def ativar_integracao(self, integracao_id: str) -> bool:
        """Ativa uma integração"""
        integ = self.integracoes.get(integracao_id)
        if integ:
            integ.ativa = True
            integ.status = StatusIntegracao.ATIVA
            return True
        return False

    def desativar_integracao(self, integracao_id: str) -> bool:
        """Desativa uma integração"""
        integ = self.integracoes.get(integracao_id)
        if integ:
            integ.ativa = False
            integ.status = StatusIntegracao.INATIVA
            return True
        return False

    def registrar_callback(self, integracao_id: str, callback: Callable) -> None:
        """Registra callback para uma integração (processamento dos dados)"""
        self._callbacks[integracao_id] = callback

    def executar_sync(self, integracao_id: str, dados: Dict = None) -> LogIntegracao:
        """
        Executa sincronização de uma integração.

        Em produção, isso chamaria as APIs externas.
        Aqui registra o log e executa o callback se registrado.
        """
        integ = self.integracoes.get(integracao_id)
        if not integ:
            return LogIntegracao(
                integracao_id=integracao_id,
                acao="sync",
                sucesso=False,
                erro="Integração não encontrada",
            )

        if not integ.ativa:
            return LogIntegracao(
                integracao_id=integracao_id,
                acao="sync",
                sucesso=False,
                erro="Integração inativa",
            )

        log = LogIntegracao(
            integracao_id=integracao_id,
            acao="sync",
            sucesso=True,
        )

        # Executa callback se registrado
        callback = self._callbacks.get(integracao_id)
        if callback and dados:
            try:
                resultado = callback(dados)
                log.registros_processados = resultado.get('processados', 0)
                log.detalhes = str(resultado)
            except Exception as e:
                log.sucesso = False
                log.erro = str(e)
                integ.status = StatusIntegracao.ERRO

        integ.ultima_sincronizacao = datetime.now()
        self.logs.append(log)
        return log

    def status_integracoes(self) -> List[Dict]:
        """Retorna status de todas as integrações"""
        return [
            {
                'id': integ.id,
                'nome': integ.nome,
                'tipo': integ.tipo.value,
                'status': integ.status.value,
                'ativa': integ.ativa,
                'frequencia': integ.frequencia_sync,
                'ultima_sync': integ.ultima_sincronizacao.isoformat() if integ.ultima_sincronizacao else None,
            }
            for integ in self.integracoes.values()
        ]

    def saude_integracoes(self) -> Dict:
        """Verifica saúde geral das integrações"""
        total = len(self.integracoes)
        ativas = len([i for i in self.integracoes.values() if i.ativa])
        com_erro = len([i for i in self.integracoes.values() if i.status == StatusIntegracao.ERRO])

        # Últimos logs de erro
        erros_recentes = [l for l in self.logs[-50:] if not l.sucesso]

        return {
            'total_integracoes': total,
            'ativas': ativas,
            'inativas': total - ativas,
            'com_erro': com_erro,
            'saude': 'verde' if com_erro == 0 else 'amarelo' if com_erro == 1 else 'vermelho',
            'erros_recentes': len(erros_recentes),
        }
