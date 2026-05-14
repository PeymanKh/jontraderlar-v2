"""ARQ worker entry point.

Run with::

    arq app.worker.WorkerSettings

This process owns:
- The LangGraph workflow + its Mongo checkpoint client
- A Motor client for users/exchange_accounts collections
- An aiogram Bot instance used to push replies back to users
"""
from __future__ import annotations

from typing import Any

from app.bot.instance import close_bot, get_bot
from app.db.client import close as close_db
from app.db.client import ensure_indexes
from app.logging import get_logger, setup_logging
from app.tasks.jobs import process_user_message
from app.tasks.pool import redis_settings
from app.workflow.graph import close_workflow, get_workflow

setup_logging()
logger = get_logger(__name__)


async def startup(ctx: dict[str, Any]) -> None:
    logger.info("Worker starting — initializing bot, workflow, and indexes")
    get_bot()                # warm the Bot singleton
    get_workflow()           # compile the LangGraph
    try:
        await ensure_indexes()
    except Exception as e:
        logger.warning("ensure_indexes failed at worker startup: %s", e)
    logger.info("Worker ready")


async def shutdown(ctx: dict[str, Any]) -> None:
    logger.info("Worker shutting down")
    await close_workflow()
    await close_bot()
    await close_db()


class WorkerSettings:
    """ARQ configuration. ARQ discovers this class via the CLI."""

    redis_settings = redis_settings()
    functions = [process_user_message]
    on_startup = startup
    on_shutdown = shutdown

    max_jobs = 10
    job_timeout = 60                # seconds — covers LLM + exchange API calls
    keep_result = 60                # short — we don't poll for results
    max_tries = 3                   # ARQ-level retry for transient failures
    health_check_interval = 60
