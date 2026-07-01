# ============================================
# Dockerfile - 智善TIC人才测评系统
# ============================================
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
FROM python:3.12-slim-bookworm
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8080
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_data; gunicorn config.wsgi --log-file - --bind 0.0.0.0:${PORT:-8080}"]
# Redeploy 20260623095625

