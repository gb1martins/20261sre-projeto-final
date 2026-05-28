# Revisão Arquitetural: Táticas de Len Bass (Northwind Medallion Pipeline)

Este documento apresenta uma revisão detalhada da arquitetura do projeto Northwind, utilizando como framework as **Táticas Arquiteturais de Len Bass** (4ª Edição), conforme as diretrizes de SRE e Cloud Computing.

---

## 1. Disponibilidade (Availability)
*Foco: Manter o sistema operacional e recuperar-se de falhas.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica |
|:--- |:--- |:--- |
| **Ping/Echo / Heartbeat** | ✅ Implementado | Uso de `healthcheck` no `docker-compose.yml` para Postgres, Airflow, ClickHouse e MinIO. Garante que dependentes só subam após o serviço estar "saudável". |
| **Retry** | ✅ Implementado | Configurado via `default_args` na DAG do Airflow (`'retries': 1`, `'retry_delay': timedelta(minutes=5)`). Essencial para falhas de rede transitórias. |
| **Exception Handling** | ✅ Implementado | O script `etl.py` utiliza blocos `try-except` com `traceback.print_exc()` para capturar e logar falhas durante a execução. |
| **Idempotency** | ✅ Implementado | O pipeline utiliza a técnica de "Drop and Recreate" (e.g., `DROP TABLE IF EXISTS ...`) nas camadas Silver e Gold, permitindo re-execuções sem duplicidade de dados. |
| **Circuit Breaker** | ❌ Lacuna | Não há um mecanismo de interrupção para evitar que o Airflow continue tentando disparar o ETL caso o ClickHouse ou MinIO estejam persistentemente fora do ar. |
| **Fail-fast** | ✅ Implementado | O pipeline interrompe a execução imediatamente (`sys.exit` implícito no erro do Python Operator) se uma tarefa crítica falhar. |

## 2. Desempenho (Performance)
*Foco: Controlar a latência, throughput e eficiência de recursos.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica |
|:--- |:--- |:--- |
| **Cache** | ✅ Implementado | Uso do decorador `@st.cache_resource` no Streamlit para manter a conexão com o ClickHouse ativa e evitar reconexões desnecessárias. |
| **Manage Sampling Rate** | ❌ Não Aplicável | Dado o volume atual (Northwind CSV), não há necessidade de amostragem, mas seria uma tática para volumes de Terabytes. |
| **Maximize Throughput** | ⚠️ Parcial | O uso do ClickHouse (colunar) maximiza a vazão em queries analíticas, mas o processamento Python (Pandas) é single-threaded e pode ser um gargalo em volumes maiores. |

## 3. Segurança (Security)
*Foco: Proteger contra acesso não autorizado e garantir a integridade.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica |
|:--- |:--- |:--- |
| **Limit Exposure** | ✅ Implementado | Mapeamento de portas não convencionais (e.g., 9004 para o Native Interface do ClickHouse) e isolamento em rede Docker interna. |
| **Authenticate Actors** | ✅ Implementado | Credenciais configuradas via variáveis de ambiente para MinIO, ClickHouse e Airflow (RBAC). |
| **Authorize Actors** | ⚠️ Parcial | Uso de perfis padrão (admin). Falta granularidade de permissões (e.g., usuário de dashboard apenas com leitura na Gold). |

## 4. Testabilidade (Testability)
*Foco: Facilitar a descoberta de defeitos e validação de requisitos.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica |
|:--- |:--- |:--- |
| **Instrumentation** | ✅ Implementado | Logs detalhados emitidos pelo script Python e capturados pelo Airflow. Uso de metadados do Airflow para monitorar duração e status. |
| **Unit Testing** | ❌ Lacuna | Ausência de testes unitários (Pytest) para as funções de transformação (`process_silver`, `process_gold`). |
| **Integration Testing** | ✅ Implementado | Validado via execução ponta-a-ponta (E2E) no ambiente Docker, simulando o ciclo de vida completo do dado. |

## 5. Modificabilidade (Modifiability)
*Foco: Reduzir o custo e tempo de implementação de mudanças.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica |
|:--- |:--- |:--- |
| **Schema-on-read** | ✅ Implementado | A Camada Bronze armazena arquivos brutos no MinIO sem validação prévia de esquema, facilitando a ingestão de novos formatos. |
| **Encapsulate** | ⚠️ Parcial | A lógica de conexão está isolada em funções (`get_s3_client`, `get_clickhouse_client`), mas a lógica de transformação está acoplada ao esquema das tabelas. |

## 6. Usabilidade (Usability)
*Foco: Melhorar a experiência do usuário e do operador.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica |
|:--- |:--- |:--- |
| **Interactive Feedback** | ✅ Implementado | Streamlit fornece feedback visual (métricas, gráficos, dataframes) imediato sobre o estado dos dados. |
| **Error Message Clarity**| ✅ Implementado | Logs do Airflow e Streamlit expõem a causa raiz dos erros (e.g., falha de conexão ou arquivo ausente). |

---

### Conclusão e Recomendações SRE
A arquitetura atual é robusta para um MVP, demonstrando maturidade em **Disponibilidade** (Healthchecks e Retries) e **Desempenho** (ClickHouse). 

**Recomendações Prioritárias:**
1. **Circuit Breaker:** Implementar verificação de saúde antes de iniciar o processamento pesado na DAG.
2. **Secret Masking:** Garantir que credenciais sensíveis no Airflow sejam gerenciadas via *Secrets Backend* para evitar exposição em logs.
3. **Unit Tests:** Adicionar testes com dados sintéticos para garantir que mudanças no esquema não quebrem o pipeline.

**Data da Revisão:** 27 de Maio de 2026
**Auditor:** Gemini CLI Agent
**Referência:** [Material Aula 05 - Cloud SRE](https://afonsolelis.github.io/cloud_sre/aulas/aula_05_integracao_etl_serverless_e_catalogo_de_dados/material/material_aula_05_integracao_etl_serverless_e_catalogo_de_dados.html)
