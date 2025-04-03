
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

EXCEL_FILE = 'Corridas.xlsx'
SHEET_NAME = 'Corridas'

@st.cache_data(ttl=0)
def carregar_dados():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, engine='openpyxl')
        df['Data'] = pd.to_datetime(df['Data']).dt.date
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Data', 'Corrida', 'Tempo', 'Distância'])
    return df

def converter_tempo(tempo_str):
    if pd.isna(tempo_str):
        return pd.NaT
    if isinstance(tempo_str, str) and tempo_str.strip().lower() in ["", "none", "nan"]:
        return pd.NaT
    try:
        return pd.to_timedelta(tempo_str)
    except:
        return pd.NaT

st.title('🔍 Diagnóstico de Corridas por Distância')

df = carregar_dados()

distancias_disponiveis = sorted(df['Distância'].dropna().unique())
distancia_selecionada = st.selectbox("Selecione a distância para inspeção", options=distancias_disponiveis)

df_filtrado = df[df['Distância'] == distancia_selecionada].copy()
df_filtrado['Tempo_td'] = df_filtrado['Tempo'].apply(converter_tempo)
df_filtrado['Data_realizada'] = df_filtrado['Data'] < pd.Timestamp.today().date()
df_filtrado['Tempo_válido'] = ~df_filtrado['Tempo_td'].isna()
df_filtrado['Valida_para_melhor_tempo'] = df_filtrado['Data_realizada'] & df_filtrado['Tempo_válido']

st.dataframe(df_filtrado)

st.markdown("✅ **Legenda**:")
st.markdown("- `Data_realizada`: `True` se a data da corrida já passou")
st.markdown("- `Tempo_válido`: `True` se o tempo está corretamente preenchido")
st.markdown("- `Valida_para_melhor_tempo`: `True` se pode ser usada como melhor tempo")
