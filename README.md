# DailyOracleMemeBot

## Deployment

Generate self-signed certificate:
```bash
chmod +x ./scripts/nginx/generate-cert.sh
./scripts/nginx/generate-cert.sh
```

Enable MinIO webhook setup:
```bash
chmod +x ./scripts/minio/minio_setup.sh
```

Create configuration files:
- `.env` based on `.env.example`
- `authorized-testers.yaml` based on `authorized-testers.yaml.example` (grants access to developer-only handlers and bypasses limits)

Build and start the project:
```bash
docker compose -f docker-compose.yaml up --build
```

## Monitoring

### Production (VPS)

Create an SSH tunnel:
```bash
ssh -L 8443:localhost:443 your-user@your-vps-ip
```

Access via browser:
- MinIO: `https://localhost:8443/`
- Adminer: `https://localhost:8443/adminer`

Ensure port `443` is blocked from external access on the VPS.

### Local Development

If running the production config locally:
- MinIO: `https://localhost:443/`
- Adminer: `https://localhost:443/adminer`

## Scripts

### Telegram Parser

Download media from a Telegram channel within a date range:
```bash
python3 scripts/tg_parser/main.py -s 2025-05-10 -e 2025-05-11
```

## TODO
- Enforce one object per user per day

## Technical Debt
- Add Alembic container for migrations
- Add fallback sync script between MinIO and Postgres `items` table
- Add video support (currently supports only photos)
- Store hashed `user_id` instead of raw integer