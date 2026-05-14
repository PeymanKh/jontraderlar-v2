#!/usr/bin/env bash
# Subsequent-deploy helper. Run as a sudo-capable user (e.g. peyman):
#
#   /opt/jontraderlar/jontraderlar-v2/deploy/deploy.sh
#
# Pulls the latest code as the jontraderlar user, refreshes dependencies,
# and restarts both systemd units.

set -euo pipefail

REPO_DIR="/opt/jontraderlar/jontraderlar-v2"
VENV="${REPO_DIR}/.venv"

echo "→ Pulling latest code..."
sudo -u jontraderlar git -C "${REPO_DIR}" pull --ff-only

echo "→ Updating Python dependencies..."
sudo -u jontraderlar "${VENV}/bin/pip" install -e "${REPO_DIR}"

echo "→ Restarting services..."
sudo systemctl restart jontraderlar-bot jontraderlar-worker

echo "→ Status:"
sudo systemctl status --no-pager --lines=5 jontraderlar-bot jontraderlar-worker

echo "✓ Deploy complete."
