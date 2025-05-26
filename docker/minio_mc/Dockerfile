FROM python:3.11-slim AS base

RUN apt-get update && apt-get install -y curl grep bash && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

WORKDIR /scripts

COPY ./docker/minio_mc/minio_setup.sh /scripts/minio_setup.sh

ENTRYPOINT ["/bin/bash", "/scripts/minio_setup.sh"]
