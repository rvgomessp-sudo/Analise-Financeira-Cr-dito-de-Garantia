#!/usr/bin/env python3
"""
Demonstração de Análise de Estrutura Societária - Zurich vs Junto

Este script demonstra a diferenciação robusta entre:
1. SUBSIDIÁRIA DE GRUPO INTERNACIONAL (Zurich Brasil)
2. SEGURADORA NACIONAL INDEPENDENTE (Junto Seguros)

CONCEITOS FUNDAMENTAIS:
======================
- MATRIZ vs FILIAL: Mesma empresa, locais diferentes
- CONTROLADORA vs SUBSIDIÁRIA: Empresas diferentes, mesmo grupo
- RATING PRÓPRIO vs RATING DE GRUPO

IMPORTANTE:
==========
Este módulo analisa APENAS a estrutura societária das SEGURADORAS.
Não se avalia resseguro aqui - isso é feito em módulo separado.
O "grupo" refere-se à estrutura societária, não à composição com resseguro.
"""

import sys
from datetime import date

# Adiciona o diretório raiz ao path
sys.path.insert(0, '/home/user/Analise-Financeira-Cr-dito-de-Garantia')

from src.data.dados_estrutura_societaria import (
    criar_zurich_minas_brasil,
    criar_junto_seguros,
    criar_comparacao_zurich_junto,
    obter_dados_comparativos_brl,
    gerar_relatorio_diferenciacao,
)
from src.analysis.analisador_estrutura_societaria import (
    AnalisadorEstruturaSocietaria,
    analisar_e_comparar,
)


def linha_dupla(tamanho: int = 90) -> str:
    """Linha dupla para separação"""
    return "═" * tamanho


def linha_simples(tamanho: int = 90) -> str:
    """Linha simples para separação"""
    return "─" * tamanho


def titulo(texto: str, tamanho: int = 90) -> str:
    """Formata título centralizado"""
    return f"\n{linha_dupla(tamanho)}\n{texto.center(tamanho)}\n{linha_dupla(tamanho)}\n"


def subtitulo(texto: str, tamanho: int = 90) -> str:
    """Formata subtítulo"""
    return f"\n{linha_simples(tamanho)}\n{texto}\n{linha_simples(tamanho)}\n"


def formatar_moeda(valor: float, prefixo: str = "R$ ") -> str:
    """Formata valor como moeda BRL"""
    if valor >= 1_000_000_000:
        return f"{prefixo}{valor/1e9:,.2f} bilhões"
    elif valor >= 1_000_000:
        return f"{prefixo}{valor/1e6:,.2f} milhões"
    else:
        return f"{prefixo}{valor:,.2f}"


def demonstrar_conceitos():
    """Demonstra os conceitos fundamentais de estrutura societária"""

    print(titulo("DEMONSTRAÇÃO DE ESTRUTURA SOCIETÁRIA"))

    print("""
    Este script demonstra como diferenciar claramente:

    1. SUBSIDIÁRIA DE GRUPO INTERNACIONAL
       → Zurich Brasil é subsidiária do Zurich Insurance Group (Suíça)
       → Rating AA vem do GRUPO, não da força isolada

    2. SEGURADORA NACIONAL INDEPENDENTE
       → Junto Seguros é matriz nacional com sede no PR
       → Rating brAAA é PRÓPRIO (força isolada)
       → Tem FILIAIS em SP, RJ, MG (mesmo CNPJ raiz)

    IMPORTANTE:
    ──────────
    • Não se avalia resseguro aqui
    • O "grupo" é a estrutura SOCIETÁRIA da seguradora
    • A análise de resseguro é feita em módulo separado
    """)


