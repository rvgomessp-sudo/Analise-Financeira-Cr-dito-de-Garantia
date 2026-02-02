"""
Modelo de Documentos

Gestão de propostas, contratos, apólices, aditivos, estudos técnicos,
laudos e certidões com controle de versão e metadados
(tipo, validade, vínculo com conta/oportunidade).
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict
import hashlib


class TipoDocumento(Enum):
    """Tipo de documento"""
    PROPOSTA = "Proposta"
    CONTRATO = "Contrato"
    APOLICE = "Apólice"
    ADITIVO = "Aditivo"
    ESTUDO_TECNICO = "Estudo Técnico"
    LAUDO = "Laudo"
    CERTIDAO = "Certidão"
    OFICIO = "Ofício"
    CONTESTACAO = "Contestação"
    PARECER = "Parecer"
    BALANCO = "Balanço"
    EDITAL = "Edital"
    ATA = "Ata"
    PROCURACAO = "Procuração"
    KYC = "Documento KYC"
    OUTRO = "Outro"


class StatusDocumento(Enum):
    """Status do documento"""
    RASCUNHO = "Rascunho"
    EM_REVISAO = "Em Revisão"
    APROVADO = "Aprovado"
    VIGENTE = "Vigente"
    VENCIDO = "Vencido"
    CANCELADO = "Cancelado"
    ARQUIVADO = "Arquivado"


class NivelConfidencialidade(Enum):
    """Nível de confidencialidade"""
    PUBLICO = "Público"
    INTERNO = "Interno"
    CONFIDENCIAL = "Confidencial"
    RESTRITO = "Restrito"


@dataclass
class VersaoDocumento:
    """Versão individual de um documento"""
    numero_versao: int
    arquivo_path: str
    hash_sha256: str
    data_criacao: datetime = field(default_factory=datetime.now)
    criado_por: str = ""
    descricao_alteracao: str = ""
    tamanho_bytes: int = 0

    @staticmethod
    def calcular_hash(conteudo: bytes) -> str:
        """Calcula SHA-256 do conteúdo do arquivo"""
        return hashlib.sha256(conteudo).hexdigest()


@dataclass
class AcessoDocumento:
    """Registro de acesso a documento"""
    usuario: str
    data: datetime
    acao: str  # visualizacao, download, edicao, impressao
    ip: str = ""


@dataclass
class Documento:
    """
    Documento vinculado a conta e/ou oportunidade.

    Controle de versão, metadados, confidencialidade e auditoria de acesso.
    Política de retenção por tipo de documento.
    """

    # Identificação
    id: str
    titulo: str
    tipo: TipoDocumento

    # Vínculos
    conta_id: Optional[str] = None
    oportunidade_id: Optional[str] = None

    # Status
    status: StatusDocumento = StatusDocumento.RASCUNHO
    confidencialidade: NivelConfidencialidade = NivelConfidencialidade.INTERNO

    # Metadados
    descricao: str = ""
    tags: List[str] = field(default_factory=list)
    data_validade: Optional[date] = None
    numero_referencia: str = ""  # Número do contrato, apólice, etc.

    # Versões
    versoes: List[VersaoDocumento] = field(default_factory=list)

    # Auditoria
    acessos: List[AcessoDocumento] = field(default_factory=list)

    # Responsável
    responsavel: str = ""

    # Retenção
    politica_retencao_anos: int = 5  # Padrão: 5 anos

    # Datas
    data_criacao: datetime = field(default_factory=datetime.now)
    data_atualizacao: datetime = field(default_factory=datetime.now)

    @property
    def versao_atual(self) -> Optional[VersaoDocumento]:
        if self.versoes:
            return self.versoes[-1]
        return None

    @property
    def numero_versoes(self) -> int:
        return len(self.versoes)

    @property
    def vencido(self) -> bool:
        if self.data_validade:
            return self.data_validade < date.today()
        return False

    @property
    def dias_para_vencer(self) -> Optional[int]:
        if self.data_validade:
            return (self.data_validade - date.today()).days
        return None

    @property
    def data_descarte(self) -> Optional[date]:
        """Data prevista para descarte baseada na política de retenção"""
        if self.versoes:
            ultima = self.versoes[-1].data_criacao.date()
            return date(
                ultima.year + self.politica_retencao_anos,
                ultima.month,
                ultima.day,
            )
        return None

    def adicionar_versao(self, arquivo_path: str, hash_sha256: str,
                         criado_por: str = "",
                         descricao: str = "",
                         tamanho: int = 0) -> VersaoDocumento:
        """Adiciona nova versão do documento"""
        numero = len(self.versoes) + 1
        versao = VersaoDocumento(
            numero_versao=numero,
            arquivo_path=arquivo_path,
            hash_sha256=hash_sha256,
            criado_por=criado_por,
            descricao_alteracao=descricao,
            tamanho_bytes=tamanho,
        )
        self.versoes.append(versao)
        self.data_atualizacao = datetime.now()
        return versao

    def registrar_acesso(self, usuario: str, acao: str = "visualizacao",
                         ip: str = "") -> AcessoDocumento:
        """Registra acesso ao documento"""
        acesso = AcessoDocumento(
            usuario=usuario,
            data=datetime.now(),
            acao=acao,
            ip=ip,
        )
        self.acessos.append(acesso)
        return acesso

    def definir_retencao(self) -> None:
        """Define política de retenção baseada no tipo"""
        politicas = {
            TipoDocumento.APOLICE: 10,
            TipoDocumento.CONTRATO: 10,
            TipoDocumento.ESTUDO_TECNICO: 10,
            TipoDocumento.CONTESTACAO: 10,
            TipoDocumento.OFICIO: 10,
            TipoDocumento.LAUDO: 10,
            TipoDocumento.CERTIDAO: 5,
            TipoDocumento.PROPOSTA: 5,
            TipoDocumento.BALANCO: 7,
            TipoDocumento.KYC: 5,
            TipoDocumento.EDITAL: 5,
        }
        self.politica_retencao_anos = politicas.get(self.tipo, 5)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo': self.tipo.value,
            'status': self.status.value,
            'confidencialidade': self.confidencialidade.value,
            'conta_id': self.conta_id,
            'oportunidade_id': self.oportunidade_id,
            'versao_atual': self.versao_atual.numero_versao if self.versao_atual else 0,
            'numero_versoes': self.numero_versoes,
            'vencido': self.vencido,
            'dias_para_vencer': self.dias_para_vencer,
            'total_acessos': len(self.acessos),
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat(),
        }

    def __repr__(self) -> str:
        return (f"Documento(titulo='{self.titulo}', "
                f"tipo={self.tipo.name}, v{self.numero_versoes})")
