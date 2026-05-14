"""FastAPI gateway — accepts Telegram webhook updates and feeds them into aiogram.

This process owns:
- The webhook HTTP endpoint
- The aiogram Bot + Dispatcher
- A connection to Redis (ARQ pool) for enqueueing work

It does NOT run the LangGraph workflow. That happens in the worker process.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request, status

from app.bot.factory import create_dispatcher
from app.bot.instance import close_bot, get_bot
from app.config import settings
from app.db.client import close as close_db
from app.db.client import ensure_indexes
from app.logging import get_logger, setup_logging
from app.tasks.pool import close_pool, get_pool

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting %s v%s (env=%s)", settings.app_name, settings.app_version, settings.environment.value)

    # Initialize singletons.
    bot = get_bot()
    dispatcher = create_dispatcher()
    arq_pool = await get_pool()

    # Make the ARQ pool injectable into handlers.
    dispatcher["arq"] = arq_pool

    app.state.bot = bot
    app.state.dispatcher = dispatcher
    app.state.arq = arq_pool

    # Ensure DB indexes exist (cheap, idempotent).
    try:
        await ensure_indexes()
    except Exception as e:
        logger.warning("ensure_indexes failed at startup: %s", e)

    # Register the webhook with Telegram if we have a public URL.
    if settings.is_production and settings.public_url:
        webhook_url = f"{settings.public_url.rstrip('/')}/webhook"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.telegram.webhook_secret.get_secret_value(),
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True,
            max_connections=100,
        )
        logger.info("Webhook registered: %s", webhook_url)
    else:
        # In dev, the user is probably using polling or a tunnel they set up
        # by hand. Don't touch the webhook.
        logger.info("Skipping webhook registration (development or no PUBLIC_URL set)")

    try:
        yield
    finally:
        logger.info("Shutting down gateway")
        if settings.is_production and settings.public_url:
            try:
                await bot.delete_webhook(drop_pending_updates=False)
            except Exception as e:
                logger.warning("delete_webhook failed: %s", e)
        await close_pool()
        await close_bot()
        await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
) -> dict[str, str]:
    """Telegram webhook endpoint. Validates secret token, feeds the update into aiogram."""
    expected = settings.telegram.webhook_secret.get_secret_value()
    if x_telegram_bot_api_secret_token != expected:
        logger.warning("Rejected webhook with invalid secret token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid secret token")

    try:
        payload = await request.json()
    except ValueError as e:
        logger.error("Invalid JSON in webhook: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

    update = Update.model_validate(payload, context={"bot": request.app.state.bot})

    # Silent drop for non-private chats — same behavior as v1.
    if update.message and update.message.chat.type != "private":
        return {"status": "ignored"}
    if update.callback_query and update.callback_query.message and update.callback_query.message.chat.type != "private":
        return {"status": "ignored"}

    await request.app.state.dispatcher.feed_update(request.app.state.bot, update)
    return {"status": "ok"}
