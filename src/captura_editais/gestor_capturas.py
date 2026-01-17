"""
Gestor de capturas de editais com exigência de rating.

Este módulo orquestra múltiplos capturadores e consolida os resultados,
gerando relatórios e alertas sobre editais relevantes.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import logging

from .modelos import (
    Edital,
    FonteEdital,
    ResultadoBusca,
    ConfiguracaoCaptura,
    NivelRating
)
from .capturador_pncp import CapturadorPNCP
from .capturador_amazonas import CapturadorAmazonas


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GestorCapturas')


@dataclass
class RelatorioConsolidado:
    """Relatório consolidado de todas as fontes."""
    data_geracao: datetime = field(default_factory=datetime.now)
    periodo_inicio: Optional[datetime] = None
    periodo_fim: Optional[datetime] = None
    total_fontes: int = 0
    total_editais: int = 0
    total_com_rating: int = 0
    total_amazonas: int = 0
    editais_rating_amazonas: int = 0
    resultados_por_fonte: Dict[str, ResultadoBusca] = field(default_factory=dict)
    todos_editais: List[Edital] = field(default_factory=list)
    editais_prioritarios: List[Edital] = field(default_factory=list)
    erros: List[str] = field(default_factory=list)
    tempo_total: float = 0.0

    @property
    def taxa_rating_geral(self) -> float:
        if self.total_editais > 0:
            return (self.total_com_rating / self.total_editais) * 100
        return 0.0

    @property
    def taxa_rating_amazonas(self) -> float:
        if self.total_amazonas > 0:
            return (self.editais_rating_amazonas / self.total_amazonas) * 100
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'data_geracao': self.data_geracao.isoformat(),
            'periodo_inicio': self.periodo_inicio.isoformat() if self.periodo_inicio else None,
            'periodo_fim': self.periodo_fim.isoformat() if self.periodo_fim else None,
            'total_fontes': self.total_fontes,
            'total_editais': self.total_editais,
            'total_com_rating': self.total_com_rating,
            'total_amazonas': self.total_amazonas,
            'editais_rating_amazonas': self.editais_rating_amazonas,
            'taxa_rating_geral': self.taxa_rating_geral,
            'taxa_rating_amazonas': self.taxa_rating_amazonas,
            'erros': self.erros,
            'tempo_total': self.tempo_total,
            'editais': [e.to_dict() for e in self.todos_editais],
            'editais_prioritarios': [e.to_dict() for e in self.editais_prioritarios]
        }


class GestorCapturas:
    """
    Gestor central para captura de editais de múltiplas fontes.

    Orquestra os capturadores, consolida resultados e gera relatórios.
    """

    def __init__(
        self,
        configuracao: Optional[ConfiguracaoCaptura] = None,
        diretorio_saida: str = './output/editais'
    ):
        """
        Inicializa o gestor de capturas.

        Args:
            configuracao: Configurações de captura
            diretorio_saida: Diretório para salvar resultados
        """
        self.config = configuracao or ConfiguracaoCaptura()
        self.diretorio_saida = diretorio_saida

        # Cria diretório de saída se não existir
        os.makedirs(self.diretorio_saida, exist_ok=True)

        # Inicializa capturadores
        self.capturadores = {
            FonteEdital.PNCP: CapturadorPNCP(self.config),
            FonteEdital.AMAZONAS: CapturadorAmazonas(self.config),
        }

        logger.info(f"GestorCapturas inicializado com {len(self.capturadores)} capturadores")

    def capturar_tudo(
        self,
        uf: Optional[str] = None,
        dias: int = 30,
        apenas_rating: bool = False
    ) -> RelatorioConsolidado:
        """
        Executa captura em todas as fontes disponíveis.

        Args:
            uf: Filtrar por UF (padrão: AM)
            dias: Dias retroativos
            apenas_rating: Se True, filtra apenas editais com rating

        Returns:
            RelatorioConsolidado com todos os resultados
        """
        import time
        tempo_inicio = time.time()

        uf = uf or self.config.uf_prioritaria
        data_fim = datetime.now()
        data_inicio = data_fim - timedelta(days=dias)

        relatorio = RelatorioConsolidado(
            periodo_inicio=data_inicio,
            periodo_fim=data_fim
        )

        logger.info(f"Iniciando captura: UF={uf}, Período={data_inicio.date()} a {data_fim.date()}")

        for fonte, capturador in self.capturadores.items():
            try:
                logger.info(f"Capturando de {fonte.value}...")

                resultado = capturador.buscar_editais(
                    uf=uf,
                    data_inicio=data_inicio,
                    data_fim=data_fim
                )

                relatorio.resultados_por_fonte[fonte.value] = resultado
                relatorio.total_fontes += 1
                relatorio.erros.extend(resultado.erros)

                logger.info(
                    f"  {fonte.value}: {resultado.total_encontrados} editais, "
                    f"{resultado.com_rating} com rating"
                )

            except Exception as e:
                logger.error(f"Erro ao capturar de {fonte.value}: {e}")
                relatorio.erros.append(f"{fonte.value}: {e}")

        # Consolida editais
        self._consolidar_editais(relatorio, apenas_rating)

        relatorio.tempo_total = time.time() - tempo_inicio

        logger.info(
            f"Captura concluída em {relatorio.tempo_total:.2f}s: "
            f"{relatorio.total_editais} editais, {relatorio.total_com_rating} com rating"
        )

        return relatorio

    def capturar_amazonas(
        self,
        dias: int = 30,
        apenas_rating: bool = False
    ) -> RelatorioConsolidado:
        """
        Captura focada apenas no Amazonas.

        Args:
            dias: Dias retroativos
            apenas_rating: Se True, retorna apenas com rating

        Returns:
            RelatorioConsolidado
        """
        return self.capturar_tudo(uf='AM', dias=dias, apenas_rating=apenas_rating)

    def _consolidar_editais(
        self,
        relatorio: RelatorioConsolidado,
        apenas_rating: bool
    ) -> None:
        """Consolida editais de todas as fontes."""
        todos = []
        numeros_vistos = set()

        for resultado in relatorio.resultados_por_fonte.values():
            for edital in resultado.editais:
                # Evita duplicatas
                chave = (edital.numero_edital.lower(), edital.orgao.lower())
                if chave in numeros_vistos:
                    continue
                numeros_vistos.add(chave)

                # Aplica filtro de rating se necessário
                if apenas_rating and not edital.tem_exigencia_rating:
                    continue

                todos.append(edital)

        # Ordena por data de abertura (mais recentes primeiro)
        todos.sort(
            key=lambda e: e.data_abertura or datetime.min,
            reverse=True
        )

        relatorio.todos_editais = todos
        relatorio.total_editais = len(todos)
        relatorio.total_com_rating = sum(1 for e in todos if e.tem_exigencia_rating)

        # Estatísticas do Amazonas
        amazonas = [e for e in todos if e.eh_amazonas]
        relatorio.total_amazonas = len(amazonas)
        relatorio.editais_rating_amazonas = sum(1 for e in amazonas if e.tem_exigencia_rating)

        # Identifica editais prioritários
        relatorio.editais_prioritarios = self._identificar_prioritarios(todos)

    def _identificar_prioritarios(self, editais: List[Edital]) -> List[Edital]:
        """
        Identifica editais prioritários para atenção.

        Critérios:
        - Exige rating
        - Alto valor
        - Amazonas
        - Prazo próximo
        """
        prioritarios = []

        for edital in editais:
            pontuacao = 0

            # Exige rating = alta prioridade
            if edital.tem_exigencia_rating:
                pontuacao += 50

            # É do Amazonas = prioridade
            if edital.eh_amazonas:
                pontuacao += 30

            # Alto valor
            if edital.valor_estimado:
                if edital.valor_estimado >= 50_000_000:
                    pontuacao += 30
                elif edital.valor_estimado >= 10_000_000:
                    pontuacao += 20
                elif edital.valor_estimado >= 1_000_000:
                    pontuacao += 10

            # Prazo próximo (próximos 7 dias)
            if edital.data_abertura:
                dias_restantes = (edital.data_abertura - datetime.now()).days
                if 0 <= dias_restantes <= 7:
                    pontuacao += 20

            # Adiciona se pontuação suficiente
            if pontuacao >= 50:
                edital.metadata['pontuacao_prioridade'] = pontuacao
                prioritarios.append(edital)

        # Ordena por pontuação
        prioritarios.sort(
            key=lambda e: e.metadata.get('pontuacao_prioridade', 0),
            reverse=True
        )

        return prioritarios

    def gerar_relatorio_texto(self, relatorio: RelatorioConsolidado) -> str:
        """Gera relatório em formato texto."""
        linhas = [
            "=" * 70,
            "RELATÓRIO DE EDITAIS COM EXIGÊNCIA DE RATING",
            f"Gerado em: {relatorio.data_geracao.strftime('%d/%m/%Y %H:%M')}",
            "=" * 70,
            "",
            "RESUMO EXECUTIVO",
            "-" * 40,
            f"Período: {relatorio.periodo_inicio.strftime('%d/%m/%Y') if relatorio.periodo_inicio else 'N/A'} "
            f"a {relatorio.periodo_fim.strftime('%d/%m/%Y') if relatorio.periodo_fim else 'N/A'}",
            f"Fontes consultadas: {relatorio.total_fontes}",
            f"Tempo de execução: {relatorio.tempo_total:.2f}s",
            "",
            f"Total de editais encontrados: {relatorio.total_editais}",
            f"Editais com exigência de rating: {relatorio.total_com_rating}",
            f"Taxa de rating: {relatorio.taxa_rating_geral:.1f}%",
            "",
            "FOCO: AMAZONAS",
            "-" * 40,
            f"Total de editais AM: {relatorio.total_amazonas}",
            f"Editais AM com rating: {relatorio.editais_rating_amazonas}",
            f"Taxa de rating AM: {relatorio.taxa_rating_amazonas:.1f}%",
            "",
        ]

        # Resultados por fonte
        linhas.extend([
            "RESULTADOS POR FONTE",
            "-" * 40,
        ])
        for fonte, resultado in relatorio.resultados_por_fonte.items():
            linhas.append(
                f"  {fonte}: {resultado.total_encontrados} editais, "
                f"{resultado.com_rating} com rating"
            )

        # Editais prioritários
        if relatorio.editais_prioritarios:
            linhas.extend([
                "",
                "EDITAIS PRIORITÁRIOS (Rating + Alta Relevância)",
                "=" * 70,
            ])

            for i, edital in enumerate(relatorio.editais_prioritarios[:10], 1):
                linhas.extend([
                    f"\n{i}. {edital.numero_edital}",
                    f"   Órgão: {edital.orgao}",
                    f"   Local: {edital.municipio or edital.uf}",
                    f"   Objeto: {edital.objeto[:100]}..." if len(edital.objeto) > 100 else f"   Objeto: {edital.objeto}",
                    f"   Valor: R$ {edital.valor_estimado:,.2f}" if edital.valor_estimado else "   Valor: Não informado",
                    f"   Abertura: {edital.data_abertura.strftime('%d/%m/%Y') if edital.data_abertura else 'N/A'}",
                ])

                if edital.tem_exigencia_rating:
                    rating = edital.exigencia_rating
                    linhas.extend([
                        f"   >>> RATING: {rating.nivel_minimo.value}",
                        f"   >>> Agências: {', '.join(a.value for a in rating.agencias_aceitas)}",
                    ])

                linhas.append(f"   URL: {edital.url}")

        # Todos editais com rating
        editais_rating = [e for e in relatorio.todos_editais if e.tem_exigencia_rating]
        if editais_rating:
            linhas.extend([
                "",
                f"TODOS EDITAIS COM EXIGÊNCIA DE RATING ({len(editais_rating)})",
                "=" * 70,
            ])

            for edital in editais_rating:
                linhas.append(f"\n{'-' * 50}")
                linhas.append(edital.resumo())

        # Erros
        if relatorio.erros:
            linhas.extend([
                "",
                "ERROS E AVISOS",
                "-" * 40,
                *[f"  - {erro}" for erro in relatorio.erros]
            ])

        linhas.append("\n" + "=" * 70)
        linhas.append("FIM DO RELATÓRIO")
        linhas.append("=" * 70)

        return '\n'.join(linhas)

    def salvar_relatorio(
        self,
        relatorio: RelatorioConsolidado,
        formato: str = 'json'
    ) -> str:
        """
        Salva relatório em arquivo.

        Args:
            relatorio: Relatório a salvar
            formato: 'json' ou 'txt'

        Returns:
            Caminho do arquivo salvo
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if formato == 'json':
            nome_arquivo = f"relatorio_editais_{timestamp}.json"
            caminho = os.path.join(self.diretorio_saida, nome_arquivo)

            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(relatorio.to_dict(), f, ensure_ascii=False, indent=2)

        else:  # txt
            nome_arquivo = f"relatorio_editais_{timestamp}.txt"
            caminho = os.path.join(self.diretorio_saida, nome_arquivo)

            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(self.gerar_relatorio_texto(relatorio))

        logger.info(f"Relatório salvo em: {caminho}")
        return caminho

    def salvar_editais_csv(
        self,
        relatorio: RelatorioConsolidado,
        apenas_rating: bool = True
    ) -> str:
        """
        Salva editais em formato CSV.

        Args:
            relatorio: Relatório com editais
            apenas_rating: Se True, salva apenas com rating

        Returns:
            Caminho do arquivo
        """
        editais = relatorio.todos_editais
        if apenas_rating:
            editais = [e for e in editais if e.tem_exigencia_rating]

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nome_arquivo = f"editais_rating_{timestamp}.csv"
        caminho = os.path.join(self.diretorio_saida, nome_arquivo)

        # Cabeçalho
        colunas = [
            'numero_edital', 'orgao', 'uf', 'municipio', 'objeto',
            'valor_estimado', 'data_abertura', 'tipo_licitacao',
            'tem_rating', 'nivel_rating', 'agencias', 'url', 'fonte'
        ]

        linhas = [';'.join(colunas)]

        for edital in editais:
            valores = [
                edital.numero_edital,
                edital.orgao,
                edital.uf,
                edital.municipio,
                edital.objeto[:200].replace(';', ','),
                str(edital.valor_estimado or ''),
                edital.data_abertura.strftime('%d/%m/%Y') if edital.data_abertura else '',
                edital.tipo_licitacao.value,
                'Sim' if edital.tem_exigencia_rating else 'Não',
                edital.exigencia_rating.nivel_minimo.value if edital.tem_exigencia_rating else '',
                ', '.join(a.value for a in edital.exigencia_rating.agencias_aceitas) if edital.tem_exigencia_rating else '',
                edital.url,
                edital.fonte.value
            ]
            linhas.append(';'.join(valores))

        with open(caminho, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(linhas))

        logger.info(f"CSV salvo em: {caminho}")
        return caminho

    def gerar_alertas(self, relatorio: RelatorioConsolidado) -> List[str]:
        """
        Gera alertas para editais que requerem atenção imediata.

        Args:
            relatorio: Relatório consolidado

        Returns:
            Lista de mensagens de alerta
        """
        alertas = []

        for edital in relatorio.editais_prioritarios:
            if not edital.tem_exigencia_rating:
                continue

            # Verifica prazo
            if edital.data_abertura:
                dias_restantes = (edital.data_abertura - datetime.now()).days

                if dias_restantes < 0:
                    continue  # Já passou

                if dias_restantes <= 3:
                    urgencia = "URGENTE"
                elif dias_restantes <= 7:
                    urgencia = "ATENÇÃO"
                else:
                    urgencia = "INFO"

                alerta = (
                    f"[{urgencia}] Edital com Rating - {edital.numero_edital}\n"
                    f"  Órgão: {edital.orgao}\n"
                    f"  Local: {edital.uf}/{edital.municipio}\n"
                    f"  Rating exigido: {edital.exigencia_rating.nivel_minimo.value}\n"
                    f"  Valor: R$ {edital.valor_estimado:,.2f}" if edital.valor_estimado else ""
                    f"  Abertura: {edital.data_abertura.strftime('%d/%m/%Y')} ({dias_restantes} dias)\n"
                    f"  URL: {edital.url}"
                )
                alertas.append(alerta)

        return alertas

    def fechar(self) -> None:
        """Fecha todos os capturadores."""
        for capturador in self.capturadores.values():
            capturador.fechar()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fechar()


