
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Caminho do arquivo Excel
EXCEL_FILE = 'Corridas.xlsx'
SHEET_NAME = 'Corridas'

@st.cache_data(ttl=0)
def carregar_dados():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME, engine='openpyxl')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Data', 'Corrida', 'Tempo', 'Distância'])
    return df

def salvar_dados(df):
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=SHEET_NAME, index=False)

def gerar_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def converter_tempo(tempo_str):
    try:
        return pd.to_timedelta(tempo_str)
    except:
        return pd.NaT

st.title('🏃‍♂️ Controle de Corridas')

aba = st.sidebar.radio("Escolha uma opção:", ["Adicionar Corrida", "Alterar Corrida", "Listagem Completa"])

df = carregar_dados()

if aba == "Adicionar Corrida":
    st.header("➕ Adicionar Corrida")
    with st.form("form_adicionar"):
        data = st.date_input("Data da corrida", value=None)
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
        opcoes_corridas = df['Corrida'] + ' - ' + pd.to_datetime(df['Data']).dt.strftime('%Y-%m-%d')
        corrida_escolhida = st.selectbox("Selecione a corrida", options=[""] + opcoes_corridas.tolist())

        if corrida_escolhida:
            idx = df[opcoes_corridas == corrida_escolhida].index[0]

            with st.form("form_alterar"):
                data = st.date_input("Data da corrida", value=pd.to_datetime(df.at[idx, 'Data']))
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

    # Seletor de distância para melhores tempos
    st.subheader("🏅 Melhores Tempos por Distância")
    distancias_disponiveis = sorted(df['Distância'].dropna().unique())
    distancia_selecionada = st.selectbox("Selecione a distância (km)", options=distancias_disponiveis)

    if distancia_selecionada:
        df['Tempo_td'] = df['Tempo'].apply(converter_tempo)
        melhores_df = df[(df['Distância'] == distancia_selecionada) & (~df['Tempo_td'].isna())]
        if not melhores_df.empty:
            melhor = melhores_df.sort_values(by='Tempo_td').iloc[0]
            tempo_formatado = melhor['Tempo']
            corrida = melhor['Corrida']
            data = pd.to_datetime(melhor['Data']).strftime('%d/%m/%Y')
            st.success(f"🏁 Melhor tempo para {int(distancia_selecionada)} km: {tempo_formatado} — {corrida} em {data}")
        else:
            st.warning("Nenhum tempo registrado para esta distância.")

    st.download_button(
        label="📥 Baixar dados em Excel",
        data=gerar_excel_download(df.drop(columns='Tempo_td', errors='ignore')),
        file_name="corridas_atualizado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
