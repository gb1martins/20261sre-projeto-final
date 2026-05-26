# Matriz de Rastreabilidade de Requisitos (RTM)

Este documento mapeia os requisitos funcionais (RF) e não-funcionais (RNF) para os componentes da arquitetura e seus respectivos casos de teste, garantindo a cobertura total do sistema conforme definido na skill `build_rtm`.

| Req | Tipo | Origem | Componente | Caso de teste | Status |
|:---|:---|:---|:---|:---|:---|
| RF-01 | Funcional | 01_functional_requirements.md | Orquestrador (Airflow/Cron) | CT-01: Verificação de disparo agendado às 03h | Aberto |
| RF-02 | Funcional | 01_functional_requirements.md | ETL Engine (Python) | CT-02: Validação de normalização de schema | Aberto |
| RF-03 | Funcional | 01_functional_requirements.md | ETL Engine (Python) | CT-03: Verificação de envio para quarentena | Aberto |
| RF-04 | Funcional | 01_functional_requirements.md | DW Engine (ClickHouse) | CT-04: Consulta ao modelo dimensional | Aberto |
| RF-05 | Funcional | 01_functional_requirements.md | Interface (Streamlit) | CT-05: Exibição de KPIs no Dashboard | Aberto |
| RF-06 | Funcional | 01_functional_requirements.md | ETL Engine (Python) | CT-06: Teste de re-execução sem duplicidade | Aberto |
| RNF-01 | Não-Funcional | 02_non_functional_requirements.md | ETL Engine / ClickHouse | CT-07: Reconciliação de contagem de registros | Aberto |
| RNF-02 | Não-Funcional | 02_non_functional_requirements.md | Pipeline (E2E) | CT-08: Medição de tempo de execução total | Aberto |
| RNF-03 | Não-Funcional | 02_non_functional_requirements.md | ETL Engine (Python) | CT-09: Teste de leitura CSV/JSON e escrita DB | Aberto |
| RNF-04 | Não-Funcional | 02_non_functional_requirements.md | Interface (Streamlit) | CT-10: Teste de latência de carregamento p95 | Aberto |
| RNF-05 | Não-Funcional | 02_non_functional_requirements.md | Orquestrador / DW | CT-11: Verificação de disponibilidade de dados às 08h | Aberto |
| RNF-06 | Não-Funcional | 02_non_functional_requirements.md | ETL Engine (Python) | CT-06: Teste de re-execução (Idempotência) | Aberto |
| RNF-07 | Não-Funcional | 02_non_functional_requirements.md | Infraestrutura (Docker/IAM) | CT-12: Teste de acesso não autorizado | Aberto |
| RNF-08 | Não-Funcional | 02_non_functional_requirements.md | Ciclo de Vida de Dev | CT-13: Validação de cobertura de testes > 80% | Aberto |
| RNF-09 | Não-Funcional | 02_non_functional_requirements.md | ETL / Orquestrador | CT-14: Verificação de geração de alertas | Aberto |
| RNF-10 | Não-Funcional | 02_non_functional_requirements.md | Infraestrutura (Docker) | CT-15: Teste de deploy em novo ambiente | Aberto |

---

**Resumo da Cobertura:**
- **Total de Requisitos:** 16
- **Requisitos Abertos:** 16
- **Requisitos Cobertos:** 0

*Nota: Os requisitos estão marcados como 'Aberto' pois, embora os componentes estejam definidos na arquitetura, os casos de teste ainda não possuem scripts de execução automatizados vinculados ao repositório para validação definitiva.*