def demonstrar_zurich():
    """Demonstra a estrutura da Zurich Brasil"""

    print(subtitulo("ZURICH MINAS BRASIL SEGUROS S.A."))

    zurich = criar_zurich_minas_brasil()

    print(f"""
    IDENTIFICAÇÃO:
    ─────────────
    Nome: {zurich.nome_oficial}
    CNPJ: {zurich.cnpj}
    Código SUSEP: {zurich.codigo_susep}
    Sede: {zurich.cidade_matriz}/{zurich.uf_matriz}

    ESTRUTURA SOCIETÁRIA:
    ────────────────────
    Tipo: {zurich.tipo_entidade.value}
    É subsidiária estrangeira: {'SIM' if zurich.eh_subsidiaria_estrangeira else 'NÃO'}
    """)

    if zurich.controladora_internacional:
        ctrl = zurich.controladora_internacional
        print(f"""
    CONTROLADORA INTERNACIONAL:
    ──────────────────────────
    Nome: {ctrl.nome}
    País: {ctrl.pais_sede}
    Rating: {ctrl.rating} ({ctrl.agencia_rating})
    Patrimônio (USD): USD {ctrl.patrimonio_liquido_usd/1e9:,.1f} bilhões
    Patrimônio (BRL): {formatar_moeda(ctrl.patrimonio_liquido_brl)}
    Anos de operação: {ctrl.anos_operacao}
    Países de atuação: {ctrl.paises_atuacao}
    Garantia explícita: {'SIM' if ctrl.garantia_explicita else 'NÃO'}
    """)

    print(f"""
    RATING:
    ──────
    Rating Declarado: {zurich.rating_declarado}
    Tipo do Rating: {zurich.tipo_rating.value}
    Rating Isolado (calculado): {zurich.rating_calculado}
    Gap: {zurich.gap_rating} notches
    Rating Inflado: {'SIM - Rating beneficiado pelo grupo' if zurich.rating_inflado else 'NÃO'}

    INDICADORES FINANCEIROS (BRL):
    ─────────────────────────────
    Patrimônio Líquido: {formatar_moeda(zurich.indicadores.patrimonio_liquido)}
    Ativo Total: {formatar_moeda(zurich.indicadores.ativo_total)}
    Prêmios Emitidos: {formatar_moeda(zurich.indicadores.premios_emitidos)}
    Lucro Líquido: {formatar_moeda(zurich.indicadores.lucro_liquido)}
    ROE: {zurich.indicadores.roe:.1f}%
    Índice de Sinistralidade: {zurich.indicadores.indice_sinistralidade:.1f}%
    Liquidez Corrente: {zurich.indicadores.liquidez_corrente:.2f}

    SEGURANÇA DA APÓLICE:
    ────────────────────
    Nota: {zurich.nota_seguranca_apolice}

    ✅ PONTOS FORTES:
    """)
    for fator in zurich.fatores_positivos[:5]:
        print(f"       • {fator}")

    if zurich.fatores_atencao:
        print("\n    ⚠️ PONTOS DE ATENÇÃO:")
        for fator in zurich.fatores_atencao[:3]:
            print(f"       • {fator}")


