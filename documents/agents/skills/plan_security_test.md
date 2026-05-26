# Skill: plan_security_test

## Quando usar
Quando o usuário solicitar um plano de testes de segurança para identificar vulnerabilidades e garantir a integridade dos dados e do sistema.

## Entrada
- `documents/03_architecture.md` (obrigatório)

## Passos
1. **Modelagem de Ameaças (STRIDE):** Aplicar o framework STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) para cada componente da arquitetura.
2. **Mapeamento OWASP:** Identificar quais itens do OWASP Top 10 são mais críticos para o tipo de aplicação (Web/API/Data).
3. **Definição de Testes Automatizados:**
    - SAST: Bandit (Python).
    - SCA: Trivy (Imagens/Dependências).
    - DAST: ZAP (Web Dashboard).
    - Secret Scan: Gitleaks.
    - Cloud Posture: Prowler (AWS/GCP context).
4. **Documentação de Casos de Teste:** Criar IDs no formato `TC-SEC-NN`.

## Saída
Arquivo `documents/06_test_plan_security.md`.

## Critérios de Aceitação
- Aplicação de STRIDE em todos os componentes principais.
- Inclusão de ao menos uma ferramenta para cada categoria (SAST, SCA, DAST, etc).
- Mapeamento claro com o OWASP Top 10.
