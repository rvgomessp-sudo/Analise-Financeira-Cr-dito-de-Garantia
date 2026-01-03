"""
Gerador de Relatórios Financeiros Comparativos
Produz relatórios em HTML, Excel e PDF
"""

import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import pandas as pd
from jinja2 import Template

from ..models.seguradora import Seguradora
from ..analysis.comparador import ComparadorSeguradora, ResultadoComparacao
from ..analysis.indicadores import AnalisadorIndicadores


class GeradorRelatorios:
    """
    Classe responsável por gerar relatórios financeiros comparativos
    em diversos formatos (HTML, Excel, PDF)
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.comparador = ComparadorSeguradora()
        self.analisador = AnalisadorIndicadores()

    def carregar_seguradoras(self, seguradoras: List[Seguradora]) -> None:
        """Carrega as seguradoras para análise"""
        self.comparador = ComparadorSeguradora()
        self.comparador.adicionar_multiplas(seguradoras)

    def gerar_relatorio_completo(
        self,
        nome_arquivo: str = "relatorio_comparativo",
        formatos: List[str] = None
    ) -> dict:
        """
        Gera relatório completo em múltiplos formatos

        Args:
            nome_arquivo: Nome base do arquivo (sem extensão)
            formatos: Lista de formatos ('html', 'excel', 'pdf')

        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        if formatos is None:
            formatos = ['html', 'excel']

        resultado = self.comparador.comparar()
        arquivos_gerados = {}

        if 'html' in formatos:
            arquivos_gerados['html'] = self._gerar_html(resultado, nome_arquivo)

        if 'excel' in formatos:
            arquivos_gerados['excel'] = self._gerar_excel(resultado, nome_arquivo)

        if 'pdf' in formatos:
            arquivos_gerados['pdf'] = self._gerar_pdf(resultado, nome_arquivo)

        return arquivos_gerados

    def _gerar_html(self, resultado: ResultadoComparacao, nome_arquivo: str) -> str:
        """Gera relatório em formato HTML"""
        html_template = self._get_html_template()

        # Prepara dados para o template
        stats = resultado.estatisticas_setor
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")

        # Converte DataFrames para HTML
        ranking_geral_html = resultado.ranking_geral.to_html(
            classes='table table-striped table-hover',
            index=False,
            float_format=lambda x: f'{x:,.2f}'
        )

        ranking_solvencia_html = resultado.ranking_solvencia.to_html(
            classes='table table-striped',
            index=False,
            float_format=lambda x: f'{x:,.2f}'
        )

        ranking_liquidez_html = resultado.ranking_liquidez.to_html(
            classes='table table-striped',
            index=False,
            float_format=lambda x: f'{x:,.2f}'
        )

        ranking_rentabilidade_html = resultado.ranking_rentabilidade.to_html(
            classes='table table-striped',
            index=False,
            float_format=lambda x: f'{x:,.2f}'
        )

        ranking_sinistralidade_html = resultado.ranking_sinistralidade.to_html(
            classes='table table-striped',
            index=False,
            float_format=lambda x: f'{x:,.2f}'
        )

        matriz_html = resultado.matriz_comparativa.to_html(
            classes='table table-bordered',
            index=False,
            float_format=lambda x: f'{x:,.2f}'
        )

        # Prepara dados para gráfico
        chart_data = {
            'labels': resultado.ranking_geral['Seguradora'].tolist(),
            'scores': resultado.ranking_geral['Score Força Financeira'].tolist(),
            'ratings': resultado.ranking_geral['Rating'].tolist()
        }

        # Dados das seguradoras para análise detalhada
        seguradoras_detalhes = []
        for seg in self.comparador.seguradoras:
            pontos_fortes, pontos_fracos = self.analisador.analisar_pontos_fortes_fracos(
                seg.indicadores
            )
            seguradoras_detalhes.append({
                'nome': seg.nome,
                'rating': seg.indicadores.classificacao_risco,
                'score': seg.indicadores.score_forca_financeira,
                'pontos_fortes': pontos_fortes,
                'pontos_fracos': pontos_fracos,
                'indicadores': seg.indicadores
            })

        # Renderiza template
        template = Template(html_template)
        html_content = template.render(
            data_geracao=data_geracao,
            total_seguradoras=stats['total_seguradoras'],
            ativo_total=stats['ativo_total_setor'],
            pl_total=stats['pl_total_setor'],
            premios_total=stats['premios_total_setor'],
            lucro_total=stats['lucro_total_setor'],
            melhor_seguradora=stats['melhor'],
            pior_seguradora=stats['pior'],
            medias=stats['media'],
            medianas=stats['mediana'],
            distribuicao_rating=stats['distribuicao_rating'],
            ranking_geral=ranking_geral_html,
            ranking_solvencia=ranking_solvencia_html,
            ranking_liquidez=ranking_liquidez_html,
            ranking_rentabilidade=ranking_rentabilidade_html,
            ranking_sinistralidade=ranking_sinistralidade_html,
            matriz_comparativa=matriz_html,
            chart_data=chart_data,
            seguradoras_detalhes=seguradoras_detalhes
        )

        # Salva arquivo
        filepath = self.output_dir / f"{nome_arquivo}.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(filepath)

    def _gerar_excel(self, resultado: ResultadoComparacao, nome_arquivo: str) -> str:
        """Gera relatório em formato Excel"""
        filepath = self.output_dir / f"{nome_arquivo}.xlsx"

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Aba de Resumo Executivo
            resumo_data = {
                'Métrica': [
                    'Total de Seguradoras',
                    'Ativo Total do Setor (R$ MM)',
                    'Patrimônio Líquido Total (R$ MM)',
                    'Prêmios Emitidos Total (R$ MM)',
                    'Lucro Líquido Total (R$ MM)',
                    '',
                    'Score Médio de Força Financeira',
                    'Índice de Solvência Médio',
                    'Liquidez Corrente Média',
                    'ROE Médio (%)',
                    'Sinistralidade Média (%)',
                    'Índice Combinado Médio (%)',
                    '',
                    'Melhor Seguradora',
                    'Score da Melhor',
                    'Rating da Melhor',
                    '',
                    'Seguradora com Menor Score',
                    'Score da Pior',
                    'Rating da Pior'
                ],
                'Valor': [
                    resultado.estatisticas_setor['total_seguradoras'],
                    f"{resultado.estatisticas_setor['ativo_total_setor']:,.2f}",
                    f"{resultado.estatisticas_setor['pl_total_setor']:,.2f}",
                    f"{resultado.estatisticas_setor['premios_total_setor']:,.2f}",
                    f"{resultado.estatisticas_setor['lucro_total_setor']:,.2f}",
                    '',
                    f"{resultado.estatisticas_setor['media']['score_forca_financeira']:.2f}",
                    f"{resultado.estatisticas_setor['media']['indice_solvencia']:.2f}",
                    f"{resultado.estatisticas_setor['media']['liquidez_corrente']:.2f}",
                    f"{resultado.estatisticas_setor['media']['roe']:.2f}",
                    f"{resultado.estatisticas_setor['media']['sinistralidade']:.2f}",
                    f"{resultado.estatisticas_setor['media']['indice_combinado']:.2f}",
                    '',
                    resultado.estatisticas_setor['melhor']['seguradora'],
                    f"{resultado.estatisticas_setor['melhor']['score']:.2f}",
                    resultado.estatisticas_setor['melhor']['rating'],
                    '',
                    resultado.estatisticas_setor['pior']['seguradora'],
                    f"{resultado.estatisticas_setor['pior']['score']:.2f}",
                    resultado.estatisticas_setor['pior']['rating']
                ]
            }
            df_resumo = pd.DataFrame(resumo_data)
            df_resumo.to_excel(writer, sheet_name='Resumo Executivo', index=False)

            # Aba de Ranking Geral
            resultado.ranking_geral.to_excel(
                writer, sheet_name='Ranking Geral', index=False
            )

            # Aba de Ranking Solvência
            resultado.ranking_solvencia.to_excel(
                writer, sheet_name='Ranking Solvência', index=False
            )

            # Aba de Ranking Liquidez
            resultado.ranking_liquidez.to_excel(
                writer, sheet_name='Ranking Liquidez', index=False
            )

            # Aba de Ranking Rentabilidade
            resultado.ranking_rentabilidade.to_excel(
                writer, sheet_name='Ranking Rentabilidade', index=False
            )

            # Aba de Ranking Sinistralidade
            resultado.ranking_sinistralidade.to_excel(
                writer, sheet_name='Ranking Sinistralidade', index=False
            )

            # Aba de Matriz Comparativa Completa
            resultado.matriz_comparativa.to_excel(
                writer, sheet_name='Matriz Comparativa', index=False
            )

            # Aba de Análise Individual
            analises = []
            for seg in self.comparador.seguradoras:
                ind = seg.indicadores
                pontos_fortes, pontos_fracos = self.analisador.analisar_pontos_fortes_fracos(ind)

                analises.append({
                    'Seguradora': seg.nome,
                    'Rating': ind.classificacao_risco,
                    'Score': ind.score_forca_financeira,
                    'Pontos Fortes': '; '.join(pontos_fortes),
                    'Pontos Fracos': '; '.join(pontos_fracos)
                })

            df_analises = pd.DataFrame(analises)
            df_analises.to_excel(writer, sheet_name='Análise Individual', index=False)

            # Aba de Distribuição de Ratings
            dist_rating = pd.DataFrame([
                {'Rating': rating, 'Quantidade': count}
                for rating, count in resultado.estatisticas_setor['distribuicao_rating'].items()
            ])
            dist_rating.to_excel(writer, sheet_name='Distribuição Ratings', index=False)

        return str(filepath)

    def _gerar_pdf(self, resultado: ResultadoComparacao, nome_arquivo: str) -> str:
        """Gera relatório em formato PDF"""
        # Primeiro gera o HTML
        html_path = self._gerar_html(resultado, f"{nome_arquivo}_temp")

        pdf_path = self.output_dir / f"{nome_arquivo}.pdf"

        try:
            # Tenta usar weasyprint
            from weasyprint import HTML
            HTML(filename=html_path).write_pdf(str(pdf_path))
        except ImportError:
            try:
                # Fallback para pdfkit
                import pdfkit
                pdfkit.from_file(html_path, str(pdf_path))
            except Exception:
                # Se nenhum funcionar, retorna o HTML
                print("Aviso: Não foi possível gerar PDF. WeasyPrint ou pdfkit não disponível.")
                return html_path

        # Remove HTML temporário
        os.remove(html_path)

        return str(pdf_path)

    def _get_html_template(self) -> str:
        """Retorna o template HTML para o relatório"""
        return '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Comparativo - Força Financeira de Seguradoras</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-color: #1a365d;
            --secondary-color: #2b6cb0;
            --success-color: #38a169;
            --warning-color: #d69e2e;
            --danger-color: #e53e3e;
            --light-bg: #f7fafc;
            --border-color: #e2e8f0;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--light-bg);
            color: #2d3748;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 40px 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-bottom: 30px;
            overflow: hidden;
        }

        .card-header {
            background: var(--primary-color);
            color: white;
            padding: 15px 20px;
            font-size: 1.2rem;
            font-weight: 600;
        }

        .card-body {
            padding: 20px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border-left: 4px solid var(--secondary-color);
        }

        .metric-card h3 {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 10px;
            text-transform: uppercase;
        }

        .metric-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .metric-card .unit {
            font-size: 0.9rem;
            color: #a0aec0;
        }

        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .table th {
            background: var(--primary-color);
            color: white;
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
        }

        .table td {
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }

        .table-striped tbody tr:nth-child(odd) {
            background-color: #f8fafc;
        }

        .table-hover tbody tr:hover {
            background-color: #edf2f7;
        }

        .rating-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
        }

        .rating-aaa, .rating-aa { background: #c6f6d5; color: #22543d; }
        .rating-a { background: #bee3f8; color: #2a4365; }
        .rating-bbb, .rating-bb { background: #fefcbf; color: #744210; }
        .rating-b, .rating-ccc { background: #fed7d7; color: #742a2a; }
        .rating-cc, .rating-c, .rating-d { background: #feb2b2; color: #742a2a; }

        .chart-container {
            position: relative;
            height: 400px;
            margin: 20px 0;
        }

        .tabs {
            display: flex;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 20px;
        }

        .tab {
            padding: 12px 24px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1rem;
            color: #718096;
            transition: all 0.3s;
        }

        .tab:hover {
            color: var(--primary-color);
        }

        .tab.active {
            color: var(--primary-color);
            border-bottom: 2px solid var(--primary-color);
            margin-bottom: -2px;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .highlight-box {
            background: linear-gradient(135deg, #ebf8ff, #bee3f8);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .highlight-box.success {
            background: linear-gradient(135deg, #f0fff4, #c6f6d5);
        }

        .highlight-box.warning {
            background: linear-gradient(135deg, #fffff0, #fefcbf);
        }

        .highlight-box h4 {
            color: var(--primary-color);
            margin-bottom: 10px;
        }

        .pontos-lista {
            list-style: none;
            padding: 0;
        }

        .pontos-lista li {
            padding: 8px 0;
            border-bottom: 1px solid var(--border-color);
        }

        .pontos-lista li:last-child {
            border-bottom: none;
        }

        .ponto-forte::before {
            content: "✓ ";
            color: var(--success-color);
            font-weight: bold;
        }

        .ponto-fraco::before {
            content: "✗ ";
            color: var(--danger-color);
            font-weight: bold;
        }

        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        @media (max-width: 768px) {
            .two-column {
                grid-template-columns: 1fr;
            }

            header h1 {
                font-size: 1.8rem;
            }

            .tabs {
                flex-wrap: wrap;
            }

            .tab {
                padding: 10px 15px;
            }
        }

        footer {
            text-align: center;
            padding: 30px;
            color: #718096;
            font-size: 0.9rem;
        }

        .print-only {
            display: none;
        }

        @media print {
            .no-print {
                display: none;
            }

            .print-only {
                display: block;
            }

            .card {
                break-inside: avoid;
            }

            body {
                background: white;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Relatório Comparativo de Força Financeira</h1>
            <p>Análise Comparativa de Seguradoras | Gerado em {{ data_geracao }}</p>
        </header>

        <!-- Métricas Resumo -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Seguradoras Analisadas</h3>
                <div class="value">{{ total_seguradoras }}</div>
            </div>
            <div class="metric-card">
                <h3>Ativo Total do Setor</h3>
                <div class="value">R$ {{ "%.2f"|format(ativo_total) }}</div>
                <div class="unit">milhões</div>
            </div>
            <div class="metric-card">
                <h3>Patrimônio Líquido Total</h3>
                <div class="value">R$ {{ "%.2f"|format(pl_total) }}</div>
                <div class="unit">milhões</div>
            </div>
            <div class="metric-card">
                <h3>Prêmios Emitidos Total</h3>
                <div class="value">R$ {{ "%.2f"|format(premios_total) }}</div>
                <div class="unit">milhões</div>
            </div>
        </div>

        <!-- Destaques -->
        <div class="two-column">
            <div class="highlight-box success">
                <h4>🏆 Melhor Seguradora</h4>
                <p><strong>{{ melhor_seguradora.seguradora }}</strong></p>
                <p>Score: {{ "%.1f"|format(melhor_seguradora.score) }} | Rating: {{ melhor_seguradora.rating }}</p>
            </div>
            <div class="highlight-box warning">
                <h4>⚠️ Requer Atenção</h4>
                <p><strong>{{ pior_seguradora.seguradora }}</strong></p>
                <p>Score: {{ "%.1f"|format(pior_seguradora.score) }} | Rating: {{ pior_seguradora.rating }}</p>
            </div>
        </div>

        <!-- Gráfico de Scores -->
        <div class="card">
            <div class="card-header">📊 Comparativo de Força Financeira</div>
            <div class="card-body">
                <div class="chart-container">
                    <canvas id="scoreChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Rankings por Categoria -->
        <div class="card">
            <div class="card-header">📈 Rankings por Categoria</div>
            <div class="card-body">
                <div class="tabs no-print">
                    <button class="tab active" onclick="showTab('geral')">Geral</button>
                    <button class="tab" onclick="showTab('solvencia')">Solvência</button>
                    <button class="tab" onclick="showTab('liquidez')">Liquidez</button>
                    <button class="tab" onclick="showTab('rentabilidade')">Rentabilidade</button>
                    <button class="tab" onclick="showTab('sinistralidade')">Sinistralidade</button>
                </div>

                <div id="tab-geral" class="tab-content active">
                    <h4>Ranking Geral de Força Financeira</h4>
                    {{ ranking_geral | safe }}
                </div>

                <div id="tab-solvencia" class="tab-content">
                    <h4>Ranking de Solvência</h4>
                    {{ ranking_solvencia | safe }}
                </div>

                <div id="tab-liquidez" class="tab-content">
                    <h4>Ranking de Liquidez</h4>
                    {{ ranking_liquidez | safe }}
                </div>

                <div id="tab-rentabilidade" class="tab-content">
                    <h4>Ranking de Rentabilidade</h4>
                    {{ ranking_rentabilidade | safe }}
                </div>

                <div id="tab-sinistralidade" class="tab-content">
                    <h4>Ranking de Sinistralidade</h4>
                    {{ ranking_sinistralidade | safe }}
                </div>
            </div>
        </div>

        <!-- Matriz Comparativa -->
        <div class="card">
            <div class="card-header">📋 Matriz Comparativa Completa</div>
            <div class="card-body" style="overflow-x: auto;">
                {{ matriz_comparativa | safe }}
            </div>
        </div>

        <!-- Estatísticas do Setor -->
        <div class="card">
            <div class="card-header">📉 Estatísticas do Setor</div>
            <div class="card-body">
                <div class="two-column">
                    <div>
                        <h4 style="margin-bottom: 15px;">Médias do Setor</h4>
                        <table class="table">
                            <tr><td>Score de Força Financeira</td><td><strong>{{ "%.2f"|format(medias.score_forca_financeira) }}</strong></td></tr>
                            <tr><td>Índice de Solvência</td><td><strong>{{ "%.2f"|format(medias.indice_solvencia) }}</strong></td></tr>
                            <tr><td>Liquidez Corrente</td><td><strong>{{ "%.2f"|format(medias.liquidez_corrente) }}</strong></td></tr>
                            <tr><td>ROE</td><td><strong>{{ "%.2f"|format(medias.roe) }}%</strong></td></tr>
                            <tr><td>Sinistralidade</td><td><strong>{{ "%.2f"|format(medias.sinistralidade) }}%</strong></td></tr>
                            <tr><td>Índice Combinado</td><td><strong>{{ "%.2f"|format(medias.indice_combinado) }}%</strong></td></tr>
                        </table>
                    </div>
                    <div>
                        <h4 style="margin-bottom: 15px;">Distribuição de Ratings</h4>
                        <div class="chart-container" style="height: 250px;">
                            <canvas id="ratingChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Análise Individual -->
        <div class="card">
            <div class="card-header">🔍 Análise Individual das Seguradoras</div>
            <div class="card-body">
                {% for seg in seguradoras_detalhes %}
                <div class="highlight-box" style="margin-bottom: 20px;">
                    <h4>{{ seg.nome }} - Rating {{ seg.rating }} (Score: {{ "%.1f"|format(seg.score) }})</h4>
                    <div class="two-column" style="margin-top: 15px;">
                        <div>
                            <h5 style="color: var(--success-color);">Pontos Fortes</h5>
                            <ul class="pontos-lista">
                                {% for ponto in seg.pontos_fortes %}
                                <li class="ponto-forte">{{ ponto }}</li>
                                {% endfor %}
                                {% if not seg.pontos_fortes %}
                                <li>Nenhum ponto forte identificado</li>
                                {% endif %}
                            </ul>
                        </div>
                        <div>
                            <h5 style="color: var(--danger-color);">Pontos de Atenção</h5>
                            <ul class="pontos-lista">
                                {% for ponto in seg.pontos_fracos %}
                                <li class="ponto-fraco">{{ ponto }}</li>
                                {% endfor %}
                                {% if not seg.pontos_fracos %}
                                <li>Nenhum ponto de atenção identificado</li>
                                {% endif %}
                            </ul>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <footer>
            <p>Relatório gerado automaticamente pelo Sistema de Análise Financeira de Seguradoras</p>
            <p>© {{ data_geracao[:4] }} - Todos os direitos reservados</p>
        </footer>
    </div>

    <script>
        // Gráfico de Scores
        const ctx = document.getElementById('scoreChart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: {{ chart_data.labels | tojson }},
                datasets: [{
                    label: 'Score de Força Financeira',
                    data: {{ chart_data.scores | tojson }},
                    backgroundColor: {{ chart_data.scores | tojson }}.map(score => {
                        if (score >= 80) return 'rgba(56, 161, 105, 0.8)';
                        if (score >= 60) return 'rgba(66, 153, 225, 0.8)';
                        if (score >= 40) return 'rgba(214, 158, 46, 0.8)';
                        return 'rgba(229, 62, 62, 0.8)';
                    }),
                    borderColor: {{ chart_data.scores | tojson }}.map(score => {
                        if (score >= 80) return 'rgba(56, 161, 105, 1)';
                        if (score >= 60) return 'rgba(66, 153, 225, 1)';
                        if (score >= 40) return 'rgba(214, 158, 46, 1)';
                        return 'rgba(229, 62, 62, 1)';
                    }),
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                return 'Rating: ' + {{ chart_data.ratings | tojson }}[context.dataIndex];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Score de Força Financeira'
                        }
                    }
                }
            }
        });

        // Gráfico de Ratings
        const ratingData = {{ distribuicao_rating | tojson }};
        const ratingLabels = Object.keys(ratingData);
        const ratingValues = Object.values(ratingData);

        new Chart(document.getElementById('ratingChart').getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ratingLabels,
                datasets: [{
                    data: ratingValues,
                    backgroundColor: [
                        '#38a169', '#48bb78', '#4299e1', '#ecc94b',
                        '#ed8936', '#e53e3e', '#c53030', '#9b2c2c', '#742a2a'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });

        // Tabs
        function showTab(tabId) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

            document.querySelector(`[onclick="showTab('${tabId}')"]`).classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        }
    </script>
</body>
</html>'''

    def gerar_relatorio_individual(
        self,
        seguradora: Seguradora,
        nome_arquivo: Optional[str] = None
    ) -> str:
        """
        Gera relatório individual de uma seguradora

        Args:
            seguradora: Seguradora para análise
            nome_arquivo: Nome do arquivo de saída

        Returns:
            Caminho do arquivo gerado
        """
        if nome_arquivo is None:
            nome_arquivo = f"relatorio_{seguradora.nome.replace(' ', '_').lower()}"

        # Calcula indicadores se necessário
        if seguradora.indicadores.score_forca_financeira == 0:
            seguradora.indicadores = self.analisador.calcular_indicadores(seguradora)

        pontos_fortes, pontos_fracos = self.analisador.analisar_pontos_fortes_fracos(
            seguradora.indicadores
        )

        # Gera HTML individual
        html_content = self._gerar_html_individual(seguradora, pontos_fortes, pontos_fracos)

        filepath = self.output_dir / f"{nome_arquivo}.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(filepath)

    def _gerar_html_individual(
        self,
        seguradora: Seguradora,
        pontos_fortes: list,
        pontos_fracos: list
    ) -> str:
        """Gera HTML para relatório individual"""
        ind = seguradora.indicadores
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")

        return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Análise Financeira - {seguradora.nome}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a365d; border-bottom: 2px solid #2b6cb0; padding-bottom: 10px; }}
        .rating {{ font-size: 3rem; font-weight: bold; color: #2b6cb0; }}
        .score {{ font-size: 1.5rem; color: #4a5568; }}
        .section {{ background: #f7fafc; padding: 20px; margin: 20px 0; border-radius: 8px; }}
        .indicator {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e2e8f0; }}
        .indicator-name {{ color: #4a5568; }}
        .indicator-value {{ font-weight: bold; color: #1a365d; }}
        .pontos {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .ponto-forte {{ color: #38a169; }}
        .ponto-fraco {{ color: #e53e3e; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 8px 0; }}
    </style>
</head>
<body>
    <h1>Análise de Força Financeira</h1>
    <h2>{seguradora.nome}</h2>
    <p>Código SUSEP: {seguradora.codigo_susep} | CNPJ: {seguradora.cnpj}</p>
    <p>Data de referência: {seguradora.data_balanco or seguradora.ano_exercicio}</p>

    <div style="text-align: center; padding: 30px;">
        <div class="rating">Rating: {ind.classificacao_risco}</div>
        <div class="score">Score de Força Financeira: {ind.score_forca_financeira:.1f}/100</div>
    </div>

    <div class="section">
        <h3>Indicadores de Solvência</h3>
        <div class="indicator"><span class="indicator-name">Índice de Solvência</span><span class="indicator-value">{ind.indice_solvencia:.2f}</span></div>
        <div class="indicator"><span class="indicator-name">Cobertura de Provisões</span><span class="indicator-value">{ind.cobertura_provisoes:.2f}x</span></div>
        <div class="indicator"><span class="indicator-name">Margem de Solvência</span><span class="indicator-value">R$ {ind.margem_solvencia/1_000_000:,.2f} MM</span></div>
    </div>

    <div class="section">
        <h3>Indicadores de Liquidez</h3>
        <div class="indicator"><span class="indicator-name">Liquidez Corrente</span><span class="indicator-value">{ind.liquidez_corrente:.2f}</span></div>
        <div class="indicator"><span class="indicator-name">Liquidez Seca</span><span class="indicator-value">{ind.liquidez_seca:.2f}</span></div>
        <div class="indicator"><span class="indicator-name">Liquidez Imediata</span><span class="indicator-value">{ind.liquidez_imediata:.2f}</span></div>
    </div>

    <div class="section">
        <h3>Indicadores de Rentabilidade</h3>
        <div class="indicator"><span class="indicator-name">ROE (Retorno sobre PL)</span><span class="indicator-value">{ind.roe:.1%}</span></div>
        <div class="indicator"><span class="indicator-name">ROA (Retorno sobre Ativos)</span><span class="indicator-value">{ind.roa:.1%}</span></div>
        <div class="indicator"><span class="indicator-name">Margem Líquida</span><span class="indicator-value">{ind.margem_liquida:.1%}</span></div>
    </div>

    <div class="section">
        <h3>Indicadores de Sinistralidade</h3>
        <div class="indicator"><span class="indicator-name">Índice de Sinistralidade</span><span class="indicator-value">{ind.indice_sinistralidade:.1%}</span></div>
        <div class="indicator"><span class="indicator-name">Índice de Despesas</span><span class="indicator-value">{ind.indice_despesas:.1%}</span></div>
        <div class="indicator"><span class="indicator-name">Índice Combinado</span><span class="indicator-value">{ind.indice_combinado:.1%}</span></div>
    </div>

    <div class="section">
        <h3>Indicadores de Estrutura</h3>
        <div class="indicator"><span class="indicator-name">Endividamento</span><span class="indicator-value">{ind.endividamento:.1%}</span></div>
        <div class="indicator"><span class="indicator-name">Imobilização do PL</span><span class="indicator-value">{ind.imobilizacao_pl:.1%}</span></div>
        <div class="indicator"><span class="indicator-name">Alavancagem</span><span class="indicator-value">{ind.alavancagem:.2f}x</span></div>
    </div>

    <div class="section">
        <h3>Análise Qualitativa</h3>
        <div class="pontos">
            <div>
                <h4 class="ponto-forte">Pontos Fortes</h4>
                <ul>
                    {"".join(f"<li>{p}</li>" for p in pontos_fortes) if pontos_fortes else "<li>Nenhum identificado</li>"}
                </ul>
            </div>
            <div>
                <h4 class="ponto-fraco">Pontos de Atenção</h4>
                <ul>
                    {"".join(f"<li>{p}</li>" for p in pontos_fracos) if pontos_fracos else "<li>Nenhum identificado</li>"}
                </ul>
            </div>
        </div>
    </div>

    <footer style="text-align: center; color: #718096; padding: 20px;">
        Relatório gerado em {data_geracao}
    </footer>
</body>
</html>'''
