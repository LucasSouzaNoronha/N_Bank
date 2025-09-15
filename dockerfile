FROM python:3.9

WORKDIR /app

# Instala as dependências de sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo requirements.txt e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do seu código
COPY . .

# Expõe a porta
EXPOSE 5000
EXPOSE 5432

# Comando para iniciar sua aplicação
CMD ["gunicorn", "--max-requests", "200", "--bind", "0.0.0.0:5000", "site_nbank:app"]