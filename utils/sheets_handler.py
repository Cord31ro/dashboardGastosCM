import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import streamlit as st

def conectar_sheets():
    # Credenciais via Streamlit secrets
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(credentials)
    
    # Use o ID da planilha
    SHEET_ID = "1X3hlEP44hNAl1RxrQi2Ak9MbkenmHlAM5fIKfVfACuQ"
    return gc.open_by_key(SHEET_ID).sheet1

def carregar_dados():
    sheet = conectar_sheets()
    dados = sheet.get_all_records()
    return pd.DataFrame(dados)

def adicionar_gasto(categoria, valor, descricao, usuario):
    sheet = conectar_sheets()
    from datetime import datetime
    
    nova_linha = [
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        usuario,
        categoria, 
        valor,
        descricao
    ]
    sheet.append_row(nova_linha)

def testar_conexao():
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", 
                   "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(credentials)
        
        # Lista todas as planilhas que o service account pode ver
        planilhas = gc.list_spreadsheet_files()
        st.write("Planilhas encontradas:")
        for p in planilhas:
            st.write(f"- {p['name']}")
            
    except Exception as e:
        st.error(f"Erro: {e}")