def demonstrar_junto():
    """Demonstra a estrutura da Junto Seguros"""

    print(subtitulo("JUNTO SEGUROS S.A."))

    junto = criar_junto_seguros()

    print(f"""
    IDENTIFICAÇÃO:
    ─────────────
    Nome: {junto.nome_oficial}
    CNPJ: {junto.cnpj}
    Código SUSEP: {junto.codigo_susep}
    Sede (MATRIZ): {junto.cidade_matriz}/{junto.uf_matriz}

    ESTRUTURA SOCIETÁRIA:
    ────────────────────
    Tipo: {junto.tipo_entidade.value}
    É subsidiária estrangeira: {'SIM' if junto.eh_subsidiaria_estrangeira else 'NÃO'}
    É matriz nacional: SIM
    Controladora internacional: Não possui

    FILIAIS (mesmo CNPJ raiz):
    ─────────────────────────
    """)

    for filial in junto.filiais:
        print(f"    • {filial.nome_filial}")
        print(f"      CNPJ: {filial.cnpj_filial}")
        print(f"      Local: {filial.cidade}/{filial.uf}")
        print(f"      Prêmios: {formatar_moeda(filial.premios_emitidos_brl)}")
        print(f"      Participação: {filial.participacao_total:.0f}% do total")
        print()

    print(f"""
    RATING:
    ──────
    Rating Declarado: {junto.rating_declarado}
    Tipo do Rating: {junto.tipo_rating.value}
    Rating Isolado (calculado): {junto.rating_calculado}
    Gap: {junto.gap_rating} notches
    Rating Inflado: {'SIM' if junto.rating_inflado else 'NÃO - Rating é próprio'}

    INDICADORES FINANCEIROS (BRL):
    ─────────────────────────────
    Patrimônio Líquido: {formatar_moeda(junto.indicadores.patrimonio_liquido)}
    Ativo Total: {formatar_moeda(junto.indicadores.ativo_total)}
    Prêmios Emitidos: {formatar_moeda(junto.indicadores.premios_emitidos)}
    Lucro Líquido: {formatar_moeda(junto.indicadores.lucro_liquido)}
    ROE: {junto.indicadores.roe:.1f}%
    Índice de Sinistralidade: {junto.indicadores.indice_sinistralidade:.1f}%
    Liquidez Corrente: {junto.indicadores.liquidez_corrente:.2f}

    SEGURANÇA DA APÓLICE:
    ────────────────────
    Nota: {junto.nota_seguranca_apolice}

    ✅ PONTOS FORTES:
    """)
    for fator in junto.fatores_positivos[:5]:
        print(f"       • {fator}")

    if junto.fatores_atencao:
        print("\n    ⚠️ PONTOS DE ATENÇÃO:")
        for fator in junto.fatores_atencao[:3]:
            print(f"       • {fator}")


def demonstrar_comparacao():
    """Demonstra a comparação entre as duas seguradoras"""

    print(titulo("ANÁLISE COMPARATIVA"))

    zurich = criar_zurich_minas_brasil()
    junto = criar_junto_seguros()

    # Usa o analisador estrutural
    analisador = AnalisadorEstruturaSocietaria()
    comparacao, relatorio = analisar_e_comparar([zurich, junto])

    # Imprime o relatório gerado pelo analisador
    print(relatorio)


