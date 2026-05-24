# Requisitos Funcionais (RF)

Este documento descreve as funcionalidades esperadas do sistema de processamento de dados Northwind.

| ID | Requisito | Ator | Prioridade |
|:---|:---|:---|:---|
| **RF-01** | Quando o agendador disparar às 03h, o ETL deve ingerir o arquivo CSV diário da fonte de dados (Northwind). | Agendador | Must |
| **RF-02** | O ETL deve aplicar normalização de schema antes de carregar os dados no banco analítico. | ETL | Must |
| **RF-03** | Se uma linha falhar na validação, o ETL deve persistir o registro em uma área de quarentena com o motivo da falha. | ETL | Must |
| **RF-04** | O sistema deve expor um banco analítico com um modelo dimensional (Fatos e Dimensões) mínimo para consulta. | Banco Analítico | Must |
| **RF-05** | O dashboard deve exibir os KPIs de crescimento (growth) e operação para a diretoria. | Dashboard | Must |
| **RF-06** | Em caso de re-execução (parcial ou total), o ETL deve ser idempotente, garantindo que não haja duplicação de registros. | ETL | Must |

---

## Detalhamento Adicional

- **RF-01 (Agendamento):** O disparo deve ser automático e monitorado.
- **RF-03 (Quarentena):** Registros em quarentena devem permitir análise posterior sem interromper o fluxo principal.
- **RF-06 (Idempotência):** Crucial para recuperação de falhas sem corromper a integridade dos dados históricos.
