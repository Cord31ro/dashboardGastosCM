import streamlit as st
import plotly.express as px
from utils.sheets_handler import carregar_dados, adicionar_gasto, testar_conexao

st.title("COMERCIAL MARTINS - Custos")

# Formulário
with st.form("novo_gasto"):
    col1, col2 = st.columns(2)
    with col1:
        #usuarios fixos 
        usuario = st.selectbox("Usuário", ["Gutemberg Filho", "Eng Arthur Cordeiro", "Gutemberg Martins", ])
          #categorias                                  
        categoria = st.selectbox("Categoria", ["Alimentação", "Transporte", "Mão de obra", "Manutenção", "Compra de Materiais", "Combustivel", "Motorista" ])
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.01)
        descricao = st.text_input("Descrição")
    
    if st.form_submit_button("💾 Adicionar"):
        adicionar_gasto(categoria, valor, descricao, usuario)
        st.success("✅ Gasto adicionado!")
        st.rerun()

# Dashboard
st.subheader("📊 Dashboard")
dados = carregar_dados()

if not dados.empty:
    fig = px.pie(dados, values='Valor', names='Categoria', title='Gastos por Categoria')
    st.plotly_chart(fig)

    # Gráfico de Barras
    fig_barras = px.bar(
        dados,
        x='Categoria',
        y='Valor',
        color='Categoria',
        title='Gastos por Categoria (Barras)',
        text_auto=True
    )

        # Gráfico de Linhas (se tiver datas registradas no seu Google Sheets)
    if 'Data' in dados.columns:  # só funciona se sua planilha tiver uma coluna de data
        fig_linha = px.line(
            dados,
            x='Data',
            y='Valor',
            color='Categoria',
            markers=True,
            title='Evolução dos Gastos ao Longo do Tempo'
        )

else:
    st.info("Nenhum gasto cadastrado ainda.")



# Teste de conexão
if st.button("Atualizar"):
    testar_conexao()