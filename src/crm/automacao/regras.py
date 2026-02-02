"""
Motor de Regras de Automação

Processa eventos e executa ações automáticas baseadas em regras.

Padrões de automação implementados:
    - Ao criar Conta com CNPJ: validar e enriquecer
    - Ao avançar etapa 3: exigir Objeto + Cronograma
    - Recusa registrada: abrir Contestação com prazo 48h
    - Marcos de contrato: criar tarefas e alertas
    - Documento com validade a vencer: alertar responsável
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Callable, Any


class TipoEvento(Enum):
    """Tipos de evento que disparam regras"""
    CONTA_CRIADA = "conta.criada"
    CONTA_ATUALIZADA = "conta.atualizada"
    CONTA_CNPJ_PREENCHIDO = "conta.cnpj_preenchido"

    CONTATO_CRIADO = "contato.criado"

    OPORTUNIDADE_CRIADA = "oportunidade.criada"
    OPORTUNIDADE_ETAPA_AVANCADA = "oportunidade.etapa_avancada"
    OPORTUNIDADE_FECHADA = "oportunidade.fechada"
    OPORTUNIDADE_PERDIDA = "oportunidade.perdida"

    RECUSA_REGISTRADA = "seguradora.recusa"
    APROVACAO_REGISTRADA = "seguradora.aprovacao"

    DOCUMENTO_VENCENDO = "documento.vencendo"
    CERTIDAO_VENCENDO = "certidao.vencendo"

    MARCO_CONTRATUAL = "marco.contratual"

    JOB_DIARIO = "job.diario"
    JOB_SEMANAL = "job.semanal"


@dataclass
class Evento:
    """Evento que dispara processamento de regras"""
    tipo: TipoEvento
    dados: Dict = field(default_factory=dict)
    usuario: str = ""
    data: datetime = field(default_factory=datetime.now)


@dataclass
class AcaoAutomacao:
    """Ação a ser executada por uma regra"""
    tipo: str  # criar_tarefa, enviar_alerta, atualizar_campo, executar_job
    descricao: str
    dados: Dict = field(default_factory=dict)
    executada: bool = False
    resultado: str = ""
    data_execucao: Optional[datetime] = None

    def marcar_executada(self, resultado: str = "OK") -> None:
        self.executada = True
        self.resultado = resultado
        self.data_execucao = datetime.now()


@dataclass
class Regra:
    """Regra de automação: evento → condição → ação"""
    id: str
    nome: str
    descricao: str
    evento_trigger: TipoEvento
    condicao: Optional[Callable[[Evento], bool]] = None  # Função que avalia condição
    acoes: List[Callable[[Evento], AcaoAutomacao]] = field(default_factory=list)
    ativa: bool = True
    prioridade: int = 5  # 1 = mais alta

    def avaliar(self, evento: Evento) -> bool:
        """Verifica se a regra se aplica ao evento"""
        if not self.ativa:
            return False
        if evento.tipo != self.evento_trigger:
            return False
        if self.condicao:
            return self.condicao(evento)
        return True


@dataclass
class ResultadoProcessamento:
    """Resultado do processamento de regras para um evento"""
    evento: Evento
    regras_avaliadas: int = 0
    regras_ativadas: int = 0
    acoes_geradas: List[AcaoAutomacao] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)
    data_processamento: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'evento_tipo': self.evento.tipo.value,
            'regras_avaliadas': self.regras_avaliadas,
            'regras_ativadas': self.regras_ativadas,
            'acoes_geradas': len(self.acoes_geradas),
            'erros': self.erros,
        }


class MotorRegras:
    """
    Motor de processamento de regras de automação.

    Recebe eventos e executa regras registradas.
    As regras são avaliadas por prioridade.
    """

    def __init__(self):
        self.regras: List[Regra] = []
        self.historico: List[ResultadoProcessamento] = []
        self._registrar_regras_padrao()

    def registrar_regra(self, regra: Regra) -> None:
        """Registra uma nova regra"""
        self.regras.append(regra)
        self.regras.sort(key=lambda r: r.prioridade)

    def processar_evento(self, evento: Evento) -> ResultadoProcessamento:
        """
        Processa um evento contra todas as regras registradas.
        Executa ações das regras que se aplicam.
        """
        resultado = ResultadoProcessamento(evento=evento)

        for regra in self.regras:
            resultado.regras_avaliadas += 1

            try:
                if regra.avaliar(evento):
                    resultado.regras_ativadas += 1

                    for gerar_acao in regra.acoes:
                        try:
                            acao = gerar_acao(evento)
                            if acao:
                                resultado.acoes_geradas.append(acao)
                        except Exception as e:
                            resultado.erros.append(
                                f"Erro na ação da regra '{regra.nome}': {str(e)}"
                            )
            except Exception as e:
                resultado.erros.append(
                    f"Erro ao avaliar regra '{regra.nome}': {str(e)}"
                )

        self.historico.append(resultado)
        return resultado

    def _registrar_regras_padrao(self) -> None:
        """Registra regras padrão do sistema"""

        # Regra 1: Ao criar Conta com CNPJ → validar e enriquecer
        self.registrar_regra(Regra(
            id="R001",
            nome="Validar e enriquecer ao criar conta",
            descricao="Ao criar conta com CNPJ, validar e enriquecer automaticamente",
            evento_trigger=TipoEvento.CONTA_CRIADA,
            acoes=[self._acao_validar_enriquecer],
            prioridade=1,
        ))

        # Regra 2: Ao avançar etapa 3 → exigir Objeto + Cronograma
        self.registrar_regra(Regra(
            id="R002",
            nome="Exigir objeto ao avançar para Descoberta",
            descricao="Ao avançar para etapa 3 (Descoberta), abrir checklist documental",
            evento_trigger=TipoEvento.OPORTUNIDADE_ETAPA_AVANCADA,
            condicao=lambda e: e.dados.get('etapa_destino') == 3,
            acoes=[self._acao_checklist_descoberta],
            prioridade=2,
        ))

        # Regra 3: Recusa registrada → abrir Contestação
        self.registrar_regra(Regra(
            id="R003",
            nome="Abrir contestação ao registrar recusa",
            descricao="Ao registrar recusa de seguradora, abrir tarefa de contestação "
                      "com prazo 48h e postar no Teams",
            evento_trigger=TipoEvento.RECUSA_REGISTRADA,
            acoes=[self._acao_abrir_contestacao, self._acao_alerta_teams_recusa],
            prioridade=1,
        ))

        # Regra 4: Marco contratual → tarefas e alertas
        self.registrar_regra(Regra(
            id="R004",
            nome="Alertar marcos contratuais",
            descricao="Ao detectar marco contratual próximo, criar tarefas "
                      "e enviar resumo para cliente",
            evento_trigger=TipoEvento.MARCO_CONTRATUAL,
            acoes=[self._acao_alerta_marco],
            prioridade=2,
        ))

        # Regra 5: Documento com validade a vencer → alertar
        self.registrar_regra(Regra(
            id="R005",
            nome="Alertar documento vencendo",
            descricao="Ao detectar documento com validade próxima ao vencimento, "
                      "alertar responsável e diretoria",
            evento_trigger=TipoEvento.DOCUMENTO_VENCENDO,
            acoes=[self._acao_alerta_documento_vencendo],
            prioridade=3,
        ))

        # Regra 6: Certidão vencendo → alertar
        self.registrar_regra(Regra(
            id="R006",
            nome="Alertar certidão vencendo",
            descricao="Ao detectar certidão próxima do vencimento, alertar",
            evento_trigger=TipoEvento.CERTIDAO_VENCENDO,
            acoes=[self._acao_alerta_certidao],
            prioridade=3,
        ))

    # === Ações padrão ===

    @staticmethod
    def _acao_validar_enriquecer(evento: Evento) -> AcaoAutomacao:
        cnpj = evento.dados.get('cnpj', '')
        return AcaoAutomacao(
            tipo="executar_job",
            descricao=f"Validar e enriquecer CNPJ: {cnpj}",
            dados={
                'job': 'enriquecer_conta',
                'conta_id': evento.dados.get('conta_id'),
                'cnpj': cnpj,
                'on_success': "marcar_dados_verificados",
                'on_failure': "criar_tarefa_completar_dados_24h",
            },
        )

    @staticmethod
    def _acao_checklist_descoberta(evento: Evento) -> AcaoAutomacao:
        return AcaoAutomacao(
            tipo="criar_tarefa",
            descricao="Abrir checklist documental (Descoberta / Objeto)",
            dados={
                'oportunidade_id': evento.dados.get('oportunidade_id'),
                'titulo': "Checklist Documental - Descoberta",
                'checklist': [
                    "Objeto contratual resumido",
                    "Cronograma físico-financeiro básico",
                    "Valor estimado da garantia",
                    "Vigência estimada",
                    "Cláusulas críticas identificadas",
                ],
                'sla_horas': 72,
            },
        )

    @staticmethod
    def _acao_abrir_contestacao(evento: Evento) -> AcaoAutomacao:
        return AcaoAutomacao(
            tipo="criar_tarefa",
            descricao="Contestação com prazo 48h",
            dados={
                'oportunidade_id': evento.dados.get('oportunidade_id'),
                'seguradora': evento.dados.get('seguradora'),
                'motivo_recusa': evento.dados.get('motivo_recusa'),
                'titulo': f"Contestação - {evento.dados.get('seguradora', 'N/A')}",
                'sla_horas': 48,
                'prioridade': 'alta',
                'checklist': [
                    "Ofício de contestação redigido",
                    "Estudo técnico anexado",
                    "Evidências compiladas",
                    "Contestação protocolada",
                ],
            },
        )

    @staticmethod
    def _acao_alerta_teams_recusa(evento: Evento) -> AcaoAutomacao:
        return AcaoAutomacao(
            tipo="enviar_alerta",
            descricao="Postar no Teams canal Operações Críticas",
            dados={
                'canal': 'teams',
                'canal_nome': 'Operações Críticas',
                'mensagem': (
                    f"Recusa registrada: {evento.dados.get('seguradora', 'N/A')}\n"
                    f"Oportunidade: {evento.dados.get('oportunidade_nome', 'N/A')}\n"
                    f"Motivo: {evento.dados.get('motivo_recusa', 'N/A')}\n"
                    f"Prazo contestação: 48h"
                ),
            },
        )

    @staticmethod
    def _acao_alerta_marco(evento: Evento) -> AcaoAutomacao:
        return AcaoAutomacao(
            tipo="criar_tarefa",
            descricao="Tarefa para marco contratual",
            dados={
                'oportunidade_id': evento.dados.get('oportunidade_id'),
                'titulo': f"Marco contratual: {evento.dados.get('descricao_marco', '')}",
                'dias_antecedencia': evento.dados.get('dias_antecedencia', 30),
                'enviar_resumo_cliente': True,
            },
        )

    @staticmethod
    def _acao_alerta_documento_vencendo(evento: Evento) -> AcaoAutomacao:
        return AcaoAutomacao(
            tipo="enviar_alerta",
            descricao="Alertar sobre documento vencendo",
            dados={
                'documento_id': evento.dados.get('documento_id'),
                'titulo': evento.dados.get('titulo_documento'),
                'dias_para_vencer': evento.dados.get('dias_para_vencer'),
                'destinatarios': ['responsavel', 'diretoria'],
                'mensagem': (
                    f"Documento '{evento.dados.get('titulo_documento', '')}' "
                    f"vence em {evento.dados.get('dias_para_vencer', '?')} dias. "
                    f"Risco de sinistro/descumprimento."
                ),
            },
        )

    @staticmethod
    def _acao_alerta_certidao(evento: Evento) -> AcaoAutomacao:
        return AcaoAutomacao(
            tipo="enviar_alerta",
            descricao="Alertar sobre certidão vencendo",
            dados={
                'conta_id': evento.dados.get('conta_id'),
                'tipo_certidao': evento.dados.get('tipo_certidao'),
                'dias_para_vencer': evento.dados.get('dias_para_vencer'),
                'destinatarios': ['responsavel'],
            },
        )

    def listar_regras(self) -> List[Dict]:
        """Lista todas as regras registradas"""
        return [
            {
                'id': r.id,
                'nome': r.nome,
                'evento': r.evento_trigger.value,
                'ativa': r.ativa,
                'prioridade': r.prioridade,
            }
            for r in self.regras
        ]

    def estatisticas(self) -> Dict:
        """Estatísticas do motor de regras"""
        total_processamentos = len(self.historico)
        total_acoes = sum(len(r.acoes_geradas) for r in self.historico)
        total_erros = sum(len(r.erros) for r in self.historico)

        return {
            'regras_registradas': len(self.regras),
            'regras_ativas': len([r for r in self.regras if r.ativa]),
            'total_processamentos': total_processamentos,
            'total_acoes_geradas': total_acoes,
            'total_erros': total_erros,
        }
