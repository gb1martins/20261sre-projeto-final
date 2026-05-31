# Revisão Arquitetural: Táticas de Len Bass (Northwind Medallion Pipeline)

Este documento apresenta uma revisão detalhada e completa da arquitetura do projeto Northwind, fundamentada nas **Táticas Arquiteturais de Len Bass** (4ª Edição), conforme as diretrizes de SRE e Cloud Computing.

---

## 1. Disponibilidade (Availability)
*Foco: Manter o sistema operacional e recuperar-se de falhas críticas.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Ping/Echo / Heartbeat** | ✅ Implementado | `healthcheck` rigoroso no `docker-compose.yml` para todos os serviços. O `airflow-scheduler` só inicia o pipeline quando MinIO, ClickHouse e Postgres estão `healthy`. |
| **Retry** | ✅ Implementado | Configurado na DAG do Airflow. Falhas de rede transitórias entre o Ingestor e o MinIO são mitigadas por retentativas automáticas com backoff. |
| **Idempotency** | ✅ Implementado | Tática central: O ETL utiliza `DROP TABLE IF EXISTS` ou `TRUNCATE` antes da carga. Garante que o estado final seja consistente mesmo após múltiplas falhas e reinícios. |
| **Circuit Breaker** | ❌ Lacuna | **Ponto Crítico:** O pipeline não "abre o circuito" se o ClickHouse estiver lento ou instável, o que pode causar um efeito cascata de consumo de CPU/Memória no host. |
| **Exception Handling** | ✅ Implementado | Blocos `try-except` capturam erros de esquema e conexão, gerando logs estruturados para diagnóstico rápido. |

## 2. Desempenho (Performance)
*Foco: Gerenciar latência (tempo de resposta) e throughput (vazão de dados).*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Cache** | ✅ Implementado | `@st.cache_resource` e `@st.cache_data` no Streamlit. Reduz o tráfego de rede e a carga no ClickHouse para consultas repetitivas de KPI. |
| **Increase Resources** | ✅ Implementado | Escolha do ClickHouse como motor OLAP. Tática de "Vertical Scaling" implícita na performance colunar para grandes agregações (Net Revenue). |
| **Batch Processing** | ⚠️ Parcial | O processamento é feito em arquivos completos (CSV). Para escalas maiores, a tática de "Micro-batching" ou processamento em chunks no Pandas/Polars seria necessária. |
| **Concurrency Management**| ❌ Lacuna | O Ingestor Python é single-process. Para aumentar o throughput, poderia ser utilizada a tática de paralelismo nas tasks da DAG (Ingestão de Orders e Details em paralelo). |

## 3. Segurança (Security)
*Foco: Resistir a ataques e proteger a integridade dos dados financeiros.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Limit Exposure** | ✅ Implementado | Uso de redes internas Docker. Serviços como ClickHouse e MinIO não expõem suas portas de administração diretamente sem mapeamento explícito. |
| **Authenticate Actors** | ✅ Implementado | Uso de credenciais fortes via ENV. Separação de identidades para Airflow, ClickHouse e MinIO. |
| **Authorize Actors** | ⚠️ Parcial | Atualmente utiliza usuários admin. Recomendação: Criar um usuário `read-only` no ClickHouse exclusivo para o Dashboard Streamlit. |

## 4. Testabilidade (Testability)
*Foco: Facilitar a descoberta de falhas antes da produção.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Instrumentation** | ✅ Implementado | Logs detalhados em todas as camadas (Bronze, Silver, Gold). O Airflow atua como painel de controle da instrumentação. |
| **Separate Interface** | ✅ Implementado | A lógica de ETL (`app/etl.py`) está desacoplada da orquestração (`dags/`), permitindo testes isolados da lógica de negócio. |
| **Unit Testing** | ❌ Lacuna | Falta de testes unitários para a fórmula de **Receita Líquida**. É uma tática de Len Bass essencial para garantir a correção de transformações complexas. |

## 5. Modificabilidade (Modifiability)
*Foco: Reduzir o custo de mudança (Schema Drift, novos KPIs).*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Schema-on-Read** | ✅ Implementado | A Camada Bronze (MinIO) aceita qualquer arquivo. A validação só ocorre na Silver, permitindo que a origem mude sem quebrar o storage. |
| **Encapsulate** | ✅ Implementado | As conexões S3 e ClickHouse estão encapsuladas em funções auxiliares, facilitando a troca do provider de Cloud (ex: S3 para GCS). |
| **Abstract Common Services**| ✅ Implementado | O uso do Airflow abstrai a lógica de agendamento e dependência do código de negócio (ETL). |

## 6. Usabilidade (Usability)
*Foco: Facilitar a operação do sistema e o consumo dos KPIs.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Interactive Feedback** | ✅ Implementado | Streamlit fornece visualização imediata. O Airflow fornece feedback visual do progresso do pipeline. |
| **Error Message Clarity**| ✅ Implementado | Erros do ClickHouse e Python são expostos de forma clara para o operador via logs de task. |

---

### 🛡️ Cenários de Stress e Resiliência (Plano de Testes SRE)
Baseado na análise ATAM (Architecture Tradeoff Analysis Method), os seguintes cenários devem ser testados:

1.  **Cenário de Perda de Conectividade:** Derrubar o container `northwind_analytics` durante a task `aggregate_to_gold`. 
    *   *Tática esperada:* O Airflow deve aguardar e realizar o **Retry** conforme configurado.
2.  **Cenário de Dados Corrompidos:** Inserir um CSV com `Discount > 1` (desconto maior que 100%).
    *   *Tática esperada:* O Ingestor deve capturar a anomalia na camada Silver via **Exception Handling** ou quarentena.
3.  **Cenário de Reprocessamento:** Executar a DAG 3 vezes seguidas para o mesmo dia.
    *   *Tática esperada:* A **Idempotência** deve garantir que o faturamento total no Dashboard permaneça inalterado.

---

### 💡 Recomendações Prioritárias (Roadmap SRE)
1.  **Implementar Circuit Breaker:** Adicionar uma task de "Pre-flight Check" na DAG para validar a saúde dos bancos antes de iniciar o ETL.
2.  **Automatizar Testes Unitários:** Criar testes para a fórmula de Receita Líquida usando dados sintéticos (Mocking).
3.  **Refinar Autorização:** Implementar o princípio do privilégio mínimo para o usuário do Dashboard.

**Data da Revisão:** 31 de Maio de 2026
**Auditor:** Gemini CLI Agent (Revisão QA Completa)
**Referência:** [Len Bass - Software Architecture in Practice, 4th Edition](https://afonsolelis.github.io/cloud_sre/aulas/aula_05_integracao_etl_serverless_e_catalogo_de_dados/material/material_aula_05_integracao_etl_serverless_e_catalogo_de_dados.html)
