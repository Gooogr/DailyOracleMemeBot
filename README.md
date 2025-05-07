# DailyOracleMemeBot

## Deploy

Create self-signed certificate
```bash
chmod +x ./scripts/nginx/generate-cert.sh
./scripts/nginx/generate-cert.sh
```

Enable minio webhook setup script
```bash
chmod +x ./scripts/minio/setup_webhook.sh
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



sync_worker   | [MINIO EVENT] Received: {'EventName': 's3:ObjectCreated:Put', 'Key': 'test/MainBefore.jpg', 'Records': [{'eventVersion': '2.0', 'eventSource': 'minio:s3', 'awsRegion': '', 'eventTime': '2025-05-07T18:27:43.866Z', 'eventName': 's3:ObjectCreated:Put', 'userIdentity': {'principalId': 'user'}, 'requestParameters': {'principalId': 'user', 'region': '', 'sourceIPAddress': '172.19.0.1'}, 'responseElements': {'x-amz-id-2': 'dd9025bab4ad464b049177c95eb6ebf374d3b3fd1af9251148b658df7ac2e3e8', 'x-amz-request-id': '183D521117E888D8', 'x-minio-deployment-id': '8e4a0955-b0aa-444b-a62f-a74cd3d6c3a6', 'x-minio-origin-endpoint': 'http://172.19.0.3:9000'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'Config', 'bucket': {'name': 'test', 'ownerIdentity': {'principalId': 'user'}, 'arn': 'arn:aws:s3:::test'}, 'object': {'key': 'MainBefore.jpg', 'size': 46806, 'eTag': '43d35848b68212475fc4dbd100b3bc6c', 'contentType': 'image/jpeg', 'userMetadata': {'content-type': 'image/jpeg'}, 'sequencer': '183D5211182CED8E'}}, 'source': {'host': '172.19.0.1', 'port': '', 'userAgent': 'MinIO (linux; amd64) minio-go/v7.0.89 MinIO Console/(dev)'}}]}
