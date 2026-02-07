"""
Processador de Dados PGFN - Base de Inscrições
Lê a base bruta de inscrições individuais, aplica filtros de negócio
e agrega por CNPJ para prospecção comercial de Seguro Garantia.

Critérios de qualificação:
1. Receita Principal: PIS, COFINS, IRPJ, CSLL, IOF, Imp. Importação, IPI
   (correlação com empresas SA/Ltda de médio e grande porte)
2. Situação: ATIVA AJUIZADA (83.5% da base)
3. Período: 2020-2025 (antes de 2020 = crime fiscal / falência)
4. Classificação por TIPO_GARANTIA:
   - HOT: já tem SEGURO_GARANTIA (cross-sell)
   - WARM: tem CARTA_FIANCA ou DEPOSITO (conversão)
   - COLD: SEM_GARANTIA (prospecção)
   - PENHORA: categoria separada (ativo penhorado)
"""

import pandas as pd
import os
from datetime import datetime


# =============================================================================
# CONSTANTES DE NEGÓCIO
# =============================================================================

# Tributos que correlacionam com PJ médio/grande porte (SA/Ltda)
RECEITAS_PJ_QUALIFICADAS = [
    'Receita da dívida ativa - PIS',
    'Receita da dívida ativa - COFINS',
    'Receita da dívida ativa - IRPJ',
    'Receita da dívida ativa - CSLL',
    'Receita da dívida ativa - IOF',
    'Receita da dívida ativa - Imposto de Importação',
    'IPI - Receita da dívida ativa',
    # Retenções na fonte (PJ que retém = porte maior)
    'Receita da dívida ativa - COFINS - Retenção na fonte',
    'Receita da dívida ativa - PIS - Retenção na fonte',
    'Receita da dívida ativa - CSLL - Retenção na fonte',
]

# Situações ativas ajuizadas (com processo judicial = precisa garantia)
SITUACOES_AJUIZADAS = [
    'ATIVA AJUIZADA',
    'ATIVA AJUIZADA NEGOCIADA NO SISPAR',
    'ATIVA AJUIZADA EM PROCESSO DE NEGOCIACAO NO SISPAR',
    'ATIVA AJUIZADA - GARANTIA - DEPOSITO',
    'ATIVA AJUIZADA - GARANTIA - PENHORA',
    'ATIVA AJUIZADA - GARANTIA - SEGURO GARANTIA',
    'ATIVA AJUIZADA - GARANTIA - CARTA FIANCA',
    'ATIVA AJUIZADA - GARANTIA - NJP',
    'ATIVA AJUIZADA COM EXIGIBILIDADE DO CREDITO SUSPENSA-DECISAO JUDICIAL',
    'ATIVA AJUIZADA NEGOCIADA NO SISPAR - BLOQUEADA',
]

# Período válido (2020-2025)
ANO_MIN_VALIDO = 2020
ANO_MAX_VALIDO = 2025

# Tipos de garantia → classificação
GARANTIAS_HOT = ['SEGURO_GARANTIA']
GARANTIAS_WARM_CONVERSAO = ['CARTA_FIANCA', 'DEPOSITO']
GARANTIAS_WARM_PENHORA = ['PENHORA']
GARANTIA_COLD = ['SEM_GARANTIA']
GARANTIA_NJP = ['NJP']

# Regiões TRF
REGIOES_TRF = {
    '1ª Região (DF/GO/MT/TO/Norte)': ['DF', 'GO', 'MT', 'TO', 'AC', 'AM', 'AP', 'PA', 'RO', 'RR'],
    '2ª Região (RJ/ES)': ['RJ', 'ES'],
    '3ª Região (SP/MS)': ['SP', 'MS'],
    '4ª Região (RS/SC/PR)': ['RS', 'SC', 'PR'],
    '5ª Região (PE/AL/PB/RN/CE/SE)': ['PE', 'AL', 'PB', 'RN', 'CE', 'SE'],
    '6ª Região (MG)': ['MG'],
}


