
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
    try:
        if pd.isna(tempo_str):
            return pd.NaT
        tempo_str = str(tempo_str).strip().lower()
        if tempo_str in ["", "none", "nan"]:
            return pd.NaT
        return pd.to_timedelta(tempo_str)
    except:
        return pd.NaT

st.title('🏁 Controle de Corridas - Melhor Tempo')

df = carregar_dados()
df['Tempo_td'] = df['Tempo'].apply(converter_tempo)

st.subheader("🏅 Melhores Tempos por Distância")
distancias_disponiveis = sorted(df['Distância'].dropna().unique())
distancia_selecionada = st.selectbox("Selecione a distância (km)", options=distancias_disponiveis)

# Aplicar os filtros de tempo válido e data realizada
filtradas = df[df['Distância'] == distancia_selecionada].copy()
filtradas['Data'] = pd.to_datetime(filtradas['Data']).dt.date
filtradas['Valida'] = (~filtradas['Tempo_td'].isna()) & (filtradas['Data'] < datetime.today().date())

# Mostrar para o usuário as corridas consideradas válidas
st.markdown("### 🐞 Corridas válidas para melhor tempo:")
st.dataframe(filtradas[filtradas['Valida']])

melhores = filtradas[filtradas['Valida']].sort_values(by='Tempo_td')

if not melhores.empty:
    melhor = melhores.iloc[0]
    st.success(f"🏃 Melhor tempo para {int(distancia_selecionada)} km: **{melhor['Tempo']}** — {melhor['Corrida']} em {melhor['Data'].strftime('%d/%m/%Y')}")
else:
    st.info("Nenhuma corrida válida encontrada com tempo registrado e data passada.")
