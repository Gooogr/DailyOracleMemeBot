# DailyOracleMemeBot

## Deploy

Create self-signed certificate
```bash
chmod +x ./scripts/nginx/generate-cert.sh
./scripts/nginx/generate-cert.sh
```

Enable minio webhook setup script
```bash
chmod +x ./scripts/minio/minio_setup.sh
```

Run docker
```bash
docker compose -f docker-compose.prod.yaml up --build
```

How to open admin panels
```bash
ssh -L 8443:localhost:443 your-user@your-vps-ip
```
Minio UI: `https://localhost:8443/`
Adminer: `https://localhost:8443/adminer`

Or if you run prod config locally:
```bash
https://localhost:443/
```
Minio UI: `https://localhost:443/`
Adminer: `https://localhost:443/adminer`

So basically we:
Browser → localhost:8443 → SSH tunnel → VPS localhost:443 → Nginx HTTPS → MinIO Console

Make sure that 443 is closed for connection on the VPS side.

TODO:
- Sync minio storage with the Items tables after start (?)
- Add logging of user intercations with tg bot with the Intercations table
- Use snake_128 for hashing user/item ids: https://stackoverflow.com/a/62699124

Хранить и имя файла, и его хеш из minioS3
Тогда не будет проблем с тем, что имя может быть как из хеша, так и просто забито рукаи
