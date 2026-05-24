# Skill: elicit_rnf

## Quando usar
Quando o usuário pedir Requisitos Não-Funcionais (RNFs) e já existir `spec/00_problem.md` e/ou `documents/02_non_functional_requirements.md`.

## Entrada
- `spec/00_problem.md` (obrigatório)
- `documents/02_non_functional_requirements.md` (obrigatório)

## Passos
1. **Análise de Contexto:** Ler stakeholders e fluxos críticos descritos no problema.
2. **Mapeamento ISO 25010:** Mapear cada fluxo crítico e modo de falha aos 8 atributos da ISO/IEC 25010:
   - Adequação Funcional
   - Eficiência de Desempenho
   - Compatibilidade
   - Usabilidade
   - Confiabilidade
   - Segurança
   - Manutenibilidade
   - Portabilidade
3. **Definição de Requisitos:** Para cada atributo, propor de 1 a 3 RNFs com SLI (Service Level Indicator) mensurável.
4. **Priorização:** Marcar a prioridade utilizando o método MoSCoW (Must, Should, Could, Won't).
5. **Formalização de Métricas:** Listar premissas e fontes de medição (ex: Logs, Prometheus, AWS CloudWatch).

## Saída
Arquivo `documents/02_non_functional_requirements.md` contendo:
- Seção detalhada por atributo ISO 25010.
- IDs únicos no formato `RNF-NN`.
- Tabela final consolidada com as colunas: `ID`, `Atributo`, `SLI`, `SLO`, `Fonte de Medição`, `Prioridade`.

## Critérios de Aceitação
- Todos os 8 atributos da ISO 25010 devem estar cobertos.
- Todo RNF deve ter uma **unidade** (ex: ms, %, registros) e uma **janela de tempo** (ex: diário, mensal, p95).
- Proibido o uso de termos aspiracionais ou subjetivos (ex: "ser confiável", "ser rápido", "fácil de usar").
