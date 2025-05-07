FROM python:3.11-slim

WORKDIR /src

RUN apt-get update && apt-get install -y curl netcat-openbsd && \
    curl -sSL https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

RUN pip install --no-cache-dir fastapi uvicorn[standard] minio psycopg2-binary sqlalchemy python-dotenv


COPY ./sync_worker /src/sync_worker
COPY ./app /src/app

# Add shell script to auto-setup webhook
COPY ./scripts/minio/setup_webhook.sh /src/sync_worker/setup_and_run.sh
RUN chmod +x /src/sync_worker/setup_and_run.sh

ENV PYTHONPATH="/src"

# Entrypoint is defined in docker-compose
