"""
================================================================================
█  VALIDAÇÃO MARCO ZERO — VERSÃO OTIMIZADA PARA BASES GRANDES (100GB+)  █
================================================================================

Processa em chunks para não estourar memória
Mostra progresso em tempo real
Gera gráficos e relatório no terminal

Executar: python validacao_base_grande.py

================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
import sys
import time

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================
BASE_PATH = Path(r"C:\Rodrigo\BasePGFN\2025")

# Arquivos
ARQUIVO_UNIFICADO = BASE_PATH / "base_brasil_marco_zero_cnpjs.csv"
ARQUIVO_INSCRICOES = BASE_PATH / "base_brasil_marco_zero_inscricoes.csv"
ARQUIVO_HOT = BASE_PATH / "base_brasil_marco_zero_hot.csv"
ARQUIVO_WARM = BASE_PATH / "base_brasil_marco_zero_warm.csv"
ARQUIVO_COLD = BASE_PATH / "base_brasil_marco_zero_cold.csv"

# Chunk size (ajuste conforme sua RAM)
CHUNK_SIZE = 100_000  # 100k linhas por vez

# ============================================================================
# TERMOS RJ/FALÊNCIA (NÃO CONFUNDIR COM RIO DE JANEIRO)
# ============================================================================
TERMOS_RJ = [
    'RECUPERACAO JUDICIAL',
    'RECUPERAÇÃO JUDICIAL', 
    'EM RECUPERACAO',
    'EM RECUPERAÇÃO',
    'RECUPERACAO JUD',
    'RECUPERAÇÃO JUD',
]

TERMOS_FALENCIA = [
    'FALENCIA',
    'FALÊNCIA',
    'MASSA FALIDA',
    'EM FALENCIA',
    'EM FALÊNCIA',
]

# ============================================================================
# FORMATAÇÃO
# ============================================================================
def fmt_brl(v):
    """Formata valor em BRL"""
    try:
        v = float(v)
        if v >= 1e12: return f"R$ {v/1e12:,.2f} tri"
        if v >= 1e9: return f"R$ {v/1e9:,.2f} bi"
        if v >= 1e6: return f"R$ {v/1e6:,.2f} mi"
        if v >= 1e3: return f"R$ {v/1e3:,.2f} mil"
        return f"R$ {v:,.2f}"
    except:
        return str(v)

def fmt_num(v):
    """Formata número com separador"""
    try:
        return f"{int(v):,}".replace(",", ".")
    except:
        return str(v)

def progress_bar(current, total, prefix='', length=50):
    """Barra de progresso no terminal"""
    pct = current / total
    filled = int(length * pct)
    bar = '█' * filled + '░' * (length - filled)
    sys.stdout.write(f'\r{prefix} |{bar}| {pct*100:.1f}% ({fmt_num(current)}/{fmt_num(total)})')
    sys.stdout.flush()
    if current >= total:
        print()

# ============================================================================
# IDENTIFICAR RJ/FALÊNCIA
# ============================================================================
def identificar_situacao(texto):
    """Identifica RJ ou Falência no texto"""
    if pd.isna(texto):
        return None
    texto = str(texto).upper()
    
    for termo in TERMOS_FALENCIA:
        if termo.upper() in texto:
            return 'FALENCIA'
    
    for termo in TERMOS_RJ:
        if termo.upper() in texto:
            return 'RECUPERACAO_JUDICIAL'
    
    return None

# ============================================================================
# 1. CARREGAR CNPJs SEGMENTADOS (PEQUENOS)
# ============================================================================
def carregar_segmentados():
    """Carrega os 3 arquivos segmentados (são pequenos)"""
    print("\n" + "="*80)
    print("█  CARREGANDO BASES SEGMENTADAS  █")
    print("="*80)
    
    segmentos = {}
    
    for nome, arquivo in [('HOT', ARQUIVO_HOT), ('WARM', ARQUIVO_WARM), ('COLD', ARQUIVO_COLD)]:
        if arquivo.exists():
            df = pd.read_csv(arquivo, sep=';', dtype=str, usecols=['CPF_CNPJ'])
            segmentos[nome] = set(df['CPF_CNPJ'].unique())
            print(f"  ✓ {nome}: {fmt_num(len(segmentos[nome]))} CNPJs")
        else:
            print(f"  ✗ {nome}: arquivo não encontrado")
            segmentos[nome] = set()
    
    return segmentos

# ============================================================================
# 2. PROCESSAR BASE UNIFICADA EM CHUNKS
# ============================================================================
def processar_unificada(segmentos):
    """Processa base unificada em chunks"""
    print("\n" + "="*80)
    print("█  PROCESSANDO BASE UNIFICADA (CHUNKS)  █")
    print("="*80)
    
    if not ARQUIVO_UNIFICADO.exists():
        print(f"  ✗ ERRO: {ARQUIVO_UNIFICADO} não encontrado!")
        return None
    
    # Contar linhas primeiro
    print("\n  Contando linhas...")
    total_linhas = sum(1 for _ in open(ARQUIVO_UNIFICADO, 'r', encoding='utf-8', errors='ignore')) - 1
    print(f"  Total: {fmt_num(total_linhas)} linhas")
    
    # Contadores
    cnpjs_unificado = set()
    cnpjs_hot_encontrados = set()
    cnpjs_warm_encontrados = set()
    cnpjs_cold_encontrados = set()
    
    contagem_rj = 0
    contagem_falencia = 0
    contagem_normal = 0
    
    contagem_uf = defaultdict(int)
    contagem_temperatura = defaultdict(int)
    contagem_inscricoes = defaultdict(int)  # qtd inscrições -> count
    
    soma_divida = 0
    soma_potencial = 0
    
    empresas_inscricao_unica = []
    
    # Detectar colunas
    sample = pd.read_csv(ARQUIVO_UNIFICADO, sep=';', nrows=5, dtype=str)
    colunas = sample.columns.tolist()
    print(f"\n  Colunas: {colunas}")
    
    # Identificar colunas chave
    col_cnpj = 'CPF_CNPJ'
    col_nome = next((c for c in colunas if 'NOME' in c.upper()), None)
    col_uf = next((c for c in colunas if c.upper() in ['UF', 'UF_DEVEDOR']), None)
    col_temp = next((c for c in colunas if 'TEMP' in c.upper()), None)
    col_qtd_insc = next((c for c in colunas if 'QTD' in c.upper() and 'INSC' in c.upper()), None)
    col_divida = next((c for c in colunas if 'DIVIDA' in c.upper() and 'TOTAL' in c.upper()), None)
    col_potencial = next((c for c in colunas if 'POTENCIAL' in c.upper()), None)
    
    print(f"\n  Mapeamento de colunas:")
    print(f"    CNPJ: {col_cnpj}")
    print(f"    Nome: {col_nome}")
    print(f"    UF: {col_uf}")
    print(f"    Temperatura: {col_temp}")
    print(f"    Qtd Inscrições: {col_qtd_insc}")
    print(f"    Dívida: {col_divida}")
    print(f"    Potencial: {col_potencial}")
    
    # Processar em chunks
    print(f"\n  Processando em chunks de {fmt_num(CHUNK_SIZE)}...")
    
    chunks_processados = 0
    linhas_processadas = 0
    
    for chunk in pd.read_csv(ARQUIVO_UNIFICADO, sep=';', dtype=str, chunksize=CHUNK_SIZE):
        chunks_processados += 1
        linhas_processadas += len(chunk)
        
        progress_bar(linhas_processadas, total_linhas, prefix='  Progresso')
        
        for _, row in chunk.iterrows():
            cnpj = row[col_cnpj]
            cnpjs_unificado.add(cnpj)
            
            # Verificar segmento
            if cnpj in segmentos['HOT']:
                cnpjs_hot_encontrados.add(cnpj)
            if cnpj in segmentos['WARM']:
                cnpjs_warm_encontrados.add(cnpj)
            if cnpj in segmentos['COLD']:
                cnpjs_cold_encontrados.add(cnpj)
            
            # RJ/Falência (buscar no nome)
            situacao = identificar_situacao(row.get(col_nome, ''))
            if situacao == 'RECUPERACAO_JUDICIAL':
                contagem_rj += 1
            elif situacao == 'FALENCIA':
                contagem_falencia += 1
            else:
                contagem_normal += 1
            
            # UF
            if col_uf:
                uf = row.get(col_uf, 'N/A')
                contagem_uf[uf] += 1
            
            # Temperatura
            if col_temp:
                temp = row.get(col_temp, 'N/A')
                contagem_temperatura[temp] += 1
            
            # Quantidade de inscrições
            if col_qtd_insc:
                try:
                    qtd = int(float(row.get(col_qtd_insc, 0)))
                except:
                    qtd = 0
                
                if qtd == 1:
                    contagem_inscricoes['1'] += 1
                    # Guardar para análise
                    if len(empresas_inscricao_unica) < 1000:  # Limitar memória
                        empresas_inscricao_unica.append({
                            'CNPJ': cnpj,
                            'NOME': row.get(col_nome, '')[:50] if col_nome else '',
                            'UF': row.get(col_uf, '') if col_uf else '',
                            'DIVIDA': row.get(col_divida, 0) if col_divida else 0
                        })
                elif qtd <= 5:
                    contagem_inscricoes['2-5'] += 1
                elif qtd <= 10:
                    contagem_inscricoes['6-10'] += 1
                elif qtd <= 50:
                    contagem_inscricoes['11-50'] += 1
                elif qtd <= 100:
                    contagem_inscricoes['51-100'] += 1
                else:
                    contagem_inscricoes['100+'] += 1
            
            # Valores
            if col_divida:
                try:
                    soma_divida += float(row.get(col_divida, 0))
                except:
                    pass
            if col_potencial:
                try:
                    soma_potencial += float(row.get(col_potencial, 0))
                except:
                    pass
    
    return {
        'total_cnpjs': len(cnpjs_unificado),
        'cnpjs_set': cnpjs_unificado,
        'hot_encontrados': cnpjs_hot_encontrados,
        'warm_encontrados': cnpjs_warm_encontrados,
        'cold_encontrados': cnpjs_cold_encontrados,
        'rj': contagem_rj,
        'falencia': contagem_falencia,
        'normal': contagem_normal,
        'por_uf': dict(contagem_uf),
        'por_temperatura': dict(contagem_temperatura),
        'por_inscricoes': dict(contagem_inscricoes),
        'soma_divida': soma_divida,
        'soma_potencial': soma_potencial,
        'empresas_inscricao_unica': empresas_inscricao_unica
    }

# ============================================================================
# 3. VALIDAR SEGMENTAÇÃO
# ============================================================================
def validar_segmentacao(segmentos, resultado):
    """Verifica se todos CNPJs segmentados estão na unificada"""
    print("\n" + "="*80)
    print("█  VALIDAÇÃO: SEGMENTAÇÃO  █")
    print("="*80)
    
    cnpjs_unif = resultado['cnpjs_set']
    
    for nome, cnpjs_seg in [('HOT', segmentos['HOT']), ('WARM', segmentos['WARM']), ('COLD', segmentos['COLD'])]:
        total = len(cnpjs_seg)
        encontrados = len(cnpjs_seg & cnpjs_unif)
        ausentes = cnpjs_seg - cnpjs_unif
        
        if len(ausentes) == 0:
            print(f"\n  ✓ {nome}: {fmt_num(total)} CNPJs — TODOS na unificada")
        else:
            print(f"\n  ✗ {nome}: {fmt_num(total)} CNPJs — {fmt_num(len(ausentes))} AUSENTES!")
            print(f"    Exemplos: {list(ausentes)[:3]}")
    
    # Soma
    total_seg = len(segmentos['HOT']) + len(segmentos['WARM']) + len(segmentos['COLD'])
    print(f"\n  " + "-"*60)
    print(f"  Total segmentados: {fmt_num(total_seg)}")
    print(f"  Total unificado:   {fmt_num(resultado['total_cnpjs'])}")
    
    if total_seg == resultado['total_cnpjs']:
        print(f"  ✓ TOTAIS CONFEREM!")
    else:
        print(f"  ⚠ DIFERENÇA: {fmt_num(abs(resultado['total_cnpjs'] - total_seg))}")

# ============================================================================
# 4. RELATÓRIO RJ/FALÊNCIA
# ============================================================================
def relatorio_rj_falencia(resultado):
    """Mostra contagem de RJ e Falência"""
    print("\n" + "="*80)
    print("█  CONTAGEM: RJ/FALÊNCIA (sem confundir com Rio de Janeiro)  █")
    print("="*80)
    
    total = resultado['rj'] + resultado['falencia'] + resultado['normal']
    
    print(f"""
  ┌─────────────────────────────────────────────────────────┐
  │  SITUAÇÃO                    QUANTIDADE          %      │
  ├─────────────────────────────────────────────────────────┤
  │  Recuperação Judicial        {resultado['rj']:>10,}     {resultado['rj']/total*100:>6.2f}%  │
  │  Falência                    {resultado['falencia']:>10,}     {resultado['falencia']/total*100:>6.2f}%  │
  │  Normal/Ativo                {resultado['normal']:>10,}     {resultado['normal']/total*100:>6.2f}%  │
  ├─────────────────────────────────────────────────────────┤
  │  TOTAL                       {total:>10,}    100.00%  │
  └─────────────────────────────────────────────────────────┘
    """)
    
    # Verificar UF Rio de Janeiro para comparação
    uf_rj = resultado['por_uf'].get('RJ', 0)
    print(f"  📍 Para referência: {fmt_num(uf_rj)} CNPJs são do ESTADO RJ (Rio de Janeiro)")
    print(f"     → Não confundir com Recuperação Judicial!")

# ============================================================================
# 5. EMPRESAS INSCRIÇÃO ÚNICA
# ============================================================================
def relatorio_inscricao_unica(resultado):
    """Mostra empresas com inscrição única"""
    print("\n" + "="*80)
    print("█  EMPRESAS COM INSCRIÇÃO ÚNICA  █")
    print("="*80)
    
    qtd_unica = resultado['por_inscricoes'].get('1', 0)
    total = sum(resultado['por_inscricoes'].values())
    
    print(f"\n  Total com inscrição única: {fmt_num(qtd_unica)} ({qtd_unica/total*100:.1f}% do total)")
    
    # Distribuição
    print(f"\n  Distribuição por quantidade de inscrições:")
    print(f"  " + "-"*50)
    ordem = ['1', '2-5', '6-10', '11-50', '51-100', '100+']
    for faixa in ordem:
        qtd = resultado['por_inscricoes'].get(faixa, 0)
        pct = qtd/total*100 if total > 0 else 0
        barra = '█' * int(pct/2)
        print(f"    {faixa:>8}: {qtd:>10,} ({pct:>5.1f}%) {barra}")
    
    # Top 10 com inscrição única (por valor)
    if resultado['empresas_inscricao_unica']:
        print(f"\n  TOP 10 EMPRESAS COM INSCRIÇÃO ÚNICA (amostra):")
        print(f"  " + "-"*70)
        
        # Ordenar por valor
        empresas = resultado['empresas_inscricao_unica']
        for e in empresas:
            try:
                e['DIVIDA_NUM'] = float(e['DIVIDA'])
            except:
                e['DIVIDA_NUM'] = 0
        
        empresas_sorted = sorted(empresas, key=lambda x: x['DIVIDA_NUM'], reverse=True)[:10]
        
        for i, e in enumerate(empresas_sorted, 1):
            print(f"    {i:>2}. {e['CNPJ']} | {e['UF']:>2} | {fmt_brl(e['DIVIDA_NUM']):>15} | {e['NOME'][:35]}")

# ============================================================================
# 6. GRÁFICOS
# ============================================================================
def gerar_graficos(resultado):
    """Gera gráficos de análise"""
    print("\n" + "="*80)
    print("█  GERANDO GRÁFICOS  █")
    print("="*80)
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('MARCO ZERO — Validação da Base Brasil\nSeguro Garantia Judicial', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    # 1. RJ/Falência vs Normal
    ax1 = axes[0, 0]
    labels = ['Normal', 'Recup. Judicial', 'Falência']
    sizes = [resultado['normal'], resultado['rj'], resultado['falencia']]
    colors = ['#2ecc71', '#f39c12', '#e74c3c']
    explode = (0, 0.05, 0.1)
    
    if sum(sizes) > 0:
        wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, 
                                            colors=colors, autopct='%1.1f%%',
                                            shadow=True, startangle=90)
        ax1.set_title('Situação: RJ/Falência', fontweight='bold')
    
    # 2. Por Temperatura
    ax2 = axes[0, 1]
    if resultado['por_temperatura']:
        temp_data = resultado['por_temperatura']
        ordem_temp = ['HOT', 'WARM', 'COLD']
        valores = [temp_data.get(t, 0) for t in ordem_temp]
        colors_temp = ['#e74c3c', '#f39c12', '#3498db']
        bars = ax2.bar(ordem_temp, valores, color=colors_temp)
        ax2.set_title('Distribuição por Temperatura', fontweight='bold')
        ax2.set_ylabel('CNPJs')
        for bar, val in zip(bars, valores):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{val:,}', ha='center', va='bottom', fontsize=9)
    
    # 3. Top 10 UFs
    ax3 = axes[0, 2]
    if resultado['por_uf']:
        uf_sorted = sorted(resultado['por_uf'].items(), key=lambda x: x[1], reverse=True)[:10]
        ufs = [x[0] for x in uf_sorted]
        qtds = [x[1] for x in uf_sorted]
        bars = ax3.barh(ufs[::-1], qtds[::-1], color='#9b59b6')
        ax3.set_title('Top 10 UFs', fontweight='bold')
        ax3.set_xlabel('CNPJs')
        for bar, val in zip(bars, qtds[::-1]):
            ax3.text(bar.get_width(), bar.get_y() + bar.get_height()/2,
                    f' {val:,}', ha='left', va='center', fontsize=8)
    
    # 4. Distribuição por Qtd Inscrições
    ax4 = axes[1, 0]
    if resultado['por_inscricoes']:
        ordem = ['1', '2-5', '6-10', '11-50', '51-100', '100+']
        valores = [resultado['por_inscricoes'].get(f, 0) for f in ordem]
        bars = ax4.bar(ordem, valores, color='#1abc9c')
        ax4.set_title('Distribuição por Qtd de Inscrições', fontweight='bold')
        ax4.set_xlabel('Quantidade de Inscrições')
        ax4.set_ylabel('CNPJs')
        ax4.tick_params(axis='x', rotation=45)
        for bar, val in zip(bars, valores):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{val:,}', ha='center', va='bottom', fontsize=8)
    
    # 5. Valores totais
    ax5 = axes[1, 1]
    labels_val = ['Dívida Total', 'Potencial SG']
    valores_val = [resultado['soma_divida']/1e12, resultado['soma_potencial']/1e12]
    bars = ax5.bar(labels_val, valores_val, color=['#e74c3c', '#2ecc71'])
    ax5.set_title('Valores Totais (R$ trilhões)', fontweight='bold')
    ax5.set_ylabel('R$ trilhões')
    for bar, val in zip(bars, valores_val):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                f'R$ {val:.2f} tri', ha='center', va='bottom', fontsize=10)
    
    # 6. Resumo textual
    ax6 = axes[1, 2]
    ax6.axis('off')
    resumo = f"""
    RESUMO DA VALIDAÇÃO
    ───────────────────────────────
    
    Total CNPJs:        {fmt_num(resultado['total_cnpjs'])}
    
    Recuperação Jud.:   {fmt_num(resultado['rj'])}
    Falência:           {fmt_num(resultado['falencia'])}
    Normal:             {fmt_num(resultado['normal'])}
    
    Dívida Total:       {fmt_brl(resultado['soma_divida'])}
    Potencial SG:       {fmt_brl(resultado['soma_potencial'])}
    
    Inscrição Única:    {fmt_num(resultado['por_inscricoes'].get('1', 0))}
    """
    ax6.text(0.1, 0.5, resumo, fontsize=12, fontfamily='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Salvar
    output_path = BASE_PATH / 'graficos_validacao_marco_zero.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"\n  ✓ Gráficos salvos: {output_path}")
    
    plt.show()

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║   █  VALIDAÇÃO MARCO ZERO — VERSÃO OTIMIZADA (100GB+)  █                    ║
    ║                                                                              ║
    ║   Vazquez & Fonseca Corretora de Seguros                                    ║
    ║   Processamento em chunks para arquivos grandes                             ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    inicio = time.time()
    
    # 1. Carregar segmentados
    segmentos = carregar_segmentados()
    
    # 2. Processar unificada
    resultado = processar_unificada(segmentos)
    
    if resultado is None:
        print("\n✗ ERRO: Não foi possível processar")
        return
    
    # 3. Validar segmentação
    validar_segmentacao(segmentos, resultado)
    
    # 4. RJ/Falência
    relatorio_rj_falencia(resultado)
    
    # 5. Inscrição única
    relatorio_inscricao_unica(resultado)
    
    # 6. Gráficos
    gerar_graficos(resultado)
    
    # Tempo
    tempo = time.time() - inicio
    print(f"\n  ⏱ Tempo total: {tempo/60:.1f} minutos")
    
    print("\n" + "="*80)
    print("█  VALIDAÇÃO CONCLUÍDA  █")
    print("="*80)

if __name__ == "__main__":
    main()
