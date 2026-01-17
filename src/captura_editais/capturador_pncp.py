"""
Capturador de editais do PNCP (Portal Nacional de Contratações Públicas).

O PNCP é o portal oficial do governo federal para publicação de
contratações públicas, conforme Lei 14.133/2021.

API Pública: https://pncp.gov.br/api/consulta/
Documentação: https://www.gov.br/pncp/pt-br
"""

import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from .capturador_base import CapturadorBase, HAS_REQUESTS
from .modelos import (
    Edital,
    FonteEdital,
    ResultadoBusca,
    ConfiguracaoCaptura,
    TipoLicitacao,
    StatusEdital
)


class CapturadorPNCP(CapturadorBase):
    """
    Capturador para o Portal Nacional de Contratações Públicas (PNCP).

    Utiliza a API pública do PNCP para buscar editais de licitações
    com foco em identificar exigências de rating.
    """

    # URLs da API do PNCP
    API_BASE = "https://pncp.gov.br/api/consulta"
    API_CONTRATACOES = f"{API_BASE}/v1/contratacoes/publicacao"
    API_DETALHES = f"{API_BASE}/v1/contratacoes"

    # Mapeamento de UFs para códigos IBGE
    UF_IBGE = {
        'AC': 12, 'AL': 27, 'AP': 16, 'AM': 13, 'BA': 29,
        'CE': 23, 'DF': 53, 'ES': 32, 'GO': 52, 'MA': 21,
        'MT': 51, 'MS': 50, 'MG': 31, 'PA': 15, 'PB': 25,
        'PR': 41, 'PE': 26, 'PI': 22, 'RJ': 33, 'RN': 24,
        'RS': 43, 'RO': 11, 'RR': 14, 'SC': 42, 'SP': 35,
        'SE': 28, 'TO': 17
    }

    # Códigos de modalidade de contratação
    MODALIDADES = {
        1: TipoLicitacao.PREGAO_ELETRONICO,
        2: TipoLicitacao.CONCORRENCIA,
        3: TipoLicitacao.CONCURSO,
        4: TipoLicitacao.LEILAO,
        5: TipoLicitacao.DIALOGO_COMPETITIVO,
        6: TipoLicitacao.DISPENSA,
        7: TipoLicitacao.INEXIGIBILIDADE,
        8: TipoLicitacao.PREGAO_PRESENCIAL,
    }

    def __init__(
        self,
        configuracao: Optional[ConfiguracaoCaptura] = None,
        logger: Optional[logging.Logger] = None
    ):
        """Inicializa o capturador do PNCP."""
        super().__init__(configuracao, logger)
        self.logger.info("Capturador PNCP inicializado")

    @property
    def fonte(self) -> FonteEdital:
        return FonteEdital.PNCP

    @property
    def url_base(self) -> str:
        return "https://pncp.gov.br"

    def buscar_editais(
        self,
        uf: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        palavras_chave: Optional[List[str]] = None
    ) -> ResultadoBusca:
        """
        Busca editais no PNCP.

        Args:
            uf: Filtrar por UF (ex: 'AM')
            data_inicio: Data inicial do período
            data_fim: Data final do período
            palavras_chave: Palavras-chave para filtrar objetos

        Returns:
            ResultadoBusca com os editais encontrados
        """
        tempo_inicio = time.time()
        resultado = ResultadoBusca(
            fonte=self.fonte,
            parametros_busca={
                'uf': uf,
                'data_inicio': data_inicio.isoformat() if data_inicio else None,
                'data_fim': data_fim.isoformat() if data_fim else None,
                'palavras_chave': palavras_chave
            }
        )

        if not HAS_REQUESTS:
            resultado.erros.append("Biblioteca 'requests' não está instalada")
            return resultado

        # Define período padrão se não especificado
        if not data_fim:
            data_fim = datetime.now()
        if not data_inicio:
            data_inicio = data_fim - timedelta(days=self.config.dias_retroativos)

        # Usa UF prioritária se não especificada
        uf_busca = uf or self.config.uf_prioritaria
        palavras = palavras_chave or self.config.palavras_chave

        try:
            editais = self._buscar_por_periodo(
                uf=uf_busca,
                data_inicio=data_inicio,
                data_fim=data_fim,
                palavras_chave=palavras,
                resultado=resultado
            )

            resultado.editais = editais
            resultado.total_encontrados = len(editais)
            resultado.com_rating = sum(1 for e in editais if e.tem_exigencia_rating)

        except Exception as e:
            self.logger.error(f"Erro na busca PNCP: {e}")
            resultado.erros.append(str(e))

        resultado.tempo_execucao = time.time() - tempo_inicio
        return resultado

    def _buscar_por_periodo(
        self,
        uf: str,
        data_inicio: datetime,
        data_fim: datetime,
        palavras_chave: List[str],
        resultado: ResultadoBusca
    ) -> List[Edital]:
        """Busca editais em um período específico."""
        editais = []
        pagina = 1
        tam_pagina = 50

        while True:
            params = {
                'dataInicial': data_inicio.strftime('%Y%m%d'),
                'dataFinal': data_fim.strftime('%Y%m%d'),
                'pagina': pagina,
                'tamanhoPagina': tam_pagina
            }

            # API usa 'uf' como string (ex: 'AM'), não código numérico
            if uf:
                params['uf'] = uf.upper()

            self.logger.info(f"Buscando página {pagina} - UF: {uf}")

            response = self._fazer_requisicao(
                url=self.API_CONTRATACOES,
                params=params,
                headers={'Accept': 'application/json'}
            )

            if not response:
                resultado.erros.append(f"Falha na requisição da página {pagina}")
                break

            try:
                dados = response.json()
            except Exception as e:
                resultado.erros.append(f"Erro ao parsear JSON: {e}")
                break

            # Processa contratações retornadas
            contratacoes = dados.get('data', [])

            if not contratacoes:
                self.logger.info(f"Nenhum resultado na página {pagina}")
                break

            for item in contratacoes:
                try:
                    edital = self._processar_contratacao(item, palavras_chave)
                    if edital:
                        editais.append(edital)
                except Exception as e:
                    self.logger.warning(f"Erro ao processar contratação: {e}")

            # Verifica se há mais páginas
            total_paginas = dados.get('totalPaginas', 1)
            if pagina >= total_paginas:
                break

            pagina += 1

            # Respeita intervalo entre requisições
            time.sleep(self.config.intervalo_requisicoes)

        return editais

    def _processar_contratacao(
        self,
        dados: Dict[str, Any],
        palavras_chave: List[str]
    ) -> Optional[Edital]:
        """Processa dados de uma contratação do PNCP."""
        objeto = dados.get('objetoCompra', '')

        # Verifica se objeto contém palavras-chave relevantes
        objeto_lower = objeto.lower()
        if palavras_chave:
            if not any(p.lower() in objeto_lower for p in palavras_chave):
                # Se não encontrar palavras-chave no objeto, busca detalhes
                # apenas se for licitação de valor alto
                valor = dados.get('valorTotalEstimado', 0) or 0
                if valor < 1000000:  # Menos de 1 milhão
                    return None

        # Extrai dados básicos
        orgao = dados.get('orgaoEntidade', {})
        local = dados.get('unidadeOrgao', {}) or {}

        edital = Edital(
            id_fonte=str(dados.get('sequencialCompra', '')),
            numero_edital=dados.get('numeroControlePNCP', ''),
            orgao=orgao.get('razaoSocial', 'Não informado'),
            objeto=objeto,
            fonte=self.fonte,
            url=self._construir_url_edital(dados),
            data_publicacao=self._extrair_data(dados.get('dataPublicacaoPncp')),
            data_abertura=self._extrair_data(dados.get('dataAberturaProposta')),
            valor_estimado=dados.get('valorTotalEstimado'),
            tipo_licitacao=self._mapear_modalidade(dados.get('modalidadeId')),
            uf=local.get('ufSigla', dados.get('uf', '')),
            municipio=local.get('municipioNome', ''),
            status=self._mapear_situacao(dados.get('situacaoCompraId'))
        )

        # Busca texto completo para análise de rating se configurado
        if self.config.salvar_texto_completo:
            texto_detalhes = self._obter_texto_completo(dados)
            if texto_detalhes:
                edital.texto_completo = texto_detalhes

        # Analisa exigência de rating
        edital = self.analisar_edital_rating(edital)

        # Calcula hash do conteúdo
        edital.hash_conteudo = self._calcular_hash(f"{edital.objeto}{edital.texto_completo}")

        # Metadata adicional
        edital.metadata = {
            'cnpj_orgao': orgao.get('cnpj', ''),
            'poder': orgao.get('poder', ''),
            'esfera': orgao.get('esferaId', ''),
            'modalidade_id': dados.get('modalidadeId'),
            'situacao_id': dados.get('situacaoCompraId'),
        }

        return edital

    def _construir_url_edital(self, dados: Dict[str, Any]) -> str:
        """Constrói URL para visualização do edital."""
        cnpj = dados.get('orgaoEntidade', {}).get('cnpj', '')
        ano = dados.get('anoCompra', '')
        seq = dados.get('sequencialCompra', '')

        if cnpj and ano and seq:
            return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"

        return f"https://pncp.gov.br"

    def _mapear_modalidade(self, modalidade_id: Optional[int]) -> TipoLicitacao:
        """Mapeia ID de modalidade para TipoLicitacao."""
        if modalidade_id:
            return self.MODALIDADES.get(modalidade_id, TipoLicitacao.OUTRO)
        return TipoLicitacao.OUTRO

    def _mapear_situacao(self, situacao_id: Optional[int]) -> StatusEdital:
        """Mapeia ID de situação para StatusEdital."""
        mapa = {
            1: StatusEdital.ABERTO,
            2: StatusEdital.EM_ANDAMENTO,
            3: StatusEdital.ENCERRADO,
            4: StatusEdital.SUSPENSO,
            5: StatusEdital.CANCELADO,
            6: StatusEdital.HOMOLOGADO,
        }
        if situacao_id:
            return mapa.get(situacao_id, StatusEdital.DESCONHECIDO)
        return StatusEdital.DESCONHECIDO

    def _obter_texto_completo(self, dados: Dict[str, Any]) -> str:
        """Obtém texto completo do edital incluindo documentos."""
        textos = []

        # Adiciona descrição do objeto
        if dados.get('objetoCompra'):
            textos.append(dados['objetoCompra'])

        # Adiciona informações complementares se disponíveis
        if dados.get('informacaoComplementar'):
            textos.append(dados['informacaoComplementar'])

        # Tenta obter arquivos do edital
        try:
            cnpj = dados.get('orgaoEntidade', {}).get('cnpj', '')
            ano = dados.get('anoCompra', '')
            seq = dados.get('sequencialCompra', '')

            if cnpj and ano and seq:
                url_arquivos = f"{self.API_DETALHES}/{cnpj}/{ano}/{seq}/arquivos"

                response = self._fazer_requisicao(
                    url=url_arquivos,
                    headers={'Accept': 'application/json'}
                )

                if response:
                    arquivos = response.json()
                    for arquivo in arquivos:
                        if arquivo.get('titulo'):
                            textos.append(f"Arquivo: {arquivo['titulo']}")
        except Exception as e:
            self.logger.debug(f"Erro ao obter arquivos: {e}")

        return '\n'.join(textos)

    def obter_detalhes_edital(self, id_edital: str) -> Optional[Edital]:
        """
        Obtém detalhes completos de um edital específico.

        Args:
            id_edital: Identificador no formato "cnpj/ano/sequencial"

        Returns:
            Edital com detalhes completos
        """
        try:
            # Parse do ID
            partes = id_edital.split('/')
            if len(partes) != 3:
                self.logger.error(f"ID inválido: {id_edital}. Formato esperado: cnpj/ano/sequencial")
                return None

            cnpj, ano, seq = partes

            url = f"{self.API_DETALHES}/{cnpj}/{ano}/{seq}"

            response = self._fazer_requisicao(
                url=url,
                headers={'Accept': 'application/json'}
            )

            if not response:
                return None

            dados = response.json()

            # Processa como contratação normal
            edital = self._processar_contratacao(dados, [])

            return edital

        except Exception as e:
            self.logger.error(f"Erro ao obter detalhes: {e}")
            return None

    def buscar_amazonas(
        self,
        dias: int = 30,
        apenas_com_rating: bool = False
    ) -> ResultadoBusca:
        """
        Busca específica para editais do Amazonas.

        Args:
            dias: Quantidade de dias retroativos
            apenas_com_rating: Retorna apenas editais com exigência de rating

        Returns:
            ResultadoBusca filtrado para Amazonas
        """
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)

        resultado = self.buscar_editais(
            uf='AM',
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        if apenas_com_rating:
            resultado.editais = [e for e in resultado.editais if e.tem_exigencia_rating]
            resultado.total_encontrados = len(resultado.editais)

        return resultado

    def buscar_por_objeto(
        self,
        termo: str,
        uf: Optional[str] = None,
        dias: int = 30
    ) -> ResultadoBusca:
        """
        Busca editais por termo no objeto.

        Args:
            termo: Termo a buscar no objeto
            uf: Filtrar por UF
            dias: Dias retroativos

        Returns:
            ResultadoBusca
        """
        return self.buscar_editais(
            uf=uf,
            data_inicio=datetime.now() - timedelta(days=dias),
            data_fim=datetime.now(),
            palavras_chave=[termo]
        )


# Função de conveniência para uso simples
def buscar_editais_pncp(
    uf: str = 'AM',
    dias: int = 30,
    apenas_rating: bool = True
) -> ResultadoBusca:
    """
    Função de conveniência para buscar editais no PNCP.

    Args:
        uf: UF para buscar (padrão: Amazonas)
        dias: Dias retroativos
        apenas_rating: Se True, retorna apenas com exigência de rating

    Returns:
        ResultadoBusca
    """
    config = ConfiguracaoCaptura(
        uf_prioritaria=uf,
        dias_retroativos=dias,
        apenas_com_rating=apenas_rating
    )

    with CapturadorPNCP(config) as capturador:
        return capturador.buscar_editais(uf=uf)


# Exemplo de uso e teste
if __name__ == '__main__':
    print("=" * 60)
    print("TESTE DO CAPTURADOR PNCP")
    print("=" * 60)

    # Verifica dependências
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

        resultado = buscar_editais_pncp(uf='AM', dias=7, apenas_rating=False)

        print(resultado.resumo())

        if resultado.editais:
            print("\nEditais encontrados:")
            for edital in resultado.editais[:5]:  # Mostra 5 primeiros
                print(edital.resumo())
