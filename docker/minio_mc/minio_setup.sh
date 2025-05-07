#!/bin/sh
set -e

echo "[minio-setup] Waiting for minio:9000 to be available..."
while ! (echo > /dev/tcp/minio/9000) >/dev/null 2>&1; do
  echo "[minio-setup] Still waiting for minio:9000..."
  sleep 2
done

echo "[minio-setup] Waiting for MinIO API to respond via mc..."
until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" && mc ls local > /dev/null 2>&1; do
  echo "[minio-setup] MinIO not ready inside mc, retrying..."
  sleep 2
done

echo "[minio-setup] Creating bucket if it doesn't exist..."
if ! mc ls local/"$MINIO_BUCKET_NAME" > /dev/null 2>&1; then
  mc mb local/"$MINIO_BUCKET_NAME"
  echo "[minio-setup] Bucket created: $MINIO_BUCKET_NAME"
else
  echo "[minio-setup] Bucket already exists."
fi

echo "[minio-setup] Waiting for sync-worker to listen on port 9000..."
while ! (echo > /dev/tcp/sync-worker/9000) >/dev/null 2>&1; do
  echo "[minio-setup] Still waiting for sync-worker:9000..."
  sleep 2
done

echo "[minio-setup] Setting webhook target 'sync'..."
mc admin config set local notify_webhook:sync endpoint="http://sync-worker:9000/events" --env || echo "[minio-setup] Webhook config already applied?"

echo "[minio-setup] Checking if webhook is already registered..."
if mc event list local/"$MINIO_BUCKET_NAME" | grep -q "arn:minio:sqs::sync:webhook"; then
  echo "[minio-setup] Webhook already registered. Skipping."
else
  echo "[minio-setup] Registering webhook..."
  mc event add local/"$MINIO_BUCKET_NAME" arn:minio:sqs::sync:webhook --event put,delete
  echo "[minio-setup] Webhook registration complete."
fi


echo "[minio-setup] Done."
