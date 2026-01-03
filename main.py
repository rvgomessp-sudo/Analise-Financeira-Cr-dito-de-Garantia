#!/usr/bin/env python3
"""
Sistema de Análise Financeira Comparativa de Seguradoras
Gera relatórios comparativos de força financeira entre seguradoras

Uso:
    python main.py                    # Gera relatório com dados de exemplo
    python main.py --output pasta     # Define pasta de saída
    python main.py --formato html     # Define formato (html, excel, pdf, all)
    python main.py --resumo           # Exibe apenas resumo no terminal
"""

import argparse
import sys
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.dados_exemplo import carregar_dados_exemplo
from src.data.dados_reais import carregar_dados_reais, get_ratings_info, get_financial_highlights
from src.analysis.indicadores import AnalisadorIndicadores
from src.analysis.comparador import ComparadorSeguradora
from src.reports.gerador_relatorios import GeradorRelatorios


def main():
    """Função principal do sistema"""
    parser = argparse.ArgumentParser(
        description="Sistema de Análise Financeira Comparativa de Seguradoras"
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Pasta de saída para os relatórios (default: output)"
    )
    parser.add_argument(
        "--formato", "-f",
        choices=["html", "excel", "pdf", "all"],
        default="all",
        help="Formato do relatório (default: all)"
    )
    parser.add_argument(
        "--resumo", "-r",
        action="store_true",
        help="Exibe apenas o resumo executivo no terminal"
    )
    parser.add_argument(
        "--individual", "-i",
        action="store_true",
        help="Gera relatórios individuais para cada seguradora"
    )
    parser.add_argument(
        "--dados-reais", "-d",
        action="store_true",
        help="Usa dados reais de seguradoras (Junto Seguros, Zurich, etc.)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("  SISTEMA DE ANÁLISE FINANCEIRA COMPARATIVA DE SEGURADORAS")
    print("  Análise de Força Financeira e Crédito de Garantia")
    print("=" * 80)
    print()

    # Carrega dados
    print("📊 Carregando dados de seguradoras...")
    if args.dados_reais:
        seguradoras = carregar_dados_reais()
        print(f"   ✓ {len(seguradoras)} seguradoras com dados REAIS carregadas")
        # Exibe informações de ratings
        ratings = get_ratings_info()
        for nome, info in ratings.items():
            print(f"   📋 {nome}:")
            for key, value in info.items():
                if key != "awards":
                    print(f"      • {key}: {value}")
    else:
        seguradoras = carregar_dados_exemplo()
        print(f"   ✓ {len(seguradoras)} seguradoras (dados de exemplo) carregadas")
    print()

    # Inicializa analisador e calcula indicadores
    print("🔍 Calculando indicadores financeiros...")
    analisador = AnalisadorIndicadores()
    for seg in seguradoras:
        seg.indicadores = analisador.calcular_indicadores(seg)
        print(f"   ✓ {seg.nome}: Score {seg.indicadores.score_forca_financeira:.1f} "
              f"(Rating {seg.indicadores.classificacao_risco})")
    print()

    # Inicializa comparador
    comparador = ComparadorSeguradora()
    comparador.adicionar_multiplas(seguradoras)

    # Exibe resumo executivo
    if args.resumo:
        print(comparador.gerar_resumo_executivo())
        return

    # Realiza comparação
    print("📈 Realizando análise comparativa...")
    resultado = comparador.comparar()

    # Exibe resumo no terminal
    print()
    print(comparador.gerar_resumo_executivo())

    # Gera relatórios
    print("📄 Gerando relatórios...")
    gerador = GeradorRelatorios(output_dir=args.output)
    gerador.carregar_seguradoras(seguradoras)

    # Define formatos
    if args.formato == "all":
        formatos = ["html", "excel"]
    else:
        formatos = [args.formato]

    # Gera relatório comparativo
    nome_base = "relatorio_comparativo_dados_reais" if args.dados_reais else "relatorio_comparativo_seguradoras"
    arquivos = gerador.gerar_relatorio_completo(
        nome_arquivo=nome_base,
        formatos=formatos
    )

    print()
    print("✅ Relatórios gerados com sucesso!")
    for formato, caminho in arquivos.items():
        print(f"   📁 {formato.upper()}: {caminho}")

    # Gera relatórios individuais se solicitado
    if args.individual:
        print()
        print("📋 Gerando relatórios individuais...")
        for seg in seguradoras:
            caminho = gerador.gerar_relatorio_individual(seg)
            print(f"   ✓ {seg.nome}: {caminho}")

    print()
    print("=" * 80)
    print("  Análise concluída com sucesso!")
    print("=" * 80)


def exemplo_uso_api():
    """
    Exemplo de uso programático da API do sistema

    Este exemplo demonstra como usar o sistema em código Python
    """
    from src.models.seguradora import Seguradora, BalancoPatrimonial, DRE
    from datetime import date

    # Cria uma seguradora manualmente
    minha_seguradora = Seguradora(
        codigo_susep="12345",
        nome="Minha Seguradora S.A.",
        cnpj="11.222.333/0001-44",
        grupo_economico="Meu Grupo",
        ano_exercicio=2024,
        data_balanco=date(2024, 12, 31),
        capital_minimo_requerido=50_000_000,
        patrimonio_liquido_ajustado=200_000_000,
        balanco=BalancoPatrimonial(
            disponibilidades=30_000_000,
            aplicacoes_financeiras_cp=150_000_000,
            premios_a_receber=40_000_000,
            creditos_operacionais=20_000_000,
            outros_creditos_cp=10_000_000,
            aplicacoes_financeiras_lp=100_000_000,
            investimentos=30_000_000,
            imobilizado=15_000_000,
            intangivel=5_000_000,
            outros_ativos_lp=3_000_000,
            provisoes_tecnicas_cp=120_000_000,
            debitos_operacionais=25_000_000,
            depositos_terceiros=15_000_000,
            emprestimos_cp=10_000_000,
            outras_obrigacoes_cp=20_000_000,
            provisoes_tecnicas_lp=70_000_000,
            emprestimos_lp=20_000_000,
            outras_obrigacoes_lp=10_000_000,
            capital_social=100_000_000,
            reservas_capital=20_000_000,
            reservas_lucros=60_000_000,
            ajustes_avaliacao=5_000_000,
            lucros_acumulados=15_000_000,
        ),
        dre=DRE(
            premios_emitidos=200_000_000,
            premios_cedidos_resseguro=30_000_000,
            variacoes_provisoes_tecnicas=-8_000_000,
            premios_ganhos=162_000_000,
            sinistros_ocorridos=-81_000_000,
            custos_aquisicao=-32_400_000,
            outras_despesas_operacionais=-12_960_000,
            receitas_financeiras=25_000_000,
            despesas_financeiras=-4_000_000,
            despesas_administrativas=-28_000_000,
            despesas_tributarias=-6_000_000,
            resultado_operacional=22_640_000,
            resultado_nao_operacional=1_000_000,
            irpj_csll=-8_000_000,
        )
    )

    # Calcula indicadores
    analisador = AnalisadorIndicadores()
    indicadores = analisador.calcular_indicadores(minha_seguradora)
    minha_seguradora.indicadores = indicadores

    # Exibe resultados
    print(f"Seguradora: {minha_seguradora.nome}")
    print(f"Score de Força Financeira: {indicadores.score_forca_financeira:.1f}")
    print(f"Rating: {indicadores.classificacao_risco}")
    print(f"Índice de Solvência: {indicadores.indice_solvencia:.2f}")
    print(f"Liquidez Corrente: {indicadores.liquidez_corrente:.2f}")
    print(f"ROE: {indicadores.roe:.1%}")
    print(f"Sinistralidade: {indicadores.indice_sinistralidade:.1%}")
    print(f"Índice Combinado: {indicadores.indice_combinado:.1%}")

    # Análise de pontos fortes e fracos
    pontos_fortes, pontos_fracos = analisador.analisar_pontos_fortes_fracos(indicadores)

    print("\nPontos Fortes:")
    for ponto in pontos_fortes:
        print(f"  ✓ {ponto}")

    print("\nPontos de Atenção:")
    for ponto in pontos_fracos:
        print(f"  ✗ {ponto}")

    return minha_seguradora


def exemplo_comparacao():
    """
    Exemplo de comparação entre seguradoras
    """
    # Carrega dados de exemplo
    seguradoras = carregar_dados_exemplo()

    # Calcula indicadores
    analisador = AnalisadorIndicadores()
    for seg in seguradoras:
        seg.indicadores = analisador.calcular_indicadores(seg)

    # Cria comparador
    comparador = ComparadorSeguradora()
    comparador.adicionar_multiplas(seguradoras)

    # Realiza comparação
    resultado = comparador.comparar()

    # Exibe ranking geral
    print("\n=== RANKING GERAL DE FORÇA FINANCEIRA ===\n")
    print(resultado.ranking_geral.to_string(index=False))

    # Estatísticas do setor
    print("\n=== ESTATÍSTICAS DO SETOR ===")
    stats = resultado.estatisticas_setor
    print(f"Total de Seguradoras: {stats['total_seguradoras']}")
    print(f"Score Médio: {stats['media']['score_forca_financeira']:.1f}")
    print(f"Melhor: {stats['melhor']['seguradora']} ({stats['melhor']['score']:.1f})")
    print(f"Pior: {stats['pior']['seguradora']} ({stats['pior']['score']:.1f})")

    # Comparação entre duas seguradoras específicas
    print("\n=== COMPARAÇÃO DIRETA: Alpha vs Beta ===")
    comp = comparador.comparar_duas_seguradoras(seguradoras[0], seguradoras[1])
    print(f"Vencedor: {comp['vencedor_geral']}")
    print(f"Diferença de Score: {comp['diferenca_score']:.1f} pontos")

    return resultado


if __name__ == "__main__":
    main()
