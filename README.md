# DailyOracleMemeBot

## Deploy

Create self-signed certificate
```bash
chmod +x ./scripts/nginx/generate-cert.sh
./scripts/nginx/generate-cert.sh
```

Run docker
```bash
docker compose -f docker-compose.prod.yaml up --build
```

How to open minio admin panel
```bash
ssh -L 8443:localhost:443 your-user@your-vps-ip
https://localhost:8443/
```

So basically we:
Browser → localhost:8443 → SSH tunnel → VPS localhost:443 → Nginx HTTPS → MinIO Console

## Scripts

### `tg_parser` <br>
Download Telegram channel media by date range.

`python3 scripts/tg_parser/parser.py -s 2025-05-10 -e 2025-05-11`
