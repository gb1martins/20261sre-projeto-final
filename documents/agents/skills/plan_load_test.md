# Skill: plan_load_test

## Quando usar
Quando o usuário solicitar um plano de testes de carga para validar a escalabilidade, estabilidade e resiliência do sistema.

## Entrada
- `documents/03_architecture.md` (obrigatório)
- `documents/02_non_functional_requirements.md` (obrigatório)

## Passos
1. **Identificação de Pontos Críticos:** Identificar os componentes da arquitetura que sofrem maior pressão (Ingestão, Banco de Dados, Dashboard).
2. **Definição de Cenários:** Criar cenários de Load, Soak, Spike e Stress.
3. **Parametrização:** Para cada cenário, definir:
    - Hipótese: O que o teste tenta provar.
    - Ferramenta: Definir k6 como padrão.
    - Volume: Quantidade de usuários/requisições.
    - Duração: Tempo de execução.
    - Métrica de Sucesso: Limiares de erro, latência ou throughput.
4. **Mapeamento RNF:** Associar cada cenário a um requisito não-funcional de desempenho ou confiabilidade.

## Saída
Arquivo `documents/05_test_plan_load.md`.

## Critérios de Aceitação
- Deve conter os 4 tipos de teste (Load, Soak, Spike, Stress).
- Todos os campos obrigatórios por cenário devem estar preenchidos.
- Alinhamento direto com os SLOs descritos nos RNFs.
