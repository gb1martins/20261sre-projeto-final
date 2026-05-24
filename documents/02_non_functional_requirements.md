# Requisitos Não-Funcionais (RNF) e SLO/SLI

Este documento define as metas de nível de serviço (SLO), indicadores (SLI) e requisitos de qualidade baseados na norma **ISO/IEC 25010** para o pipeline de dados Northwind.

## 1. Adequação Funcional (Functional Suitability)
Garantir que o sistema forneça as funções que atendam às necessidades declaradas e implícitas.
- **RNF-01 (Integridade de Dados):** O sistema deve garantir que nenhum registro seja perdido ou duplicado durante o ETL.
- **SLI:** Porcentagem de registros na origem vs. destino após processamento.
- **SLO:** 100% de reconciliação de contagem de registros diariamente.

## 2. Eficiência de Desempenho (Performance Efficiency)
Desempenho em relação à quantidade de recursos utilizados.
- **RNF-02 (Tempo de Processamento):** O pipeline completo (Ingestão ao Dashboard) deve ser concluído dentro de uma janela específica.
- **SLI:** Tempo total de execução do pipeline (End-to-End Latency).
- **SLO:** Execução completa em menos de 2 horas para volumes de até 1 milhão de registros/dia.

## 3. Compatibilidade (Compatibility)
Capacidade de trocar informações com outros sistemas.
- **RNF-03 (Interoperabilidade):** O sistema deve ser capaz de ler arquivos CSV/JSON do Northwind e exportar para PostgreSQL/BigQuery.
- **SLI:** Taxa de sucesso de conexões com conectores de entrada/saída.
- **SLO:** > 99.9% de sucesso em tentativas de conexão.

## 4. Usabilidade (Usability)
Facilidade de uso e aprendizado para os usuários finais.
- **RNF-04 (Operabilidade do Dashboard):** O dashboard deve carregar visualizações críticas em tempo satisfatório.
- **SLI:** Tempo de carregamento da página principal do dashboard.
- **SLO:** < 3 segundos para 95% das requisições (p95).

## 5. Confiabilidade (Reliability)
Capacidade de manter o nível de desempenho sob condições estabelecidas.
- **RNF-05 (Disponibilidade dos Dados):** Os dados processados devem estar disponíveis para consulta no horário acordado.
- **SLI:** Disponibilidade do dado atualizado (Freshness).
- **SLO:** Dados de D-1 disponíveis até as 08:00 AM em 99% dos dias do mês.
- **RNF-06 (Recuperabilidade):** O pipeline deve suportar re-execuções (backfill) de forma idempotente.
- **SLO:** Sucesso em 100% das tentativas de reprocessamento manual sem duplicação de dados.

## 6. Segurança (Security)
Proteção de informações e dados.
- **RNF-07 (Integridade e Acesso):** Apenas usuários autorizados podem acessar os dados brutos e o dashboard.
- **SLI:** Taxa de acessos não autorizados bloqueados.
- **SLO:** 0 (zero) incidentes de acesso a dados sem autenticação/autorização devida.

## 7. Manutenibilidade (Maintainability)
Facilidade de modificação e evolução do sistema.
- **RNF-08 (Testabilidade):** Todo novo código de transformação deve possuir testes unitários e de integração.
- **SLI:** Cobertura de código (Code Coverage).
- **SLO:** > 80% de cobertura de testes nas camadas de transformação de dados.
- **RNF-09 (Observabilidade):** O sistema deve gerar logs e métricas detalhadas de cada etapa do pipeline.
- **SLO:** 100% das falhas críticas devem gerar alertas em tempo real (< 5 min).

## 8. Portabilidade (Portability)
Facilidade de transferir o sistema de um ambiente para outro.
- **RNF-10 (Adaptabilidade):** O pipeline deve ser executável em ambiente local (Docker) e em nuvem (AWS/GCP).
- **SLO:** Tempo de configuração de um novo ambiente de desenvolvimento < 30 minutos.

---

## Premissas
1. O volume de dados diário do Northwind não excederá 10GB na fase inicial.
2. A infraestrutura de rede entre a fonte de dados e o ambiente de processamento é estável.
3. As janelas de manutenção do banco analítico não coincidirão com o horário crítico de processamento (02:00 AM - 08:00 AM).
4. O esquema dos arquivos de origem (Northwind) é estável, e mudanças serão comunicadas com antecedência.
