# Jön Traderlar — Telegram Verification Bot (v2)

Verifies that Turkish-speaking traders have signed up to BingX or ByBit
through Hirozaki's referral, completed KYC, and made at least one deposit —
then issues a single-use invite link to a private Telegram group.

## Architecture

```
Telegram → nginx (TLS) → FastAPI gateway ──► Redis (ARQ queue)
                                              │
                                              ▼
                                          ARQ worker(s) → LangGraph → MongoDB
                                              │
                                              └────► Telegram (bot.send_message)
```

- **FastAPI** receives webhook updates, validates Telegram's secret token,
  feeds them into aiogram's dispatcher.
- **aiogram 3** routes commands. Trivial commands reply inline. Anything that
  hits MongoDB or exchange APIs is enqueued onto **ARQ**.
- **ARQ workers** run the **LangGraph** flow (router → exchange check →
  database check → invite link) and push the result back to the user.
- **MongoDB** persists users, exchange accounts, and LangGraph state via the
  Mongo checkpointer (multi-turn "evet/hayır" works out of the box).

## Local development

Requires Python 3.11+, Redis, and MongoDB running locally.

```bash
# Create venv and install
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Copy and edit env
cp .env.example .env
$EDITOR .env

# Terminal 1 — gateway (FastAPI on :8080)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

# Terminal 2 — worker
arq app.worker.WorkerSettings
```

To expose the gateway to Telegram from your laptop, use a tunnel:

```bash
cloudflared tunnel --url http://localhost:8080
# or:  ngrok http 8080
```

Set `PUBLIC_URL` in `.env` to the public URL and restart the gateway — it
will register the webhook with Telegram on startup.

### Easier local mode: polling

If you don't want to mess with tunnels, run the bot in polling mode
instead of webhook mode (still requires the worker to be running):

```bash
# Terminal 1 — worker
arq app.worker.WorkerSettings

# Terminal 2 — bot in polling mode
python -m app.dev_polling
```

## Production (VPS) deployment

One-time setup on a clean Ubuntu/Debian VPS:

```bash
# As root
adduser --system --group --home /opt/jontraderlar jontraderlar
mkdir -p /etc/jontraderlar
chown -R jontraderlar:jontraderlar /opt/jontraderlar
apt-get install -y python3.11 python3.11-venv redis-server mongodb-org nginx certbot python3-certbot-nginx

# Code
sudo -u jontraderlar git clone <your-repo> /opt/jontraderlar
cd /opt/jontraderlar
sudo -u jontraderlar python3.11 -m venv .venv
sudo -u jontraderlar .venv/bin/pip install -e .

# Config
cp .env.example /etc/jontraderlar/.env
$EDITOR /etc/jontraderlar/.env
chown root:jontraderlar /etc/jontraderlar/.env
chmod 640 /etc/jontraderlar/.env

# systemd
cp deploy/jontraderlar-bot.service /etc/systemd/system/
cp deploy/jontraderlar-worker.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now jontraderlar-bot jontraderlar-worker

# nginx + TLS
cp deploy/nginx.conf.example /etc/nginx/sites-available/jontraderlar
ln -s /etc/nginx/sites-available/jontraderlar /etc/nginx/sites-enabled/
# edit the server_name in the config to match your domain
certbot --nginx -d bot.example.com
systemctl reload nginx
```

Subsequent deploys:

```bash
sudo -u jontraderlar /opt/jontraderlar/deploy/deploy.sh
```

## Operations

- Logs: `journalctl -u jontraderlar-bot -f` / `journalctl -u jontraderlar-worker -f`
- Restart: `systemctl restart jontraderlar-bot jontraderlar-worker`
- Health check: `curl https://bot.example.com/health`

## Project layout

See [`app/`](app/) — each subpackage owns one concern (bot, tasks, workflow,
exchanges, db). Read [`app/main.py`](app/main.py) and
[`app/worker.py`](app/worker.py) first to understand the two entry points.
