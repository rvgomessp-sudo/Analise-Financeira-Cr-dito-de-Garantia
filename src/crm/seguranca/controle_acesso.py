"""
Controle de Acesso Baseado em Papéis (RBAC)

Papéis:
    Comercial: leitura/edição limitada
    Técnico: estudos/risco
    Jurídico: cláusulas/contratos
    Diretoria: acesso total
    Parceiros: acesso restrito
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Set


class Permissao(Enum):
    """Permissões granulares do sistema"""
    # Contas
    CONTA_VISUALIZAR = "conta.visualizar"
    CONTA_CRIAR = "conta.criar"
    CONTA_EDITAR = "conta.editar"
    CONTA_EXCLUIR = "conta.excluir"

    # Contatos
    CONTATO_VISUALIZAR = "contato.visualizar"
    CONTATO_CRIAR = "contato.criar"
    CONTATO_EDITAR = "contato.editar"
    CONTATO_DADOS_PESSOAIS = "contato.dados_pessoais"

    # Oportunidades
    OPORTUNIDADE_VISUALIZAR = "oportunidade.visualizar"
    OPORTUNIDADE_CRIAR = "oportunidade.criar"
    OPORTUNIDADE_EDITAR = "oportunidade.editar"
    OPORTUNIDADE_AVANCAR_ETAPA = "oportunidade.avancar_etapa"
    OPORTUNIDADE_FECHAR = "oportunidade.fechar"

    # Risco
    RISCO_VISUALIZAR = "risco.visualizar"
    RISCO_CRIAR = "risco.criar"
    RISCO_EDITAR = "risco.editar"

    # Estudos Técnicos
    ESTUDO_VISUALIZAR = "estudo.visualizar"
    ESTUDO_CRIAR = "estudo.criar"
    ESTUDO_EDITAR = "estudo.editar"
    ESTUDO_DOWNLOAD = "estudo.download"

    # Documentos
    DOCUMENTO_VISUALIZAR = "documento.visualizar"
    DOCUMENTO_CRIAR = "documento.criar"
    DOCUMENTO_EDITAR = "documento.editar"
    DOCUMENTO_EXCLUIR = "documento.excluir"
    DOCUMENTO_CONFIDENCIAL = "documento.confidencial"

    # Dashboard
    DASHBOARD_VISUALIZAR = "dashboard.visualizar"
    DASHBOARD_EXECUTIVO = "dashboard.executivo"

    # Administração
    ADMIN_USUARIOS = "admin.usuarios"
    ADMIN_CONFIGURACOES = "admin.configuracoes"
    ADMIN_AUDITORIA = "admin.auditoria"


class TipoPerfil(Enum):
    """Tipos de perfil padrão"""
    COMERCIAL = "Comercial"
    TECNICO = "Técnico"
    JURIDICO = "Jurídico"
    DIRETORIA = "Diretoria"
    PARCEIRO = "Parceiro"
    ADMIN = "Administrador"


@dataclass
class Perfil:
    """Perfil de acesso com permissões"""
    nome: str
    tipo: TipoPerfil
    descricao: str = ""
    permissoes: Set[Permissao] = field(default_factory=set)
    ativo: bool = True

    def tem_permissao(self, permissao: Permissao) -> bool:
        return permissao in self.permissoes

    def adicionar_permissao(self, permissao: Permissao) -> None:
        self.permissoes.add(permissao)

    def remover_permissao(self, permissao: Permissao) -> None:
        self.permissoes.discard(permissao)

    def to_dict(self) -> Dict:
        return {
            'nome': self.nome,
            'tipo': self.tipo.value,
            'permissoes': [p.value for p in self.permissoes],
            'ativo': self.ativo,
        }


@dataclass
class Usuario:
    """Usuário do CRM"""
    id: str
    nome: str
    email: str
    perfil: Perfil
    ativo: bool = True
    data_criacao: datetime = field(default_factory=datetime.now)
    ultimo_acesso: Optional[datetime] = None


@dataclass
class LogAcesso:
    """Log de auditoria de acesso"""
    usuario_id: str
    acao: str
    recurso: str
    recurso_id: str
    permitido: bool
    data: datetime = field(default_factory=datetime.now)
    ip: str = ""
    detalhes: str = ""


class ControleAcesso:
    """
    Motor de controle de acesso baseado em papéis (RBAC).

    Gerencia perfis, usuários e verificação de permissões.
    Mantém log de auditoria para todas as verificações.
    """

    def __init__(self):
        self.perfis: Dict[str, Perfil] = {}
        self.usuarios: Dict[str, Usuario] = {}
        self.logs: List[LogAcesso] = []
        self._criar_perfis_padrao()

    def _criar_perfis_padrao(self) -> None:
        """Cria os perfis padrão do sistema"""

        # COMERCIAL: leitura/edição limitada
        comercial = Perfil(
            nome="Comercial",
            tipo=TipoPerfil.COMERCIAL,
            descricao="Acesso comercial: contas, contatos, oportunidades (leitura/edição limitada)",
            permissoes={
                Permissao.CONTA_VISUALIZAR, Permissao.CONTA_CRIAR, Permissao.CONTA_EDITAR,
                Permissao.CONTATO_VISUALIZAR, Permissao.CONTATO_CRIAR, Permissao.CONTATO_EDITAR,
                Permissao.OPORTUNIDADE_VISUALIZAR, Permissao.OPORTUNIDADE_CRIAR,
                Permissao.OPORTUNIDADE_EDITAR, Permissao.OPORTUNIDADE_AVANCAR_ETAPA,
                Permissao.RISCO_VISUALIZAR,
                Permissao.DOCUMENTO_VISUALIZAR, Permissao.DOCUMENTO_CRIAR,
                Permissao.DASHBOARD_VISUALIZAR,
            },
        )
        self.perfis["comercial"] = comercial

        # TÉCNICO: estudos e risco
        tecnico = Perfil(
            nome="Técnico",
            tipo=TipoPerfil.TECNICO,
            descricao="Acesso técnico: estudos, risco, documentos especializados",
            permissoes={
                Permissao.CONTA_VISUALIZAR,
                Permissao.CONTATO_VISUALIZAR,
                Permissao.OPORTUNIDADE_VISUALIZAR, Permissao.OPORTUNIDADE_EDITAR,
                Permissao.RISCO_VISUALIZAR, Permissao.RISCO_CRIAR, Permissao.RISCO_EDITAR,
                Permissao.ESTUDO_VISUALIZAR, Permissao.ESTUDO_CRIAR,
                Permissao.ESTUDO_EDITAR, Permissao.ESTUDO_DOWNLOAD,
                Permissao.DOCUMENTO_VISUALIZAR, Permissao.DOCUMENTO_CRIAR,
                Permissao.DOCUMENTO_EDITAR,
                Permissao.DASHBOARD_VISUALIZAR,
            },
        )
        self.perfis["tecnico"] = tecnico

        # JURÍDICO: cláusulas e contratos
        juridico = Perfil(
            nome="Jurídico",
            tipo=TipoPerfil.JURIDICO,
            descricao="Acesso jurídico: contratos, cláusulas, contestações",
            permissoes={
                Permissao.CONTA_VISUALIZAR,
                Permissao.CONTATO_VISUALIZAR,
                Permissao.OPORTUNIDADE_VISUALIZAR,
                Permissao.RISCO_VISUALIZAR,
                Permissao.ESTUDO_VISUALIZAR, Permissao.ESTUDO_DOWNLOAD,
                Permissao.DOCUMENTO_VISUALIZAR, Permissao.DOCUMENTO_CRIAR,
                Permissao.DOCUMENTO_EDITAR, Permissao.DOCUMENTO_CONFIDENCIAL,
                Permissao.DASHBOARD_VISUALIZAR,
            },
        )
        self.perfis["juridico"] = juridico

        # DIRETORIA: acesso total
        diretoria = Perfil(
            nome="Diretoria",
            tipo=TipoPerfil.DIRETORIA,
            descricao="Acesso total: todas as funcionalidades",
            permissoes=set(Permissao),  # Todas as permissões
        )
        self.perfis["diretoria"] = diretoria

        # PARCEIRO: acesso restrito
        parceiro = Perfil(
            nome="Parceiro",
            tipo=TipoPerfil.PARCEIRO,
            descricao="Acesso restrito: apenas visualização de informações compartilhadas",
            permissoes={
                Permissao.CONTA_VISUALIZAR,
                Permissao.OPORTUNIDADE_VISUALIZAR,
                Permissao.DOCUMENTO_VISUALIZAR,
            },
        )
        self.perfis["parceiro"] = parceiro

        # ADMIN: gerenciamento do sistema
        admin = Perfil(
            nome="Administrador",
            tipo=TipoPerfil.ADMIN,
            descricao="Administração: gerenciamento de usuários e configurações",
            permissoes=set(Permissao),
        )
        self.perfis["admin"] = admin

    def verificar_permissao(self, usuario_id: str, permissao: Permissao,
                            recurso_id: str = "", ip: str = "") -> bool:
        """
        Verifica se o usuário tem permissão.
        Registra log de auditoria.
        """
        usuario = self.usuarios.get(usuario_id)

        if not usuario or not usuario.ativo:
            self._registrar_log(usuario_id, permissao.value, "", recurso_id, False, ip)
            return False

        if not usuario.perfil.ativo:
            self._registrar_log(usuario_id, permissao.value, "", recurso_id, False, ip)
            return False

        permitido = usuario.perfil.tem_permissao(permissao)
        self._registrar_log(
            usuario_id, permissao.value,
            usuario.perfil.nome, recurso_id,
            permitido, ip,
        )
        return permitido

    def registrar_usuario(self, id: str, nome: str, email: str,
                           perfil_nome: str) -> Optional[Usuario]:
        """Registra novo usuário"""
        perfil = self.perfis.get(perfil_nome.lower())
        if not perfil:
            return None

        usuario = Usuario(
            id=id,
            nome=nome,
            email=email,
            perfil=perfil,
        )
        self.usuarios[id] = usuario
        return usuario

    def alterar_perfil(self, usuario_id: str, novo_perfil_nome: str) -> bool:
        """Altera perfil de um usuário"""
        usuario = self.usuarios.get(usuario_id)
        perfil = self.perfis.get(novo_perfil_nome.lower())
        if not usuario or not perfil:
            return False
        usuario.perfil = perfil
        return True

    def _registrar_log(self, usuario_id: str, acao: str, perfil: str,
                        recurso_id: str, permitido: bool, ip: str = "") -> None:
        """Registra log de auditoria"""
        self.logs.append(LogAcesso(
            usuario_id=usuario_id,
            acao=acao,
            recurso=perfil,
            recurso_id=recurso_id,
            permitido=permitido,
            ip=ip,
        ))

    def logs_usuario(self, usuario_id: str,
                      limite: int = 100) -> List[LogAcesso]:
        """Retorna logs de um usuário"""
        logs = [l for l in self.logs if l.usuario_id == usuario_id]
        return logs[-limite:]

    def logs_negados(self, limite: int = 100) -> List[LogAcesso]:
        """Retorna acessos negados (para auditoria)"""
        negados = [l for l in self.logs if not l.permitido]
        return negados[-limite:]

    def resumo_acessos(self) -> Dict:
        """Resumo de acessos para auditoria"""
        total = len(self.logs)
        permitidos = sum(1 for l in self.logs if l.permitido)
        negados = total - permitidos

        por_usuario = {}
        for log in self.logs:
            por_usuario[log.usuario_id] = por_usuario.get(log.usuario_id, 0) + 1

        return {
            'total_verificacoes': total,
            'permitidos': permitidos,
            'negados': negados,
            'taxa_negacao': negados / total * 100 if total > 0 else 0,
            'por_usuario': por_usuario,
            'usuarios_ativos': len(self.usuarios),
        }
