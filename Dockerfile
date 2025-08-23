# ---- base Python slim (Debian) ----
FROM python:3.12-slim

# Evita .pyc e deixa logs “na hora”
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências de runtime p/ WeasyPrint + wget p/ healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
  wget \
  libcairo2 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf-2.0-0 \
  libffi-dev \
  libxml2 \
  libxslt1.1 \
  shared-mime-info \
  fonts-dejavu-core \
  fonts-liberation \
  && rm -rf /var/lib/apt/lists/*

# Melhor cache: requirements primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Pasta do SQLite
RUN mkdir -p /app/data

# Usuário não-root
RUN adduser --disabled-password --gecos '' appuser \
  && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Importante: com SQLite mantenha 1 worker
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
