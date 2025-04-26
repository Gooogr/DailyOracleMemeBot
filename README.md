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


TODO:
- add self-signed certificate
- use ssh + VPS localhost 443 listening 
- use iptables to close ports except local host
