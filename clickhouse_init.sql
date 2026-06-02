-- Criação do usuário northwind para o ETL
CREATE USER IF NOT EXISTS northwind IDENTIFIED WITH sha256_password BY 'northwind';
GRANT SELECT, INSERT, ALTER, CREATE, DROP, TRUNCATE, OPTIMIZE, SHOW, SYSTEM ON *.* TO northwind WITH GRANT OPTION;

-- Criação de usuário read-only para o Dashboard Streamlit
CREATE USER IF NOT EXISTS streamlit_ro IDENTIFIED WITH sha256_password BY 'streamlit_ro_pass';
GRANT SELECT ON *.* TO streamlit_ro;
