"""
Modelo de Contato (Pessoa Física dentro da PJ)

Representa decisores e influenciadores dentro de uma Conta.
Inclui mapeamento de stakeholders (MAPA), canais de comunicação
e controle LGPD (opt-in/propósitos).
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict


class AreaContato(Enum):
    """Área funcional do contato na empresa"""
    COMPRAS = "Compras"
    ENGENHARIA = "Engenharia"
    FINANCEIRO = "Financeiro"
    JURIDICO = "Jurídico"
    DIRETORIA = "Diretoria"
    PRESIDENCIA = "Presidência"
    COMERCIAL = "Comercial"
    OPERACOES = "Operações"
    TI = "Tecnologia da Informação"
    RH = "Recursos Humanos"
    OUTRO = "Outro"


class NivelInfluencia(Enum):
    """Nível de influência/autoridade no processo de decisão (MAPA de stakeholders)"""
    DECISOR = "Decisor Final"
    INFLUENCIADOR = "Influenciador"
    USUARIO = "Usuário / Executor"
    GATEKEEPER = "Gatekeeper"
    CHAMPION = "Champion (Patrocinador Interno)"
    BLOQUEADOR = "Potencial Bloqueador"


class StatusContato(Enum):
    """Status do contato"""
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    SAIU_DA_EMPRESA = "Saiu da Empresa"
    NAO_RESPONDE = "Não Responde"


class CanalPreferido(Enum):
    """Canal preferido de comunicação"""
    EMAIL = "E-mail"
    TELEFONE = "Telefone"
    WHATSAPP = "WhatsApp"
    LINKEDIN = "LinkedIn"
    PRESENCIAL = "Presencial"
    TEAMS = "Microsoft Teams"


@dataclass
class ConsentimentoLGPD:
    """Registro de consentimento LGPD"""
    proposito: str  # ex: "Comunicação Comercial", "Envio de Propostas"
    consentido: bool
    data_consentimento: datetime
    meio_obtencao: str  # "E-mail", "Formulário", "Verbal (registrado)"
    base_legal: str = "Consentimento"  # Consentimento, Legítimo Interesse, Execução Contratual
    data_revogacao: Optional[datetime] = None

    @property
    def ativo(self) -> bool:
        return self.consentido and self.data_revogacao is None

    def revogar(self) -> None:
        """Revoga o consentimento"""
        self.data_revogacao = datetime.now()


@dataclass
class InteracaoContato:
    """Registro de interação com o contato"""
    data: datetime
    tipo: str  # Ligação, E-mail, Reunião, WhatsApp
    direcao: str  # Inbound, Outbound
    resumo: str
    proxima_acao: str = ""
    usuario_responsavel: str = ""


@dataclass
class Contato:
    """
    Contato (Pessoa Física dentro da PJ).

    Vinculado a uma Conta (empresa).
    Inclui mapeamento de stakeholders, canais e controle LGPD.
    """

    # Identificação
    id: str
    conta_id: str  # FK para Conta

    # Dados pessoais
    nome: str
    cargo: str
    area: AreaContato = AreaContato.OUTRO
    nivel_influencia: NivelInfluencia = NivelInfluencia.USUARIO

    # Canais de comunicação
    email: str = ""
    telefone: str = ""
    celular: str = ""
    linkedin: str = ""
    canal_preferido: CanalPreferido = CanalPreferido.EMAIL

    # Status
    status: StatusContato = StatusContato.ATIVO
    principal: bool = False  # Contato principal da conta

    # LGPD
    consentimentos: List[ConsentimentoLGPD] = field(default_factory=list)

    # Interações
    interacoes: List[InteracaoContato] = field(default_factory=list)

    # Notas de relacionamento
    notas_relacionamento: str = ""
    interesse_demonstrado: str = ""  # O que especificamente interessa ao contato
    objecoes_conhecidas: List[str] = field(default_factory=list)

    # Datas
    data_criacao: datetime = field(default_factory=datetime.now)
    data_ultimo_contato: Optional[datetime] = None
    data_atualizacao: datetime = field(default_factory=datetime.now)

    @property
    def tem_consentimento_comercial(self) -> bool:
        """Verifica se tem consentimento ativo para comunicação comercial"""
        return any(
            c.ativo and c.proposito in ("Comunicação Comercial", "Envio de Propostas")
            for c in self.consentimentos
        )

    @property
    def dias_sem_contato(self) -> Optional[int]:
        if not self.data_ultimo_contato:
            return None
        return (datetime.now() - self.data_ultimo_contato).days

    @property
    def total_interacoes(self) -> int:
        return len(self.interacoes)

    def registrar_consentimento(self, proposito: str, meio: str,
                                base_legal: str = "Consentimento") -> ConsentimentoLGPD:
        """Registra novo consentimento LGPD"""
        consent = ConsentimentoLGPD(
            proposito=proposito,
            consentido=True,
            data_consentimento=datetime.now(),
            meio_obtencao=meio,
            base_legal=base_legal,
        )
        self.consentimentos.append(consent)
        self.data_atualizacao = datetime.now()
        return consent

    def revogar_consentimento(self, proposito: str) -> bool:
        """Revoga consentimento para um propósito específico"""
        for c in self.consentimentos:
            if c.proposito == proposito and c.ativo:
                c.revogar()
                self.data_atualizacao = datetime.now()
                return True
        return False

    def registrar_interacao(self, tipo: str, direcao: str, resumo: str,
                            proxima_acao: str = "",
                            usuario: str = "") -> InteracaoContato:
        """Registra interação com o contato"""
        interacao = InteracaoContato(
            data=datetime.now(),
            tipo=tipo,
            direcao=direcao,
            resumo=resumo,
            proxima_acao=proxima_acao,
            usuario_responsavel=usuario,
        )
        self.interacoes.append(interacao)
        self.data_ultimo_contato = datetime.now()
        self.data_atualizacao = datetime.now()
        return interacao

    def to_dict(self, mascarar_dados: bool = False) -> Dict:
        """Serializa contato. mascarar_dados=True para LGPD"""
        dados = {
            'id': self.id,
            'conta_id': self.conta_id,
            'nome': self.nome if not mascarar_dados else self._mascarar_nome(),
            'cargo': self.cargo,
            'area': self.area.value,
            'nivel_influencia': self.nivel_influencia.value,
            'email': self.email if not mascarar_dados else self._mascarar_email(),
            'telefone': self.telefone if not mascarar_dados else "***-****",
            'canal_preferido': self.canal_preferido.value,
            'status': self.status.value,
            'principal': self.principal,
            'tem_consentimento_comercial': self.tem_consentimento_comercial,
            'total_interacoes': self.total_interacoes,
            'dias_sem_contato': self.dias_sem_contato,
            'data_ultimo_contato': self.data_ultimo_contato.isoformat() if self.data_ultimo_contato else None,
        }
        return dados

    def _mascarar_nome(self) -> str:
        """Mascara nome para LGPD"""
        partes = self.nome.split()
        if len(partes) <= 1:
            return self.nome[0] + "***" if self.nome else ""
        return partes[0] + " " + "***"

    def _mascarar_email(self) -> str:
        """Mascara email para LGPD"""
        if "@" not in self.email:
            return "***"
        usuario, dominio = self.email.split("@", 1)
        return usuario[:2] + "***@" + dominio

    def __repr__(self) -> str:
        return (f"Contato(nome='{self.nome}', cargo='{self.cargo}', "
                f"area={self.area.name}, influencia={self.nivel_influencia.name})")
