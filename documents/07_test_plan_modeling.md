# Análise de Modelagem Arquitetural (ATAM)

Este documento apresenta uma análise enxuta do framework ATAM (Architecture Tradeoff Analysis Method) sobre a arquitetura do projeto Northwind.

## 1. Utility Tree & Cenários

Baseado nos RNFs da `02_non_functional_requirements.md`:

| Atributo | Cenário | Classificação | Justificativa |
|:---|:---|:---|:---|
| **Confiabilidade** | O pipeline deve ser idempotente em caso de falha (RNF-06). | **Sensibilidade** | A lógica de "Clean/Drop" na camada Silver é sensível para garantir a integridade sem duplicidade. |
| **Performance** | Carregar 1M de registros em menos de 2h (RNF-02). | **Trade-off** | O uso de ClickHouse favorece a escrita/leitura rápida, mas exige recursos de memória (Trade-off: Memória vs. Velocidade). |
| **Segurança** | 0 incidentes de acesso não autorizado (RNF-07). | **Risco** | O uso de credenciais `minioadmin` em containers docker-compose representa um risco alto de segurança se exposto. |
| **Disponibilidade** | Dados de D-1 disponíveis até as 08:00 AM (RNF-05). | **Sensibilidade** | Depende diretamente da estabilidade do orquestrador e da latência da rede com o MinIO. |
| **Portabilidade** | Execução em Docker Local e Nuvem em < 30min (RNF-10). | **Trade-off** | A portabilidade simplifica o dev, mas pode ocultar diferenças de performance entre ambientes (Trade-off: Simplicidade vs. Fidelidade). |

## 2. Análise de Riscos e Trade-offs

- **Risco [R1]:** Credenciais hardcoded em variáveis de ambiente no `docker-compose.yml`. Se o repositório for público, as chaves do MinIO e ClickHouse estão expostas.
- **Sensibilidade [S1]:** A performance das visões na camada Gold é altamente sensível ao volume de dados na camada Silver. O uso de `MergeTree` no ClickHouse é vital.
- **Trade-off [T1]:** **ClickHouse vs Postgres.** Escolheu-se o ClickHouse pela performance analítica (OLAP), sacrificando a facilidade de realizar updates/deletes individuais que o Postgres (OLTP) permitiria.
- **Trade-off [T2]:** **MinIO vs Local Files.** O uso de MinIO adiciona uma camada de complexidade (S3 API), mas garante escalabilidade e paridade com ambiente de produção em nuvem.
