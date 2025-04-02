
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# Caminho do arquivo Excel
EXCEL_FILE = 'Corridas Mauricio.xlsx'
SHEET_NAME = 'Planilha1'

# Carrega os dados
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Data', 'Corridas', 'Tempo', 'Distância (km)'])
    return df

def salvar_dados(df):
    df.to_excel(EXCEL_FILE, sheet_name=SHEET_NAME, index=False)

def gerar_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

st.title('🏃‍♂️ Controle de Corridas')

aba = st.sidebar.radio("Escolha uma opção:", ["Adicionar Corrida", "Alterar Corrida", "Listagem Completa"])

df = carregar_dados()

if aba == "Adicionar Corrida":
    st.header("➕ Adicionar Corrida")
    with st.form("form_adicionar"):
        data = st.date_input("Data da corrida", value=datetime.today())
        nome = st.text_input("Nome da corrida")
        tempo = st.text_input("Tempo (hh:mm:ss)")
        distancia = st.number_input("Distância (km)", min_value=1, step=1)
        enviar = st.form_submit_button("Salvar")

        if enviar:
            nova_corrida = {
                'Data': data,
                'Corridas': nome,
                'Tempo': tempo,
                'Distância (km)': distancia
            }
            df = pd.concat([df, pd.DataFrame([nova_corrida])], ignore_index=True)
            salvar_dados(df)
            st.success("Corrida adicionada com sucesso!")

elif aba == "Alterar Corrida":
    st.header("✏️ Alterar Corrida")
    if df.empty:
        st.warning("Nenhuma corrida cadastrada.")
    else:
        corrida_escolhida = st.selectbox(
            "Escolha a corrida para editar:",
            df['Corridas'] + ' - ' + pd.to_datetime(df['Data']).dt.strftime('%Y-%m-%d')
        )
        idx = df[df['Corridas'] + ' - ' + pd.to_datetime(df['Data']).dt.strftime('%Y-%m-%d') == corrida_escolhida].index[0]

        with st.form("form_alterar"):
            data = st.date_input("Data da corrida", value=pd.to_datetime(df.at[idx, 'Data']))
            nome = st.text_input("Nome da corrida", value=df.at[idx, 'Corridas'])
            tempo = st.text_input("Tempo (hh:mm:ss)", value=df.at[idx, 'Tempo'])
            distancia = st.number_input("Distância (km)", min_value=1, step=1, value=int(df.at[idx, 'Distância (km)']))
            atualizar = st.form_submit_button("Atualizar")

            if atualizar:
                df.at[idx, 'Data'] = data
                df.at[idx, 'Corridas'] = nome
                df.at[idx, 'Tempo'] = tempo
                df.at[idx, 'Distância (km)'] = distancia
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
