#!/usr/bin/env bash
# Copy the WebDAV deployment files to the Pi, do a clean rebuild, and confirm
# the running container is using the local nginx.conf.
# Usage: ./deploy.sh <user@host>
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: $0 <user@host>" >&2
  exit 1
fi

PI="$1"
REMOTE_DIR="webdav"

cd "$(dirname "$0")"

echo "==> Copying files to $PI:~/$REMOTE_DIR/"
scp Dockerfile nginx.conf docker-compose.yml "$PI:~/$REMOTE_DIR/"

# --no-cache: `up -d --build` can reuse a cached COPY layer and miss nginx.conf edits
echo "==> Rebuilding and restarting"
ssh "$PI" "cd ~/$REMOTE_DIR && docker compose down && docker compose build --no-cache && docker compose up -d"

echo "==> Checking the running config matches local nginx.conf"
if ssh "$PI" "cd ~/$REMOTE_DIR && docker compose exec -T webdav cat /etc/nginx/nginx.conf" | diff -q nginx.conf - >/dev/null; then
  echo "OK: container is running the current nginx.conf"
else
  echo "MISMATCH: container config differs from local nginx.conf" >&2
  exit 1
fi
