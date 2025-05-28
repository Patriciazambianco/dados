import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Inspeção EPI", layout="wide")

st.title("Dashboard de Pendências de Inspeção de EPI")

# === Dados simulados - troque isso pelos seus arquivos reais depois ===
kit_epi = pd.DataFrame({
    'IDTEL_TECNICO': [101, 102, 103, 104, 105],
    'PRODUTO_PRINC_INSPECAO': ['EPI1', 'EPI2', 'EPI1', 'EPI3', 'EPI2']
})

inspecao = pd.DataFrame({
    'IDTEL': [101, 101, 102, 104],
    'DATA_INSPECAO': pd.to_datetime([
        '2024-05-01', '2024-01-01', '2023-12-01', '2023-11-15'
    ])
})

microsiga = pd.DataFrame({
    'IDTEL': [101, 102, 103, 104, 105],
    'GERENTE_IMEDIATO': ['Gerente A', 'Gerente A', 'Gerente B', 'Gerente B', 'Gerente A'],
    'COORDENADOR_IMEDIATO': ['Coord 1', 'Coord 2', 'Coord 1', 'Coord 3', 'Coord 2']
})

# === Processamento dos dados ===
ultima_inspecao = (
    inspecao.groupby('IDTEL')['DATA_INSPECAO']
    .max()
    .reset_index()
)

df = (
    kit_epi
    .merge(ultima_inspecao, left_on='IDTEL_TECNICO', right_on='IDTEL', how='left')
    .merge(microsiga[['IDTEL', 'GERENTE_IMEDIATO', 'COORDENADOR_IMEDIATO']], left_on='IDTEL_TECNICO', right_on='IDTEL', how='left')
)

hoje = pd.to_datetime(datetime.today().date())
limite = hoje - timedelta(days=180)

def status_inspecao(row):
    if pd.isna(row['DATA_INSPECAO']):
        return 'Pendente (sem inspeção)'
    elif row['DATA_INSPECAO'] < limite:
        return 'Pendente (inspeção vencida)'
    else:
        return 'OK'

df['STATUS'] = df.apply(status_inspecao, axis=1)

# === Filtros no Streamlit ===
gerentes = ['Todos'] + sorted(df['GERENTE_IMEDIATO'].dropna().unique().tolist())
coordenadores = ['Todos'] + sorted(df['COORDENADOR_IMEDIATO'].dropna().unique().tolist())

gerente_selecionado = st.selectbox("Filtrar por Gerente:", gerentes)
coordenador_selecionado = st.selectbox("Filtrar por Coordenador:", coordenadores)

df_filtrado = df.copy()
if gerente_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['GERENTE_IMEDIATO'] == gerente_selecionado]
if coordenador_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['COORDENADOR_IMEDIATO'] == coordenador_selecionado]

resumo = (
    df_filtrado.groupby(['GERENTE_IMEDIATO', 'COORDENADOR_IMEDIATO', 'STATUS'])
    .size()
    .reset_index(name='QTD')
)

# === Gráfico ===
if resumo.empty:
    st.warning("Nenhum dado para os filtros selecionados.")
else:
    fig = px.bar(
        resumo,
        x='COORDENADOR_IMEDIATO',
        y='QTD',
        color='STATUS',
        barmode='group',
        facet_col='GERENTE_IMEDIATO',
        title="Pendências e Inspeções OK por Coordenador e Gerente",
        labels={'COORDENADOR_IMEDIATO': 'Coordenador', 'QTD': 'Quantidade', 'STATUS': 'Status'}
    )
    st.plotly_chart(fig, use_container_width=True)

# === Mostrar dados detalhados ===
if st.checkbox("Mostrar dados detalhados"):
    st.dataframe(df_filtrado[['IDTEL_TECNICO', 'PRODUTO_PRINC_INSPECAO', 'DATA_INSPECAO', 'GERENTE_IMEDIATO', 'COORDENADOR_IMEDIATO', 'STATUS']])
