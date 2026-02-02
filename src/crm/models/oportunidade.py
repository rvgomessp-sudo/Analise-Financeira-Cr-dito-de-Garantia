"""
Modelo de Oportunidade (Deal)

Amarra contrato/objeto, risco, seguradora e fluxo.
Inclui: tipo de garantia, objeto contratual, montantes, matriz de risco,
contragarantias, mercado segurador, economia da operação, governança.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict
from decimal import Decimal
import hashlib


class TipoGarantiaOportunidade(Enum):
    """Tipo de garantia da oportunidade"""
    PARTICIPACAO = "Participação (Bid Bond)"
    PERFORMANCE = "Performance"
    ADIANTAMENTO = "Adiantamento de Pagamento"
    JUDICIAL = "Judicial"
    ICMS = "ICMS"
    ADUANEIRA = "Aduaneira"
    FINANCEIRA = "Financeira"
    MANUTENCAO = "Manutenção"
    RETENCAO = "Retenção"
    OUTRO = "Outro"


class EtapaOportunidade(Enum):
    """Etapa no pipeline comercial"""
    PESQUISA_SINAIS = "1. Pesquisa & Sinais"
    QUALIFICACAO_PJ = "2. Qualificação PJ"
    DESCOBERTA_OBJETO = "3. Descoberta / Objeto"
    PRE_RISCO = "4. Pré-Risco"
    ESTRUTURACAO_SUBMISSAO = "5. Estruturação / Submissão"
    NEGOCIACAO = "6. Negociação"
    FECHAMENTO_EMISSAO = "7. Fechamento / Emissão"
    POS_EMISSAO = "8. Pós-Emissão / Monitoramento"
    PERDIDA = "Perdida"
    CANCELADA = "Cancelada"


class CategoriaRisco(Enum):
    """Categoria de risco na matriz"""
    ENGENHARIA = "Engenharia"
    FINANCEIRO = "Financeiro"
    JURIDICO = "Jurídico"
    REGULATORIO = "Regulatório"
    AMBIENTAL = "Ambiental"
    OPERACIONAL = "Operacional"


class NivelRisco(Enum):
    """Nível de risco"""
    BAIXO = "Baixo"
    MODERADO = "Moderado"
    ALTO = "Alto"
    CRITICO = "Crítico"


class TipoContragarantia(Enum):
    """Tipo de contragarantia"""
    FIANCA_PESSOAL = "Fiança Pessoal"
    FIANCA_CORPORATIVA = "Fiança Corporativa"
    CESSAO_RECEBIVEIS = "Cessão de Recebíveis"
    PENHOR_ATIVOS = "Penhor de Ativos"
    HIPOTECA = "Hipoteca"
    FUNDO_GARANTIDOR = "Fundo Garantidor"
    CARTA_CREDITO = "Carta de Crédito"
    SEGURO_CREDITO = "Seguro de Crédito"
    DEPOSITO_CAUCAO = "Depósito Caução"
    OUTRO = "Outro"


class StatusSeguradoraOportunidade(Enum):
    """Status da seguradora na oportunidade"""
    NAO_ABORDADA = "Não Abordada"
    EM_ANALISE = "Em Análise"
    APROVADA = "Aprovada"
    RECUSADA = "Recusada"
    PENDENTE_DOCUMENTOS = "Pendente de Documentos"
    EM_CONTESTACAO = "Em Contestação"


@dataclass
class ItemRiscoMatriz:
    """Item individual da matriz de risco"""
    categoria: CategoriaRisco
    descricao: str
    nivel: NivelRisco
    probabilidade: int  # 1-5
    impacto: int  # 1-5
    mitigacao: str = ""
    responsavel: str = ""
    data_identificacao: date = field(default_factory=date.today)

    @property
    def score_risco(self) -> int:
        """Score = Probabilidade x Impacto"""
        return self.probabilidade * self.impacto

    @property
    def semaforo(self) -> str:
        """Verde/Amarelo/Vermelho baseado no score"""
        s = self.score_risco
        if s <= 6:
            return "verde"
        elif s <= 15:
            return "amarelo"
        return "vermelho"


@dataclass
class MatrizRisco:
    """Matriz de risco completa (engenharia/financeiro/jurídico)"""
    itens: List[ItemRiscoMatriz] = field(default_factory=list)
    lgd_assumida: Optional[float] = None  # Loss Given Default (%)
    data_elaboracao: date = field(default_factory=date.today)
    responsavel: str = ""
    observacoes: str = ""

    def adicionar_risco(self, categoria: CategoriaRisco, descricao: str,
                        nivel: NivelRisco, probabilidade: int, impacto: int,
                        mitigacao: str = "") -> ItemRiscoMatriz:
        item = ItemRiscoMatriz(
            categoria=categoria,
            descricao=descricao,
            nivel=nivel,
            probabilidade=probabilidade,
            impacto=impacto,
            mitigacao=mitigacao,
        )
        self.itens.append(item)
        return item

    @property
    def score_medio(self) -> float:
        if not self.itens:
            return 0.0
        return sum(i.score_risco for i in self.itens) / len(self.itens)

    @property
    def riscos_criticos(self) -> List[ItemRiscoMatriz]:
        return [i for i in self.itens if i.semaforo == "vermelho"]

    @property
    def semaforo_geral(self) -> str:
        if any(i.semaforo == "vermelho" for i in self.itens):
            return "vermelho"
        if any(i.semaforo == "amarelo" for i in self.itens):
            return "amarelo"
        return "verde"

    @property
    def tem_mitigacoes_completas(self) -> bool:
        return all(i.mitigacao for i in self.itens)


@dataclass
class Contragarantia:
    """Contragarantia vinculada à oportunidade"""
    tipo: TipoContragarantia
    descricao: str
    valor: Optional[Decimal] = None
    percentual_cobertura: Optional[float] = None
    status: str = "Proposta"  # Proposta, Aceita, Formalizada, Liberada
    garantidor: str = ""  # Quem fornece a garantia
    data_formalizacao: Optional[date] = None
    data_validade: Optional[date] = None
    observacoes: str = ""


@dataclass
class StatusSeguradora:
    """Status de uma seguradora/resseguradora na oportunidade"""
    nome: str
    tipo: str = "Seguradora"  # Seguradora, Resseguradora
    status: StatusSeguradoraOportunidade = StatusSeguradoraOportunidade.NAO_ABORDADA
    data_submissao: Optional[date] = None
    data_resposta: Optional[date] = None
    razao_recusa: str = ""
    oficio_contestacao: str = ""
    observacoes: str = ""
    contato_subscritor: str = ""

    @property
    def dias_em_analise(self) -> Optional[int]:
        if not self.data_submissao:
            return None
        fim = self.data_resposta or date.today()
        return (fim - self.data_submissao).days


@dataclass
class EconomiaOperacao:
    """Economia da operação (taxa, prêmio, comissão, custos, margem)"""
    taxa_praticada: Optional[float] = None  # % ao ano
    premio_anual: Optional[Decimal] = None
    premio_total: Optional[Decimal] = None
    comissao_percentual: Optional[float] = None  # %
    comissao_valor: Optional[Decimal] = None
    custos_operacionais: Optional[Decimal] = None
    honorarios: Optional[Decimal] = None

    @property
    def margem(self) -> Optional[Decimal]:
        """Margem = Comissão + Honorários - Custos"""
        if self.comissao_valor is not None and self.custos_operacionais is not None:
            receita = (self.comissao_valor or Decimal('0')) + (self.honorarios or Decimal('0'))
            return receita - self.custos_operacionais
        return None

    @property
    def margem_percentual(self) -> Optional[float]:
        """Margem % sobre receita total"""
        if self.margem is not None:
            receita = (self.comissao_valor or Decimal('0')) + (self.honorarios or Decimal('0'))
            if receita > 0:
                return float(self.margem / receita * 100)
        return None


@dataclass
class EstudoTecnico:
    """Versão de estudo técnico vinculada à oportunidade (com controle PI)"""
    id: str
    versao: int
    titulo: str
    arquivo_path: str
    hash_arquivo: str  # SHA-256 para integridade
    data_criacao: datetime = field(default_factory=datetime.now)
    autor: str = ""
    resumo: str = ""
    acessos: List[Dict] = field(default_factory=list)  # [{usuario, data, acao}]

    def registrar_acesso(self, usuario: str, acao: str = "visualizacao") -> None:
        """Registra acesso ao estudo técnico"""
        self.acessos.append({
            'usuario': usuario,
            'data': datetime.now().isoformat(),
            'acao': acao,
        })

    @staticmethod
    def calcular_hash(conteudo: bytes) -> str:
        """Calcula SHA-256 do conteúdo"""
        return hashlib.sha256(conteudo).hexdigest()


@dataclass
class ObjetoContratual:
    """Objeto contratual detalhado"""
    descricao_resumida: str
    escopo_tecnico: str = ""
    cronograma_fisico_financeiro: str = ""
    kpis: List[str] = field(default_factory=list)
    clausulas_criticas: List[str] = field(default_factory=list)  # reajuste, multas, retomada
    data_inicio_prevista: Optional[date] = None
    data_fim_prevista: Optional[date] = None
    valor_total_contrato: Optional[Decimal] = None


@dataclass
class Oportunidade:
    """
    Oportunidade (Deal) no pipeline de garantias.

    Vinculada a uma Conta e associada a Contatos.
    Amarra contrato/objeto, risco, seguradora e fluxo.
    """

    # Identificação
    id: str
    conta_id: str  # FK para Conta
    nome: str

    # Tipo e Etapa
    tipo_garantia: TipoGarantiaOportunidade
    etapa: EtapaOportunidade = EtapaOportunidade.PESQUISA_SINAIS

    # Objeto Contratual
    objeto_contratual: Optional[ObjetoContratual] = None

    # Montantes
    valor_contrato: Optional[Decimal] = None
    valor_garantia: Optional[Decimal] = None
    vigencia_meses: Optional[int] = None
    data_inicio_vigencia: Optional[date] = None
    data_fim_vigencia: Optional[date] = None
    renovacao_prevista: bool = False
    cronograma_liberacoes: str = ""

    # Risco
    matriz_risco: Optional[MatrizRisco] = None
    contragarantias: List[Contragarantia] = field(default_factory=list)

    # Mercado Segurador
    seguradoras: List[StatusSeguradora] = field(default_factory=list)

    # Economia
    economia: Optional[EconomiaOperacao] = None

    # Governança - Estudos Técnicos
    estudos_tecnicos: List[EstudoTecnico] = field(default_factory=list)

    # Contatos envolvidos
    contatos_ids: List[str] = field(default_factory=list)

    # Scoring
    score_propensao: Optional[float] = None  # 0-100
    probabilidade_fechamento: Optional[float] = None  # %

    # Datas
    data_criacao: datetime = field(default_factory=datetime.now)
    data_atualizacao: datetime = field(default_factory=datetime.now)
    data_previsao_fechamento: Optional[date] = None
    data_fechamento_real: Optional[date] = None

    # Responsável
    proprietario: str = ""
    equipe: List[str] = field(default_factory=list)

    # Motivo perda
    motivo_perda: str = ""
    concorrente_vencedor: str = ""

    # Observações
    observacoes: str = ""

    @property
    def etapa_numero(self) -> int:
        """Número da etapa atual (1-8)"""
        mapa = {
            EtapaOportunidade.PESQUISA_SINAIS: 1,
            EtapaOportunidade.QUALIFICACAO_PJ: 2,
            EtapaOportunidade.DESCOBERTA_OBJETO: 3,
            EtapaOportunidade.PRE_RISCO: 4,
            EtapaOportunidade.ESTRUTURACAO_SUBMISSAO: 5,
            EtapaOportunidade.NEGOCIACAO: 6,
            EtapaOportunidade.FECHAMENTO_EMISSAO: 7,
            EtapaOportunidade.POS_EMISSAO: 8,
        }
        return mapa.get(self.etapa, 0)

    @property
    def aberta(self) -> bool:
        return self.etapa not in (
            EtapaOportunidade.PERDIDA,
            EtapaOportunidade.CANCELADA,
        )

    @property
    def fechada_ganha(self) -> bool:
        return self.etapa in (
            EtapaOportunidade.FECHAMENTO_EMISSAO,
            EtapaOportunidade.POS_EMISSAO,
        ) and self.data_fechamento_real is not None

    @property
    def dias_no_pipeline(self) -> int:
        return (datetime.now() - self.data_criacao).days

    @property
    def valor_ponderado(self) -> Optional[Decimal]:
        """Valor ponderado pela probabilidade"""
        if self.valor_garantia and self.probabilidade_fechamento:
            return self.valor_garantia * Decimal(str(self.probabilidade_fechamento / 100))
        return None

    @property
    def tem_objeto_contratual(self) -> bool:
        return self.objeto_contratual is not None and bool(self.objeto_contratual.descricao_resumida)

    @property
    def tem_matriz_risco(self) -> bool:
        return self.matriz_risco is not None and len(self.matriz_risco.itens) > 0

    @property
    def tem_contragarantias(self) -> bool:
        return len(self.contragarantias) > 0

    @property
    def seguradoras_aprovadas(self) -> List[StatusSeguradora]:
        return [s for s in self.seguradoras
                if s.status == StatusSeguradoraOportunidade.APROVADA]

    @property
    def seguradoras_recusadas(self) -> List[StatusSeguradora]:
        return [s for s in self.seguradoras
                if s.status == StatusSeguradoraOportunidade.RECUSADA]

    @property
    def seguradoras_em_contestacao(self) -> List[StatusSeguradora]:
        return [s for s in self.seguradoras
                if s.status == StatusSeguradoraOportunidade.EM_CONTESTACAO]

    def avancar_etapa(self) -> bool:
        """Tenta avançar para próxima etapa. Retorna False se não for possível."""
        ordem = [
            EtapaOportunidade.PESQUISA_SINAIS,
            EtapaOportunidade.QUALIFICACAO_PJ,
            EtapaOportunidade.DESCOBERTA_OBJETO,
            EtapaOportunidade.PRE_RISCO,
            EtapaOportunidade.ESTRUTURACAO_SUBMISSAO,
            EtapaOportunidade.NEGOCIACAO,
            EtapaOportunidade.FECHAMENTO_EMISSAO,
            EtapaOportunidade.POS_EMISSAO,
        ]
        try:
            idx = ordem.index(self.etapa)
            if idx < len(ordem) - 1:
                self.etapa = ordem[idx + 1]
                self.data_atualizacao = datetime.now()
                return True
        except ValueError:
            pass
        return False

    def marcar_perdida(self, motivo: str, concorrente: str = "") -> None:
        """Marca oportunidade como perdida"""
        self.etapa = EtapaOportunidade.PERDIDA
        self.motivo_perda = motivo
        self.concorrente_vencedor = concorrente
        self.data_atualizacao = datetime.now()

    def marcar_cancelada(self, motivo: str) -> None:
        """Marca oportunidade como cancelada"""
        self.etapa = EtapaOportunidade.CANCELADA
        self.motivo_perda = motivo
        self.data_atualizacao = datetime.now()

    def adicionar_seguradora(self, nome: str, tipo: str = "Seguradora") -> StatusSeguradora:
        """Adiciona seguradora à oportunidade"""
        seg = StatusSeguradora(nome=nome, tipo=tipo)
        self.seguradoras.append(seg)
        self.data_atualizacao = datetime.now()
        return seg

    def registrar_recusa(self, nome_seguradora: str, razao: str) -> bool:
        """Registra recusa de seguradora"""
        for seg in self.seguradoras:
            if seg.nome == nome_seguradora:
                seg.status = StatusSeguradoraOportunidade.RECUSADA
                seg.razao_recusa = razao
                seg.data_resposta = date.today()
                self.data_atualizacao = datetime.now()
                return True
        return False

    def registrar_aprovacao(self, nome_seguradora: str) -> bool:
        """Registra aprovação de seguradora"""
        for seg in self.seguradoras:
            if seg.nome == nome_seguradora:
                seg.status = StatusSeguradoraOportunidade.APROVADA
                seg.data_resposta = date.today()
                self.data_atualizacao = datetime.now()
                return True
        return False

    def adicionar_contragarantia(self, tipo: TipoContragarantia, descricao: str,
                                  valor: Decimal = None,
                                  garantidor: str = "") -> Contragarantia:
        """Adiciona contragarantia"""
        cg = Contragarantia(
            tipo=tipo,
            descricao=descricao,
            valor=valor,
            garantidor=garantidor,
        )
        self.contragarantias.append(cg)
        self.data_atualizacao = datetime.now()
        return cg

    def adicionar_estudo_tecnico(self, id_estudo: str, titulo: str,
                                  arquivo_path: str, hash_arquivo: str,
                                  autor: str = "", resumo: str = "") -> EstudoTecnico:
        """Adiciona versão de estudo técnico"""
        versao = len(self.estudos_tecnicos) + 1
        estudo = EstudoTecnico(
            id=id_estudo,
            versao=versao,
            titulo=titulo,
            arquivo_path=arquivo_path,
            hash_arquivo=hash_arquivo,
            autor=autor,
            resumo=resumo,
        )
        self.estudos_tecnicos.append(estudo)
        self.data_atualizacao = datetime.now()
        return estudo

    def to_dict(self) -> Dict:
        """Serializa oportunidade para dicionário"""
        return {
            'id': self.id,
            'conta_id': self.conta_id,
            'nome': self.nome,
            'tipo_garantia': self.tipo_garantia.value,
            'etapa': self.etapa.value,
            'etapa_numero': self.etapa_numero,
            'valor_contrato': str(self.valor_contrato) if self.valor_contrato else None,
            'valor_garantia': str(self.valor_garantia) if self.valor_garantia else None,
            'valor_ponderado': str(self.valor_ponderado) if self.valor_ponderado else None,
            'vigencia_meses': self.vigencia_meses,
            'tem_objeto_contratual': self.tem_objeto_contratual,
            'tem_matriz_risco': self.tem_matriz_risco,
            'tem_contragarantias': self.tem_contragarantias,
            'score_propensao': self.score_propensao,
            'probabilidade_fechamento': self.probabilidade_fechamento,
            'seguradoras_aprovadas': len(self.seguradoras_aprovadas),
            'seguradoras_recusadas': len(self.seguradoras_recusadas),
            'economia': {
                'taxa': self.economia.taxa_praticada,
                'premio_total': str(self.economia.premio_total) if self.economia and self.economia.premio_total else None,
                'margem_pct': self.economia.margem_percentual if self.economia else None,
            } if self.economia else None,
            'dias_no_pipeline': self.dias_no_pipeline,
            'data_previsao_fechamento': self.data_previsao_fechamento.isoformat() if self.data_previsao_fechamento else None,
            'proprietario': self.proprietario,
            'aberta': self.aberta,
        }

    def __repr__(self) -> str:
        return (f"Oportunidade(nome='{self.nome}', "
                f"tipo={self.tipo_garantia.name}, "
                f"etapa={self.etapa.value})")
