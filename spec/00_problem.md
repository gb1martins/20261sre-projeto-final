# Engenharia de Requisitos: Problema Northwind (Modelo SWEBOK)

Este documento aplica os princípios da Engenharia de Requisitos do SWEBOK para formalizar o problema de processamento de dados do Northwind.

## 1. Elicitação de Requisitos

### 1.1 Stakeholders e Expectativas
| Stakeholder | Expectativa Principal | Fonte de Requisitos |
|:---|:---|:---|
| **Negócio (Business Owners)** | Decisões baseadas em indicadores financeiros confiáveis. | Reuniões de Planejamento Estratégico |
| **Time de Dados (DE/DA)** | Pipeline estável, testável e de fácil manutenção. | Padrões Internos de Engenharia |
| **Clientes Internos** | KPIs disponíveis no início da jornada de trabalho (D-1). | Acordos de Nível de Serviço (SLA) |
| **Plataforma / SRE** | Infraestrutura resiliente e custo-eficiente. | Diretrizes de Infraestrutura Cloud |

### 1.2 Contexto de Negócio
O Northwind requer um fluxo de dados diário para monitorar KPIs de vendas e operação. A confiança nos números é o pilar para o uso do dashboard; sem integridade de dados, o sistema perde sua utilidade estratégica.

---

## 2. Análise de Requisitos

### 2.1 Fronteiras do Sistema
- **In-Scope:** Ingestão de arquivos CSV da fonte Northwind, transformações ETL, carga no Banco Analítico, atualização do Dashboard e monitoramento de integridade.
- **Out-of-Scope:** Limpeza de dados na fonte de origem, geração de relatórios manuais e suporte a dashboards de terceiros.

### 2.2 Análise de Conflitos
- **Integridade vs. Latência:** O rigor na validação de dados (quarentena) pode atrasar a carga. *Resolução: Priorizar integridade (Must-have).*
- **Custo vs. Performance:** Processamento em tempo real vs. processamento em lote diário. *Resolução: Processamento diário às 03:00 AM para otimização de custo.*

### 2.3 Decomposição do Problema
1. **Sub-problema de Ingestão:** Garantir o transporte seguro dos dados brutos.
2. **Sub-problema de Transformação:** Converter dados brutos em modelos dimensionais (Star Schema).
3. **Sub-problema de Distribuição:** Disponibilizar dados para consumo final (Dashboard).

---

## 3. Especificação de Riscos e Modos de Falha (FMEA)

| Modo de Falha | Causa Potencial | Efeito no Negócio | Severidade |
|:---|:---|:---|:---|
| **Dados Incompletos** | Falha na extração da origem | Dashboards com valores subestimados | Alta |
| **Duplicação de Dados** | Falha na idempotência do ETL | Inflação artificial de KPIs (vendas duplicadas) | Crítica |
| **Schema Drift** | Mudança no CSV de origem | Quebra total do pipeline | Média |
| **Stale Data** | Atraso no processamento | Decisões baseadas no dia anterior (D-2) | Alta |

---

## 4. Validação de Requisitos e Critérios de Sucesso

O sistema será considerado validado quando:
1. **Reconciliação:** O número de pedidos no dashboard for idêntico ao número de pedidos no arquivo de origem (D-1).
2. **Disponibilidade:** O dashboard estiver atualizado até as 08:00 AM.
3. **Auditabilidade:** Todo registro em quarentena for rastreável a um motivo técnico/negócio.
4. **Resiliência:** O sistema recuperar-se automaticamente de falhas transitórias de infraestrutura.
