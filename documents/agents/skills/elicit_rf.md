# Skill: elicit_rf

## Quando usar
Quando o usuário pedir Requisitos Funcionais (RFs) e já existir `spec/00_problem.md` e/ou `documents/01_functional_requirements.md`.

## Entrada
- `spec/00_problem.md` (obrigatório)
- `documents/01_functional_requirements.md` (obrigatório)

## Passos
1. **Análise de Fluxos:** Identificar os fluxos críticos e stakeholders descritos no problema.
2. **Decomposição:** Quebrar cada fluxo crítico em ações atômicas necessárias para sua realização.
3. **Identificação de Atores:** Determinar quem ou o quê (usuário, sistema, agendador, serviço externo) executa cada ação.
4. **Escrita de Requisitos:** Redigir os RFs seguindo o padrão: "O [Ator] deve [Ação] para que [Objetivo/Resultado]".
5. **Priorização:** Marcar a prioridade utilizando o método MoSCoW (Must, Should, Could, Won't).
6. **Definição de Critérios de Aceite:** Para cada RF, descrever brevemente como validar que ele foi atendido.

## Saída
Arquivo `documents/01_functional_requirements.md` contendo:
- Tabela consolidada com as colunas: `ID`, `Requisito`, `Ator`, `Prioridade`.
- Seção de detalhamento com Critérios de Aceite para cada ID.
- IDs únicos no formato `RF-NN`.

## Critérios de Aceitação
- Todos os fluxos críticos listados em `00_problem.md` devem ter ao menos um RF associado.
- Os requisitos devem ser **atômicos** (uma única ação clara por ID).
- **Independência de Ferramenta:** Não deve citar ferramentas específicas (ex: usar "Banco Analítico" em vez de "Postgres").
- Linguagem clara e testável.
