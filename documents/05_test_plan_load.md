# Plano de Testes de Carga (Load Test Plan)

Este documento descreve os cenários de teste de carga para validar a performance e resiliência do pipeline Northwind, conforme os requisitos de RNF-02 e RNF-04.

## Cenários de Teste

### 1. Load Test (Teste de Carga)
- **Hipótese:** O sistema suporta a carga nominal de 100 usuários simultâneos no dashboard sem degradar o tempo de resposta além do SLO.
- **Ferramenta:** k6
- **Volume:** 100 VUs (Virtual Users)
- **Duração:** 30 minutos
- **Métrica de Sucesso:** 95% das requisições (p95) < 3 segundos; Taxa de erro < 1%.
- **RNF Coberto:** RNF-04 (Operabilidade do Dashboard)

### 2. Soak Test (Teste de Resistência)
- **Hipótese:** O pipeline de ingestão e o banco ClickHouse mantêm a estabilidade e não apresentam vazamento de memória durante processamento contínuo.
- **Ferramenta:** k6 (estimulando ingestão via API se disponível ou consultas massivas)
- **Volume:** 50 VUs (consultas constantes)
- **Duração:** 8 horas
- **Métrica de Sucesso:** Estabilidade no consumo de RAM/CPU; Sem falhas de conexão com ClickHouse.
- **RNF Coberto:** RNF-05 (Disponibilidade dos Dados)

### 3. Spike Test (Teste de Pico)
- **Hipótese:** O sistema sobrevive a um aumento repentino de acessos no dashboard durante a abertura do mercado (início do expediente).
- **Ferramenta:** k6
- **Volume:** Salto de 10 para 500 VUs em 2 minutos.
- **Duração:** 10 minutos
- **Métrica de Sucesso:** Recuperação total após o pico; Nenhum crash no container do Dashboard.
- **RNF Coberto:** RNF-02 (Tempo de Processamento/Escalabilidade)

### 4. Stress Test (Teste de Estresse)
- **Hipótese:** Identificar o ponto de ruptura do ClickHouse e como o sistema se comporta sob carga extrema de ingestão concorrente com consultas.
- **Ferramenta:** k6
- **Volume:** Incremental até 2000 VUs.
- **Duração:** Até a exaustão de recursos.
- **Métrica de Sucesso:** Identificação clara do gargalo; Log de erro apropriado quando o limite for atingido.
- **RNF Coberto:** RNF-02 (Eficiência de Desempenho)
