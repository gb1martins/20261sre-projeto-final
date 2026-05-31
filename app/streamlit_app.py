import streamlit as st
import clickhouse_connect
import os
import pandas as pd

st.set_page_config(page_title="Northwind Medallion Dashboard", layout="wide")

st.title("🚀 Northwind Analytics Dashboard (Medallion Architecture)")

# Configurações de conexão
CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CH_USER = os.getenv("CLICKHOUSE_USER", "northwind")
CH_PASS = os.getenv("CLICKHOUSE_PASSWORD", "northwind")

@st.cache_resource
def get_client():
    try:
        return clickhouse_connect.get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASS)
    except Exception as e:
        st.error(f"Erro ao conectar no ClickHouse: {e}")
        return None

client = get_client()

if client:
    st.sidebar.success("Conectado ao ClickHouse!")
    
    # Sidebar: Navegação entre camadas
    layer = st.sidebar.selectbox("Selecione a Camada de Dados", ["Ouro (Business)", "Prata (Trusted)"])
    
    if layer == "Ouro (Business)":
        st.header("🏆 Camada Ouro - Métricas de Negócio")
        
        try:
            # KPI: Resumo Geral
            kpi_data = client.query("""
                SELECT 
                    round(sum(total_order_value), 2) as faturamento,
                    count(order_id) as total_pedidos,
                    round(avg(total_order_value), 2) as ticket_medio
                FROM gold_order_metrics
            """).result_rows[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Faturamento Total", f"$ {kpi_data[0]:,.2f}")
            col2.metric("Total de Pedidos", f"{kpi_data[1]}")
            col3.metric("Ticket Médio", f"$ {kpi_data[2]:,.2f}")
            
            # Gráficos de Negócio
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("🏆 Top 10 Produtos (Receita)")
                df_products = client.query_df("SELECT CAST(product_id AS String) as product_id, net_revenue FROM gold_product_ranking LIMIT 10")
                st.bar_chart(df_products.set_index('product_id'))
            
            with col_right:
                st.subheader("🌎 Vendas por País")
                df_country = client.query_df("SELECT ship_country, sum(total_order_value) as vendas FROM gold_order_metrics GROUP BY ship_country ORDER BY vendas DESC")
                st.bar_chart(df_country.set_index('ship_country'))

            st.subheader("📈 Evolução Mensal da Receita")
            df_monthly = client.query_df("SELECT month, net_revenue FROM gold_monthly_revenue ORDER BY month")
            st.line_chart(df_monthly.set_index('month'))
            
            # Tabela de Dados Gold
            st.subheader("📋 Detalhes dos Pedidos (Gold)")
            df_gold = client.query_df("SELECT * FROM gold_order_metrics LIMIT 100")
            st.dataframe(df_gold)
            
        except Exception as e:
            st.error(f"Erro ao carregar dados da Camada Ouro: {e}")
            st.info("Certifique-se de que o pipeline ETL foi executado.")

    else:
        st.header("🥈 Camada Prata - Dados Estruturados")
        table_silver = st.selectbox("Selecione a Tabela", ["silver_orders", "silver_order_details"])
        
        try:
            df_silver = client.query_df(f"SELECT * FROM {table_silver} LIMIT 100")
            st.dataframe(df_silver)
        except Exception as e:
            st.error(f"Erro ao carregar dados da Camada Prata: {e}")

else:
    st.warning("Verifique se o serviço ClickHouse está rodando.")
