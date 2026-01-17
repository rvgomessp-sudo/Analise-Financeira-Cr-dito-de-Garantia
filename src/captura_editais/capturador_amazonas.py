"""
Capturador de editais do Portal de Compras do Amazonas.

Este módulo captura editais de licitações dos portais oficiais do
Governo do Estado do Amazonas.

Fontes:
- Portal e-Compras AM: https://www.e-compras.am.gov.br/
- PNCP (filtrado por AM): https://pncp.gov.br/
"""

import re
import time
import json
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
    - Portal e-Compras do Governo do Estado do Amazonas
    - PNCP filtrado por UF=AM
    """

    # URLs corretas do Portal e-Compras AM
    PORTAL_ESTADO = "https://www.e-compras.am.gov.br"
    URL_LICITACOES = "https://www.e-compras.am.gov.br/publico/licitacoes_todas.asp"
    URL_DADOS = "https://www.e-compras.am.gov.br/publico/qry/qry_licitacoes_todas.asp"
    URL_DETALHES = "https://www.e-compras.am.gov.br/publico/licitacoes_detalhes.asp"

    # Mapeamento de modalidades
    MODALIDADES = {
        'pregão eletrônico': TipoLicitacao.PREGAO_ELETRONICO,
        'pregao eletronico': TipoLicitacao.PREGAO_ELETRONICO,
        'pe': TipoLicitacao.PREGAO_ELETRONICO,
        'pregão presencial': TipoLicitacao.PREGAO_PRESENCIAL,
        'concorrência': TipoLicitacao.CONCORRENCIA,
        'concorrencia': TipoLicitacao.CONCORRENCIA,
        'tomada de preços': TipoLicitacao.TOMADA_PRECOS,
        'tomada de precos': TipoLicitacao.TOMADA_PRECOS,
        'convite': TipoLicitacao.CONVITE,
        'dispensa': TipoLicitacao.DISPENSA,
        'inexigibilidade': TipoLicitacao.INEXIGIBILIDADE,
        'rdc': TipoLicitacao.RDC,
    }

    # Mapeamento de situações
    SITUACOES = {
        'aberto': StatusEdital.ABERTO,
        'em andamento': StatusEdital.EM_ANDAMENTO,
        'encerrado': StatusEdital.ENCERRADO,
        'suspenso': StatusEdital.SUSPENSO,
        'cancelado': StatusEdital.CANCELADO,
        'homologado': StatusEdital.HOMOLOGADO,
        'adjudicado': StatusEdital.HOMOLOGADO,
        'revogado': StatusEdital.CANCELADO,
        'anulado': StatusEdital.CANCELADO,
        'deserto': StatusEdital.ENCERRADO,
        'fracassado': StatusEdital.ENCERRADO,
    }

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
        Busca editais no Portal e-Compras do Amazonas.

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

        if not HAS_REQUESTS:
            resultado.erros.append(
                "Dependência 'requests' não instalada. Execute: pip install requests"
            )
            return resultado

        # Define período padrão
        if not data_fim:
            data_fim = datetime.now()
        if not data_inicio:
            data_inicio = data_fim - timedelta(days=self.config.dias_retroativos)

        palavras = palavras_chave or self.config.palavras_chave
        editais = []

        # Busca no Portal e-Compras do Estado
        try:
            self.logger.info("Buscando no Portal e-Compras AM...")
            editais_estado = self._buscar_portal_ecompras(
                data_inicio, data_fim, palavras, resultado
            )
            editais.extend(editais_estado)
            self.logger.info(f"  Encontrados: {len(editais_estado)} editais")
        except Exception as e:
            self.logger.error(f"Erro no Portal e-Compras: {e}")
            resultado.erros.append(f"Portal e-Compras: {e}")

        # Remove duplicatas
        editais_unicos = self._remover_duplicatas(editais)

        resultado.editais = editais_unicos
        resultado.total_encontrados = len(editais_unicos)
        resultado.com_rating = sum(1 for e in editais_unicos if e.tem_exigencia_rating)
        resultado.tempo_execucao = time.time() - tempo_inicio

        return resultado

    def _buscar_portal_ecompras(
        self,
        data_inicio: datetime,
        data_fim: datetime,
        palavras_chave: List[str],
        resultado: ResultadoBusca
    ) -> List[Edital]:
        """
        Busca editais no Portal e-Compras AM usando a API DataTable.

        O portal usa jQuery DataTables com server-side processing.
        """
        editais = []

        # Headers específicos para o portal
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.URL_LICITACOES,
            'Origin': self.PORTAL_ESTADO
        }

        # Parâmetros do DataTable (server-side)
        # draw: contador de requisições
        # start: offset
        # length: quantidade por página
        start = 0
        length = 50
        draw = 1
        total_processado = 0
        max_registros = 500  # Limite de segurança

        while total_processado < max_registros:
            # Dados para POST (formato DataTables)
            data = {
                'draw': str(draw),
                'start': str(start),
                'length': str(length),
                'search[value]': '',
                'search[regex]': 'false',
                # Colunas do DataTable
                'columns[0][data]': '0',
                'columns[0][searchable]': 'true',
                'columns[1][data]': '1',
                'columns[1][searchable]': 'true',
                'columns[2][data]': '2',
                'columns[2][searchable]': 'true',
                'columns[3][data]': '3',
                'columns[3][searchable]': 'true',
                'columns[4][data]': '4',
                'columns[4][searchable]': 'true',
                # Filtros
                'ano': str(data_fim.year),
                'situacao': '',
                'modalidade': '',
                'registroPreco': '',
            }

            self.logger.debug(f"Buscando registros {start} a {start + length}...")

            response = self._fazer_requisicao(
                url=self.URL_DADOS,
                method='POST',
                data=data,
                headers=headers
            )

            if not response:
                resultado.erros.append(f"Falha na requisição (offset {start})")
                break

            try:
                json_data = response.json()
            except Exception as e:
                # Se não for JSON, tenta parsear como HTML
                self.logger.debug(f"Resposta não é JSON, tentando HTML: {e}")
                editais_html = self._parsear_html_licitacoes(
                    response.text, palavras_chave, data_inicio, data_fim
                )
                editais.extend(editais_html)
                break

            # Processa dados do DataTable
            registros = json_data.get('data', [])
            total_registros = json_data.get('recordsTotal', 0)

            if not registros:
                self.logger.debug("Nenhum registro retornado")
                break

            for registro in registros:
                try:
                    edital = self._processar_registro_datatable(
                        registro, palavras_chave, data_inicio, data_fim
                    )
                    if edital:
                        editais.append(edital)
                except Exception as e:
                    self.logger.debug(f"Erro ao processar registro: {e}")

            total_processado += len(registros)

            # Verifica se há mais registros
            if total_processado >= total_registros or len(registros) < length:
                break

            start += length
            draw += 1
            time.sleep(self.config.intervalo_requisicoes)

        return editais

    def _processar_registro_datatable(
        self,
        registro: List[Any],
        palavras_chave: List[str],
        data_inicio: datetime,
        data_fim: datetime
    ) -> Optional[Edital]:
        """Processa um registro do DataTable."""
        # Estrutura esperada do registro:
        # [0] Modalidade/Edital (com link)
        # [1] UG (Unidade Gestora)
        # [2] Objeto
        # [3] Situação
        # [4] Processo
        # [5+] Dados ocultos (id_modalidade, id_status, etc)

        if len(registro) < 5:
            return None

        modalidade_html = str(registro[0]) if registro[0] else ''
        ug = str(registro[1]) if registro[1] else ''
        objeto = str(registro[2]) if registro[2] else ''
        situacao = str(registro[3]) if registro[3] else ''
        processo = str(registro[4]) if registro[4] else ''

        # Extrai número do edital e link do HTML
        numero_edital = ''
        url_edital = ''
        id_edital = ''

        # Parse do link no campo modalidade
        if HAS_BS4:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(modalidade_html, 'html.parser')
            link = soup.find('a')
            if link:
                numero_edital = link.get_text(strip=True)
                href = link.get('href', '')
                if 'ident=' in href:
                    id_edital = href.split('ident=')[-1].split('&')[0]
                    url_edital = f"{self.URL_DETALHES}?ident={id_edital}"
        else:
            # Fallback sem BeautifulSoup
            match = re.search(r'>([^<]+)</a>', modalidade_html)
            if match:
                numero_edital = match.group(1).strip()
            match = re.search(r'ident=(\d+)', modalidade_html)
            if match:
                id_edital = match.group(1)
                url_edital = f"{self.URL_DETALHES}?ident={id_edital}"

        # Verifica palavras-chave
        texto_busca = f"{numero_edital} {objeto} {ug}".lower()
        if palavras_chave:
            if not any(p.lower() in texto_busca for p in palavras_chave):
                return None

        # Mapeia tipo de licitação
        tipo = TipoLicitacao.OUTRO
        for chave, valor in self.MODALIDADES.items():
            if chave in numero_edital.lower():
                tipo = valor
                break

        # Mapeia status
        status = StatusEdital.DESCONHECIDO
        situacao_lower = situacao.lower()
        for chave, valor in self.SITUACOES.items():
            if chave in situacao_lower:
                status = valor
                break

        # Extrai código e nome do órgão
        orgao = ug.strip()
        if ' - ' in orgao:
            partes = orgao.split(' - ', 1)
            orgao = partes[1] if len(partes) > 1 else orgao

        edital = Edital(
            id_fonte=id_edital or f"AM-{hash(objeto) % 100000}",
            numero_edital=numero_edital,
            orgao=orgao or 'Governo do Estado do Amazonas',
            objeto=objeto,
            fonte=self.fonte,
            url=url_edital or self.URL_LICITACOES,
            tipo_licitacao=tipo,
            uf='AM',
            municipio='',
            status=status,
            metadata={
                'processo': processo,
                'ug_codigo': ug.split(' - ')[0] if ' - ' in ug else '',
                'situacao_original': situacao
            }
        )

        # Busca detalhes se tiver URL
        if url_edital and self.config.salvar_texto_completo:
            detalhes = self._obter_detalhes_edital_am(id_edital)
            if detalhes:
                edital.texto_completo = detalhes.get('texto', '')
                edital.valor_estimado = detalhes.get('valor')
                edital.data_abertura = detalhes.get('data_abertura')
                edital.data_publicacao = detalhes.get('data_publicacao')

        # Analisa exigência de rating
        edital = self.analisar_edital_rating(edital)

        return edital

    def _parsear_html_licitacoes(
        self,
        html: str,
        palavras_chave: List[str],
        data_inicio: datetime,
        data_fim: datetime
    ) -> List[Edital]:
        """Fallback: parseia HTML direto se API DataTable falhar."""
        editais = []

        if not HAS_BS4:
            return editais

        soup = self._parsear_html(html)
        if not soup:
            return editais

        # Procura tabela de licitações
        tabela = soup.find('table', {'id': 'tblLicitacoes'}) or soup.find('table')
        if not tabela:
            return editais

        linhas = tabela.find_all('tr')[1:]  # Pula cabeçalho

        for linha in linhas:
            colunas = linha.find_all('td')
            if len(colunas) < 4:
                continue

            try:
                link = colunas[0].find('a')
                numero_edital = link.get_text(strip=True) if link else ''
                href = link.get('href', '') if link else ''
                id_edital = ''
                if 'ident=' in href:
                    id_edital = href.split('ident=')[-1].split('&')[0]

                ug = colunas[1].get_text(strip=True)
                objeto = colunas[2].get_text(strip=True)
                situacao = colunas[3].get_text(strip=True)

                # Verifica palavras-chave
                texto_busca = f"{numero_edital} {objeto} {ug}".lower()
                if palavras_chave and not any(p.lower() in texto_busca for p in palavras_chave):
                    continue

                edital = Edital(
                    id_fonte=id_edital or f"AM-{hash(objeto) % 100000}",
                    numero_edital=numero_edital,
                    orgao=ug,
                    objeto=objeto,
                    fonte=self.fonte,
                    url=f"{self.URL_DETALHES}?ident={id_edital}" if id_edital else self.URL_LICITACOES,
                    uf='AM',
                    status=self._mapear_status(situacao)
                )

                edital = self.analisar_edital_rating(edital)
                editais.append(edital)

            except Exception as e:
                self.logger.debug(f"Erro ao processar linha: {e}")

        return editais

    def _obter_detalhes_edital_am(self, id_edital: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes completos de um edital do portal AM."""
        if not id_edital:
            return None

        url = f"{self.URL_DETALHES}?ident={id_edital}"
        response = self._fazer_requisicao(url)

        if not response or not HAS_BS4:
            return None

        soup = self._parsear_html(response.text)
        if not soup:
            return None

        detalhes = {'texto': ''}

        # Extrai texto completo da página
        # Remove scripts e estilos
        for elem in soup(['script', 'style', 'nav', 'header', 'footer']):
            elem.decompose()

        # Procura conteúdo principal
        conteudo = soup.select_one('.conteudo, .detalhes, main, #conteudo')
        if conteudo:
            detalhes['texto'] = conteudo.get_text(separator=' ', strip=True)
        else:
            detalhes['texto'] = soup.get_text(separator=' ', strip=True)[:15000]

        # Tenta extrair valor estimado
        texto = detalhes['texto'].lower()
        match = re.search(r'valor\s+(?:estimado|total|global)[:\s]*r?\$?\s*([\d.,]+)', texto)
        if match:
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                detalhes['valor'] = float(valor_str)
            except ValueError:
                pass

        # Tenta extrair data de abertura
        match = re.search(r'(?:abertura|sessão)[:\s]*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})', texto)
        if match:
            detalhes['data_abertura'] = self._extrair_data(match.group(1))

        return detalhes

    def _remover_duplicatas(self, editais: List[Edital]) -> List[Edital]:
        """Remove editais duplicados."""
        vistos = set()
        unicos = []

        for edital in editais:
            chave = (edital.numero_edital.lower(), edital.orgao.lower())
            if chave not in vistos:
                vistos.add(chave)
                unicos.append(edital)

        return unicos

    def obter_detalhes_edital(self, id_edital: str) -> Optional[Edital]:
        """Obtém detalhes completos de um edital específico."""
        if id_edital.startswith('http'):
            # Extrai ID da URL
            if 'ident=' in id_edital:
                id_edital = id_edital.split('ident=')[-1].split('&')[0]
            else:
                return None

        detalhes = self._obter_detalhes_edital_am(id_edital)
        if not detalhes:
            return None

        edital = Edital(
            id_fonte=id_edital,
            numero_edital=f"Edital {id_edital}",
            orgao="Governo do Estado do Amazonas",
            objeto=detalhes.get('texto', '')[:200],
            fonte=self.fonte,
            url=f"{self.URL_DETALHES}?ident={id_edital}",
            uf='AM',
            texto_completo=detalhes.get('texto', ''),
            valor_estimado=detalhes.get('valor'),
            data_abertura=detalhes.get('data_abertura')
        )

        edital = self.analisar_edital_rating(edital)
        return edital

    def buscar_seguro_garantia(self, dias: int = 30) -> ResultadoBusca:
        """Busca específica por editais de seguro garantia."""
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


# Função de conveniência
def buscar_editais_amazonas(
    dias: int = 30,
    apenas_rating: bool = True
) -> ResultadoBusca:
    """
    Busca editais no Amazonas.

    Args:
        dias: Dias retroativos
        apenas_rating: Se True, retorna apenas com exigência de rating

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
