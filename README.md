# DailyOracleMemeBot

## Deployment

### Environment Setup

Create the environment configuration file:
```bash
cp .env.example .env
```

### Log Rotation (Nginx Only)

All services use internal logging via `loguru`, except Nginx, which requires manual setup:

Make the config accessible for `crontab`:
```bash
sudo chown root:root docker/nginx/nginx_logrotate.conf
```

Edit the crontab:
```bash
crontab -e
```

Add the following entry:
```bash
0 0 * * * cd /full/path/to/DailyOracleMemeBot && /usr/sbin/logrotate -s /tmp/nginx-logrotate.status docker/nginx/nginx_logrotate.conf
```

### SSL Certificate

Generate a self-signed certificate:
```bash
chmod +x ./scripts/nginx/generate-cert.sh
./scripts/nginx/generate-cert.sh
```

### MinIO Webhook

Enable webhook integration:
```bash
chmod +x ./scripts/minio/minio_setup.sh
./scripts/minio/minio_setup.sh
```

### Start Services

Build and launch the project:
```bash
docker compose up --build
```

---

## Monitoring

### Production (VPS)

Create an SSH tunnel:
```bash
ssh -L 8443:localhost:443 your-user@your-vps-ip
```

Access services in your browser:
- MinIO: `https://localhost:8443/`
- Adminer: `https://localhost:8443/adminer`

**Note:** Ensure external access to port `443` is restricted on the VPS.

### Local Development

If using the production configuration locally:
- MinIO: `https://localhost:443/`
- Adminer: `https://localhost:443/adminer`

---

## Scripts

### Telegram Media Parser

Download media from a tg channel for a specific date range:
```bash
python3 scripts/tg_parser/main.py -s 2025-05-10 -e 2025-05-11
```

---

## TODO

- Add Alembic container for schema migrations  
- Implement fallback sync between MinIO and the Postgres `items` table  
- Store hashed `user_id` instead of raw integers (TBD)
