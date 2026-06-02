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
| **Batch Processing** | ✅ Implementado | **Solução:** Implementação de Micro-batching via processamento em chunks (10k linhas) usando `pandas` e streams do S3. Evita o carregamento de arquivos gigantes na RAM. |
| **Concurrency Management**| ✅ Implementado | **Solução:** Paralelismo nas tasks da DAG para as camadas Bronze e Silver (Orders e Details). Reduz o tempo total de execução ao processar tabelas independentes simultaneamente. |

## 3. Segurança (Security)
*Foco: Resistir a ataques e proteger a integridade dos dados financeiros.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Limit Exposure** | ✅ Implementado | Uso de redes internas Docker. Serviços como ClickHouse e MinIO não expõem suas portas de administração diretamente sem mapeamento explícito. |
| **Authenticate Actors** | ✅ Implementado | Uso de credenciais fortes via ENV. Separação de identidades para Airflow, ClickHouse e MinIO. |
| **Authorize Actors** | ✅ Implementado | **Solução:** Criação do usuário `streamlit_ro` via script de init SQL com privilégios limitados (`GRANT SELECT`). Dashboard desacoplado do usuário admin do ETL. |

## 4. Testabilidade (Testability)
*Foco: Facilitar a descoberta de falhas antes da produção.*

| Tática (Bass) | Implementação no Projeto | Observação Técnica (SRE) |
|:--- |:--- |:--- |
| **Instrumentation** | ✅ Implementado | Logs detalhados em todas as camadas (Bronze, Silver, Gold). O Airflow atua como painel de controle da instrumentação. |
| **Separate Interface** | ✅ Implementado | A lógica de ETL (`app/etl.py`) está desacoplada da orquestração (`dags/`), permitindo testes isolados da lógica de negócio. |
| **Unit Testing** | ✅ Implementado | **Solução:** Encapsulamento da fórmula de Receita Líquida em `business_logic.py` e criação de suíte de testes unitários com `unittest`. |

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
2.  **Manutenção de Testes Unitários:** Expandir a suíte de testes unitários para cobrir novas métricas financeiras.
3.  **Refinar Autorização:** Implementar o princípio do privilégio mínimo para o usuário do Dashboard.

