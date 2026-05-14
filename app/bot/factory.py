"""Dispatcher and router wiring."""
from __future__ import annotations

from aiogram import Dispatcher

from app.bot.routers.commands import router as commands_router
from app.bot.routers.messages import router as messages_router
from app.logging import get_logger

logger = get_logger(__name__)


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    dp.include_router(commands_router)
    dp.include_router(messages_router)
    logger.info("Dispatcher created")
    return dp
