"""ARQ job functions executed by the worker."""
from __future__ import annotations

from typing import Any

from aiogram.exceptions import TelegramAPIError
from aiogram.utils.chat_action import ChatActionSender

from app.bot.instance import get_bot
from app.logging import get_logger
from app.messages import Errors
from app.workflow.graph import get_workflow
from app.workflow.state import UserMetadata, WorkflowState

logger = get_logger(__name__)


async def process_user_message(
    ctx: dict[str, Any],
    *,
    chat_id: int,
    telegram_id: int,
    username: str,
    full_name: str,
    text: str,
) -> None:
    """Run the LangGraph workflow for a user message and reply via the bot."""
    bot = get_bot()
    workflow = get_workflow()

    try:
        input_state = {
            "user_message": text,
            "user_metadata": UserMetadata(
                telegram_id=telegram_id,
                telegram_username=f"@{username}" if username else "",
                telegram_full_name=full_name,
            ),
        }

        # Show a "typing…" indicator in the chat for the whole duration of
        # processing. ChatActionSender re-sends the action every few seconds
        # until the block exits, then the reply clears it.
        async with ChatActionSender.typing(bot=bot, chat_id=chat_id):
            result: Any = await workflow.ainvoke(
                input_state,
                config={"configurable": {"thread_id": str(telegram_id)}},
            )

            if isinstance(result, dict):
                response = result.get("response_message")
            else:
                response = getattr(result, "response_message", None)

            if not response:
                logger.warning("No response generated for user %s", telegram_id)
                response = Errors.UNEXPECTED

            await bot.send_message(chat_id=chat_id, text=response)

        logger.info("Replied to user %s (job %s)", telegram_id, ctx.get("job_id"))

    except TelegramAPIError as e:
        logger.error("Telegram API error replying to %s: %s", telegram_id, e, exc_info=True)
    except Exception as e:
        logger.error("process_user_message failed for %s: %s", telegram_id, e, exc_info=True)
        try:
            await bot.send_message(chat_id=chat_id, text=Errors.UNEXPECTED)
        except Exception as send_err:
            logger.error("Failed to send fallback error message to %s: %s", telegram_id, send_err)
