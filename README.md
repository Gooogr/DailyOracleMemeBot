# DailyOracleMemeBot

## Deploy

Create password for Minio UI proxy
```bash
chmod +x ./scripts/create_htpasswd.sh
./scripts/create_htpasswd.sh [username]
```
default `[username]` is `admin`

Run docker
```bash
docker compose -f docker-compose.prod.yaml up --build
```



