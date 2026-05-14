#!/usr/bin/env bash
# Subsequent-deploy helper. Run as the `jontraderlar` user.
#
#   sudo -u jontraderlar /opt/jontraderlar/deploy/deploy.sh
#
# It pulls the latest code, refreshes dependencies, and restarts both
# systemd units. The restart itself is fast — Telegram retries on
# transient failures, so a few seconds of downtime is fine.

set -euo pipefail

APP_DIR="/opt/jontraderlar"
VENV="${APP_DIR}/.venv"

cd "${APP_DIR}"

echo "→ Pulling latest code..."
git pull --ff-only

echo "→ Updating Python dependencies..."
"${VENV}/bin/pip" install --upgrade pip
"${VENV}/bin/pip" install -e .

echo "→ Restarting services..."
sudo systemctl restart jontraderlar-bot jontraderlar-worker

echo "→ Status:"
sudo systemctl status --no-pager --lines=5 jontraderlar-bot jontraderlar-worker

echo "✓ Deploy complete."
