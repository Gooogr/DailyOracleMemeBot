#!/bin/bash

# Script to install apache2-utils and create a basic auth password file for Nginx

set -e

# Configuration
USERNAME=${1:-admin}
HTPASSWD_FILE="./docker/nginx/prod/htpasswd.users"

# Install apache2-utils if not installed
if ! command -v htpasswd &> /dev/null; then
  echo "Installing apache2-utils..."
  sudo apt update && sudo apt install -y apache2-utils
fi

# Create password file (will overwrite if it already exists)
echo "Creating htpasswd file at $HTPASSWD_FILE for user $USERNAME"
mkdir -p "$(dirname "$HTPASSWD_FILE")"
htpasswd -c "$HTPASSWD_FILE" "$USERNAME"

echo "Done. Make sure to mount $HTPASSWD_FILE into your nginx container."
