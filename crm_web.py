"""
CRM de Prospecção e Operações de Garantia - Interface Web
Versão inicial funcional com Streamlit
"""

import streamlit as st
import pandas as pd
import os
from decimal import Decimal
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="CRM Garantias - PGFN",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Importar módulos do CRM
from src.crm.importador.importador_bases import ImportadorBasesPGFN
from src.crm.scoring.score_fit import ScoreFit
from src.crm.models.conta import TemperaturaLead


@st.cache_data
def carregar_dados():
    """Carrega e processa os dados PGFN (com cache)"""
    diretorio = os.path.dirname(os.path.abspath(__file__))
    importador = ImportadorBasesPGFN(diretorio=diretorio)
    contas, oportunidades, stats = importador.importar_todas(limite_cold=500)

    # Calcular scores
    score_fit = ScoreFit()
    scores = {}
    for conta in contas:
        resultado = score_fit.calcular(conta)
        scores[conta.id] = {
            'score': resultado.score_total,
            'semaforo': resultado.semaforo,
            'recomendacao': resultado.recomendacao
        }

    return contas, oportunidades, stats, scores


def formatar_moeda(valor):
    """Formata valor em R$"""
    if valor >= 1e9:
        return f"R$ {valor/1e9:.2f} bi"
    elif valor >= 1e6:
        return f"R$ {valor/1e6:.1f} M"
    elif valor >= 1e3:
        return f"R$ {valor/1e3:.1f} K"
    else:
        return f"R$ {valor:.2f}"


def contas_para_dataframe(contas, scores):
    """Converte lista de contas para DataFrame"""
    dados = []
    for c in contas:
        pgfn = c.dados_pgfn
        score_info = scores.get(c.id, {'score': 0, 'semaforo': 'vermelho'})

        dados.append({
            'ID': c.id,
            'CNPJ': c.cnpj_formatado,
            'Razão Social': c.razao_social,
            'UF': pgfn.uf if pgfn else '',
            'Região': pgfn.regiao if pgfn else '',
            'Temperatura': c.temperatura.value if c.temperatura else '',
            'Porte': c.porte.value if c.porte else '',
            'Score': score_info['score'],
            'Semáforo': score_info['semaforo'].upper(),
            'Dívida Total': float(pgfn.divida_total) if pgfn else 0,
            'Potencial SG': float(pgfn.potencial_sg) if pgfn else 0,
            'Valor Descoberto': float(pgfn.valor_descoberto) if pgfn else 0,
            'Qtd Inscrições': pgfn.qtd_inscricoes if pgfn else 0,
            'Qtd SG Atual': pgfn.qtd_seguro_garantia if pgfn else 0,
            'Qtd Carta Fiança': pgfn.qtd_carta_fianca if pgfn else 0,
            'Qtd Depósito': pgfn.qtd_deposito if pgfn else 0,
        })

    return pd.DataFrame(dados)


def oportunidades_para_dataframe(oportunidades):
    """Converte lista de oportunidades para DataFrame"""
    dados = []
    for o in oportunidades:
        dados.append({
            'ID': o.id,
            'Nome': o.nome,
            'Conta ID': o.conta_id,
            'Tipo': o.tipo.value if o.tipo else '',
            'Etapa': o.etapa.nome if o.etapa else '',
            'Valor Garantia': float(o.valor_garantia) if o.valor_garantia else 0,
            'Data Criação': o.data_criacao.strftime('%d/%m/%Y') if o.data_criacao else '',
        })

    return pd.DataFrame(dados)


