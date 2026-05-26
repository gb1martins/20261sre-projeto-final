# Plano de Testes de Segurança (Security Test Plan)

Este plano aplica modelagem de ameaças e define testes automatizados para garantir a segurança do ambiente Northwind.

## 1. Modelagem de Ameaças (STRIDE)

| Componente | S (Spoofing) | T (Tampering) | R (Repudiation) | I (Info Disclosure) | D (DoS) | E (Elevation of Priv) |
|:---|:---|:---|:---|:---|:---|:---|
| **MinIO** | Acesso não autorizado ao bucket. | Alteração de CSVs brutos. | Falta de log de quem deletou arquivo. | Exposição de dados sensíveis em buckets públicos. | Inundação de requisições de upload. | Uso de chaves `minioadmin` em produção. |
| **ETL Engine** | Injeção de código via arquivos maliciosos. | Modificação do script de transformação. | Falta de logs de execução. | Vazamento de credenciais em logs. | Loop infinito por arquivo corrompido. | Execução do container como root. |
| **ClickHouse** | Conexão sem senha ou senha padrão. | SQL Injection via dashboard. | Falta de auditoria de queries. | Acesso direto às tabelas silver/gold. | Queries complexas que travam o banco. | Usuário 'northwind' com permissões de 'admin'. |
| **Streamlit** | Sequestro de sessão. | Injeção de scripts no frontend. | - | Exposição de metadados de conexão. | Exaustão de conexões via botnet. | - |

## 2. OWASP Top 10 Aplicáveis
- **A01:2021-Broken Access Control:** Crítico para o console do MinIO e Dashboard.
- **A03:2021-Injection:** SQL Injection no ClickHouse via filtros do dashboard.
- **A05:2021-Security Misconfiguration:** Uso de credenciais padrão (`minioadmin`).
- **A07:2021-Identification and Authentication Failures:** Falta de MFA ou políticas de senha.

## 3. Casos de Teste (TC-SEC)

| ID | Tipo | Ferramenta | Descrição |
|:---|:---|:---|:---|
| **TC-SEC-01** | SAST | Bandit | Varredura estática no código do `etl.py` para detectar vulnerabilidades Python. |
| **TC-SEC-02** | SCA | Trivy | Análise de vulnerabilidades em bibliotecas do `requirements.txt` e camadas da imagem Docker. |
| **TC-SEC-03** | DAST | OWASP ZAP | Teste dinâmico no dashboard Streamlit para detectar XSS e falhas de sessão. |
| **TC-SEC-04** | Secrets | Gitleaks | Varredura no histórico do Git para garantir que nenhuma chave S3/DB foi commitada. |
| **TC-SEC-05** | Posture | Prowler | (Se em Cloud) Validação de conformidade das políticas de IAM e Buckets S3. |
