import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request

from app.db.postgres.factory import PostgresItemRepositoryFactory
from app.db.postgres.provider import PostgresProvider
from sync_worker.event_handlers import MinioEventHandler
from sync_worker.event_models import MinioWebhookPayload

load_dotenv(dotenv_path="../.env")

app = FastAPI()

handler = MinioEventHandler(
    provider=PostgresProvider(
        user=os.getenv("POSTGRES_USER", ""),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        db=os.getenv("POSTGRES_DB", ""),
    ),
    item_repo_factory=PostgresItemRepositoryFactory(),
)


@app.post("/events")
async def receive_minio_event(request: Request):
    payload = await request.json()
    print("[MINIO EVENT] Received:", payload)
    data = MinioWebhookPayload(**payload)
    handler.handle_event(data)
    return {"status": "received"}
