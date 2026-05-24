import streamlit as st
import clickhouse_connect
import os

st.set_page_config(page_title="Northwind Dashboard", layout="wide")

st.title("🚀 Northwind Analytics Dashboard")

# Configurações de conexão
CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CH_USER = os.getenv("CLICKHOUSE_USER", "default")
CH_PASS = os.getenv("CLICKHOUSE_PASSWORD", "")

@st.cache_resource
def get_client():
    try:
        return clickhouse_connect.get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASS)
    except Exception as e:
        st.error(f"Erro ao conectar no ClickHouse: {e}")
        return None

client = get_client()

if client:
    st.success("Conectado ao ClickHouse!")
    
    # Exemplo de consulta
    try:
        tables = client.query("SHOW TABLES").result_rows
        st.sidebar.write("### Tabelas Disponíveis")
        for table in tables:
            st.sidebar.code(table[0])
            
        st.info("Aguardando dados serem carregados pelo ETL...")
    except Exception as e:
        st.error(f"Erro ao executar query: {e}")
else:
    st.warning("Verifique se o serviço ClickHouse está rodando.")
