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

If you run prod config locally:
```bash
https://localhost:443/
```

So basically we:
Browser → localhost:8443 → SSH tunnel → VPS localhost:443 → Nginx HTTPS → MinIO Console

Make sure that 443 is closed for connection on the VPS side.

TODO:
- Add postgres tables schemes from start
- Add simple admin panel (Adminer)
- Sync minio storage with the Items tables (migrations?)
- Add logging of user intercations with tg bot with the Intercations table

```bash
PostgreSQL DB

Interactions
user_id 
item_id
intercation datetime

Items
item_id
type (img/video)
upload datetime
```

- Use snake_128 for hashing user/item ids: https://stackoverflow.com/a/62699124
