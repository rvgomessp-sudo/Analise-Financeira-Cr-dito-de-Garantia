"""
Capturador de editais do Portal de Compras do Amazonas.

Este módulo captura editais de licitações dos portais oficiais do
Governo do Estado do Amazonas e da Prefeitura de Manaus.

Fontes:
- Portal de Compras AM: https://www.compras.am.gov.br/
- Portal e-compras Manaus: https://ecompras.manaus.am.gov.br/
- TCE-AM: https://www.tce.am.gov.br/
"""

import re
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from .capturador_base import CapturadorBase, HAS_REQUESTS, HAS_BS4
from .modelos import (
    Edital,
    FonteEdital,
    ResultadoBusca,
    ConfiguracaoCaptura,
    TipoLicitacao,
    StatusEdital
)


class CapturadorAmazonas(CapturadorBase):
    """
    Capturador para portais de licitações do Amazonas.

    Captura editais de:
    - Portal de Compras do Governo do Estado do Amazonas
    - Portal e-Compras da Prefeitura de Manaus
    - Transparência e TCE-AM
    """

    # URLs dos portais
    PORTAL_ESTADO = "https://www.compras.am.gov.br"
    PORTAL_MANAUS = "https://ecompras.manaus.am.gov.br"
    PORTAL_TRANSPARENCIA = "https://www.transparencia.am.gov.br"

    # API do Portal de Compras AM (se disponível)
    API_COMPRAS_AM = "https://www.compras.am.gov.br/api"

    def __init__(
        self,
        configuracao: Optional[ConfiguracaoCaptura] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Inicializa o capturador do Amazonas."""
        super().__init__(configuracao, logger)
        self.logger.info("Capturador Amazonas inicializado")

    @property
    def fonte(self) -> FonteEdital:
        return FonteEdital.AMAZONAS

    @property
    def url_base(self) -> str:
        return self.PORTAL_ESTADO

    def buscar_editais(
        self,
        uf: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        palavras_chave: Optional[List[str]] = None
    ) -> ResultadoBusca:
        """
        Busca editais nos portais do Amazonas.

        Args:
            uf: Ignorado (sempre busca AM)
            data_inicio: Data inicial do período
            data_fim: Data final do período
            palavras_chave: Palavras-chave para filtrar

        Returns:
            ResultadoBusca com os editais encontrados
        """
        tempo_inicio = time.time()
        resultado = ResultadoBusca(
            fonte=self.fonte,
            parametros_busca={
                'data_inicio': data_inicio.isoformat() if data_inicio else None,
                'data_fim': data_fim.isoformat() if data_fim else None,
                'palavras_chave': palavras_chave
            }
        )

        if not HAS_REQUESTS or not HAS_BS4:
            resultado.erros.append(
                "Dependências não instaladas. Execute: pip install requests beautifulsoup4 lxml"
            )
            return resultado

        # Define período padrão
        if not data_fim:
            data_fim = datetime.now()
        if not data_inicio:
            data_inicio = data_fim - timedelta(days=self.config.dias_retroativos)

        palavras = palavras_chave or self.config.palavras_chave
        editais = []

        # Busca no Portal do Estado
        try:
            self.logger.info("Buscando no Portal de Compras do Estado...")
            editais_estado = self._buscar_portal_estado(
                data_inicio, data_fim, palavras, resultado
            )
            editais.extend(editais_estado)
        except Exception as e:
            self.logger.error(f"Erro no Portal do Estado: {e}")
            resultado.erros.append(f"Portal Estado: {e}")

        # Busca no Portal de Manaus
        try:
            self.logger.info("Buscando no Portal e-Compras Manaus...")
            editais_manaus = self._buscar_portal_manaus(
                data_inicio, data_fim, palavras, resultado
            )
            editais.extend(editais_manaus)
        except Exception as e:
            self.logger.error(f"Erro no Portal Manaus: {e}")
            resultado.erros.append(f"Portal Manaus: {e}")

        # Remove duplicatas por número do edital
        editais_unicos = self._remover_duplicatas(editais)

        resultado.editais = editais_unicos
        resultado.total_encontrados = len(editais_unicos)
        resultado.com_rating = sum(1 for e in editais_unicos if e.tem_exigencia_rating)
        resultado.tempo_execucao = time.time() - tempo_inicio

        return resultado

    def _buscar_portal_estado(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        palavras_chave: List[str],
        resultado: ResultadoBusca
    ) -> List[Edital]:
        """Busca editais no Portal de Compras do Estado."""
        editais = []

        # URL de busca de licitações
        url_busca = f"{self.PORTAL_ESTADO}/licitacoes"

        # Parâmetros de busca
        params = {
            'dataInicio': data_inicio.strftime('%d/%m/%Y'),
            'dataFim': data_fim.strftime('%d/%m/%Y'),
            'status': 'todos'
        }

        response = self._fazer_requisicao(url_busca, params=params)

        if not response:
            resultado.erros.append("Falha ao acessar Portal do Estado")
            return editais

        soup = self._parsear_html(response.text)
        if not soup:
            resultado.erros.append("Falha ao parsear HTML do Portal do Estado")
            return editais

        # Procura por containers de licitação
        # Ajustar seletores conforme estrutura real do portal
        containers = soup.select('.licitacao-item, .card-licitacao, tr.licitacao')

        for container in containers:
            try:
                edital = self._extrair_edital_estado(container, palavras_chave)
                if edital:
                    editais.append(edital)
            except Exception as e:
                self.logger.debug(f"Erro ao extrair edital: {e}")

        return editais

    def _extrair_edital_estado(
        self,
        container: Any,
        palavras_chave: List[str]
    ) -> Optional[Edital]:
        """Extrai dados de um edital do Portal do Estado."""
        # Extrai número do edital
        numero_elem = container.select_one('.numero-edital, .edital-numero, td:first-child')
        numero = numero_elem.get_text(strip=True) if numero_elem else ''

        # Extrai objeto
        objeto_elem = container.select_one('.objeto, .descricao, td.objeto')
        objeto = objeto_elem.get_text(strip=True) if objeto_elem else ''

        # Verifica palavras-chave
        texto_busca = f"{numero} {objeto}".lower()
        if palavras_chave and not any(p.lower() in texto_busca for p in palavras_chave):
            return None

        # Extrai órgão
        orgao_elem = container.select_one('.orgao, .entidade, td.orgao')
        orgao = orgao_elem.get_text(strip=True) if orgao_elem else 'Governo do Estado do Amazonas'

        # Extrai data de abertura
        data_elem = container.select_one('.data-abertura, .data, td.data')
        data_texto = data_elem.get_text(strip=True) if data_elem else ''
        data_abertura = self._extrair_data(data_texto)

        # Extrai valor
        valor_elem = container.select_one('.valor, .valor-estimado, td.valor')
        valor_texto = valor_elem.get_text(strip=True) if valor_elem else ''
        valor = self._extrair_valor(valor_texto)

        # Extrai link
        link_elem = container.select_one('a[href*="edital"], a[href*="licitacao"]')
        url = ''
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            if href.startswith('http'):
                url = href
            else:
                url = f"{self.PORTAL_ESTADO}{href}"

        # Extrai tipo de licitação
        tipo_elem = container.select_one('.modalidade, .tipo, td.modalidade')
        tipo_texto = tipo_elem.get_text(strip=True) if tipo_elem else ''
        tipo = self._mapear_tipo_licitacao(tipo_texto)

        # Extrai status
        status_elem = container.select_one('.status, .situacao, td.status')
        status_texto = status_elem.get_text(strip=True) if status_elem else ''
        status = self._mapear_status(status_texto)

        if not numero and not objeto:
            return None

        edital = Edital(
            id_fonte=numero or f"AM-{hash(objeto) % 100000}",
            numero_edital=numero,
            orgao=orgao,
            objeto=objeto,
            fonte=self.fonte,
            url=url or self.PORTAL_ESTADO,
            data_abertura=data_abertura,
            valor_estimado=valor,
            tipo_licitacao=tipo,
            uf='AM',
            municipio='',
            status=status
        )

        # Busca texto completo se tiver URL
        if url and self.config.salvar_texto_completo:
            texto = self._obter_texto_edital(url)
            if texto:
                edital.texto_completo = texto

        # Analisa exigência de rating
        edital = self.analisar_edital_rating(edital)

        return edital

    def _buscar_portal_manaus(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        palavras_chave: List[str],
        resultado: ResultadoBusca
    ) -> List[Edital]:
        """Busca editais no Portal e-Compras de Manaus."""
        editais = []

        url_busca = f"{self.PORTAL_MANAUS}/licitacoes"

        params = {
            'dtInicio': data_inicio.strftime('%Y-%m-%d'),
            'dtFim': data_fim.strftime('%Y-%m-%d'),
        }

        response = self._fazer_requisicao(url_busca, params=params)

        if not response:
            resultado.erros.append("Falha ao acessar Portal de Manaus")
            return editais

        soup = self._parsear_html(response.text)
        if not soup:
            resultado.erros.append("Falha ao parsear HTML do Portal de Manaus")
            return editais

        # Procura por containers de licitação
        containers = soup.select('.licitacao, .processo, tr[data-id]')

        for container in containers:
            try:
                edital = self._extrair_edital_manaus(container, palavras_chave)
                if edital:
                    editais.append(edital)
            except Exception as e:
                self.logger.debug(f"Erro ao extrair edital Manaus: {e}")

        return editais

    def _extrair_edital_manaus(
        self,
        container: Any,
        palavras_chave: List[str]
    ) -> Optional[Edital]:
        """Extrai dados de um edital do Portal de Manaus."""
        # Similar ao portal do estado, ajustar seletores
        numero_elem = container.select_one('.numero, .processo-numero')
        numero = numero_elem.get_text(strip=True) if numero_elem else ''

        objeto_elem = container.select_one('.objeto, .descricao')
        objeto = objeto_elem.get_text(strip=True) if objeto_elem else ''

        # Verifica palavras-chave
        texto_busca = f"{numero} {objeto}".lower()
        if palavras_chave and not any(p.lower() in texto_busca for p in palavras_chave):
            return None

        orgao_elem = container.select_one('.orgao, .secretaria')
        orgao = orgao_elem.get_text(strip=True) if orgao_elem else 'Prefeitura de Manaus'

        data_elem = container.select_one('.data-abertura, .data')
        data_texto = data_elem.get_text(strip=True) if data_elem else ''
        data_abertura = self._extrair_data(data_texto)

        valor_elem = container.select_one('.valor')
        valor_texto = valor_elem.get_text(strip=True) if valor_elem else ''
        valor = self._extrair_valor(valor_texto)

        link_elem = container.select_one('a[href]')
        url = ''
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            if href.startswith('http'):
                url = href
            else:
                url = f"{self.PORTAL_MANAUS}{href}"

        if not numero and not objeto:
            return None

        edital = Edital(
            id_fonte=numero or f"MAO-{hash(objeto) % 100000}",
            numero_edital=numero,
            orgao=orgao,
            objeto=objeto,
            fonte=FonteEdital.MANAUS,
            url=url or self.PORTAL_MANAUS,
            data_abertura=data_abertura,
            valor_estimado=valor,
            tipo_licitacao=TipoLicitacao.OUTRO,
            uf='AM',
            municipio='Manaus',
            status=StatusEdital.DESCONHECIDO
        )

        # Busca texto completo
        if url and self.config.salvar_texto_completo:
            texto = self._obter_texto_edital(url)
            if texto:
                edital.texto_completo = texto

        # Analisa exigência de rating
        edital = self.analisar_edital_rating(edital)

        return edital

    def _obter_texto_edital(self, url: str) -> str:
        """Obtém texto completo do edital a partir da URL."""
        response = self._fazer_requisicao(url)
        if not response:
            return ""

        soup = self._parsear_html(response.text)
        if not soup:
            return ""

        # Remove scripts e estilos
        for elemento in soup(['script', 'style', 'nav', 'header', 'footer']):
            elemento.decompose()

        # Procura por conteúdo principal
        conteudo = soup.select_one(
            'main, .conteudo, .content, #conteudo, article, .edital-texto'
        )

        if conteudo:
            return conteudo.get_text(separator=' ', strip=True)

        # Fallback para body
        return soup.get_text(separator=' ', strip=True)[:10000]

    def _remover_duplicatas(self, editais: List[Edital]) -> List[Edital]:
        """Remove editais duplicados por número."""
        vistos = set()
        unicos = []

        for edital in editais:
            chave = (edital.numero_edital.lower(), edital.orgao.lower())
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(edital)

        return unicos

    def obter_detalhes_edital(self, id_edital: str) -> Optional[Edital]:
        """
        Obtém detalhes completos de um edital específico.

        Args:
            id_edital: Identificador do edital ou URL

        Returns:
            Edital com detalhes completos
        """
        # Se for URL, busca diretamente
        if id_edital.startswith('http'):
            return self._obter_por_url(id_edital)

        # Tenta buscar em cada portal
        resultado = self.buscar_editais(palavras_chave=[id_edital])

        for edital in resultado.editais:
            if id_edital in edital.numero_edital or id_edital in edital.id_fonte:
                return edital

        return None

    def _obter_por_url(self, url: str) -> Optional[Edital]:
        """Obtém edital diretamente pela URL."""
        response = self._fazer_requisicao(url)
        if not response:
            return None

        soup = self._parsear_html(response.text)
        if not soup:
            return None

        # Tenta extrair informações da página
        titulo = soup.select_one('h1, .titulo, .title')
        titulo_texto = titulo.get_text(strip=True) if titulo else 'Edital'

        texto_completo = self._obter_texto_edital(url)

        edital = Edital(
            id_fonte=f"URL-{hash(url) % 100000}",
            numero_edital=titulo_texto,
            orgao="Governo do Amazonas",
            objeto=titulo_texto,
            fonte=self.fonte,
            url=url,
            uf='AM',
            texto_completo=texto_completo
        )

        # Analisa rating
        edital = self.analisar_edital_rating(edital)

        return edital

    def buscar_seguro_garantia(self, dias: int = 30) -> ResultadoBusca:
        """
        Busca específica por editais de seguro garantia no Amazonas.

        Args:
            dias: Dias retroativos

        Returns:
            ResultadoBusca focado em seguro garantia
        """
        palavras = [
            'seguro garantia',
            'garantia contratual',
            'apólice',
            'seguradora',
            'rating',
            'classificação de risco'
        ]

        return self.buscar_editais(
            data_inicio=datetime.now() - timedelta(days=dias),
            data_fim=datetime.now(),
            palavras_chave=palavras
        )

    def buscar_grandes_obras(
        self,
        valor_minimo: float = 10_000_000,
        dias: int = 60
    ) -> ResultadoBusca:
        """
        Busca editais de grandes obras (maior probabilidade de exigir rating).

        Args:
            valor_minimo: Valor mínimo em reais
            dias: Dias retroativos

        Returns:
            ResultadoBusca de grandes obras
        """
        palavras = [
            'obra',
            'construção',
            'infraestrutura',
            'reforma',
            'ampliação',
            'edificação',
            'pavimentação',
            'saneamento'
        ]

        resultado = self.buscar_editais(
            data_inicio=datetime.now() - timedelta(days=dias),
            palavras_chave=palavras
        )

        # Filtra por valor mínimo
        resultado.editais = [
            e for e in resultado.editais
            if e.valor_estimado and e.valor_estimado >= valor_minimo
        ]
        resultado.total_encontrados = len(resultado.editais)
        resultado.com_rating = sum(1 for e in resultado.editais if e.tem_exigencia_rating)

        return resultado


class CapturadorTCEAmazonas(CapturadorBase):
    """
    Capturador para o TCE-AM (Tribunal de Contas do Estado do Amazonas).

    Útil para verificar editais e contratos registrados no TCE.
    """

    URL_TCE = "https://www.tce.am.gov.br"

    @property
    def fonte(self) -> FonteEdital:
        return FonteEdital.TCE_AM

    @property
    def url_base(self) -> str:
        return self.URL_TCE

    def buscar_editais(
        self,
        uf: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        palavras_chave: Optional[List[str]] = None
    ) -> ResultadoBusca:
        """Busca editais no TCE-AM."""
        # Implementação similar ao portal do estado
        resultado = ResultadoBusca(fonte=self.fonte)
        resultado.erros.append("Capturador TCE-AM em desenvolvimento")
        return resultado

    def obter_detalhes_edital(self, id_edital: str) -> Optional[Edital]:
        """Obtém detalhes de edital no TCE-AM."""
        return None


# Função de conveniência
def buscar_editais_amazonas(
    dias: int = 30,
    apenas_rating: bool = True,
    incluir_manaus: bool = True
) -> ResultadoBusca:
    """
    Função de conveniência para buscar editais no Amazonas.

    Args:
        dias: Dias retroativos
        apenas_rating: Se True, retorna apenas com exigência de rating
        incluir_manaus: Se True, inclui portal de Manaus

    Returns:
        ResultadoBusca
    """
    config = ConfiguracaoCaptura(
        uf_prioritaria='AM',
        dias_retroativos=dias,
        apenas_com_rating=apenas_rating
    )

    with CapturadorAmazonas(config) as capturador:
        resultado = capturador.buscar_editais()

        if apenas_rating:
            resultado.editais = [e for e in resultado.editais if e.tem_exigencia_rating]
            resultado.total_encontrados = len(resultado.editais)

        return resultado


# Teste do módulo
if __name__ == '__main__':
    print("=" * 60)
    print("TESTE DO CAPTURADOR AMAZONAS")
    print("=" * 60)

    from .capturador_base import verificar_dependencias

    deps = verificar_dependencias()
    print("\nDependências:")
    for dep, instalada in deps.items():
        status = "✅" if instalada else "❌"
        print(f"  {status} {dep}")

    if not all(deps.values()):
        print("\n⚠️ Instale as dependências: pip install requests beautifulsoup4 lxml")
    else:
        print("\nBuscando editais do Amazonas...")

        resultado = buscar_editais_amazonas(dias=7, apenas_rating=False)

        print(resultado.resumo())

        if resultado.editais:
            print("\nEditais encontrados:")
            for edital in resultado.editais[:5]:
                print(edital.resumo())
