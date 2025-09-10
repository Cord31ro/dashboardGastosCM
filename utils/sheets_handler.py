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
    return gc.open("Controle de Gastos CM").sheet1  # Nome da sua planilha

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