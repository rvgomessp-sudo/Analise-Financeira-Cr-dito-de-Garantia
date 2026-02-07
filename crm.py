"""
CRM de Prospecção - Seguro Garantia Judicial PGFN
Interface funcional Streamlit para prospecção imediata.

Lê diretamente a base de inscrições (1M+ linhas), aplica filtros
de negócio e apresenta empresas qualificadas para prospecção.

Uso:
    streamlit run crm.py
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from processador_pgfn import (
    processar_base_completa,
    carregar_base_inscricoes,
    aplicar_filtros_negocio,
    RECEITAS_PJ_QUALIFICADAS,
    SITUACOES_AJUIZADAS,
)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

st.set_page_config(
    page_title="CRM Seguro Garantia - PGFN",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# FUNÇÕES DE FORMATAÇÃO
# =============================================================================

def fmt_moeda(valor):
    if valor >= 1e9:
        return f"R$ {valor/1e9:.2f} bi"
    elif valor >= 1e6:
        return f"R$ {valor/1e6:.1f} M"
    elif valor >= 1e3:
        return f"R$ {valor/1e3:.0f} K"
    return f"R$ {valor:,.0f}"


def fmt_pct(valor, total):
    if total == 0:
        return "0%"
    return f"{valor/total*100:.1f}%"


def semaforo_cor(semaforo):
    cores = {'VERDE': '🟢', 'AMARELO': '🟡', 'VERMELHO': '🔴'}
    return cores.get(semaforo, '⚪')


def temp_icone(temp):
    icones = {'HOT': '🔥', 'WARM': '🌡️', 'COLD': '❄️'}
    return icones.get(temp, '⚪')


# =============================================================================
# CACHE DE DADOS
# =============================================================================

@st.cache_data(show_spinner="Processando base PGFN (1M+ inscrições)...")
def carregar_e_processar(caminho):
    """Carrega e processa dados com cache do Streamlit"""
    return processar_base_completa(caminho)


@st.cache_data(show_spinner="Carregando inscrições detalhadas...")
def carregar_inscricoes_filtradas(caminho):
    """Carrega inscrições filtradas para drill-down"""
    df = carregar_base_inscricoes(caminho)
    df = aplicar_filtros_negocio(df)
    return df


# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================

def main():
    st.title("🏦 CRM Seguro Garantia - PGFN Marco Zero")
    st.caption("Prospecção de empresas com dívida ativa para Seguro Garantia Judicial")

    # --- Seleção do arquivo ---
    caminho_padrao = r"C:\Rodrigo\BasePGFN\2025\base_brasil_marco_zero_inscricoes_LIMPA.csv"

    with st.sidebar:
        st.header("⚙️ Configuração")
        caminho = st.text_input("Caminho da base CSV", value=caminho_padrao)

        if not os.path.exists(caminho):
            st.error(f"Arquivo não encontrado: {caminho}")
            st.stop()

    # --- Carregar dados ---
    df = carregar_e_processar(caminho)

    # =========================================================================
    # SIDEBAR - FILTROS
    # =========================================================================
    with st.sidebar:
        st.header("🔍 Filtros")

        # Temperatura
        temps = st.multiselect(
            "Temperatura",
            ['HOT', 'WARM', 'COLD'],
            default=['HOT', 'WARM', 'COLD'],
            format_func=lambda x: f"{temp_icone(x)} {x}"
        )

        # UF
        ufs_disponiveis = sorted(df['UF_DEVEDOR'].unique().tolist())
        ufs = st.multiselect("UF", ufs_disponiveis, default=[])

        # Região
        regioes_disponiveis = sorted(df['REGIAO'].unique().tolist())
        regioes = st.multiselect("Região TRF", regioes_disponiveis, default=[])

        # Porte
        portes = st.multiselect(
            "Porte Estimado",
            ['GRANDE', 'MEDIO', 'PEQUENO', 'MICRO'],
            default=['GRANDE', 'MEDIO']
        )

        # Semáforo
        semaforos = st.multiselect(
            "Semáforo",
            ['VERDE', 'AMARELO', 'VERMELHO'],
            default=['VERDE', 'AMARELO'],
            format_func=lambda x: f"{semaforo_cor(x)} {x}"
        )

        # Potencial mínimo
        pot_min = st.slider(
            "Potencial SG mínimo (R$ milhões)",
            min_value=0, max_value=500, value=0, step=5
        )

        # Score mínimo
        score_min = st.slider(
            "Score mínimo",
            min_value=0, max_value=100, value=0, step=5
        )

    # --- Aplicar filtros ---
    mask = df['TEMPERATURA'].isin(temps)
    if ufs:
        mask &= df['UF_DEVEDOR'].isin(ufs)
    if regioes:
        mask &= df['REGIAO'].isin(regioes)
    mask &= df['PORTE_ESTIMADO'].isin(portes)
    mask &= df['SEMAFORO'].isin(semaforos)
    if pot_min > 0:
        mask &= df['POTENCIAL_SG'] >= pot_min * 1e6
    if score_min > 0:
        mask &= df['SCORE_PROSPECCAO'] >= score_min

    df_f = df[mask].copy()

    # =========================================================================
    # DASHBOARD
    # =========================================================================
    st.markdown("---")

    # KPIs principais
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Empresas", f"{len(df_f):,}", f"de {len(df):,}")
    with col2:
        st.metric("Potencial SG", fmt_moeda(df_f['POTENCIAL_SG'].sum()))
    with col3:
        st.metric("Dívida Total", fmt_moeda(df_f['DIVIDA_TOTAL'].sum()))
    with col4:
        st.metric("Valor Descoberto", fmt_moeda(df_f['VALOR_DESCOBERTO'].sum()))
    with col5:
        st.metric("Ticket Médio", fmt_moeda(df_f['TICKET_MEDIO'].mean()) if len(df_f) > 0 else "R$ 0")

    # KPIs por temperatura
    col1, col2, col3, col4 = st.columns(4)
    hot = df_f[df_f['TEMPERATURA'] == 'HOT']
    warm = df_f[df_f['TEMPERATURA'] == 'WARM']
    cold = df_f[df_f['TEMPERATURA'] == 'COLD']

    with col1:
        st.metric(f"🔥 HOT", f"{len(hot):,}", f"Cross-sell | {fmt_moeda(hot['POTENCIAL_SG'].sum())}")
    with col2:
        st.metric(f"🌡️ WARM", f"{len(warm):,}", f"Conversão | {fmt_moeda(warm['POTENCIAL_SG'].sum())}")
    with col3:
        st.metric(f"❄️ COLD", f"{len(cold):,}", f"Prospecção | {fmt_moeda(cold['POTENCIAL_SG'].sum())}")
    with col4:
        score_medio = df_f['SCORE_PROSPECCAO'].mean() if len(df_f) > 0 else 0
        st.metric("Score Médio", f"{score_medio:.0f}/100")

    # =========================================================================
    # TABS
    # =========================================================================
    st.markdown("---")
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Empresas",
        "📊 Análises",
        "🔍 Detalhe Empresa",
        "📈 Preditivo",
        "📥 Exportar"
    ])

    # --- TAB 1: LISTA DE EMPRESAS ---
    with tab1:
        st.subheader(f"Empresas qualificadas ({len(df_f):,})")

        # Colunas de exibição
        colunas_padrao = [
            'CPF_CNPJ', 'NOME_DEVEDOR', 'UF_DEVEDOR', 'TEMPERATURA',
            'PORTE_ESTIMADO', 'SCORE_PROSPECCAO', 'SEMAFORO',
            'QTD_INSCRICOES', 'POTENCIAL_SG', 'DIVIDA_TOTAL',
            'VALOR_DESCOBERTO', 'QTD_SEGURO_GARANTIA', 'QTD_CARTA_FIANCA',
            'QTD_DEPOSITO', 'QTD_PENHORA', 'QTD_SEM_GARANTIA',
        ]
        colunas_disponiveis = [c for c in colunas_padrao if c in df_f.columns]

        df_display = df_f[colunas_disponiveis].copy()

        # Formatar valores monetários
        for col in ['POTENCIAL_SG', 'DIVIDA_TOTAL', 'VALOR_DESCOBERTO', 'TICKET_MEDIO']:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(
                    lambda x: fmt_moeda(x) if x > 0 else '-'
                )

        st.dataframe(
            df_display,
            use_container_width=True,
            height=600,
            column_config={
                'SCORE_PROSPECCAO': st.column_config.ProgressColumn(
                    "Score",
                    min_value=0,
                    max_value=100,
                    format="%d",
                ),
            }
        )

    # --- TAB 2: ANÁLISES ---
    with tab2:
        st.subheader("Análises")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Distribuição por Temperatura**")
            temp_data = df_f['TEMPERATURA'].value_counts()
            st.bar_chart(temp_data)

            st.markdown("**Distribuição por Porte**")
            porte_data = df_f['PORTE_ESTIMADO'].value_counts()
            st.bar_chart(porte_data)

        with col2:
            st.markdown("**Top 10 UFs**")
            uf_data = df_f['UF_DEVEDOR'].value_counts().head(10)
            st.bar_chart(uf_data)

            st.markdown("**Distribuição por Semáforo**")
            sem_data = df_f['SEMAFORO'].value_counts()
            st.bar_chart(sem_data)

        # Resumo por região
        st.markdown("---")
        st.markdown("**Resumo por Região TRF**")
        resumo_regiao = df_f.groupby('REGIAO').agg(
            Empresas=('CPF_CNPJ', 'count'),
            Potencial_SG=('POTENCIAL_SG', 'sum'),
            Divida_Total=('DIVIDA_TOTAL', 'sum'),
            Score_Medio=('SCORE_PROSPECCAO', 'mean'),
            Hot=('TEMPERATURA', lambda x: (x == 'HOT').sum()),
            Warm=('TEMPERATURA', lambda x: (x == 'WARM').sum()),
            Cold=('TEMPERATURA', lambda x: (x == 'COLD').sum()),
        ).sort_values('Potencial_SG', ascending=False)

        resumo_regiao['Potencial_SG'] = resumo_regiao['Potencial_SG'].apply(fmt_moeda)
        resumo_regiao['Divida_Total'] = resumo_regiao['Divida_Total'].apply(fmt_moeda)
        resumo_regiao['Score_Medio'] = resumo_regiao['Score_Medio'].round(1)

        st.dataframe(resumo_regiao, use_container_width=True)

        # Resumo por UF
        st.markdown("**Resumo por UF (Top 15)**")
        resumo_uf = df_f.groupby('UF_DEVEDOR').agg(
            Empresas=('CPF_CNPJ', 'count'),
            Potencial_SG=('POTENCIAL_SG', 'sum'),
            Ticket_Medio=('TICKET_MEDIO', 'mean'),
            Hot=('TEMPERATURA', lambda x: (x == 'HOT').sum()),
            Warm=('TEMPERATURA', lambda x: (x == 'WARM').sum()),
        ).sort_values('Potencial_SG', ascending=False).head(15)

        resumo_uf['Potencial_SG'] = resumo_uf['Potencial_SG'].apply(fmt_moeda)
        resumo_uf['Ticket_Medio'] = resumo_uf['Ticket_Medio'].apply(fmt_moeda)

        st.dataframe(resumo_uf, use_container_width=True)

    # --- TAB 3: DETALHE DA EMPRESA ---
    with tab3:
        st.subheader("Detalhe da Empresa")

        # Buscar empresa
        busca = st.text_input("Buscar por CNPJ ou Nome", "")

        if busca:
            busca_upper = busca.upper().strip()
            mask_busca = (
                df_f['CPF_CNPJ'].str.contains(busca, case=False, na=False) |
                df_f['NOME_DEVEDOR'].str.contains(busca_upper, case=False, na=False)
            )
            resultados = df_f[mask_busca]

            if len(resultados) == 0:
                st.warning("Nenhuma empresa encontrada.")
            else:
                for _, emp in resultados.head(5).iterrows():
                    with st.expander(
                        f"{temp_icone(emp['TEMPERATURA'])} {emp['NOME_DEVEDOR']} | "
                        f"{emp['CPF_CNPJ']} | Score: {emp['SCORE_PROSPECCAO']}"
                    ):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown("**Identificação**")
                            st.write(f"CNPJ: {emp['CPF_CNPJ']}")
                            st.write(f"Nome: {emp['NOME_DEVEDOR']}")
                            st.write(f"UF: {emp['UF_DEVEDOR']}")
                            st.write(f"Região: {emp['REGIAO']}")
                            st.write(f"Porte: {emp['PORTE_ESTIMADO']}")

                        with col2:
                            st.markdown("**Financeiro**")
                            st.write(f"Dívida Total: {fmt_moeda(emp['DIVIDA_TOTAL'])}")
                            st.write(f"Potencial SG: {fmt_moeda(emp['POTENCIAL_SG'])}")
                            st.write(f"Valor Descoberto: {fmt_moeda(emp['VALOR_DESCOBERTO'])}")
                            st.write(f"Ticket Médio: {fmt_moeda(emp['TICKET_MEDIO'])}")
                            st.write(f"Inscrições: {emp['QTD_INSCRICOES']}")

                        with col3:
                            st.markdown("**Garantias**")
                            st.write(f"Seguro Garantia: {emp['QTD_SEGURO_GARANTIA']}")
                            st.write(f"Carta Fiança: {emp['QTD_CARTA_FIANCA']}")
                            st.write(f"Depósito: {emp['QTD_DEPOSITO']}")
                            st.write(f"Penhora: {emp['QTD_PENHORA']}")
                            st.write(f"Sem Garantia: {emp['QTD_SEM_GARANTIA']}")

                        # Perfil tributário
                        st.markdown("**Perfil Tributário**")
                        trib_cols = ['QTD_IRPJ', 'QTD_CSLL', 'QTD_COFINS', 'QTD_PIS', 'QTD_IPI']
                        trib_data = {c.replace('QTD_', ''): emp[c] for c in trib_cols if c in emp.index}
                        st.bar_chart(pd.Series(trib_data))
        else:
            st.info("Digite um CNPJ ou nome para buscar.")

    # --- TAB 4: PREDITIVO ---
    with tab4:
        st.subheader("📈 Análise Preditiva (base para expansão)")

        st.markdown("""
        **Estrutura preparada para análise preditiva:**

        **Variáveis disponíveis para modelagem:**
        - `QTD_INSCRICOES` - Volume de inscrições (proxy de complexidade jurídica)
        - `DIVIDA_TOTAL` / `TICKET_MEDIO` - Dimensão financeira
        - `ANO_MIN` / `ANO_MAX` - Perfil temporal (safra)
        - `QTD_IRPJ` / `QTD_CSLL` / `QTD_COFINS` / `QTD_PIS` / `QTD_IPI` - Perfil tributário
        - `QTD_AJUIZADA` / `QTD_NEGOCIADA_SISPAR` - Situação processual
        - `UF_DEVEDOR` / `REGIAO` - Localização geográfica
        - `TIPO_GARANTIA` mix - Comportamento de garantia atual

        **Modelos sugeridos:**
        1. **Propensão à conversão**: P(empresa aceitar SG) baseado em perfil tributário + porte + região
        2. **Valor esperado**: Valor provável de prêmio SG por empresa
        3. **Clustering**: Segmentação automática por perfil (K-means sobre variáveis normalizadas)
        4. **Churn**: Probabilidade de perder interesse (tempo desde última inscrição)
        """)

        # Correlação básica
        st.markdown("**Correlação entre variáveis numéricas**")
        numericas = ['QTD_INSCRICOES', 'DIVIDA_TOTAL', 'TICKET_MEDIO', 'POTENCIAL_SG',
                     'SCORE_PROSPECCAO', 'QTD_SEGURO_GARANTIA', 'QTD_SEM_GARANTIA']
        numericas_disp = [c for c in numericas if c in df_f.columns]
        if len(df_f) > 0:
            corr = df_f[numericas_disp].corr().round(2)
            st.dataframe(corr, use_container_width=True)

        # Distribuição de scores
        st.markdown("**Distribuição de Scores**")
        if len(df_f) > 0:
            hist_data = df_f['SCORE_PROSPECCAO'].value_counts().sort_index()
            st.bar_chart(hist_data)

    # --- TAB 5: EXPORTAR ---
    with tab5:
        st.subheader("📥 Exportar Dados")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**CSV (todas as empresas filtradas)**")
            csv = df_f.to_csv(sep=';', index=False, decimal=',')
            st.download_button(
                "⬇️ Baixar CSV",
                data=csv,
                file_name=f"crm_pgfn_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            st.caption(f"{len(df_f):,} empresas")

        with col2:
            st.markdown("**Excel (com abas)**")
            from io import BytesIO
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # HOT
                df_f[df_f['TEMPERATURA'] == 'HOT'].to_excel(
                    writer, sheet_name='HOT', index=False)
                # WARM
                df_f[df_f['TEMPERATURA'] == 'WARM'].to_excel(
                    writer, sheet_name='WARM', index=False)
                # COLD
                df_f[df_f['TEMPERATURA'] == 'COLD'].to_excel(
                    writer, sheet_name='COLD', index=False)
                # Resumo
                resumo = pd.DataFrame({
                    'Métrica': ['Total Empresas', 'HOT', 'WARM', 'COLD',
                                'Potencial SG', 'Dívida Total', 'Score Médio'],
                    'Valor': [len(df_f), len(hot), len(warm), len(cold),
                              df_f['POTENCIAL_SG'].sum(), df_f['DIVIDA_TOTAL'].sum(),
                              df_f['SCORE_PROSPECCAO'].mean()]
                })
                resumo.to_excel(writer, sheet_name='Resumo', index=False)

            st.download_button(
                "⬇️ Baixar Excel",
                data=buffer.getvalue(),
                file_name=f"crm_pgfn_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col3:
            st.markdown("**Lista de prospecção (Top 100)**")
            top100 = df_f.head(100)[['CPF_CNPJ', 'NOME_DEVEDOR', 'UF_DEVEDOR',
                                      'TEMPERATURA', 'SCORE_PROSPECCAO', 'POTENCIAL_SG']].copy()
            top100['POTENCIAL_SG'] = top100['POTENCIAL_SG'].apply(fmt_moeda)
            csv_top = top100.to_csv(sep=';', index=False)
            st.download_button(
                "⬇️ Top 100 para prospectar",
                data=csv_top,
                file_name=f"top100_prospeccao_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    # Footer
    st.markdown("---")
    st.caption(
        f"CRM Seguro Garantia PGFN | "
        f"{len(df):,} empresas processadas | "
        f"Base: inscrições individuais (11 colunas verificadas) | "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )


if __name__ == "__main__":
    main()
