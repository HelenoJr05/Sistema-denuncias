FROM python:3.11-slim

# Versão da aplicação (injetada pelo pipeline de CD; "dev" em builds locais)
ARG APP_VERSION=dev

LABEL org.opencontainers.image.title="sistema-denuncias" \
      org.opencontainers.image.version="${APP_VERSION}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION} \
    DENUNCIAS_FILE=/data/denuncias.json

WORKDIR /app

# Dependências primeiro: aproveita o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Apenas o que a aplicação precisa em runtime
COPY main.py .
COPY templates ./templates

# Usuário sem privilégios + diretório de dados persistente
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data
USER appuser

VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
