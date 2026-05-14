"""Local development entry point — runs the bot in polling mode.

Useful when you don't want to expose a webhook via a tunnel. Note: this
still requires the ARQ worker to be running in a second terminal,
otherwise messages will queue but never be processed.

Usage::

    # Terminal 1
    arq app.worker.WorkerSettings

    # Terminal 2
    python -m app.dev_polling
"""
from __future__ import annotations

import asyncio

from app.bot.factory import create_dispatcher
from app.bot.instance import close_bot, get_bot
from app.db.client import close as close_db
from app.db.client import ensure_indexes
from app.logging import get_logger, setup_logging
from app.tasks.pool import close_pool, get_pool


async def main() -> None:
    setup_logging()
    logger = get_logger(__name__)

    bot = get_bot()
    dispatcher = create_dispatcher()
    arq_pool = await get_pool()
    dispatcher["arq"] = arq_pool

    try:
        await ensure_indexes()
    except Exception as e:
        logger.warning("ensure_indexes failed: %s", e)

    # Make sure no leftover webhook intercepts our polling updates.
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Starting polling — Ctrl+C to stop")
    try:
        await dispatcher.start_polling(bot, allowed_updates=["message", "callback_query"])
    finally:
        await close_pool()
        await close_bot()
        await close_db()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
