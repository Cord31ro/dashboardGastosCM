import streamlit as st
import plotly.express as px
from utils.sheets_handler import carregar_dados, adicionar_gasto

st.title("💰 Controle de Gastos")

# Formulário
with st.form("novo_gasto"):
    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Nome")
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer"])
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.01)
        descricao = st.text_input("Descrição")
    
    if st.form_submit_button("💾 Adicionar"):
        adicionar_gasto(categoria, valor, descricao, usuario)
        st.success("✅ Gasto adicionado!")
        st.experimental_rerun()

# Dashboard
st.subheader("📊 Dashboard")
dados = carregar_dados()

if not dados.empty:
    fig = px.pie(dados, values='Valor', names='Categoria', title='Gastos por Categoria')
    st.plotly_chart(fig)
else:
    st.info("Nenhum gasto cadastrado ainda.")