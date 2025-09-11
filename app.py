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
        usuario = st.selectbox("Usuário", ["Gutemberg Filho", "Eng Arthur Cordeiro", "Gutemberg Martins"])
        categoria = st.selectbox(
            "Categoria",
            ["Alimentação", "Transporte", "Mão de obra", "Manutenção",
             "Compra de Materiais", "Combustivel", "Motorista", "Tijolo", "Outro"]
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
    # normaliza nomes de colunas (remove espaços)
    dados.columns = dados.columns.str.strip()

    # garante que Valor é numérico
    if 'Valor' in dados.columns:
        dados['Valor'] = pd.to_numeric(dados['Valor'], errors='coerce')
        dados = dados.dropna(subset=['Valor'])

    # Pizza
    fig = px.pie(dados, values='Valor', names='Categoria', title='Gastos por Categoria', hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

    # Barras
    fig_barras = px.bar(dados, x='Categoria', y='Valor', color='Categoria',
                        title='Gastos por Categoria (Barras)', text_auto=True)
    st.plotly_chart(fig_barras, use_container_width=True)

    # Linhas (agrupado por dia)
    if 'Data' in dados.columns:
        try:
            # converter Data para datetime e remover valores inválidos
            dados['Data'] = pd.to_datetime(dados['Data'], errors='coerce')
            dados = dados.dropna(subset=['Data'])

            # criar coluna 'Dia' sem hora (datetime em meia-noite)
            dados['Dia'] = dados['Data'].dt.normalize()

            # agrupamento por dia + categoria (gera colunas: Dia, Categoria, Valor)
            dados_cat = dados.groupby(['Dia', 'Categoria'], as_index=False)['Valor'].sum()
            dados_cat = dados_cat.sort_values('Dia')

            fig_linha_cat = px.line(
                dados_cat,
                x='Dia',
                y='Valor',
                color='Categoria',
                markers=True,
                title='Evolução dos Gastos por Dia (por Categoria)'
            )
            fig_linha_cat.update_layout(xaxis_title='Data')
            st.plotly_chart(fig_linha_cat, use_container_width=True)

            # total diário (independente da categoria)
            dados_total = dados.groupby('Dia', as_index=False)['Valor'].sum().sort_values('Dia')

            fig_linha_total = px.line(
                dados_total,
                x='Dia',
                y='Valor',
                markers=True,
                title='Evolução dos Gastos por Dia (Total Geral)'
            )
            fig_linha_total.update_layout(xaxis_title='Data')
            st.plotly_chart(fig_linha_total, use_container_width=True)

        except Exception as e:
            st.warning(f"⚠️ Não foi possível gerar os gráficos de linhas: {e}")
    else:
        st.info("Nenhuma coluna de 'Data' encontrada na planilha. Adicione datas para usar o gráfico de evolução.")
else:
    st.info("Nenhum gasto cadastrado ainda.")

if st.button("Atualizar"):
    testar_conexao()