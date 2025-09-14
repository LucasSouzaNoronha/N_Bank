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

# Comando para iniciar sua aplicação
CMD ["python", "site_nbank.py", "--host=0.0.0.0", "--port=5000"]