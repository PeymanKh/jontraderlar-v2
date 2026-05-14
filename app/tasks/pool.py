"""ARQ Redis pool — singletons for both the gateway (producer) and worker."""
from __future__ import annotations

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

_pool: ArqRedis | None = None


def redis_settings() -> RedisSettings:
    return RedisSettings(
        host=settings.redis.host,
        port=settings.redis.port,
        database=settings.redis.database,
        password=(
            settings.redis.password.get_secret_value()
            if settings.redis.password
            else None
        ),
    )


async def get_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(redis_settings())
        logger.info("ARQ Redis pool created")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.aclose()
        logger.info("ARQ Redis pool closed")
    _pool = None