def carregar_base_inscricoes(caminho: str) -> pd.DataFrame:
    """
    Carrega a base bruta de inscrições PGFN.
    Aceita separador ; e encoding utf-8.
    """
    print(f"  Carregando: {os.path.basename(caminho)}")
    print(f"  Tamanho: {os.path.getsize(caminho) / (1024*1024):.1f} MB")

    df = pd.read_csv(
        caminho,
        sep=';',
        encoding='utf-8',
        dtype={
            'CPF_CNPJ': str,
            'NOME_DEVEDOR': str,
            'UF_DEVEDOR': str,
            'REGIAO': str,
            'NUMERO_INSCRICAO': str,
            'RECEITA_PRINCIPAL': str,
            'SITUACAO_INSCRICAO': str,
            'TIPO_GARANTIA': str,
            'DATA_INSCRICAO': str,
            'ANO_INSCRICAO': str,
        },
        on_bad_lines='skip',
    )

    # Converter valor para float
    df['VALOR_CONSOLIDADO'] = pd.to_numeric(
        df['VALOR_CONSOLIDADO'].astype(str).str.replace(',', '.'),
        errors='coerce'
    ).fillna(0)

    # Converter ano para int
    df['ANO_INSCRICAO'] = pd.to_numeric(df['ANO_INSCRICAO'], errors='coerce').fillna(0).astype(int)

    print(f"  Total carregado: {len(df):,} inscrições")
    return df