def main():
    # Header
    st.title("🏦 CRM de Prospecção - Garantias PGFN")
    st.markdown("**Sistema de gestão de oportunidades de Seguro Garantia Judicial**")

    # Carregar dados
    with st.spinner("Carregando dados PGFN..."):
        contas, oportunidades, stats, scores = carregar_dados()

    # Converter para DataFrames
    df_contas = contas_para_dataframe(contas, scores)
    df_oportunidades = oportunidades_para_dataframe(oportunidades)

    # ========== SIDEBAR - FILTROS ==========
    st.sidebar.header("🔍 Filtros")

    # Filtro de Temperatura
    temperaturas = ['Todas'] + sorted(df_contas['Temperatura'].unique().tolist())
    temp_selecionada = st.sidebar.selectbox("Temperatura", temperaturas)

    # Filtro de UF
    ufs = ['Todas'] + sorted(df_contas['UF'].unique().tolist())
    uf_selecionada = st.sidebar.selectbox("UF", ufs)

    # Filtro de Porte
    portes = ['Todos'] + sorted(df_contas['Porte'].unique().tolist())
    porte_selecionado = st.sidebar.selectbox("Porte", portes)

    # Filtro de Semáforo
    semaforos = ['Todos'] + sorted(df_contas['Semáforo'].unique().tolist())
    semaforo_selecionado = st.sidebar.selectbox("Semáforo Score", semaforos)

    # Filtro de Potencial mínimo
    potencial_min = st.sidebar.slider(
        "Potencial SG Mínimo (R$ milhões)",
        min_value=0,
        max_value=500,
        value=0,
        step=10
    )

    # Aplicar filtros
    df_filtrado = df_contas.copy()
    if temp_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Temperatura'] == temp_selecionada]
    if uf_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['UF'] == uf_selecionada]
    if porte_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Porte'] == porte_selecionado]
    if semaforo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Semáforo'] == semaforo_selecionado]
    if potencial_min > 0:
        df_filtrado = df_filtrado[df_filtrado['Potencial SG'] >= potencial_min * 1e6]

    # Filtrar oportunidades pelas contas filtradas
    contas_ids = df_filtrado['ID'].tolist()
    df_ops_filtrado = df_oportunidades[df_oportunidades['Conta ID'].isin(contas_ids)]

    # ========== DASHBOARD ==========
    st.markdown("---")
    st.header("📊 Dashboard")

    # KPIs principais
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Contas",
            f"{len(df_filtrado):,}",
            f"de {len(df_contas):,}"
        )

    with col2:
        st.metric(
            "Oportunidades",
            f"{len(df_ops_filtrado):,}",
            f"de {len(df_oportunidades):,}"
        )

    with col3:
        pipeline_total = df_ops_filtrado['Valor Garantia'].sum()
        st.metric(
            "Pipeline Total",
            formatar_moeda(pipeline_total)
        )

    with col4:
        potencial_total = df_filtrado['Potencial SG'].sum()
        st.metric(
            "Potencial SG",
            formatar_moeda(potencial_total)
        )

    with col5:
        descoberto_total = df_filtrado['Valor Descoberto'].sum()
        st.metric(
            "Descoberto",
            formatar_moeda(descoberto_total)
        )

    # Segunda linha de KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        hot = len(df_filtrado[df_filtrado['Temperatura'] == 'HOT'])
        st.metric("🔥 HOT", hot, "Já usa SG")

    with col2:
        warm = len(df_filtrado[df_filtrado['Temperatura'] == 'WARM'])
        st.metric("🌡️ WARM", warm, "Carta/Depósito")

    with col3:
        cold = len(df_filtrado[df_filtrado['Temperatura'] == 'COLD'])
        st.metric("❄️ COLD", cold, "Sem garantia")

    with col4:
        ticket_medio = df_filtrado['Potencial SG'].mean() if len(df_filtrado) > 0 else 0
        st.metric("Ticket Médio", formatar_moeda(ticket_medio))

    # ========== TABS ==========
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Contas", "💼 Oportunidades", "📈 Análises", "📥 Exportar"])

    # TAB 1 - CONTAS
    with tab1:
        st.subheader(f"Contas ({len(df_filtrado):,} registros)")

        # Opções de visualização
        colunas_visiveis = st.multiselect(
            "Colunas visíveis",
            df_filtrado.columns.tolist(),
            default=['CNPJ', 'Razão Social', 'UF', 'Temperatura', 'Porte', 'Score', 'Semáforo', 'Potencial SG', 'Valor Descoberto']
        )

        # Ordenação
        col_ordem = st.selectbox("Ordenar por", colunas_visiveis, index=colunas_visiveis.index('Potencial SG') if 'Potencial SG' in colunas_visiveis else 0)
        ordem_desc = st.checkbox("Decrescente", value=True)

        df_exibir = df_filtrado[colunas_visiveis].sort_values(col_ordem, ascending=not ordem_desc)

        # Formatar colunas monetárias para exibição
        df_display = df_exibir.copy()
        for col in ['Dívida Total', 'Potencial SG', 'Valor Descoberto']:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(lambda x: formatar_moeda(x) if x > 0 else '-')

        st.dataframe(df_display, use_container_width=True, height=500)

    # TAB 2 - OPORTUNIDADES
    with tab2:
        st.subheader(f"Oportunidades ({len(df_ops_filtrado):,} registros)")

        # Filtro adicional por tipo
        tipos_op = ['Todos'] + sorted(df_ops_filtrado['Nome'].str.split('—').str[0].str.strip().unique().tolist())
        tipo_op_selecionado = st.selectbox("Tipo de Oportunidade", tipos_op)

        df_ops_exibir = df_ops_filtrado.copy()
        if tipo_op_selecionado != 'Todos':
            df_ops_exibir = df_ops_exibir[df_ops_exibir['Nome'].str.contains(tipo_op_selecionado, case=False)]

        df_ops_exibir = df_ops_exibir.sort_values('Valor Garantia', ascending=False)

        # Formatar valor
        df_ops_display = df_ops_exibir.copy()
        df_ops_display['Valor Garantia'] = df_ops_display['Valor Garantia'].apply(lambda x: formatar_moeda(x) if x > 0 else '-')

        st.dataframe(df_ops_display, use_container_width=True, height=500)

    # TAB 3 - ANÁLISES
    with tab3:
        st.subheader("Análises")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Distribuição por Temperatura**")
            temp_counts = df_filtrado['Temperatura'].value_counts()
            st.bar_chart(temp_counts)

        with col2:
            st.markdown("**Distribuição por UF (Top 10)**")
            uf_counts = df_filtrado['UF'].value_counts().head(10)
            st.bar_chart(uf_counts)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**Distribuição por Porte**")
            porte_counts = df_filtrado['Porte'].value_counts()
            st.bar_chart(porte_counts)

        with col4:
            st.markdown("**Distribuição por Semáforo**")
            semaforo_counts = df_filtrado['Semáforo'].value_counts()
            st.bar_chart(semaforo_counts)

        # Resumo por UF
        st.markdown("---")
        st.markdown("**Resumo por UF**")
        resumo_uf = df_filtrado.groupby('UF').agg({
            'ID': 'count',
            'Potencial SG': 'sum',
            'Valor Descoberto': 'sum',
            'Score': 'mean'
        }).rename(columns={
            'ID': 'Qtd Contas',
            'Potencial SG': 'Potencial Total',
            'Valor Descoberto': 'Descoberto Total',
            'Score': 'Score Médio'
        }).sort_values('Potencial Total', ascending=False)

        resumo_uf['Potencial Total'] = resumo_uf['Potencial Total'].apply(formatar_moeda)
        resumo_uf['Descoberto Total'] = resumo_uf['Descoberto Total'].apply(formatar_moeda)
        resumo_uf['Score Médio'] = resumo_uf['Score Médio'].round(1)

        st.dataframe(resumo_uf, use_container_width=True)

    # TAB 4 - EXPORTAR
    with tab4:
        st.subheader("Exportar Dados")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📊 Contas (filtradas)**")
            csv_contas = df_filtrado.to_csv(index=False, sep=';', decimal=',')
            st.download_button(
                label="⬇️ Baixar Contas (CSV)",
                data=csv_contas,
                file_name=f"contas_pgfn_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            st.caption(f"{len(df_filtrado):,} registros")

        with col2:
            st.markdown("**💼 Oportunidades (filtradas)**")
            csv_ops = df_ops_filtrado.to_csv(index=False, sep=';', decimal=',')
            st.download_button(
                label="⬇️ Baixar Oportunidades (CSV)",
                data=csv_ops,
                file_name=f"oportunidades_pgfn_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            st.caption(f"{len(df_ops_filtrado):,} registros")

        st.markdown("---")
        st.markdown("**📦 Exportar Tudo (Excel)**")

        # Criar Excel com múltiplas abas
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, sheet_name='Contas', index=False)
            df_ops_filtrado.to_excel(writer, sheet_name='Oportunidades', index=False)

            # Resumo
            resumo_data = {
                'Métrica': [
                    'Total Contas', 'Total Oportunidades', 'Pipeline (R$)',
                    'Potencial SG (R$)', 'Descoberto (R$)',
                    'Contas HOT', 'Contas WARM', 'Contas COLD'
                ],
                'Valor': [
                    len(df_filtrado), len(df_ops_filtrado), pipeline_total,
                    potencial_total, descoberto_total,
                    hot, warm, cold
                ]
            }
            pd.DataFrame(resumo_data).to_excel(writer, sheet_name='Resumo', index=False)

        st.download_button(
            label="⬇️ Baixar Excel Completo",
            data=buffer.getvalue(),
            file_name=f"crm_pgfn_completo_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Footer
    st.markdown("---")
    st.caption(f"CRM Garantias PGFN | Dados: {stats.total_contas:,} contas | {stats.oportunidades_geradas:,} oportunidades | Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")


if __name__ == "__main__":
    main()
