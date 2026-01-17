"""
Modelos de dados para captura de editais com exigência de rating.

Este módulo define as estruturas de dados utilizadas para representar
editais, exigências de rating e resultados de busca.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class FonteEdital(Enum):
    """Fontes de onde os editais podem ser capturados."""
    PNCP = "Portal Nacional de Contratações Públicas"
    AMAZONAS = "Portal de Compras do Amazonas"
    COMPRASNET = "ComprasNet"
    TCE_AM = "TCE Amazonas"
    MANAUS = "Portal de Compras Manaus"
    OUTRO = "Outra Fonte"


class TipoLicitacao(Enum):
    """Tipos de procedimentos licitatórios."""
    PREGAO_ELETRONICO = "Pregão Eletrônico"
    PREGAO_PRESENCIAL = "Pregão Presencial"
    CONCORRENCIA = "Concorrência"
    TOMADA_PRECOS = "Tomada de Preços"
    CONVITE = "Convite"
    CONCURSO = "Concurso"
    LEILAO = "Leilão"
    DISPENSA = "Dispensa de Licitação"
    INEXIGIBILIDADE = "Inexigibilidade"
    RDC = "Regime Diferenciado de Contratações"
    DIALOGO_COMPETITIVO = "Diálogo Competitivo"
    OUTRO = "Outro"


class TipoGarantia(Enum):
    """Tipos de garantia exigidos em licitações."""
    SEGURO_GARANTIA = "Seguro Garantia"
    FIANCA_BANCARIA = "Fiança Bancária"
    CAUCAO_DINHEIRO = "Caução em Dinheiro"
    TITULO_DIVIDA_PUBLICA = "Título da Dívida Pública"
    MULTIPLA = "Múltiplas Opções"
    NAO_ESPECIFICADO = "Não Especificado"


class NivelRating(Enum):
    """Níveis de rating exigidos."""
    AAA = "AAA"
    AA_PLUS = "AA+"
    AA = "AA"
    AA_MINUS = "AA-"
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    BBB_PLUS = "BBB+"
    BBB = "BBB"
    BBB_MINUS = "BBB-"
    BB_PLUS = "BB+"
    BB = "BB"
    INVESTIMENTO = "Grau de Investimento"
    NAO_ESPECIFICADO = "Não Especificado"


class AgenciaRating(Enum):
    """Agências de classificação de risco reconhecidas."""
    SP = "Standard & Poor's"
    MOODYS = "Moody's"
    FITCH = "Fitch Ratings"
    AM_BEST = "A.M. Best"
    AUSTIN = "Austin Rating"
    LF_RATING = "LF Rating"
    SR_RATING = "SR Rating"
    QUALQUER = "Qualquer Agência Reconhecida"
    NAO_ESPECIFICADO = "Não Especificado"


class StatusEdital(Enum):
    """Status do edital."""
    ABERTO = "Aberto"
    EM_ANDAMENTO = "Em Andamento"
    SUSPENSO = "Suspenso"
    CANCELADO = "Cancelado"
    ENCERRADO = "Encerrado"
    HOMOLOGADO = "Homologado"
    DESCONHECIDO = "Desconhecido"


@dataclass
class ExigenciaRating:
    """
    Representa uma exigência de rating encontrada em um edital.

    Attributes:
        encontrada: Se foi encontrada exigência de rating
        nivel_minimo: Nível mínimo de rating exigido
        agencias_aceitas: Lista de agências aceitas
        texto_original: Texto original do edital sobre rating
        clausula_referencia: Referência da cláusula no edital
        escala_nacional: Se aceita escala nacional (vs global)
        permite_grupo: Se aceita rating do grupo econômico
        observacoes: Observações adicionais
    """
    encontrada: bool = False
    nivel_minimo: NivelRating = NivelRating.NAO_ESPECIFICADO
    agencias_aceitas: List[AgenciaRating] = field(default_factory=list)
    texto_original: str = ""
    clausula_referencia: str = ""
    escala_nacional: Optional[bool] = None
    permite_grupo: Optional[bool] = None
    observacoes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'encontrada': self.encontrada,
            'nivel_minimo': self.nivel_minimo.value,
            'agencias_aceitas': [a.value for a in self.agencias_aceitas],
            'texto_original': self.texto_original,
            'clausula_referencia': self.clausula_referencia,
            'escala_nacional': self.escala_nacional,
            'permite_grupo': self.permite_grupo,
            'observacoes': self.observacoes
        }


@dataclass
class Edital:
    """
    Representa um edital de licitação capturado.

    Attributes:
        id_fonte: Identificador único na fonte
        numero_edital: Número do edital
        orgao: Órgão responsável
        objeto: Objeto da licitação
        fonte: Fonte de onde foi capturado
        url: URL do edital
        data_publicacao: Data de publicação
        data_abertura: Data de abertura das propostas
        valor_estimado: Valor estimado da contratação
        tipo_licitacao: Tipo de procedimento licitatório
        tipo_garantia: Tipo de garantia exigida
        percentual_garantia: Percentual de garantia exigido
        exigencia_rating: Detalhes da exigência de rating
        uf: Unidade Federativa
        municipio: Município
        status: Status atual do edital
        texto_completo: Texto completo do edital (se disponível)
        data_captura: Data/hora da captura
        hash_conteudo: Hash do conteúdo para detectar alterações
        metadata: Metadados adicionais
    """
    id_fonte: str
    numero_edital: str
    orgao: str
    objeto: str
    fonte: FonteEdital
    url: str

    data_publicacao: Optional[datetime] = None
    data_abertura: Optional[datetime] = None
    valor_estimado: Optional[float] = None
    tipo_licitacao: TipoLicitacao = TipoLicitacao.OUTRO
    tipo_garantia: TipoGarantia = TipoGarantia.NAO_ESPECIFICADO
    percentual_garantia: Optional[float] = None

    exigencia_rating: ExigenciaRating = field(default_factory=ExigenciaRating)

    uf: str = ""
    municipio: str = ""
    status: StatusEdital = StatusEdital.DESCONHECIDO

    texto_completo: str = ""
    data_captura: datetime = field(default_factory=datetime.now)
    hash_conteudo: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def tem_exigencia_rating(self) -> bool:
        """Verifica se o edital tem exigência de rating."""
        return self.exigencia_rating.encontrada

    @property
    def eh_amazonas(self) -> bool:
        """Verifica se o edital é do Amazonas."""
        return self.uf.upper() in ['AM', 'AMAZONAS']

    @property
    def valor_garantia_estimado(self) -> Optional[float]:
        """Calcula o valor estimado da garantia."""
        if self.valor_estimado and self.percentual_garantia:
            return self.valor_estimado * (self.percentual_garantia / 100)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'id_fonte': self.id_fonte,
            'numero_edital': self.numero_edital,
            'orgao': self.orgao,
            'objeto': self.objeto,
            'fonte': self.fonte.value,
            'url': self.url,
            'data_publicacao': self.data_publicacao.isoformat() if self.data_publicacao else None,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'valor_estimado': self.valor_estimado,
            'tipo_licitacao': self.tipo_licitacao.value,
            'tipo_garantia': self.tipo_garantia.value,
            'percentual_garantia': self.percentual_garantia,
            'exigencia_rating': self.exigencia_rating.to_dict(),
            'uf': self.uf,
            'municipio': self.municipio,
            'status': self.status.value,
            'data_captura': self.data_captura.isoformat(),
            'tem_exigencia_rating': self.tem_exigencia_rating,
            'eh_amazonas': self.eh_amazonas,
            'valor_garantia_estimado': self.valor_garantia_estimado,
            'metadata': self.metadata
        }

    def resumo(self) -> str:
        """Retorna um resumo do edital."""
        linhas = [
            f"{'='*60}",
            f"EDITAL: {self.numero_edital}",
            f"{'='*60}",
            f"Órgão: {self.orgao}",
            f"UF/Município: {self.uf}/{self.municipio}",
            f"Objeto: {self.objeto[:100]}..." if len(self.objeto) > 100 else f"Objeto: {self.objeto}",
            f"Valor Estimado: R$ {self.valor_estimado:,.2f}" if self.valor_estimado else "Valor Estimado: Não informado",
            f"Tipo: {self.tipo_licitacao.value}",
            f"Status: {self.status.value}",
            f"Data Abertura: {self.data_abertura.strftime('%d/%m/%Y %H:%M') if self.data_abertura else 'Não informada'}",
        ]

        if self.tem_exigencia_rating:
            linhas.extend([
                f"\n>>> EXIGÊNCIA DE RATING DETECTADA <<<",
                f"Nível Mínimo: {self.exigencia_rating.nivel_minimo.value}",
                f"Agências: {', '.join([a.value for a in self.exigencia_rating.agencias_aceitas]) or 'Não especificadas'}",
            ])
            if self.exigencia_rating.texto_original:
                linhas.append(f"Texto: \"{self.exigencia_rating.texto_original[:200]}...\"")

        linhas.extend([
            f"\nURL: {self.url}",
            f"Fonte: {self.fonte.value}",
            f"Capturado em: {self.data_captura.strftime('%d/%m/%Y %H:%M')}",
            f"{'='*60}"
        ])

        return '\n'.join(linhas)


@dataclass
class ResultadoBusca:
    """
    Resultado de uma busca por editais.

    Attributes:
        fonte: Fonte pesquisada
        total_encontrados: Total de editais encontrados
        com_rating: Editais com exigência de rating
        editais: Lista de editais encontrados
        data_busca: Data/hora da busca
        parametros_busca: Parâmetros utilizados na busca
        erros: Erros ocorridos durante a busca
        tempo_execucao: Tempo de execução em segundos
    """
    fonte: FonteEdital
    total_encontrados: int = 0
    com_rating: int = 0
    editais: List[Edital] = field(default_factory=list)
    data_busca: datetime = field(default_factory=datetime.now)
    parametros_busca: Dict[str, Any] = field(default_factory=dict)
    erros: List[str] = field(default_factory=list)
    tempo_execucao: float = 0.0

    @property
    def taxa_rating(self) -> float:
        """Retorna a taxa de editais com exigência de rating."""
        if self.total_encontrados > 0:
            return (self.com_rating / self.total_encontrados) * 100
        return 0.0

    def editais_amazonas(self) -> List[Edital]:
        """Retorna apenas editais do Amazonas."""
        return [e for e in self.editais if e.eh_amazonas]

    def editais_com_rating(self) -> List[Edital]:
        """Retorna apenas editais com exigência de rating."""
        return [e for e in self.editais if e.tem_exigencia_rating]

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'fonte': self.fonte.value,
            'total_encontrados': self.total_encontrados,
            'com_rating': self.com_rating,
            'taxa_rating': self.taxa_rating,
            'data_busca': self.data_busca.isoformat(),
            'parametros_busca': self.parametros_busca,
            'erros': self.erros,
            'tempo_execucao': self.tempo_execucao,
            'editais': [e.to_dict() for e in self.editais]
        }

    def resumo(self) -> str:
        """Retorna um resumo da busca."""
        linhas = [
            f"\n{'#'*60}",
            f"RESULTADO DA BUSCA - {self.fonte.value}",
            f"{'#'*60}",
            f"Data da Busca: {self.data_busca.strftime('%d/%m/%Y %H:%M')}",
            f"Tempo de Execução: {self.tempo_execucao:.2f}s",
            f"",
            f"Total de Editais: {self.total_encontrados}",
            f"Com Exigência de Rating: {self.com_rating}",
            f"Taxa de Rating: {self.taxa_rating:.1f}%",
            f"",
            f"Editais do Amazonas: {len(self.editais_amazonas())}",
        ]

        if self.erros:
            linhas.extend([
                f"\n⚠️ ERROS ({len(self.erros)}):",
                *[f"  - {erro}" for erro in self.erros]
            ])

        linhas.append(f"{'#'*60}\n")

        return '\n'.join(linhas)


@dataclass
class ConfiguracaoCaptura:
    """
    Configuração para execução de capturas.

    Attributes:
        uf_prioritaria: UF com prioridade na busca
        dias_retroativos: Quantos dias retroativos buscar
        apenas_com_rating: Se deve filtrar apenas editais com rating
        palavras_chave: Palavras-chave para filtrar objetos
        valor_minimo: Valor mínimo da licitação
        valor_maximo: Valor máximo da licitação
        tipos_licitacao: Tipos de licitação a considerar
        salvar_texto_completo: Se deve salvar o texto completo
        timeout_requisicao: Timeout para requisições HTTP
        intervalo_requisicoes: Intervalo entre requisições (segundos)
    """
    uf_prioritaria: str = "AM"
    dias_retroativos: int = 30
    apenas_com_rating: bool = False
    palavras_chave: List[str] = field(default_factory=lambda: [
        "seguro garantia",
        "garantia contratual",
        "rating",
        "classificação de risco",
        "seguradora"
    ])
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    tipos_licitacao: List[TipoLicitacao] = field(default_factory=list)
    salvar_texto_completo: bool = True
    timeout_requisicao: int = 30
    intervalo_requisicoes: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'uf_prioritaria': self.uf_prioritaria,
            'dias_retroativos': self.dias_retroativos,
            'apenas_com_rating': self.apenas_com_rating,
            'palavras_chave': self.palavras_chave,
            'valor_minimo': self.valor_minimo,
            'valor_maximo': self.valor_maximo,
            'tipos_licitacao': [t.value for t in self.tipos_licitacao],
            'salvar_texto_completo': self.salvar_texto_completo,
            'timeout_requisicao': self.timeout_requisicao,
            'intervalo_requisicoes': self.intervalo_requisicoes
        }
