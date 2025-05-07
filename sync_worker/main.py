from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/events")
async def receive_minio_event(request: Request):
    payload = await request.json()
    print("[MINIO EVENT] Received:", payload)
    return {"status": "received"}