**Data da Revisão:** 31 de Maio de 2026
**Auditor:** Gemini CLI Agent (Revisão QA Completa)
**Referência:** [Len Bass - Software Architecture in Practice, 4th Edition](https://afonsolelis.github.io/cloud_sre/aulas/aula_05_integracao_etl_serverless_e_catalogo_de_dados/material/material_aula_05_integracao_etl_serverless_e_catalogo_de_dados.html)

---

### 🚀 Detalhamento: Concurrency Management (Item 2)

**Solução Adotada:**
Refatoração do script `app/etl.py` para granularizar as funções de processamento (`process_bronze_file`, `process_silver_orders`, `process_silver_order_details`) e reestruturação da DAG `northwind_medallion_pipeline` para executar a ingestão e transformação das tabelas `Orders` e `Order Details` em paralelo.

**Justificativa Técnica:**
Tabelas independentes na origem não possuem dependências de dados entre si até a camada Gold (agregação). Utilizar o agendador do Airflow para gerenciar a execução concorrente dessas tasks otimiza o uso de recursos e reduz o tempo de ociosidade do pipeline.

**Benefícios:**
*   **Redução de Latência:** O tempo total do pipeline (E2E) é reduzido, pois as tarefas de I/O intensivo (S3) e processamento (Pandas) ocorrem simultaneamente.
*   **Escalabilidade:** Prepara o sistema para suportar mais tabelas no futuro sem aumentar linearmente o tempo de execução total.

---

### 📦 Detalhamento: Batch Processing (Item 2)

**Solução Adotada:**
Implementação de processamento em chunks (Micro-batching) no script `app/etl.py`. Ao invés de ler o arquivo CSV inteiro para a memória, utilizamos o parâmetro `chunksize` do `pandas` e consumimos o stream diretamente do S3 (MinIO). Os dados são processados e inseridos no ClickHouse em lotes de 10.000 linhas.

**Justificativa Técnica:**
O carregamento de arquivos CSV grandes (Big Data) em memória RAM pode causar falhas por `OutOfMemory (OOM)` no container de execução. O uso de iteradores e chunks garante que a pegada de memória permaneça constante, independentemente do tamanho do arquivo de entrada.

**Benefícios:**
*   **Escalabilidade Linear:** O pipeline agora pode processar arquivos de GBs de tamanho com a mesma quantidade de memória RAM (aprox. 200MB-500MB).
*   **Estabilidade:** Reduz o risco de crash do processo de ETL por falta de recursos.

**Riscos:**
*   **Fragmentação no ClickHouse:** Inserções muito pequenas e frequentes podem gerar muitos "parts" no ClickHouse. O chunk de 10.000 linhas foi escolhido para equilibrar uso de RAM e eficiência do MergeTree.

**Trade-offs:**
*   **Tempo de CPU vs. RAM:** O processamento em chunks pode ser levemente mais lento em termos de CPU devido ao overhead de múltiplas chamadas de insert, mas é infinitamente mais seguro em termos de disponibilidade (RAM).

**Status da Implementação:** ✅ **Finalizado**

---

### 🔐 Detalhamento: Authorize Actors (Item 3)

**Solução Adotada:**
Criação de um usuário exclusivo para leitura (`streamlit_ro`) no ClickHouse. A implementação utiliza um script de inicialização SQL (`clickhouse_init.sql`) montado no container via Docker Volumes. O Dashboard Streamlit foi reconfigurado para utilizar estas credenciais restritas ao invés da conta administrativa do pipeline de ETL.

**Justificativa Técnica:**
Seguindo o princípio do **Menor Privilégio (Least Privilege)** de Len Bass, um ator que necessita apenas visualizar dados (Dashboard) não deve possuir permissões de escrita ou deleção (`DROP`, `TRUNCATE`, `INSERT`). Isso mitiga o risco de ataques de injeção SQL ou erros operacionais que poderiam comprometer a integridade dos dados na camada de Analytics.

**Benefícios:**
*   **Segurança Reforçada:** Caso o container do Dashboard seja comprometido, o atacante terá acesso apenas de leitura, impossibilitando a destruição de dados.
*   **Auditabilidade:** Permite distinguir nos logs do ClickHouse quais consultas originaram do Dashboard e quais vieram do processo de ETL.
*   **Isolamento de Credenciais:** As senhas do processo de ingestão (escrita) e do dashboard (leitura) são independentes.

**Riscos:**
*   **Gestão de Credenciais:** Adiciona um novo par de usuário/senha para ser gerenciado e rotacionado.

**Trade-offs:**
*   **Segurança vs. Simplicidade:** Requer um passo adicional de configuração (script SQL e ENV extras), mas o ganho em postura de segurança justifica a pequena complexidade operacional.

**Status da Implementação:** ✅ **Finalizado**

---

### 🧪 Detalhamento: Unit Testing (Item 4)

**Solução Adotada:**
Desacoplamento da lógica de cálculo financeiro da camada de banco de dados através da criação do módulo `app/business_logic.py`. Implementação de uma suíte de testes unitários em `tests/test_business_logic.py` utilizando o framework `unittest`. Os testes validam a fórmula de **Receita Líquida** em diversos cenários (sem desconto, desconto total, arredondamento e tratamento de erros).

**Justificativa Técnica:**
Cálculos de KPIs são o coração de um sistema de Analytics. Validá-los apenas via SQL (integração) é complexo e lento. A tática de **Unit Testing** de Len Bass permite garantir a correção matemática da lógica de negócio de forma isolada, rápida e repetível, sem depender da infraestrutura (ClickHouse) estar ativa.

**Benefícios:**
*   **Confiabilidade do KPI:** Garantia de que a fórmula de Receita Líquida (base de todas as agregações Gold) está correta.
*   **Documentação Executável:** Os testes servem como especificação da regra de negócio.
*   **Facilidade de Refatoração:** Alterações na lógica podem ser validadas instantaneamente.

**Riscos:**
*   **Divergência Código/SQL:** Existe o risco da lógica no Python (testada) divergir da implementação no SQL (produção). Recomendação: No futuro, migrar para uma ferramenta de transformação que utilize a mesma definição para ambos (ex: dbt ou UDFs).

**Trade-offs:**
*   **Esforço de Manutenção:** Requer manter o código de teste e a lógica em Python, além da implementação SQL, mas reduz drasticamente o tempo de depuração de erros de cálculo.

**Status da Implementação:** ✅ **Finalizado**
