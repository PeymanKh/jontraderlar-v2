"""Helpers that wrap raw Telegram Bot API calls — invite links + admin notifications."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from aiogram.exceptions import TelegramAPIError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.bot.instance import get_bot
from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)


@retry(
    retry=retry_if_exception_type(TelegramAPIError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def generate_invite_link(
    expire_minutes: int = 1440,
    member_limit: int = 1,
) -> dict[str, str | None]:
    """Create a single-use invite link to the private group."""
    bot = get_bot()
    expire_date = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

    try:
        link = await bot.create_chat_invite_link(
            chat_id=int(settings.telegram.group_id.get_secret_value()),
            expire_date=expire_date,
            member_limit=member_limit,
        )
        logger.info("Generated new invite link")
        return {"status": "success", "group_url": link.invite_link}
    except Exception as e:
        logger.error("Invite link generation failed: %s", e, exc_info=True)
        return {"status": "failed", "group_url": None}


@retry(
    retry=retry_if_exception_type(TelegramAPIError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def send_admin_notification(message: str) -> None:
    bot = get_bot()
    chat_id = int(settings.telegram.admin_chat_id.get_secret_value())
    await bot.send_message(chat_id=chat_id, text=message)
    logger.info("Notification sent to admin chat")
