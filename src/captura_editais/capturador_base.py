"""
Capturador base para editais de licitação.

Este módulo define a classe base abstrata para capturadores de editais
de diferentes portais de licitações públicas.
"""

import hashlib
import time
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Generator
from urllib.parse import urljoin, urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from .modelos import (
    Edital,
    ExigenciaRating,
    FonteEdital,
    ResultadoBusca,
    ConfiguracaoCaptura,
    TipoLicitacao,
    TipoGarantia,
    StatusEdital
)
from .detector_rating import DetectorRating


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class CapturadorBase(ABC):
    """
    Classe base abstrata para capturadores de editais.

    Define a interface comum e funcionalidades compartilhadas
    entre todos os capturadores de portais de licitações.
    """

    # Headers padrão para requisições
    HEADERS_PADRAO = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }

    def __init__(
        self,
        configuracao: Optional[ConfiguracaoCaptura] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Inicializa o capturador.

        Args:
            configuracao: Configurações de captura
            logger: Logger customizado (opcional)
        """
        self.config = configuracao or ConfiguracaoCaptura()
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.detector = DetectorRating()

        self._session: Optional[Any] = None
        self._ultima_requisicao: Optional[datetime] = None

        # Verifica dependências
        self._verificar_dependencias()

    def _verificar_dependencias(self) -> None:
        """Verifica se as dependências necessárias estão instaladas."""
        if not HAS_REQUESTS:
            self.logger.warning(
                "Biblioteca 'requests' não instalada. "
                "Execute: pip install requests"
            )
        if not HAS_BS4:
            self.logger.warning(
                "Biblioteca 'beautifulsoup4' não instalada. "
                "Execute: pip install beautifulsoup4 lxml"
            )

    @property
    @abstractmethod
    def fonte(self) -> FonteEdital:
        """Retorna a fonte deste capturador."""
        pass

    @property
    @abstractmethod
    def url_base(self) -> str:
        """Retorna a URL base do portal."""
        pass

    @abstractmethod
    def buscar_editais(
        self,
        uf: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        palavras_chave: Optional[List[str]] = None
    ) -> ResultadoBusca:
        """
        Busca editais no portal.

        Args:
            uf: Filtrar por UF (ex: 'AM' para Amazonas)
            data_inicio: Data inicial do período
            data_fim: Data final do período
            palavras_chave: Palavras-chave para filtrar

        Returns:
            ResultadoBusca com os editais encontrados
        """
        pass

    @abstractmethod
    def obter_detalhes_edital(self, id_edital: str) -> Optional[Edital]:
        """
        Obtém detalhes completos de um edital específico.

        Args:
            id_edital: Identificador do edital na fonte

        Returns:
            Edital com detalhes completos ou None se não encontrado
        """
        pass

    def _criar_sessao(self) -> Any:
        """Cria sessão HTTP com retry automático."""
        if not HAS_REQUESTS:
            raise RuntimeError("Biblioteca 'requests' não está instalada")

        session = requests.Session()

        # Configura retry para resiliência
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update(self.HEADERS_PADRAO)

        return session

    @property
    def session(self) -> Any:
        """Retorna sessão HTTP, criando se necessário."""
        if self._session is None:
            self._session = self._criar_sessao()
        return self._session

    def _respeitar_intervalo(self) -> None:
        """Respeita intervalo mínimo entre requisições."""
        if self._ultima_requisicao:
            elapsed = (datetime.now() - self._ultima_requisicao).total_seconds()
            if elapsed < self.config.intervalo_requisicoes:
                time.sleep(self.config.intervalo_requisicoes - elapsed)

        self._ultima_requisicao = datetime.now()

    def _fazer_requisicao(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[Any]:
        """
        Faz requisição HTTP com tratamento de erros.

        Args:
            url: URL para requisição
            method: Método HTTP (GET, POST, etc.)
            params: Parâmetros de query string
            data: Dados para POST (form)
            json_data: Dados para POST (JSON)
            headers: Headers adicionais

        Returns:
            Response object ou None em caso de erro
        """
        if not HAS_REQUESTS:
            self.logger.error("Biblioteca 'requests' não está instalada")
            return None

        self._respeitar_intervalo()

        try:
            request_headers = {**self.HEADERS_PADRAO, **(headers or {})}

            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.config.timeout_requisicao
            )

            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout ao acessar {url}")
        except requests.exceptions.TooManyRedirects:
            self.logger.error(f"Muitos redirects ao acessar {url}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"Erro HTTP {e.response.status_code} ao acessar {url}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro de requisição: {e}")

        return None

    def _parsear_html(self, html: str) -> Optional[Any]:
        """
        Parseia conteúdo HTML.

        Args:
            html: Conteúdo HTML como string

        Returns:
            BeautifulSoup object ou None
        """
        if not HAS_BS4:
            self.logger.error("Biblioteca 'beautifulsoup4' não está instalada")
            return None

        try:
            return BeautifulSoup(html, 'lxml')
        except Exception:
            try:
                return BeautifulSoup(html, 'html.parser')
            except Exception as e:
                self.logger.error(f"Erro ao parsear HTML: {e}")
                return None

    def _calcular_hash(self, conteudo: str) -> str:
        """Calcula hash MD5 do conteúdo."""
        return hashlib.md5(conteudo.encode('utf-8')).hexdigest()

    def _extrair_valor(self, texto: str) -> Optional[float]:
        """
        Extrai valor monetário de texto.

        Args:
            texto: Texto contendo valor (ex: "R$ 1.234.567,89")

        Returns:
            Valor como float ou None
        """
        import re

        if not texto:
            return None

        # Remove caracteres não numéricos exceto vírgula e ponto
        texto_limpo = re.sub(r'[^\d,.]', '', texto)

        # Trata formato brasileiro (1.234.567,89)
        if ',' in texto_limpo:
            # Remove pontos de milhar e troca vírgula por ponto
            texto_limpo = texto_limpo.replace('.', '').replace(',', '.')

        try:
            return float(texto_limpo)
        except ValueError:
            return None

    def _extrair_data(self, texto: str) -> Optional[datetime]:
        """
        Extrai data de texto em diversos formatos.

        Args:
            texto: Texto contendo data

        Returns:
            datetime ou None
        """
        import re

        if not texto:
            return None

        # Formatos comuns de data
        formatos = [
            '%d/%m/%Y',
            '%d/%m/%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%d-%m-%Y',
            '%d.%m.%Y',
        ]

        # Limpa o texto
        texto = texto.strip()

        for formato in formatos:
            try:
                return datetime.strptime(texto, formato)
            except ValueError:
                continue

        # Tenta extrair data com regex
        match = re.search(r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})', texto)
        if match:
            dia, mes, ano = match.groups()
            try:
                return datetime(int(ano), int(mes), int(dia))
            except ValueError:
                pass

        return None

    def _mapear_tipo_licitacao(self, texto: str) -> TipoLicitacao:
        """Mapeia texto para tipo de licitação."""
        texto_lower = texto.lower()

        mapeamentos = {
            'pregão eletrônico': TipoLicitacao.PREGAO_ELETRONICO,
            'pregao eletronico': TipoLicitacao.PREGAO_ELETRONICO,
            'pregão presencial': TipoLicitacao.PREGAO_PRESENCIAL,
            'pregao presencial': TipoLicitacao.PREGAO_PRESENCIAL,
            'concorrência': TipoLicitacao.CONCORRENCIA,
            'concorrencia': TipoLicitacao.CONCORRENCIA,
            'tomada de preços': TipoLicitacao.TOMADA_PRECOS,
            'tomada de precos': TipoLicitacao.TOMADA_PRECOS,
            'convite': TipoLicitacao.CONVITE,
            'concurso': TipoLicitacao.CONCURSO,
            'leilão': TipoLicitacao.LEILAO,
            'leilao': TipoLicitacao.LEILAO,
            'dispensa': TipoLicitacao.DISPENSA,
            'inexigibilidade': TipoLicitacao.INEXIGIBILIDADE,
            'rdc': TipoLicitacao.RDC,
            'diálogo competitivo': TipoLicitacao.DIALOGO_COMPETITIVO,
            'dialogo competitivo': TipoLicitacao.DIALOGO_COMPETITIVO,
        }

        for chave, tipo in mapeamentos.items():
            if chave in texto_lower:
                return tipo

        return TipoLicitacao.OUTRO

    def _mapear_status(self, texto: str) -> StatusEdital:
        """Mapeia texto para status do edital."""
        texto_lower = texto.lower()

        mapeamentos = {
            'aberto': StatusEdital.ABERTO,
            'em andamento': StatusEdital.EM_ANDAMENTO,
            'suspenso': StatusEdital.SUSPENSO,
            'cancelado': StatusEdital.CANCELADO,
            'encerrado': StatusEdital.ENCERRADO,
            'homologado': StatusEdital.HOMOLOGADO,
            'finalizado': StatusEdital.ENCERRADO,
            'concluído': StatusEdital.ENCERRADO,
            'concluido': StatusEdital.ENCERRADO,
        }

        for chave, status in mapeamentos.items():
            if chave in texto_lower:
                return status

        return StatusEdital.DESCONHECIDO

    def analisar_edital_rating(self, edital: Edital) -> Edital:
        """
        Analisa edital para detectar exigências de rating.

        Args:
            edital: Edital a ser analisado

        Returns:
            Edital atualizado com informações de rating
        """
        # Analisa o texto do objeto e texto completo
        texto_analise = f"{edital.objeto} {edital.texto_completo}"

        resultado = self.detector.analisar_completo(texto_analise)

        edital.exigencia_rating = resultado['exigencia_rating']

        # Atualiza tipo de garantia se não definido
        if edital.tipo_garantia == TipoGarantia.NAO_ESPECIFICADO:
            edital.tipo_garantia = resultado['tipo_garantia']

        # Atualiza percentual se encontrado e não definido
        if resultado['percentual_garantia'] and not edital.percentual_garantia:
            edital.percentual_garantia = resultado['percentual_garantia']

        return edital

    def fechar(self) -> None:
        """Fecha recursos do capturador."""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.fechar()


def verificar_dependencias() -> Dict[str, bool]:
    """
    Verifica quais dependências estão instaladas.

    Returns:
        Dicionário com status de cada dependência
    """
    deps = {
        'requests': HAS_REQUESTS,
        'beautifulsoup4': HAS_BS4,
    }

    # Verifica lxml
    try:
        import lxml
        deps['lxml'] = True
    except ImportError:
        deps['lxml'] = False

    return deps


def instalar_dependencias() -> str:
    """
    Retorna comando para instalar dependências.

    Returns:
        Comando pip install
    """
    return "pip install requests beautifulsoup4 lxml"
