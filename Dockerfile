FROM python:3.11-slim

WORKDIR /app

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de dependências
# (Assumindo que criaremos o requirements.txt a seguir)
COPY requirements.txt .

# Instalação das bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

EXPOSE 8501

# O comando padrão será sobrescrito pelo docker-compose para cada serviço