def aplicar_filtros_negocio(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica os filtros de qualificação de negócio:
    1. Apenas receitas PJ qualificadas
    2. Apenas situações ativas ajuizadas
    3. Apenas período 2020-2025
    """
    total_original = len(df)
    print(f"\n  Aplicando filtros de negócio...")

    # Filtro 1: Receitas PJ qualificadas
    df_filtrado = df[df['RECEITA_PRINCIPAL'].isin(RECEITAS_PJ_QUALIFICADAS)].copy()
    print(f"    Receitas PJ qualificadas: {len(df_filtrado):,} ({len(df_filtrado)/total_original*100:.1f}%)")

    # Filtro 2: Situações ativas ajuizadas
    df_filtrado = df_filtrado[df_filtrado['SITUACAO_INSCRICAO'].isin(SITUACOES_AJUIZADAS)]
    print(f"    + Ativas ajuizadas: {len(df_filtrado):,} ({len(df_filtrado)/total_original*100:.1f}%)")

    # Filtro 3: Período 2020-2025
    df_filtrado = df_filtrado[
        (df_filtrado['ANO_INSCRICAO'] >= ANO_MIN_VALIDO) &
        (df_filtrado['ANO_INSCRICAO'] <= ANO_MAX_VALIDO)
    ]
    print(f"    + Período 2020-2025: {len(df_filtrado):,} ({len(df_filtrado)/total_original*100:.1f}%)")

    cnpjs = df_filtrado['CPF_CNPJ'].nunique()
    print(f"    Empresas qualificadas: {cnpjs:,}")

    return df_filtrado


def agregar_por_cnpj(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega inscrições individuais por CNPJ.
    Gera uma linha por empresa com métricas consolidadas.
    """
    print(f"\n  Agregando por CNPJ...")

    agg = df.groupby('CPF_CNPJ').agg(
        NOME_DEVEDOR=('NOME_DEVEDOR', 'first'),
        UF_DEVEDOR=('UF_DEVEDOR', 'first'),
        REGIAO=('REGIAO', 'first'),

        # Quantidades
        QTD_INSCRICOES=('NUMERO_INSCRICAO', 'nunique'),
        DIVIDA_TOTAL=('VALOR_CONSOLIDADO', 'sum'),
        VALOR_MIN=('VALOR_CONSOLIDADO', 'min'),
        VALOR_MAX=('VALOR_CONSOLIDADO', 'max'),
        TICKET_MEDIO=('VALOR_CONSOLIDADO', 'mean'),

        # Período
        ANO_MIN=('ANO_INSCRICAO', 'min'),
        ANO_MAX=('ANO_INSCRICAO', 'max'),

        # Garantias (contar inscrições por tipo)
        QTD_SEGURO_GARANTIA=('TIPO_GARANTIA', lambda x: (x == 'SEGURO_GARANTIA').sum()),
        QTD_CARTA_FIANCA=('TIPO_GARANTIA', lambda x: (x == 'CARTA_FIANCA').sum()),
        QTD_DEPOSITO=('TIPO_GARANTIA', lambda x: (x == 'DEPOSITO').sum()),
        QTD_PENHORA=('TIPO_GARANTIA', lambda x: (x == 'PENHORA').sum()),
        QTD_SEM_GARANTIA=('TIPO_GARANTIA', lambda x: (x == 'SEM_GARANTIA').sum()),
        QTD_NJP=('TIPO_GARANTIA', lambda x: (x == 'NJP').sum()),

        # Receitas (contar por tipo para perfil tributário)
        QTD_IRPJ=('RECEITA_PRINCIPAL', lambda x: x.str.contains('IRPJ', case=False).sum()),
        QTD_CSLL=('RECEITA_PRINCIPAL', lambda x: x.str.contains('CSLL', case=False).sum()),
        QTD_COFINS=('RECEITA_PRINCIPAL', lambda x: x.str.contains('COFINS', case=False).sum()),
        QTD_PIS=('RECEITA_PRINCIPAL', lambda x: x.str.contains('PIS', case=False).sum()),
        QTD_IPI=('RECEITA_PRINCIPAL', lambda x: x.str.contains('IPI', case=False).sum()),

        # Situações
        QTD_AJUIZADA=('SITUACAO_INSCRICAO', lambda x: (x == 'ATIVA AJUIZADA').sum()),
        QTD_NEGOCIADA_SISPAR=('SITUACAO_INSCRICAO', lambda x: x.str.contains('SISPAR', case=False).sum()),
        QTD_SUSPENSA=('SITUACAO_INSCRICAO', lambda x: x.str.contains('SUSPENSA', case=False).sum()),

        # Datas
        DATA_INSCRICAO_MIN=('DATA_INSCRICAO', 'min'),
        DATA_INSCRICAO_MAX=('DATA_INSCRICAO', 'max'),
    ).reset_index()

    # Calcular valores derivados
    agg['VALOR_GARANTIDO_SG'] = 0.0  # Será calculado por join se disponível
    agg['VALOR_GARANTIA_INEFICIENTE'] = 0.0
    agg['VALOR_DESCOBERTO'] = 0.0

    # Estimar valores por tipo de garantia
    for idx, row in agg.iterrows():
        total_insc = row['QTD_INSCRICOES']
        if total_insc > 0:
            ticket = row['TICKET_MEDIO']
            agg.at[idx, 'VALOR_GARANTIDO_SG'] = row['QTD_SEGURO_GARANTIA'] * ticket
            agg.at[idx, 'VALOR_GARANTIA_INEFICIENTE'] = (
                row['QTD_CARTA_FIANCA'] + row['QTD_DEPOSITO']
            ) * ticket
            agg.at[idx, 'VALOR_DESCOBERTO'] = row['QTD_SEM_GARANTIA'] * ticket

    # Potencial SG = descoberto + garantias ineficientes
    agg['POTENCIAL_SG'] = agg['VALOR_DESCOBERTO'] + agg['VALOR_GARANTIA_INEFICIENTE']

    print(f"  Empresas agregadas: {len(agg):,}")
    return agg


def classificar_temperatura(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifica cada empresa por temperatura de lead:
    HOT:  Já usa Seguro Garantia + tem valor descoberto
    WARM: Usa garantias ineficientes (carta fiança / depósito)
    COLD: Sem nenhuma garantia (100% descoberto)
    """
    print(f"\n  Classificando temperatura dos leads...")

    def _classificar(row):
        if row['QTD_SEGURO_GARANTIA'] > 0:
            return 'HOT'
        elif row['QTD_CARTA_FIANCA'] > 0 or row['QTD_DEPOSITO'] > 0:
            return 'WARM'
        else:
            return 'COLD'

    df['TEMPERATURA'] = df.apply(_classificar, axis=1)

    # Sub-classificação WARM
    def _sub_warm(row):
        if row['TEMPERATURA'] != 'WARM':
            return ''
        partes = []
        if row['QTD_CARTA_FIANCA'] > 0:
            partes.append('CARTA_FIANCA')
        if row['QTD_DEPOSITO'] > 0:
            partes.append('DEPOSITO')
        if row['QTD_PENHORA'] > 0:
            partes.append('PENHORA')
        return '+'.join(partes)

    df['SUB_TIPO_WARM'] = df.apply(_sub_warm, axis=1)

    # Flag penhora (categoria separada)
    df['TEM_PENHORA'] = df['QTD_PENHORA'] > 0

    # Estimar porte
    def _estimar_porte(row):
        divida = row['DIVIDA_TOTAL']
        ticket = row['TICKET_MEDIO']
        if divida > 100_000_000 or ticket > 10_000_000:
            return 'GRANDE'
        elif divida > 10_000_000 or ticket > 1_000_000:
            return 'MEDIO'
        elif divida > 1_000_000 or ticket > 100_000:
            return 'PEQUENO'
        else:
            return 'MICRO'

    df['PORTE_ESTIMADO'] = df.apply(_estimar_porte, axis=1)

    # Resumo
    for temp in ['HOT', 'WARM', 'COLD']:
        subset = df[df['TEMPERATURA'] == temp]
        print(f"    {temp}: {len(subset):,} empresas | R$ {subset['POTENCIAL_SG'].sum()/1e9:.2f} bi potencial")

    return df


def gerar_score_prospeccao(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera score de priorização para prospecção.
    Fatores: potencial financeiro, recorrência, tipo garantia, porte.
    """
    print(f"\n  Calculando score de prospecção...")

    def _score(row):
        score = 0

        # Fator 1: Potencial SG (40%)
        pot = row['POTENCIAL_SG']
        if pot > 100_000_000:
            score += 40
        elif pot > 50_000_000:
            score += 35
        elif pot > 10_000_000:
            score += 30
        elif pot > 5_000_000:
            score += 25
        elif pot > 1_000_000:
            score += 20
        elif pot > 500_000:
            score += 10
        else:
            score += 5

        # Fator 2: Recorrência / Volume inscrições (20%)
        qtd = row['QTD_INSCRICOES']
        if qtd >= 50:
            score += 20
        elif qtd >= 20:
            score += 16
        elif qtd >= 10:
            score += 12
        elif qtd >= 5:
            score += 8
        else:
            score += 4

        # Fator 3: Tipo garantia existente (25%)
        if row['QTD_SEGURO_GARANTIA'] > 0:
            score += 25  # Já usa SG = mais receptivo
        elif row['QTD_CARTA_FIANCA'] > 0:
            score += 20  # Carta fiança = conhece garantia judicial
        elif row['QTD_DEPOSITO'] > 0:
            score += 18  # Depósito = tem dinheiro preso
        elif row['QTD_PENHORA'] > 0:
            score += 12  # Penhora = precisa liberar ativo
        else:
            score += 5   # Sem garantia = precisa educar

        # Fator 4: Porte estimado (15%)
        porte = row['PORTE_ESTIMADO']
        if porte == 'GRANDE':
            score += 15
        elif porte == 'MEDIO':
            score += 12
        elif porte == 'PEQUENO':
            score += 6
        else:
            score += 2

        return min(score, 100)

    df['SCORE_PROSPECCAO'] = df.apply(_score, axis=1)

    # Semáforo
    df['SEMAFORO'] = df['SCORE_PROSPECCAO'].apply(
        lambda s: 'VERDE' if s >= 70 else ('AMARELO' if s >= 40 else 'VERMELHO')
    )

    return df


def processar_base_completa(caminho_csv: str) -> pd.DataFrame:
    """
    Pipeline completo: carregar → filtrar → agregar → classificar → pontuar
    """
    inicio = datetime.now()

    print("=" * 70)
    print("  PROCESSAMENTO BASE PGFN - INSCRIÇÕES INDIVIDUAIS")
    print("=" * 70)

    # 1. Carregar
    df_raw = carregar_base_inscricoes(caminho_csv)

    # 2. Filtrar
    df_filtrado = aplicar_filtros_negocio(df_raw)

    # 3. Agregar por CNPJ
    df_empresas = agregar_por_cnpj(df_filtrado)

    # 4. Classificar temperatura
    df_empresas = classificar_temperatura(df_empresas)

    # 5. Gerar score
    df_empresas = gerar_score_prospeccao(df_empresas)

    # 6. Ordenar por score (melhor primeiro)
    df_empresas = df_empresas.sort_values(
        ['TEMPERATURA', 'SCORE_PROSPECCAO', 'POTENCIAL_SG'],
        ascending=[True, False, False]
    )

    # Ordem da temperatura para sort: HOT primeiro, depois WARM, depois COLD
    temp_order = {'HOT': 0, 'WARM': 1, 'COLD': 2}
    df_empresas['_temp_order'] = df_empresas['TEMPERATURA'].map(temp_order)
    df_empresas = df_empresas.sort_values(
        ['_temp_order', 'SCORE_PROSPECCAO', 'POTENCIAL_SG'],
        ascending=[True, False, False]
    ).drop('_temp_order', axis=1)

    duracao = (datetime.now() - inicio).total_seconds()

    print(f"\n  RESUMO FINAL:")
    print(f"  {'='*50}")
    print(f"  Empresas qualificadas: {len(df_empresas):,}")
    print(f"  Dívida total: R$ {df_empresas['DIVIDA_TOTAL'].sum()/1e9:.2f} bi")
    print(f"  Potencial SG: R$ {df_empresas['POTENCIAL_SG'].sum()/1e9:.2f} bi")
    print(f"  Processado em: {duracao:.1f}s")
    print(f"  {'='*50}")

    return df_empresas


if __name__ == '__main__':
    import sys
    caminho = sys.argv[1] if len(sys.argv) > 1 else r"C:\Rodrigo\BasePGFN\2025\base_brasil_marco_zero_inscricoes_LIMPA.csv"

    df = processar_base_completa(caminho)

    # Salvar resultado
    output = caminho.replace('.csv', '_EMPRESAS_CRM.csv')
    df.to_csv(output, sep=';', index=False, encoding='utf-8')
    print(f"\n  Salvo em: {output}")
