"""Per-process Bot singleton.

Both the FastAPI gateway and the ARQ worker import `get_bot()` to obtain
a fully configured `Bot` instance. Each process gets its own — they are
separate processes, so no shared state.
"""
from __future__ import annotations

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.telegram.bot_token.get_secret_value(),
            default=DefaultBotProperties(
                parse_mode=ParseMode.HTML,
                link_preview_is_disabled=True,
            ),
        )
        logger.info("aiogram Bot initialized")
    return _bot


async def close_bot() -> None:
    global _bot
    if _bot is not None:
        await _bot.session.close()
        logger.info("aiogram Bot session closed")
    _bot = None
