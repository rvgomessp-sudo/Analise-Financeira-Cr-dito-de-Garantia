"""
Analisador de Base CSV - PGFN Marco Zero
Mostra: colunas, tipos, formatos e valores unicos de cada coluna.

Uso:
    python analisar_base.py "caminho_do_arquivo.csv"
    python analisar_base.py  (usa caminho padrao)
"""

import pandas as pd
import sys
import os


def detectar_separador(caminho):
    """Detecta se o CSV usa ; ou , como separador"""
    with open(caminho, 'r', encoding='utf-8', errors='replace') as f:
        primeira_linha = f.readline()
    if primeira_linha.count(';') > primeira_linha.count(','):
        return ';'
    return ','


def formatar_numero(n):
    """Formata numero grande"""
    if n >= 1e9:
        return f"R$ {n/1e9:.2f} bi"
    elif n >= 1e6:
        return f"R$ {n/1e6:.2f} mi"
    elif n >= 1e3:
        return f"R$ {n/1e3:.1f} K"
    else:
        return f"{n:,.2f}"


def analisar_coluna(df, col):
    """Analisa uma coluna em detalhe"""
    serie = df[col]
    total = len(serie)
    nulos = serie.isna().sum()
    preenchidos = total - nulos
    pct_preenchido = (preenchidos / total * 100) if total > 0 else 0

    print(f"\n{'='*80}")
    print(f"  COLUNA: {col}")
    print(f"{'='*80}")
    print(f"  Tipo pandas:    {serie.dtype}")
    print(f"  Total linhas:   {total:,}")
    print(f"  Preenchidos:    {preenchidos:,} ({pct_preenchido:.1f}%)")
    print(f"  Nulos/Vazios:   {nulos:,}")

    # Valores unicos
    unicos = serie.dropna().unique()
    n_unicos = len(unicos)
    print(f"  Valores unicos: {n_unicos:,}")

    # Detectar tipo real
    if serie.dtype == 'object':
        # Tentar detectar se sao numeros formatados
        amostra_str = serie.dropna().head(20).astype(str).tolist()
        tem_ponto = any('.' in s for s in amostra_str)
        tem_virgula = any(',' in s for s in amostra_str)
        comprimentos = serie.dropna().astype(str).str.len()

        print(f"  Comprimento min: {comprimentos.min() if len(comprimentos) > 0 else 'N/A'}")
        print(f"  Comprimento max: {comprimentos.max() if len(comprimentos) > 0 else 'N/A'}")

        if tem_virgula and not tem_ponto:
            print(f"  Obs: Parece usar VIRGULA como decimal")
        elif tem_ponto:
            print(f"  Obs: Usa PONTO (pode ser decimal ou milhar)")

    elif serie.dtype in ['int64', 'float64']:
        print(f"  Min:     {serie.min():,.4f}")
        print(f"  Max:     {serie.max():,.4f}")
        print(f"  Media:   {serie.mean():,.4f}")
        print(f"  Mediana: {serie.median():,.4f}")
        print(f"  Soma:    {formatar_numero(serie.sum())}")

    # Mostrar valores
    print()
    if n_unicos <= 30:
        # Poucos valores - mostrar todos com contagem
        print(f"  TODOS OS VALORES (frequencia):")
        print(f"  {'-'*60}")
        contagem = serie.value_counts(dropna=False).head(30)
        for val, cnt in contagem.items():
            pct = cnt / total * 100
            barra = '#' * int(pct / 2)
            val_str = str(val) if pd.notna(val) else '<VAZIO>'
            print(f"    {val_str:<40} {cnt:>8,}  ({pct:>5.1f}%)  {barra}")
    else:
        # Muitos valores - mostrar top 20
        print(f"  TOP 20 VALORES MAIS FREQUENTES:")
        print(f"  {'-'*60}")
        contagem = serie.value_counts(dropna=False).head(20)
        for val, cnt in contagem.items():
            pct = cnt / total * 100
            val_str = str(val)[:40] if pd.notna(val) else '<VAZIO>'
            print(f"    {val_str:<40} {cnt:>8,}  ({pct:>5.1f}%)")

        # Mostrar amostra dos primeiros 5 e ultimos 5
        print(f"\n  AMOSTRA (5 primeiros):")
        for v in serie.dropna().head(5):
            print(f"    {v}")
        print(f"\n  AMOSTRA (5 ultimos):")
        for v in serie.dropna().tail(5):
            print(f"    {v}")


