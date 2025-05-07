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

# ✅ Start FastAPI in background
echo "[sync-worker] Starting FastAPI in background..."
uvicorn sync_worker.main:app --host 0.0.0.0 --port 9000 &
uvicorn_pid=$!

# ✅ Wait for FastAPI to start listening
echo "[sync-worker] Waiting for FastAPI to accept connections..."
until nc -z localhost 9000; do
  echo "[sync-worker] Waiting for local FastAPI on port 9000..."
  sleep 1
done

# ✅ Now MinIO can successfully connect to the webhook
echo "[sync-worker] Configuring webhook target 'sync'"
mc admin config set local notify_webhook:sync endpoint="http://sync-worker:9000/events" --env

#echo "[sync-worker] Restarting MinIO to apply webhook config"
#mc admin service restart local --quiet

echo "[sync-worker] Registering webhook on bucket: $MINIO_BUCKET_NAME"
mc event add local/"$MINIO_BUCKET_NAME" arn:minio:sqs::sync:webhook --event put,delete

# ✅ Wait for FastAPI to finish (keep the container running)
echo "[sync-worker] Setup complete. Waiting for FastAPI server to exit..."
wait $uvicorn_pid
