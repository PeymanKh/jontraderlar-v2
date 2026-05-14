"""MongoDB connection management — one motor client per process."""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.database.uri.get_secret_value(),
            maxPoolSize=10,
            minPoolSize=2,
            maxIdleTimeMS=30_000,
        )
        logger.info("MongoDB client initialized")
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[settings.database.name]
    return _db


async def ensure_indexes() -> None:
    """Create the unique indexes the application relies on. Safe to call repeatedly."""
    db = get_db()
    await db.users.create_index([("telegram_id", 1)], unique=True)
    await db.exchange_accounts.create_index(
        [("exchange_name", 1), ("exchange_uid", 1)],
        unique=True,
    )
    await db.exchange_accounts.create_index([("telegram_id", 1)])
    logger.info("MongoDB indexes ensured")


async def close() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
        logger.info("MongoDB client closed")
    _client = None
    _db = None
