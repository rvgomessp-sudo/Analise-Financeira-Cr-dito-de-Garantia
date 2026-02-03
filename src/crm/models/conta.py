"""
Modelo de Conta (Empresa/PJ) - Centro do CRM

A Conta é o objeto central do CRM PJ-first.
Chave primária: CNPJ (com status e data de atualização).

Seções:
    Identidade: Razão Social, CNPJ, CNAE, Porte, etc.
    Estrutura & Risco: Quadro societário, indicadores financeiros, rating, limites.
    Operacional: Endereços, licenças, certidões, KYC.
    Sinais de mercado: Editais, notícias, mudanças societárias.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, List, Dict
from decimal import Decimal
import hashlib
import re


class PorteEmpresa(Enum):
    """Porte da empresa conforme classificação BNDES/Receita Federal"""
    MEI = "MEI (até R$ 81 mil/ano)"
    MICRO = "Micro (até R$ 360 mil/ano)"
    PEQUENO = "Pequeno (até R$ 4,8 milhões/ano)"
    MEDIO = "Médio (até R$ 300 milhões/ano)"
    GRANDE = "Grande (acima de R$ 300 milhões/ano)"


class TemperaturaLead(Enum):
    """Temperatura do lead conforme base PGFN Marco Zero"""
    HOT = "HOT — Já usa Seguro Garantia + valor descoberto"
    WARM = "WARM — Usa garantias ineficientes (carta fiança, depósito)"
    COLD = "COLD — Sem nenhuma garantia constituída"


class SituacaoCadastral(Enum):
    """Situação cadastral na Receita Federal"""
    ATIVA = "Ativa"
    SUSPENSA = "Suspensa"
    INAPTA = "Inapta"
    BAIXADA = "Baixada"
    NULA = "Nula"
    NAO_VERIFICADA = "Não Verificada"


class TipoEstabelecimento(Enum):
    """Tipo de estabelecimento"""
    MATRIZ = "Matriz"
    FILIAL = "Filial"


class StatusDados(Enum):
    """Status de verificação dos dados"""
    NAO_VERIFICADO = "Não Verificado"
    VERIFICADO = "Verificado (API)"
    VERIFICADO_MANUAL = "Verificado Manualmente"
    DESATUALIZADO = "Desatualizado"
    ERRO_VALIDACAO = "Erro na Validação"


@dataclass
class QuadroSocietario:
    """Membro do quadro societário"""
    nome: str
    cpf_cnpj: str
    qualificacao: str  # ex: Sócio-Administrador, Diretor, etc.
    percentual_participacao: Optional[float] = None
    data_entrada: Optional[date] = None
    representante_legal: bool = False


@dataclass
class IndicadoresFinanceiros:
    """Indicadores financeiros da conta (do último balanço disponível)"""
    data_referencia: date
    faturamento_anual: Optional[Decimal] = None
    ebitda: Optional[Decimal] = None
    lucro_liquido: Optional[Decimal] = None
    patrimonio_liquido: Optional[Decimal] = None
    divida_bruta: Optional[Decimal] = None
    divida_liquida: Optional[Decimal] = None
    ativo_total: Optional[Decimal] = None

    @property
    def liquidez_corrente(self) -> Optional[float]:
        """Calculado se houver dados disponíveis"""
        return None

    @property
    def alavancagem(self) -> Optional[float]:
        """Dívida Líquida / EBITDA"""
        if self.divida_liquida and self.ebitda and self.ebitda > 0:
            return float(self.divida_liquida / self.ebitda)
        return None

    @property
    def margem_ebitda(self) -> Optional[float]:
        """EBITDA / Faturamento"""
        if self.ebitda and self.faturamento_anual and self.faturamento_anual > 0:
            return float(self.ebitda / self.faturamento_anual * 100)
        return None


@dataclass
class LimiteSeguradora:
    """Limite histórico com seguradora"""
    seguradora: str
    valor_limite: Decimal
    data_aprovacao: date
    data_validade: Optional[date] = None
    status: str = "Ativo"  # Ativo, Expirado, Revogado
    observacoes: str = ""

    @property
    def vigente(self) -> bool:
        if self.data_validade and self.data_validade < date.today():
            return False
        return self.status == "Ativo"


@dataclass
class Sinistro:
    """Registro de sinistro/ocorrência"""
    data_ocorrencia: date
    seguradora: str
    tipo: str
    valor: Decimal
    status: str  # Aberto, Em Análise, Pago, Contestado, Encerrado
    descricao: str = ""
    data_resolucao: Optional[date] = None


@dataclass
class CertidaoDocumento:
    """Certidão ou documento KYC"""
    tipo: str  # CND Federal, CND Estadual, CND Municipal, FGTS, Trabalhista, etc.
    numero: str
    data_emissao: date
    data_validade: date
    status: str = "Válida"
    arquivo_path: Optional[str] = None

    @property
    def dias_para_vencer(self) -> int:
        return (self.data_validade - date.today()).days

    @property
    def vencida(self) -> bool:
        return self.data_validade < date.today()

    @property
    def vencendo_em_30_dias(self) -> bool:
        return 0 <= self.dias_para_vencer <= 30


@dataclass
class SinalMercado:
    """Sinal de mercado detectado (edital, notícia, mudança societária)"""
    data_deteccao: datetime
    tipo: str  # edital, noticia, mudanca_societaria, capex, renovacao_publica
    fonte: str
    titulo: str
    descricao: str
    relevancia: int = 3  # 1-5
    url: Optional[str] = None
    id_externo: Optional[str] = None  # ID do edital/órgão
    processado: bool = False


@dataclass
class Endereco:
    """Endereço (fiscal ou de obra/projeto)"""
    tipo: str  # Fiscal, Obra, Projeto, Filial
    logradouro: str
    numero: str
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    uf: str = ""
    cep: str = ""
    pais: str = "Brasil"


@dataclass
class DadosPGFN:
    """
    Dados da base PGFN (Procuradoria-Geral da Fazenda Nacional).

    Representa informações de dívidas ativas e garantias judiciais
    extraídas das bases Marco Zero (hot/warm/cold).

    Campos mapeados diretamente das colunas CSV:
        qtd_inscricoes, divida_total, ticket_medio, etc.
    """
    # Localização
    uf: str = ""
    regiao: str = ""

    # Quantidades
    qtd_inscricoes: int = 0
    divida_total: float = 0.0
    ticket_medio: float = 0.0
    ano_min: Optional[int] = None
    ano_max: Optional[int] = None

    # Garantias existentes
    qtd_seguro_garantia: int = 0
    qtd_carta_fianca: int = 0
    qtd_deposito: int = 0
    qtd_penhora: int = 0
    qtd_sem_garantia: int = 0

    # Valores de oportunidade
    valor_descoberto: float = 0.0
    valor_garantia_ineficiente: float = 0.0
    potencial_sg: float = 0.0

    @property
    def total_garantias(self) -> int:
        """Total de inscrições com alguma garantia"""
        return (self.qtd_seguro_garantia + self.qtd_carta_fianca +
                self.qtd_deposito + self.qtd_penhora)

    @property
    def percentual_coberto(self) -> float:
        """Percentual de inscrições cobertas por alguma garantia"""
        if self.qtd_inscricoes == 0:
            return 0.0
        return self.total_garantias / self.qtd_inscricoes * 100

    @property
    def percentual_sg(self) -> float:
        """Percentual coberto especificamente por Seguro Garantia"""
        if self.qtd_inscricoes == 0:
            return 0.0
        return self.qtd_seguro_garantia / self.qtd_inscricoes * 100

    @property
    def usa_seguro_garantia(self) -> bool:
        return self.qtd_seguro_garantia > 0

    @property
    def usa_garantia_ineficiente(self) -> bool:
        return (self.qtd_carta_fianca + self.qtd_deposito) > 0

    @property
    def anos_ativo(self) -> Optional[int]:
        """Número de anos com inscrições ativas"""
        if self.ano_min and self.ano_max:
            return self.ano_max - self.ano_min + 1
        return None

    def to_dict(self) -> Dict:
        return {
            'qtd_inscricoes': self.qtd_inscricoes,
            'divida_total': self.divida_total,
            'ticket_medio': self.ticket_medio,
            'ano_min': self.ano_min,
            'ano_max': self.ano_max,
            'qtd_seguro_garantia': self.qtd_seguro_garantia,
            'qtd_carta_fianca': self.qtd_carta_fianca,
            'qtd_deposito': self.qtd_deposito,
            'qtd_penhora': self.qtd_penhora,
            'qtd_sem_garantia': self.qtd_sem_garantia,
            'valor_descoberto': self.valor_descoberto,
            'valor_garantia_ineficiente': self.valor_garantia_ineficiente,
            'potencial_sg': self.potencial_sg,
            'total_garantias': self.total_garantias,
            'percentual_coberto': round(self.percentual_coberto, 1),
            'percentual_sg': round(self.percentual_sg, 1),
            'usa_seguro_garantia': self.usa_seguro_garantia,
            'anos_ativo': self.anos_ativo,
        }


@dataclass
class Conta:
    """
    Conta (Empresa/PJ) - Objeto central do CRM.

    Chave primária de negócio: CNPJ
    Todas as relações (Contato, Oportunidade, Documento) se vinculam à Conta.

    Seções:
        Identidade: dados cadastrais básicos
        Estrutura & Risco: indicadores, rating, limites, sinistros
        Operacional: endereços, certidões, KYC
        Sinais de mercado: editais, notícias, mudanças
        PGFN: dados da base PGFN Marco Zero
    """

    # === IDENTIDADE ===
    id: str
    cnpj: str  # Chave primária de negócio (14 dígitos, sem pontuação)
    razao_social: str
    nome_fantasia: str = ""
    situacao_cadastral: SituacaoCadastral = SituacaoCadastral.NAO_VERIFICADA
    porte: PorteEmpresa = PorteEmpresa.MEDIO
    cnae_principal: str = ""
    cnae_descricao: str = ""
    cnaes_secundarias: List[str] = field(default_factory=list)
    tipo_estabelecimento: TipoEstabelecimento = TipoEstabelecimento.MATRIZ
    grupo_economico: str = ""
    data_abertura: Optional[date] = None
    natureza_juridica: str = ""

    # === ESTRUTURA & RISCO ===
    quadro_societario: List[QuadroSocietario] = field(default_factory=list)
    indicadores_financeiros: Optional[IndicadoresFinanceiros] = None
    rating_interno: Optional[str] = None  # AAA, AA, A, BBB, BB, B, CCC, CC, C, D
    limites_seguradoras: List[LimiteSeguradora] = field(default_factory=list)
    sinistros: List[Sinistro] = field(default_factory=list)

    # === OPERACIONAL ===
    endereco_fiscal: Optional[Endereco] = None
    enderecos_obra: List[Endereco] = field(default_factory=list)
    certidoes: List[CertidaoDocumento] = field(default_factory=list)
    site: str = ""
    telefone_geral: str = ""
    email_geral: str = ""

    # === SINAIS DE MERCADO ===
    sinais_mercado: List[SinalMercado] = field(default_factory=list)

    # === STATUS DE DADOS ===
    status_dados: StatusDados = StatusDados.NAO_VERIFICADO
    data_ultima_verificacao: Optional[datetime] = None
    fonte_enriquecimento: str = ""  # API que enriqueceu
    dados_verificados: bool = False

    # === DADOS PGFN (Base Marco Zero) ===
    temperatura: Optional[TemperaturaLead] = None
    regiao: str = ""  # Região TRF (ex: "3ª Região (SP/MS)")
    dados_pgfn: Optional[DadosPGFN] = None

    # === CAMPOS CRM ===
    proprietario: str = ""  # Usuário responsável
    segmento: str = ""  # Segmento de mercado
    icp_fit: bool = False  # Se encaixa no ICP (Ideal Customer Profile)
    score_fit: Optional[float] = None  # 0-100 (maior = melhor fit)
    tags: List[str] = field(default_factory=list)

    # === DATAS ===
    data_criacao: datetime = field(default_factory=datetime.now)
    data_atualizacao: datetime = field(default_factory=datetime.now)

    # === OBSERVAÇÕES ===
    observacoes: str = ""

    def __post_init__(self):
        """Normaliza CNPJ ao criar"""
        self.cnpj = self.normalizar_cnpj(self.cnpj)

    @staticmethod
    def normalizar_cnpj(cnpj: str) -> str:
        """Remove formatação do CNPJ, mantendo apenas dígitos"""
        return re.sub(r'[^0-9]', '', cnpj)

    @staticmethod
    def formatar_cnpj(cnpj: str) -> str:
        """Formata CNPJ: XX.XXX.XXX/XXXX-XX"""
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj_limpo) != 14:
            return cnpj
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"

    @property
    def cnpj_formatado(self) -> str:
        return self.formatar_cnpj(self.cnpj)

    @property
    def cnpj_valido(self) -> bool:
        """Validação básica de CNPJ (14 dígitos)"""
        return len(self.cnpj) == 14 and self.cnpj.isdigit()

    @property
    def dados_completos(self) -> bool:
        """Verifica se campos obrigatórios estão preenchidos"""
        return all([
            self.cnpj_valido,
            self.razao_social,
            self.cnae_principal,
            self.porte,
            self.situacao_cadastral != SituacaoCadastral.NAO_VERIFICADA,
        ])

    @property
    def limites_vigentes(self) -> List[LimiteSeguradora]:
        return [l for l in self.limites_seguradoras if l.vigente]

    @property
    def certidoes_vencidas(self) -> List[CertidaoDocumento]:
        return [c for c in self.certidoes if c.vencida]

    @property
    def certidoes_vencendo(self) -> List[CertidaoDocumento]:
        return [c for c in self.certidoes if c.vencendo_em_30_dias]

    @property
    def sinistros_abertos(self) -> List[Sinistro]:
        return [s for s in self.sinistros if s.status in ("Aberto", "Em Análise")]

    @property
    def sinais_nao_processados(self) -> List[SinalMercado]:
        return [s for s in self.sinais_mercado if not s.processado]

    @property
    def completude_dados(self) -> Dict[str, bool]:
        """Retorna mapa de completude dos campos críticos"""
        return {
            'cnpj_valido': self.cnpj_valido,
            'razao_social': bool(self.razao_social),
            'cnae_principal': bool(self.cnae_principal),
            'porte': self.porte is not None,
            'situacao_verificada': self.situacao_cadastral != SituacaoCadastral.NAO_VERIFICADA,
            'endereco_fiscal': self.endereco_fiscal is not None,
            'telefone': bool(self.telefone_geral),
            'site': bool(self.site),
            'indicadores_financeiros': self.indicadores_financeiros is not None,
            'quadro_societario': len(self.quadro_societario) > 0,
        }

    @property
    def percentual_completude(self) -> float:
        """Percentual de completude dos campos críticos"""
        campos = self.completude_dados
        if not campos:
            return 0.0
        preenchidos = sum(1 for v in campos.values() if v)
        return preenchidos / len(campos) * 100

    def marcar_verificado(self, fonte: str = "API") -> None:
        """Marca dados como verificados"""
        self.dados_verificados = True
        self.status_dados = StatusDados.VERIFICADO if fonte == "API" else StatusDados.VERIFICADO_MANUAL
        self.data_ultima_verificacao = datetime.now()
        self.fonte_enriquecimento = fonte
        self.data_atualizacao = datetime.now()

    def adicionar_limite(self, seguradora: str, valor: Decimal,
                         data_aprovacao: date,
                         data_validade: Optional[date] = None) -> LimiteSeguradora:
        """Adiciona limite com seguradora"""
        limite = LimiteSeguradora(
            seguradora=seguradora,
            valor_limite=valor,
            data_aprovacao=data_aprovacao,
            data_validade=data_validade,
        )
        self.limites_seguradoras.append(limite)
        self.data_atualizacao = datetime.now()
        return limite

    def adicionar_sinistro(self, data_ocorrencia: date, seguradora: str,
                           tipo: str, valor: Decimal, descricao: str = "") -> Sinistro:
        """Registra sinistro"""
        sinistro = Sinistro(
            data_ocorrencia=data_ocorrencia,
            seguradora=seguradora,
            tipo=tipo,
            valor=valor,
            status="Aberto",
            descricao=descricao,
        )
        self.sinistros.append(sinistro)
        self.data_atualizacao = datetime.now()
        return sinistro

    def adicionar_sinal_mercado(self, tipo: str, fonte: str, titulo: str,
                                descricao: str, relevancia: int = 3,
                                url: str = None, id_externo: str = None) -> SinalMercado:
        """Registra sinal de mercado"""
        sinal = SinalMercado(
            data_deteccao=datetime.now(),
            tipo=tipo,
            fonte=fonte,
            titulo=titulo,
            descricao=descricao,
            relevancia=relevancia,
            url=url,
            id_externo=id_externo,
        )
        self.sinais_mercado.append(sinal)
        self.data_atualizacao = datetime.now()
        return sinal

    def to_dict(self) -> Dict:
        """Serializa conta para dicionário"""
        d = {
            'id': self.id,
            'cnpj': self.cnpj,
            'cnpj_formatado': self.cnpj_formatado,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'situacao_cadastral': self.situacao_cadastral.value,
            'porte': self.porte.value,
            'cnae_principal': self.cnae_principal,
            'cnae_descricao': self.cnae_descricao,
            'tipo_estabelecimento': self.tipo_estabelecimento.value,
            'grupo_economico': self.grupo_economico,
            'rating_interno': self.rating_interno,
            'dados_verificados': self.dados_verificados,
            'score_fit': self.score_fit,
            'percentual_completude': self.percentual_completude,
            'limites_vigentes': len(self.limites_vigentes),
            'sinistros_abertos': len(self.sinistros_abertos),
            'sinais_pendentes': len(self.sinais_nao_processados),
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat(),
        }
        if self.temperatura:
            d['temperatura'] = self.temperatura.name
        if self.regiao:
            d['regiao'] = self.regiao
        if self.dados_pgfn:
            d['dados_pgfn'] = self.dados_pgfn.to_dict()
        return d

    def __repr__(self) -> str:
        return (f"Conta(cnpj={self.cnpj_formatado}, "
                f"razao_social='{self.razao_social}', "
                f"porte={self.porte.name})")
