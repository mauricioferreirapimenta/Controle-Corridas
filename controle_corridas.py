
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

def salvar_dados(df):
    df_export = df.copy()
    df_export['Data'] = pd.to_datetime(df_export['Data'])
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name=SHEET_NAME, index=False)

def gerar_excel_download(df):
    output = BytesIO()
    df_export = df.copy()
    df_export['Data'] = pd.to_datetime(df_export['Data'])
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False)
    return output.getvalue()

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

st.title('🏃‍♂️ Controle de Corridas')

aba = st.sidebar.radio("Escolha uma opção:", [
    "Adicionar Corrida",
    "Alterar Corrida",
    "Listagem Completa",
    "Melhor Tempo por Distância",
    "Diagnóstico por Distância"
])

df = carregar_dados()

if aba == "Adicionar Corrida":
    st.header("➕ Adicionar Corrida")
    with st.form("form_adicionar"):
        data = st.date_input("Data da corrida")
        nome = st.text_input("Nome da corrida")
        tempo = st.text_input("Tempo (hh:mm:ss)")
        distancia = st.number_input("Distância (km)", min_value=1, step=1)
        enviar = st.form_submit_button("Salvar")

        if enviar:
            nova_corrida = {
                'Data': data,
                'Corrida': nome,
                'Tempo': tempo,
                'Distância': distancia
            }
            df = pd.concat([df, pd.DataFrame([nova_corrida])], ignore_index=True)
            salvar_dados(df)
            st.success("Corrida adicionada com sucesso!")

elif aba == "Alterar Corrida":
    st.header("✏️ Alterar Corrida")
    if df.empty:
        st.warning("Nenhuma corrida cadastrada.")
    else:
        opcoes_corridas = df['Corrida'] + ' - ' + pd.to_datetime(df['Data']).astype(str)
        corrida_escolhida = st.selectbox("Selecione a corrida", options=[""] + opcoes_corridas.tolist())

        if corrida_escolhida:
            idx = df[opcoes_corridas == corrida_escolhida].index[0]

            with st.form("form_alterar"):
                data = st.date_input("Data da corrida", value=df.at[idx, 'Data'])
                nome = st.text_input("Nome da corrida", value=df.at[idx, 'Corrida'])
                tempo = st.text_input("Tempo (hh:mm:ss)", value=df.at[idx, 'Tempo'])
                distancia = st.number_input("Distância (km)", min_value=1, step=1, value=int(df.at[idx, 'Distância']))
                atualizar = st.form_submit_button("Atualizar")

                if atualizar:
                    df.at[idx, 'Data'] = data
                    df.at[idx, 'Corrida'] = nome
                    df.at[idx, 'Tempo'] = tempo
                    df.at[idx, 'Distância'] = distancia
                    salvar_dados(df)
                    st.success("Corrida atualizada com sucesso!")

elif aba == "Listagem Completa":
    st.header("📋 Todas as Corridas")
    st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)

    st.download_button(
        label="📥 Baixar dados em Excel",
        data=gerar_excel_download(df),
        file_name="corridas_atualizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif aba == "Melhor Tempo por Distância":
    st.header("🏅 Melhores Tempos por Distância")
    df['Tempo_td'] = df['Tempo'].apply(converter_tempo)

    distancias_disponiveis = sorted(df['Distância'].dropna().unique())
    distancia_selecionada = st.selectbox("Selecione a distância (km)", options=distancias_disponiveis)

    filtradas = df[df['Distância'] == distancia_selecionada].copy()
    filtradas['Data'] = pd.to_datetime(filtradas['Data']).dt.date
    filtradas['Valida'] = (~filtradas['Tempo_td'].isna()) & (filtradas['Data'] < datetime.today().date())

    st.markdown("### 🐞 Corridas válidas para melhor tempo:")
    st.dataframe(filtradas[filtradas['Valida']])

    melhores = filtradas[filtradas['Valida']].sort_values(by='Tempo_td')

    if not melhores.empty:
        melhor = melhores.iloc[0]
        st.success(f"🏁 Melhor tempo para {int(distancia_selecionada)} km: **{melhor['Tempo']}** — {melhor['Corrida']} em {melhor['Data'].strftime('%d/%m/%Y')}")
    else:
        st.info("Nenhuma corrida válida encontrada com tempo registrado e data passada.")

elif aba == "Diagnóstico por Distância":
    st.header("🧪 Diagnóstico por Distância")
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
