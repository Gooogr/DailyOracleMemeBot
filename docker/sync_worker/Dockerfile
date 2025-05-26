FROM python:3.11-slim

# Ensure output is immediately flushed to the terminal
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/src"

WORKDIR /src

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY ./docker/sync_worker/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./sync_worker /src/sync_worker
COPY ./app /src/app


CMD ["uvicorn", "sync_worker.main:app", "--host", "0.0.0.0", "--port", "9000"]