def demonstrar_tabela_comparativa():
    """Demonstra a tabela comparativa lado a lado"""

    print(titulo("TABELA COMPARATIVA - ZURICH vs JUNTO"))

    zurich = criar_zurich_minas_brasil()
    junto = criar_junto_seguros()

    print("""
┌────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│ CARACTERÍSTICA             │ ZURICH MINAS BRASIL             │ JUNTO SEGUROS                   │
├────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤""")

    print(f"│ {'Tipo de Entidade':<26} │ {'Subsidiária Internacional':<31} │ {'Matriz Nacional':<31} │")
    print(f"│ {'CNPJ':<26} │ {zurich.cnpj:<31} │ {junto.cnpj:<31} │")
    print(f"│ {'Sede':<26} │ {zurich.cidade_matriz + '/' + zurich.uf_matriz:<31} │ {junto.cidade_matriz + '/' + junto.uf_matriz:<31} │")
    print(f"│ {'Controladora':<26} │ {'Zurich Insurance Group':<31} │ {'Não possui':<31} │")
    print(f"│ {'Filiais':<26} │ {'Não possui':<31} │ {'SP, RJ, MG (3 filiais)':<31} │")

    print("├────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤")

    print(f"│ {'Rating Declarado':<26} │ {zurich.rating_declarado:<31} │ {junto.rating_declarado:<31} │")
    print(f"│ {'Origem do Rating':<26} │ {'Grupo (emprestado)':<31} │ {'Próprio (força isolada)':<31} │")
    print(f"│ {'Rating se Isolada':<26} │ {zurich.rating_calculado:<31} │ {junto.rating_calculado:<31} │")
    gap_z = f"{zurich.gap_rating:+d} notches" if zurich.gap_rating else "0"
    gap_j = f"{junto.gap_rating:+d} notches" if junto.gap_rating else "0"
    print(f"│ {'Gap de Rating':<26} │ {gap_z:<31} │ {gap_j:<31} │")
    print(f"│ {'Rating Inflado?':<26} │ {'SIM':<31} │ {'NÃO':<31} │")

    print("├────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤")

    pl_z = f"R$ {zurich.indicadores.patrimonio_liquido/1e6:,.0f} milhões"
    pl_j = f"R$ {junto.indicadores.patrimonio_liquido/1e6:,.0f} milhões"
    print(f"│ {'Patrimônio Líquido':<26} │ {pl_z:<31} │ {pl_j:<31} │")

    at_z = f"R$ {zurich.indicadores.ativo_total/1e6:,.0f} milhões"
    at_j = f"R$ {junto.indicadores.ativo_total/1e6:,.0f} milhões"
    print(f"│ {'Ativo Total':<26} │ {at_z:<31} │ {at_j:<31} │")

    pr_z = f"R$ {zurich.indicadores.premios_emitidos/1e6:,.0f} milhões"
    pr_j = f"R$ {junto.indicadores.premios_emitidos/1e6:,.0f} milhões"
    print(f"│ {'Prêmios Emitidos':<26} │ {pr_z:<31} │ {pr_j:<31} │")

    ll_z = f"R$ {zurich.indicadores.lucro_liquido/1e6:,.0f} milhões"
    ll_j = f"R$ {junto.indicadores.lucro_liquido/1e6:,.0f} milhões"
    print(f"│ {'Lucro Líquido':<26} │ {ll_z:<31} │ {ll_j:<31} │")

    roe_z = f"{zurich.indicadores.roe:.1f}%"
    roe_j = f"{junto.indicadores.roe:.1f}%"
    print(f"│ {'ROE':<26} │ {roe_z:<31} │ {roe_j:<31} │")

    print("├────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤")

    if zurich.controladora_internacional:
        suporte_z = f"R$ {zurich.controladora_internacional.patrimonio_liquido_brl/1e9:,.0f} bi (PL grupo)"
    else:
        suporte_z = "Nenhum"
    print(f"│ {'Suporte de Grupo':<26} │ {suporte_z:<31} │ {'Nenhum':<31} │")
    print(f"│ {'Nota Segurança':<26} │ {zurich.nota_seguranca_apolice:<31} │ {junto.nota_seguranca_apolice:<31} │")

    print("└────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘")


