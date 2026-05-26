# Northwind Data Pipeline & Analytics

Este projeto implementa um pipeline de dados Medallion (Bronze, Silver, Gold) utilizando ferramentas modernas de Engenharia de Dados e SRE.

## Arquitetura

O sistema é composto pelos seguintes componentes:
- **MinIO:** Object Storage (S3-compatible) para a camada Bronze (Raw Data).
- **ClickHouse:** DW Analítico de alta performance para as camadas Silver e Gold.
- **Apache Airflow:** Orquestrador para agendamento e monitoramento do ETL.
- **Streamlit:** Dashboard para visualização de KPIs.
- **Python:** Linguagem base para os scripts de ETL.

## Como Executar

1.  **Subir o ambiente:**
    ```bash
    docker-compose up -d
    ```

2.  **Acessar as Ferramentas:**
    *   **Airflow (Orquestração):** `http://localhost:8081` (Usuário: `airflow`, Senha: `airflow`)
    *   **Streamlit (Dashboard):** `http://localhost:8501`
    *   **MinIO (Storage):** `http://localhost:9001` (Usuário: `minioadmin`, Senha: `minioadmin`)
    *   **ClickHouse (Analytics):** `http://localhost:8123/play`

3.  **Executar o Pipeline:**
    *   Acesse o Airflow.
    *   Ative a DAG `northwind_medallion_pipeline`.
    *   Dispare manualmente para processar os dados iniciais.

## Estrutura do Projeto

- `/app`: Contém os scripts de ETL e a aplicação Streamlit.
- `/data`: Arquivos CSV de origem (Northwind).
- `/dags`: Definição dos pipelines do Airflow.
- `/documents`: Documentação detalhada de requisitos, arquitetura e testes.
