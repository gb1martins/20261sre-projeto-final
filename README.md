# Northwind Data Pipeline & Analytics

Este projeto implementa um pipeline de dados Medallion (Bronze, Silver, Gold) utilizando ferramentas modernas de Engenharia de Dados e SRE.

## Arquitetura

O sistema é composto pelos seguintes componentes:
- **MinIO:** Object Storage (S3-compatible) para a camada Bronze (Raw Data).
- **ClickHouse:** DW Analítico de alta performance para as camadas Silver e Gold.
- **Apache Airflow:** Orquestrador para agendamento e monitoramento do ETL.
- **Streamlit:** Dashboard para visualização de KPIs.
- **OpenTelemetry & Jaeger:** Rastreamento distribuído (Tracing) para monitorar a execução do pipeline.
- **Prometheus:** Coleta e armazenamento de métricas de negócio e performance.
- **k6:** Ferramenta de testes de carga para validar requisitos não funcionais.

## Como Executar

1.  **Subir o ambiente:**
    ```bash
    docker-compose up -d --build
    ```

2.  **Acessar as Ferramentas:**
    *   **Airflow (Orquestração):** `http://localhost:8081` (Login: `airflow` / `airflow`)
    *   **Streamlit (Dashboard):** `http://localhost:8501`
    *   **MinIO (Storage):** `http://localhost:9001` (Login: `minioadmin` / `minioadmin`)
    *   **Prometheus (Métricas):** `http://localhost:9090`
    *   **Jaeger (Traces):** `http://localhost:16686`
    *   **ClickHouse:** `http://localhost:8123`

3.  **Executar Testes de Carga (k6):**
    ```bash
    # Teste de carga no Dashboard
    docker run --rm -v "${PWD}/tests/load:/scripts" grafana/k6 run /scripts/dashboard_load.js

    # Teste de carga no ClickHouse
    docker run --rm -v "${PWD}/tests/load:/scripts" grafana/k6 run /scripts/clickhouse_load.js
    ```

4.  **Observabilidade de Negócio:**
    As métricas de negócio (Receita e Pedidos) são enviadas via OpenTelemetry para o Prometheus. Consulte:
    - `business_revenue_USD_total`
    - `business_orders_count_total`

## Estrutura do Projeto

- `/app`: Scripts de ETL (instrumentados com OTel) e Streamlit.
- `/data`: Arquivos CSV de origem.
- `/dags`: Pipelines do Airflow.
- `/documents`: Documentação de requisitos, arquitetura e planos de teste.
- `/tests/load`: Scripts k6 para testes de performance.