# Funções de conveniência
def capturar_editais_rating_amazonas(
    dias: int = 30,
    salvar: bool = True
) -> RelatorioConsolidado:
    """
    Função rápida para capturar editais com rating do Amazonas.

    Args:
        dias: Dias retroativos
        salvar: Se True, salva automaticamente

    Returns:
        RelatorioConsolidado
    """
    with GestorCapturas() as gestor:
        relatorio = gestor.capturar_amazonas(dias=dias, apenas_rating=False)

        if salvar:
            gestor.salvar_relatorio(relatorio, formato='json')
            gestor.salvar_relatorio(relatorio, formato='txt')
            gestor.salvar_editais_csv(relatorio, apenas_rating=True)

        return relatorio


def buscar_e_alertar(dias: int = 7) -> None:
    """
    Busca editais e imprime alertas importantes.

    Args:
        dias: Dias retroativos
    """
    with GestorCapturas() as gestor:
        relatorio = gestor.capturar_amazonas(dias=dias)

        print("\n" + "=" * 60)
        print("ALERTAS DE EDITAIS COM EXIGÊNCIA DE RATING")
        print("=" * 60)

        alertas = gestor.gerar_alertas(relatorio)

        if alertas:
            for alerta in alertas:
                print(f"\n{alerta}")
        else:
            print("\nNenhum edital com rating encontrado com prazo próximo.")

        print(f"\n\nResumo: {relatorio.total_com_rating} editais com rating de {relatorio.total_editais} total")
        print(f"Amazonas: {relatorio.editais_rating_amazonas} com rating de {relatorio.total_amazonas} total")


if __name__ == '__main__':
    print("Iniciando captura de editais...")
    buscar_e_alertar(dias=30)
