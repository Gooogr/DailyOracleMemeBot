FROM python:3.11-slim

WORKDIR /src

# Install system tools
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir fastapi uvicorn[standard] python-dotenv

# Copy app code
COPY ./sync_worker /src/sync_worker
COPY ./app /src/app


# Set PYTHONPATH and run FastAPI app
ENV PYTHONPATH="/src"

CMD ["uvicorn", "sync_worker.main:app", "--host", "0.0.0.0", "--port", "9000"]
