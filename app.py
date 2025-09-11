import streamlit as st
import plotly.express as px
import pandas as pd
from utils.sheets_handler import carregar_dados, adicionar_gasto, testar_conexao

st.title("COMERCIAL MARTINS - Custos")

# ================================
# Formulário de novo gasto
# ================================
with st.form("novo_gasto"):
    col1, col2 = st.columns(2)
    with col1:
        # usuários fixos 
        usuario = st.selectbox("Usuário", ["Gutemberg Filho", "Eng Arthur Cordeiro", "Gutemberg Martins"])
        # categorias                                  
        categoria = st.selectbox(
            "Categoria",
            ["Alimentação", "Transporte", "Mão de obra", "Manutenção", 
             "Compra de Materiais", "Combustivel", "Motorista", "Outro"]
        )
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.01)
        descricao = st.text_input("Descrição")
    
    if st.form_submit_button("💾 Adicionar"):
        adicionar_gasto(categoria, valor, descricao, usuario)
        st.success("✅ Gasto adicionado!")
        st.rerun()

# ================================
# Dashboard
# ================================
st.subheader("📊 Dashboard")
dados = carregar_dados()

if not dados.empty:
    # -------------------------------
    # Gráfico de Pizza
    # -------------------------------
    fig = px.pie(dados, values='Valor', names='Categoria', title='Gastos por Categoria', hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Gráfico de Barras
    # -------------------------------
    fig_barras = px.bar(
        dados,
        x='Categoria',
        y='Valor',
        color='Categoria',
        title='Gastos por Categoria (Barras)',
        text_auto=True
    )
    st.plotly_chart(fig_barras, use_container_width=True)

    # -------------------------------
    # Gráficos de Linhas (Evolução no tempo)
    # -------------------------------
    if "Data" in dados.columns:
        try:
            # Converter para datetime
            dados['Data'] = pd.to_datetime(dados['Data'], errors='coerce')

            # === Evolução por Categoria (agrupado por dia) ===
            dados_cat = (
                dados.groupby([dados['Data'].dt.date, 'Categoria'], as_index=False)['Valor'].sum()
            )
            fig_linha_cat = px.line(
                dados_cat,
                x='Data',
                y='Valor',
                color='Categoria',
                markers=True,
                title='Evolução dos Gastos por Dia (por Categoria)'
            )
            st.plotly_chart(fig_linha_cat, use_container_width=True)

            # === Evolução Total Diária (independente da categoria) ===
            dados_total = (
                dados.groupby(dados['Data'].dt.date, as_index=False)['Valor'].sum()
            )
            fig_linha_total = px.line(
                dados_total,
                x='Data',
                y='Valor',
                markers=True,
                title='Evolução dos Gastos por Dia (Total Geral)'
            )
            st.plotly_chart(fig_linha_total, use_container_width=True)

        except Exception as e:
            st.warning(f"⚠️ Não foi possível gerar os gráficos de linhas: {e}")
    else:
        st.info("Nenhuma coluna de 'Data' encontrada na planilha.")
else:
    st.info("Nenhum gasto cadastrado ainda.")

# ================================
# Botão de teste de conexão
# ================================
if st.button("Atualizar"):
    testar_conexao()
