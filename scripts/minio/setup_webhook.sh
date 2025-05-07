#!/bin/sh
set -e

echo "[sync-worker] Waiting for MinIO TCP socket on port 9000..."

until nc -z minio 9000; do
  echo "[sync-worker] Still waiting for minio:9000..."
  sleep 2
done

echo "[sync-worker] Waiting for MinIO to respond to mc..."

until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" && mc ls local > /dev/null 2>&1; do
  echo "[sync-worker] MinIO not ready inside mc, retrying..."
  sleep 2
done

echo "[sync-worker] Starting FastAPI in background..."
uvicorn sync_worker.main:app --host 0.0.0.0 --port 9000 &
uvicorn_pid=$!

echo "[sync-worker] Waiting for FastAPI to accept connections..."
until nc -z localhost 9000; do
  echo "[sync-worker] Waiting for local FastAPI on port 9000..."
  sleep 1
done

echo "[sync-worker] Configuring webhook target 'sync'"
mc admin config set local notify_webhook:sync endpoint="http://sync-worker:9000/events" --env

echo "[sync-worker] Ensuring bucket '$MINIO_BUCKET_NAME' exists..."
if ! mc ls local/"$MINIO_BUCKET_NAME" > /dev/null 2>&1; then
  echo "[sync-worker] Bucket does not exist. Creating..."
  mc mb local/"$MINIO_BUCKET_NAME"
else
  echo "[sync-worker] Bucket already exists."
fi

echo "[sync-worker] Checking existing events for bucket: $MINIO_BUCKET_NAME"
if mc event list local/"$MINIO_BUCKET_NAME" | grep -q "arn:minio:sqs::sync:webhook"; then
  echo "[sync-worker] Webhook already registered, skipping mc event add."
else
  echo "[sync-worker] Registering webhook on bucket: $MINIO_BUCKET_NAME"
  mc event add local/"$MINIO_BUCKET_NAME" arn:minio:sqs::sync:webhook --event put,delete
fi

# Wait for FastAPI to finish (keep the container running)
echo "[sync-worker] Setup complete. Waiting for FastAPI server to exit..."
wait $uvicorn_pid