def main():
    # Caminho do arquivo
    if len(sys.argv) > 1:
        caminho = sys.argv[1]
    else:
        # Caminho padrao
        caminho = r"C:\Rodrigo\BasePGFN\2025\base_brasil_marco_zero_inscricoes_LIMPA.csv"

    if not os.path.exists(caminho):
        print(f"\n  ERRO: Arquivo nao encontrado: {caminho}")
        print(f"  Uso: python analisar_base.py \"caminho_do_arquivo.csv\"")
        return

    print(f"\n{'#'*80}")
    print(f"  ANALISADOR DE BASE CSV - PGFN MARCO ZERO")
    print(f"{'#'*80}")
    print(f"\n  Arquivo: {caminho}")
    print(f"  Tamanho: {os.path.getsize(caminho) / (1024*1024):.1f} MB")

    # Detectar separador
    sep = detectar_separador(caminho)
    print(f"  Separador: '{sep}'")

    # Ler CSV
    print(f"\n  Carregando...")
    df = pd.read_csv(
        caminho,
        sep=sep,
        encoding='utf-8',
        dtype=str,  # Ler tudo como texto primeiro
        on_bad_lines='skip'
    )

    print(f"  Linhas:  {len(df):,}")
    print(f"  Colunas: {len(df.columns)}")

    # Resumo das colunas
    print(f"\n{'='*80}")
    print(f"  RESUMO DAS COLUNAS")
    print(f"{'='*80}")
    print(f"\n  {'#':<4} {'COLUNA':<35} {'NULOS':<10} {'UNICOS':<10} {'AMOSTRA'}")
    print(f"  {'-'*4} {'-'*35} {'-'*10} {'-'*10} {'-'*30}")

    for i, col in enumerate(df.columns):
        nulos = df[col].isna().sum()
        unicos = df[col].nunique()
        amostra = str(df[col].dropna().iloc[0])[:30] if len(df[col].dropna()) > 0 else '<vazio>'
        print(f"  {i+1:<4} {col:<35} {nulos:<10,} {unicos:<10,} {amostra}")

    # Tentar converter colunas numericas
    print(f"\n{'='*80}")
    print(f"  DETECTANDO TIPOS DE DADOS")
    print(f"{'='*80}")

    for col in df.columns:
        amostra = df[col].dropna().head(10).tolist()
        if not amostra:
            print(f"  {col:<35} -> VAZIO")
            continue

        # Tentar converter para numero
        try:
            teste = df[col].str.replace(',', '.', regex=False).str.replace(' ', '', regex=False)
            numerico = pd.to_numeric(teste, errors='coerce')
            pct_numerico = numerico.notna().sum() / df[col].notna().sum() * 100 if df[col].notna().sum() > 0 else 0

            if pct_numerico > 90:
                print(f"  {col:<35} -> NUMERICO ({pct_numerico:.0f}% conversivel)")
                df[col] = numerico  # Converter
                continue
        except:
            pass

        # Tentar detectar data
        try:
            datas = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            pct_data = datas.notna().sum() / df[col].notna().sum() * 100 if df[col].notna().sum() > 0 else 0
            if pct_data > 80:
                print(f"  {col:<35} -> DATA ({pct_data:.0f}% conversivel)")
                continue
        except:
            pass

        # Texto
        n_unicos = df[col].nunique()
        if n_unicos <= 30:
            print(f"  {col:<35} -> CATEGORICO ({n_unicos} valores)")
        else:
            print(f"  {col:<35} -> TEXTO ({n_unicos:,} valores unicos)")

    # Analise detalhada de cada coluna
    print(f"\n\n{'#'*80}")
    print(f"  ANALISE DETALHADA POR COLUNA")
    print(f"{'#'*80}")

    for col in df.columns:
        analisar_coluna(df, col)

    # Resumo final
    print(f"\n\n{'#'*80}")
    print(f"  RESUMO FINAL")
    print(f"{'#'*80}")
    print(f"  Arquivo: {os.path.basename(caminho)}")
    print(f"  Total linhas: {len(df):,}")
    print(f"  Total colunas: {len(df.columns)}")
    print(f"  Colunas: {', '.join(df.columns.tolist())}")
    print()


if __name__ == "__main__":
    main()
