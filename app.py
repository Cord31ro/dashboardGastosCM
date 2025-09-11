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
            [ "Alimentação", "Transporte", "Mão de obra", "Manutenção",
             "Compra de Materiais", "Combustivel",
               "Motorista", "Tijolo", "Outro", "Cimento", "Brita", "Canaleta", ]
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

    # ================================
    # VALOR TOTAL GASTO
    # ================================
    valor_total = dados['Valor'].sum()
    
    # Exibir valor total em destaque
    col1, col2, col3 = st.columns(3)
    with col2:  # Coluna central para centralizar
        st.metric(
            label="💰 TOTAL GASTO", 
            value=f"R$ {valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        )
    
    st.divider()  # Linha separadora

    # ================================
    # RESUMO POR CATEGORIA E USUÁRIO
    # ================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Total por Categoria")
        gastos_categoria = dados.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)
        for categoria, valor in gastos_categoria.items():
            valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            st.write(f"**{categoria}:** {valor_formatado}")
    
    with col2:
        st.subheader("👤 Total por Usuário")
        if 'Usuario' in dados.columns or 'Usuário' in dados.columns:
            usuario_col = 'Usuario' if 'Usuario' in dados.columns else 'Usuário'
            gastos_usuario = dados.groupby(usuario_col)['Valor'].sum().sort_values(ascending=False)
            for usuario, valor in gastos_usuario.items():
                valor_formatado = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                st.write(f"**{usuario}:** {valor_formatado}")

    st.divider()

    # ================================
    # GRÁFICOS
    # ================================
    
    # Pizza
    fig = px.pie(dados, values='Valor', names='Categoria', title='Gastos por Categoria', hole=0.3)
    st.plotly_chart(fig, use_container_width=True)

    # Barras
    fig_barras = px.bar(dados, x='Categoria', y='Valor', color='Categoria',
                        title='Gastos por Categoria (Barras)', text_auto=True)
    fig_barras.update_layout(xaxis_tickangle=-45)  # Inclina os rótulos do eixo X
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

            # Gráfico de linha acumulativo
            dados_acumulativo = dados_total.copy()
            dados_acumulativo['Valor_Acumulado'] = dados_acumulativo['Valor'].cumsum()
            
            fig_acumulativo = px.line(
                dados_acumulativo,
                x='Dia',
                y='Valor_Acumulado',
                markers=True,
                title='Gastos Acumulados ao Longo do Tempo'
            )
            fig_acumulativo.update_layout(xaxis_title='Data', yaxis_title='Valor Acumulado (R$)')
            st.plotly_chart(fig_acumulativo, use_container_width=True)

        except Exception as e:
            st.warning(f"⚠️ Não foi possível gerar os gráficos de linhas: {e}")
    else:
        st.info("Nenhuma coluna de 'Data' encontrada na planilha. Adicione datas para usar o gráfico de evolução.")

    # ================================
    # TABELA DE GASTOS RECENTES
    # ================================
    st.subheader("📋 Últimos Gastos")
    if 'Data' in dados.columns:
        dados_recentes = dados.sort_values('Data', ascending=False).head(10)
    else:
        dados_recentes = dados.tail(10)
    
    st.dataframe(dados_recentes, use_container_width=True)

else:
    st.info("Nenhum gasto cadastrado ainda.")

if st.button("Atualizar"):
    testar_conexao()