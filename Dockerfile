# dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_MODULE=email_service.main:app \
    HOST=0.0.0.0 \
    PORT=8081 \
    WEB_CONCURRENCY=1 \
    PYTHONPATH=/app:/app/src \
    TIMEOUT=60 \
    KEEP_ALIVE=5 \
    GRACEFUL_TIMEOUT=30 \
    MAX_REQUESTS=1000 \
    MAX_REQUESTS_JITTER=100

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8081

CMD ["sh", "-c", "exec gunicorn ${APP_MODULE} -k uvicorn.workers.UvicornWorker --bind ${HOST}:${PORT} --workers ${WEB_CONCURRENCY} --timeout ${TIMEOUT:-60} --keep-alive ${KEEP_ALIVE:-5} --graceful-timeout ${GRACEFUL_TIMEOUT:-30} --max-requests ${MAX_REQUESTS:-1000} --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} --access-logfile - --error-logfile -"]
