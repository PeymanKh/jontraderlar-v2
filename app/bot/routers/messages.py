"""Free-text message handler — pushes work onto the ARQ queue."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message
from arq import ArqRedis

from app.logging import get_logger

logger = get_logger(__name__)

router = Router(name="messages")


@router.message(F.text & ~F.text.startswith("/"))
async def text_message(message: Message, arq: ArqRedis) -> None:
    """Enqueue the message for the worker and return immediately."""
    if message.chat.type != ChatType.PRIVATE:
        return

    user = message.from_user
    if user is None or message.text is None:
        return

    logger.info(
        "Enqueueing message from user_id=%s username=@%s",
        user.id,
        user.username,
    )

    await arq.enqueue_job(
        "process_user_message",
        chat_id=message.chat.id,
        telegram_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        text=message.text,
    )
