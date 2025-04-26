#!/bin/bash

NGINX_FOLDER_PATH='./docker/nginx/prod'

mkdir -p $NGINX_FOLDER_PATH/ssl
openssl req -x509 -nodes -days 365 \
  -subj "/CN=localhost" \
  -newkey rsa:2048 \
  -keyout $NGINX_FOLDER_PATH/ssl/nginx.key \
  -out $NGINX_FOLDER_PATH/ssl/nginx.crt
