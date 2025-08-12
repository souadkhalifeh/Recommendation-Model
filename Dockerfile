FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8080

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python setup_models.py

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 app:app