def demonstrar_seguranca_apolice():
    """Demonstra a análise de segurança da apólice"""

    print(titulo("SEGURANÇA DA APÓLICE - RATING7"))

    print("""
    ╔═══════════════════════════════════════════════════════════════════════════════════════╗
    ║                        ANÁLISE DE SEGURANÇA DA APÓLICE                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════════════╝

    O "toque do Rating7" representa a análise integrada que considera:

    1. RATING DECLARADO
       → Classificação de risco emitida por agência (S&P, Fitch, AM Best)
       → Pode ser PRÓPRIO ou do GRUPO

    2. ORIGEM DO RATING
       → Rating Próprio: baseado na força financeira isolada
       → Rating de Grupo: "emprestado" da controladora

    3. INDICADORES FINANCEIROS
       → Patrimônio Líquido
       → Liquidez
       → Rentabilidade
       → Sinistralidade

    4. ESTRUTURA SOCIETÁRIA
       → Subsidiária com suporte de grupo internacional
       → Matriz nacional com força própria

    ─────────────────────────────────────────────────────────────────────────────────────────
    """)

    zurich = criar_zurich_minas_brasil()
    junto = criar_junto_seguros()

    print(f"""
    ► ZURICH MINAS BRASIL SEGUROS
      ──────────────────────────
      Rating Declarado: {zurich.rating_declarado}
      Tipo: Rating de GRUPO (emprestado)

      A segurança da apólice DEPENDE INDIRETAMENTE do grupo:
      • Se o Zurich Insurance Group mantiver suporte → AA garantido
      • Força isolada da entidade brasileira seria → {zurich.rating_calculado}

      ✅ Suporte do grupo: {formatar_moeda(zurich.controladora_internacional.patrimonio_liquido_brl)} (PL)
      ✅ 152 anos de operação global
      ✅ Presença em 210 países

      PARECER: {zurich.parecer_seguranca[:100]}...


    ► JUNTO SEGUROS
      ──────────────
      Rating Declarado: {junto.rating_declarado}
      Tipo: Rating PRÓPRIO (força isolada)

      A segurança da apólice DEPENDE DA FORÇA PRÓPRIA:
      • Rating brAAA = máxima classificação nacional
      • Não há dependência de suporte externo

      ✅ 33 anos de experiência
      ✅ Líder em Seguro Garantia (16% market share)
      ✅ 99% das apólices digitais

      PARECER: {junto.parecer_seguranca[:100]}...
    """)

    print("""
    ─────────────────────────────────────────────────────────────────────────────────────────

    CONCLUSÃO - RATING7:
    ═══════════════════

    ╔═════════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                     ║
    ║   AMBAS AS SEGURADORAS SÃO SEGURAS PARA EMISSÃO DE APÓLICES DE GARANTIA            ║
    ║                                                                                     ║
    ║   A diferença está na ORIGEM da segurança:                                          ║
    ║                                                                                     ║
    ║   • ZURICH: Segurança vem do SUPORTE DO GRUPO INTERNACIONAL                        ║
    ║     → Rating AA = força do Zurich Insurance Group (Suíça)                          ║
    ║     → Patrimônio do grupo: R$ 231 bilhões                                          ║
    ║                                                                                     ║
    ║   • JUNTO: Segurança vem da FORÇA FINANCEIRA PRÓPRIA                               ║
    ║     → Rating brAAA = máximo em escala nacional brasileira                          ║
    ║     → Não depende de suporte externo                                               ║
    ║                                                                                     ║
    ╚═════════════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    """Função principal de demonstração"""

    print("\n" * 2)
    print("═" * 90)
    print("    SISTEMA DE ANÁLISE FINANCEIRA - ESTRUTURA SOCIETÁRIA DE SEGURADORAS")
    print("═" * 90)
    print(f"    Data: {date.today().strftime('%d/%m/%Y')}")
    print("    Versão: 1.0")
    print("═" * 90)

    # Menu
    print("""

    DEMONSTRAÇÕES DISPONÍVEIS:
    ─────────────────────────

    1. Conceitos Fundamentais (Matriz/Filial/Subsidiária)
    2. Análise Zurich Brasil (Subsidiária Internacional)
    3. Análise Junto Seguros (Matriz Nacional)
    4. Tabela Comparativa
    5. Análise Comparativa Detalhada
    6. Segurança da Apólice - Rating7
    7. Executar Todas as Demonstrações

    """)

    # Para demonstração, executa todas
    print("\n>>> Executando demonstração completa...\n")

    demonstrar_conceitos()
    input("\n[Pressione ENTER para continuar...]\n")

    demonstrar_zurich()
    input("\n[Pressione ENTER para continuar...]\n")

    demonstrar_junto()
    input("\n[Pressione ENTER para continuar...]\n")

    demonstrar_tabela_comparativa()
    input("\n[Pressione ENTER para continuar...]\n")

    demonstrar_comparacao()
    input("\n[Pressione ENTER para continuar...]\n")

    demonstrar_seguranca_apolice()

    print("\n" + "═" * 90)
    print("    DEMONSTRAÇÃO CONCLUÍDA")
    print("═" * 90 + "\n")


def executar_rapido():
    """Execução rápida sem pausas para input"""

    print(titulo("ANÁLISE DE ESTRUTURA SOCIETÁRIA - EXECUÇÃO RÁPIDA"))

    # Relatório de diferenciação
    print(gerar_relatorio_diferenciacao())

    # Tabela comparativa
    print("\n")
    comparacao = criar_comparacao_zurich_junto()
    print(comparacao.gerar_tabela_comparativa())


if __name__ == "__main__":
    # Verifica argumentos
    if len(sys.argv) > 1 and sys.argv[1] == "--rapido":
        executar_rapido()
    else:
        # Tenta executar interativo, se falhar executa rápido
        try:
            main()
        except EOFError:
            # Não tem input disponível, executa versão rápida
            executar_rapido()
