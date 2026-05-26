FROM apache/airflow:2.7.1-python3.11

USER root

# Instalação de dependências do sistema necessárias para ClickHouse e outras libs
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Streamlit
EXPOSE 8501
