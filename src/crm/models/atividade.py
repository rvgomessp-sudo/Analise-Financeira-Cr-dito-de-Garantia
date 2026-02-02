"""
Modelo de Atividades & Cadências

Gerencia ligações, e-mails, reuniões e tarefas por etapa do pipeline,
com SLA de retorno e checklist por fase.
Suporta cadências de prospecção consultiva com etapas programadas.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Dict


class TipoAtividade(Enum):
    """Tipo de atividade"""
    LIGACAO = "Ligação"
    EMAIL = "E-mail"
    REUNIAO = "Reunião"
    TAREFA = "Tarefa"
    WHATSAPP = "WhatsApp"
    LINKEDIN = "LinkedIn"
    VISITA = "Visita Presencial"
    ENVIO_DOCUMENTO = "Envio de Documento"
    FOLLOW_UP = "Follow-up"
    CONTESTACAO = "Contestação"
    ANALISE_INTERNA = "Análise Interna"


class StatusAtividade(Enum):
    """Status da atividade"""
    PENDENTE = "Pendente"
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"
    CANCELADA = "Cancelada"
    ATRASADA = "Atrasada"
    REAGENDADA = "Reagendada"


class PrioridadeAtividade(Enum):
    """Prioridade da atividade"""
    CRITICA = "Crítica"
    ALTA = "Alta"
    MEDIA = "Média"
    BAIXA = "Baixa"


@dataclass
class ChecklistItemAtividade:
    """Item de checklist dentro de uma atividade"""
    descricao: str
    obrigatorio: bool = True
    concluido: bool = False
    data_conclusao: Optional[datetime] = None

    def concluir(self) -> None:
        self.concluido = True
        self.data_conclusao = datetime.now()


@dataclass
class Atividade:
    """
    Atividade vinculada a uma conta, contato ou oportunidade.

    Registra ligações, e-mails, reuniões, tarefas por etapa
    com SLA de retorno e checklist.
    """

    # Identificação
    id: str
    tipo: TipoAtividade
    titulo: str
    descricao: str = ""

    # Vínculos
    conta_id: Optional[str] = None
    contato_id: Optional[str] = None
    oportunidade_id: Optional[str] = None

    # Status e prioridade
    status: StatusAtividade = StatusAtividade.PENDENTE
    prioridade: PrioridadeAtividade = PrioridadeAtividade.MEDIA

    # Agendamento
    data_agendada: Optional[datetime] = None
    data_vencimento: Optional[datetime] = None
    duracao_minutos: Optional[int] = None

    # SLA
    sla_horas: Optional[int] = None  # Horas para completar
    sla_alertado: bool = False

    # Execução
    data_inicio: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    resultado: str = ""  # Resultado/desfecho
    proxima_acao: str = ""  # Próxima ação definida

    # Checklist
    checklist: List[ChecklistItemAtividade] = field(default_factory=list)

    # Responsável
    responsavel: str = ""
    delegado_por: str = ""

    # Datas
    data_criacao: datetime = field(default_factory=datetime.now)
    data_atualizacao: datetime = field(default_factory=datetime.now)

    @property
    def atrasada(self) -> bool:
        if self.data_vencimento and self.status == StatusAtividade.PENDENTE:
            return datetime.now() > self.data_vencimento
        return False

    @property
    def sla_estourado(self) -> bool:
        if self.sla_horas and self.data_criacao:
            limite = self.data_criacao + timedelta(hours=self.sla_horas)
            return datetime.now() > limite and self.status not in (
                StatusAtividade.CONCLUIDA, StatusAtividade.CANCELADA
            )
        return False

    @property
    def checklist_completo(self) -> bool:
        obrigatorios = [c for c in self.checklist if c.obrigatorio]
        if not obrigatorios:
            return True
        return all(c.concluido for c in obrigatorios)

    @property
    def percentual_checklist(self) -> float:
        if not self.checklist:
            return 100.0
        concluidos = sum(1 for c in self.checklist if c.concluido)
        return concluidos / len(self.checklist) * 100

    def iniciar(self) -> None:
        """Marca atividade como em andamento"""
        self.status = StatusAtividade.EM_ANDAMENTO
        self.data_inicio = datetime.now()
        self.data_atualizacao = datetime.now()

    def concluir(self, resultado: str = "", proxima_acao: str = "") -> None:
        """Marca atividade como concluída"""
        self.status = StatusAtividade.CONCLUIDA
        self.data_conclusao = datetime.now()
        self.resultado = resultado
        self.proxima_acao = proxima_acao
        self.data_atualizacao = datetime.now()

    def cancelar(self, motivo: str = "") -> None:
        """Cancela a atividade"""
        self.status = StatusAtividade.CANCELADA
        self.resultado = f"Cancelada: {motivo}" if motivo else "Cancelada"
        self.data_atualizacao = datetime.now()

    def reagendar(self, nova_data: datetime) -> None:
        """Reagenda a atividade"""
        self.status = StatusAtividade.REAGENDADA
        self.data_agendada = nova_data
        self.data_atualizacao = datetime.now()

    def adicionar_checklist(self, descricao: str, obrigatorio: bool = True) -> ChecklistItemAtividade:
        """Adiciona item ao checklist"""
        item = ChecklistItemAtividade(descricao=descricao, obrigatorio=obrigatorio)
        self.checklist.append(item)
        return item

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'tipo': self.tipo.value,
            'titulo': self.titulo,
            'status': self.status.value,
            'prioridade': self.prioridade.value,
            'conta_id': self.conta_id,
            'contato_id': self.contato_id,
            'oportunidade_id': self.oportunidade_id,
            'data_agendada': self.data_agendada.isoformat() if self.data_agendada else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'atrasada': self.atrasada,
            'sla_estourado': self.sla_estourado,
            'checklist_pct': self.percentual_checklist,
            'responsavel': self.responsavel,
        }


@dataclass
class EtapaCadencia:
    """Etapa dentro de uma cadência de prospecção"""
    numero: int
    dia_offset: int  # Dias após início da cadência
    tipo: TipoAtividade
    titulo: str
    descricao: str
    template: str = ""  # Template de mensagem/script
    obrigatoria: bool = True

    @property
    def atividade_padrao(self) -> Dict:
        """Retorna configuração para criar atividade"""
        return {
            'tipo': self.tipo,
            'titulo': self.titulo,
            'descricao': self.descricao,
        }


@dataclass
class Cadencia:
    """
    Cadência de prospecção consultiva.

    Sequência de atividades programadas (ligações, e-mails, reuniões)
    com intervalos definidos, vinculada a conta + contato.
    """

    # Identificação
    id: str
    nome: str
    descricao: str = ""

    # Etapas
    etapas: List[EtapaCadencia] = field(default_factory=list)

    # Vinculação
    conta_id: Optional[str] = None
    contato_id: Optional[str] = None
    oportunidade_id: Optional[str] = None

    # Execução
    data_inicio: Optional[datetime] = None
    etapa_atual: int = 0
    ativa: bool = True

    # Métricas
    respostas_obtidas: int = 0
    reunioes_agendadas: int = 0

    # Datas
    data_criacao: datetime = field(default_factory=datetime.now)

    @property
    def duracao_total_dias(self) -> int:
        """Duração total da cadência em dias"""
        if not self.etapas:
            return 0
        return max(e.dia_offset for e in self.etapas)

    @property
    def percentual_concluido(self) -> float:
        if not self.etapas:
            return 0.0
        return self.etapa_atual / len(self.etapas) * 100

    @property
    def proxima_etapa(self) -> Optional[EtapaCadencia]:
        if self.etapa_atual < len(self.etapas):
            return self.etapas[self.etapa_atual]
        return None

    @property
    def data_proxima_acao(self) -> Optional[datetime]:
        if self.data_inicio and self.proxima_etapa:
            return self.data_inicio + timedelta(days=self.proxima_etapa.dia_offset)
        return None

    def iniciar(self) -> None:
        """Inicia a cadência"""
        self.data_inicio = datetime.now()
        self.etapa_atual = 0
        self.ativa = True

    def avancar(self, resposta_obtida: bool = False) -> Optional[EtapaCadencia]:
        """Avança para próxima etapa. Retorna etapa avançada ou None"""
        if resposta_obtida:
            self.respostas_obtidas += 1
        if self.etapa_atual < len(self.etapas):
            etapa = self.etapas[self.etapa_atual]
            self.etapa_atual += 1
            return etapa
        self.ativa = False
        return None

    def pausar(self) -> None:
        """Pausa a cadência"""
        self.ativa = False

    def retomar(self) -> None:
        """Retoma a cadência"""
        self.ativa = True

    def gerar_atividades(self) -> List[Dict]:
        """Gera lista de atividades a partir das etapas restantes"""
        atividades = []
        for etapa in self.etapas[self.etapa_atual:]:
            data_agendada = None
            if self.data_inicio:
                data_agendada = self.data_inicio + timedelta(days=etapa.dia_offset)
            atividades.append({
                'tipo': etapa.tipo,
                'titulo': etapa.titulo,
                'descricao': etapa.descricao,
                'template': etapa.template,
                'data_agendada': data_agendada,
                'obrigatoria': etapa.obrigatoria,
            })
        return atividades

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'nome': self.nome,
            'etapas_total': len(self.etapas),
            'etapa_atual': self.etapa_atual,
            'percentual_concluido': self.percentual_concluido,
            'ativa': self.ativa,
            'respostas': self.respostas_obtidas,
            'reunioes': self.reunioes_agendadas,
            'data_proxima_acao': self.data_proxima_acao.isoformat() if self.data_proxima_acao else None,
        }


# === Fábricas de Cadências ===

def criar_cadencia_prospeccao_consultiva(
    id: str,
    conta_id: str,
    contato_id: str,
    nome: str = "Cadência Consultiva Padrão",
) -> Cadencia:
    """
    Cria cadência de prospecção consultiva padrão (90 dias).

    Sequência: pesquisa → conexão → conteúdo → valor → reunião → follow-up
    """
    etapas = [
        EtapaCadencia(
            numero=1, dia_offset=0,
            tipo=TipoAtividade.LINKEDIN,
            titulo="Conexão LinkedIn + pesquisa",
            descricao="Conectar no LinkedIn, pesquisar empresa e contexto. "
                      "Identificar projetos, editais, necessidades.",
        ),
        EtapaCadencia(
            numero=2, dia_offset=2,
            tipo=TipoAtividade.EMAIL,
            titulo="E-mail de abertura consultivo",
            descricao="E-mail personalizado referenciando contexto específico "
                      "(edital, projeto, desafio do setor). Sem pitch.",
            template="Assunto: {contexto_especifico}\n\n"
                     "Olá {nome},\n\n"
                     "Identifiquei que a {empresa} está envolvida em {contexto}. "
                     "Temos trabalhado com empresas do setor em desafios semelhantes "
                     "de garantias...",
        ),
        EtapaCadencia(
            numero=3, dia_offset=5,
            tipo=TipoAtividade.LIGACAO,
            titulo="Ligação de referência ao e-mail",
            descricao="Ligar referenciando e-mail enviado. "
                      "Objetivo: entender contexto, não vender.",
        ),
        EtapaCadencia(
            numero=4, dia_offset=10,
            tipo=TipoAtividade.EMAIL,
            titulo="E-mail com conteúdo de valor",
            descricao="Enviar artigo, caso de sucesso ou insight relevante "
                      "para o contexto do prospect.",
        ),
        EtapaCadencia(
            numero=5, dia_offset=17,
            tipo=TipoAtividade.LIGACAO,
            titulo="Ligação de follow-up + convite reunião",
            descricao="Follow-up sobre conteúdo enviado. "
                      "Propor reunião técnica (não comercial).",
        ),
        EtapaCadencia(
            numero=6, dia_offset=25,
            tipo=TipoAtividade.EMAIL,
            titulo="E-mail com caso similar",
            descricao="Compartilhar caso de sucesso similar ao contexto do prospect.",
        ),
        EtapaCadencia(
            numero=7, dia_offset=35,
            tipo=TipoAtividade.LIGACAO,
            titulo="Ligação - proposta de diagnóstico",
            descricao="Propor diagnóstico técnico gratuito ou de baixo custo "
                      "para mapear necessidades de garantias.",
        ),
        EtapaCadencia(
            numero=8, dia_offset=50,
            tipo=TipoAtividade.EMAIL,
            titulo="E-mail de reengajamento",
            descricao="Se não houve resposta: e-mail direto questionando "
                      "se o timing é adequado, oferecendo retomar no futuro.",
            obrigatoria=False,
        ),
        EtapaCadencia(
            numero=9, dia_offset=70,
            tipo=TipoAtividade.LINKEDIN,
            titulo="Interação LinkedIn + conteúdo",
            descricao="Engajar com conteúdo do prospect no LinkedIn. "
                      "Compartilhar insight relevante.",
            obrigatoria=False,
        ),
        EtapaCadencia(
            numero=10, dia_offset=90,
            tipo=TipoAtividade.EMAIL,
            titulo="E-mail de encerramento / nurturing",
            descricao="Última tentativa ou transição para nurturing de longo prazo.",
            obrigatoria=False,
        ),
    ]

    return Cadencia(
        id=id,
        nome=nome,
        etapas=etapas,
        conta_id=conta_id,
        contato_id=contato_id,
    )
