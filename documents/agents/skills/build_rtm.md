# Skill: build_rtm

## Quando usar
Quando o usuário solicitar a criação ou atualização da Matriz de Rastreabilidade de Requisitos (RTM), garantindo que as necessidades de negócio estejam mapeadas para componentes da arquitetura e casos de teste.

## Entrada
- `documents/01_functional_requirements.md` (obrigatório)
- `documents/02_non_functional_requirements.md` (obrigatório)
- `documents/03_architecture.md` (obrigatório)

## Passos
1. **Coleta de Requisitos:** Listar todos os IDs de RFs e RNFs dos documentos de requisitos.
2. **Mapeamento de Componentes:** Para cada requisito, identificar na Visão Computacional ou de Engenharia da `03_architecture.md` qual componente (ou componentes) é responsável por atendê-lo.
3. **Definição de Casos de Teste:** Criar ou referenciar um identificador de caso de teste (ex: `CT-NN`) que valide o requisito de forma objetiva.
4. **Verificação de Status:**
    - Definir como `Coberto` se houver um Componente associado **E** um Caso de Teste definido/implementado.
    - Definir como `Aberto` se faltar Componente ou Caso de Teste.
5. **Consolidação:** Organizar as informações em uma tabela Markdown.

## Saída
Arquivo `documents/04_rtm.md` contendo:
- Tabela com as colunas: `Req`, `Tipo`, `Origem`, `Componente`, `Caso de teste`, `Status`.
- Resumo estatístico ao final: Total de requisitos, quantos estão abertos e quantos estão cobertos.

## Critérios de Aceitação
- **Totalidade:** 100% dos requisitos listados em `01_functional_requirements.md` e `02_non_functional_requirements.md` devem estar na matriz.
- **Rastreabilidade Bidirecional:** Deve ser possível identificar qual documento de origem gerou o requisito.
- **Precisão:** O componente mapeado deve ter relação técnica direta com a funcionalidade do requisito.
- **Clareza de Status:** Requisitos sem validação explícita não podem ser marcados como cobertos.
