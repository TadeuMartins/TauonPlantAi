FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
 && apt-get update && apt-get install -y tesseract-ocr \
 && rm -rf /var/lib/apt/lists/*

# Copiar o código
COPY . /app

# Garantir que o Python enxergue /app como raiz dos módulos
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app

EXPOSE 8000

# Rodar a API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

