"""Unified async facade over the supported exchange clients."""
from __future__ import annotations

from typing import Any

from app.exchanges.bingx import BingXClient
from app.exchanges.bybit import ByBitClient


class ExchangeClient:
    """Use as an async context manager:

        async with ExchangeClient() as ex:
            result = await ex.verify_user("bingx", 12345)
    """

    def __init__(self) -> None:
        self.bingx = BingXClient()
        self.bybit = ByBitClient()

    async def __aenter__(self) -> "ExchangeClient":
        await self.bingx.__aenter__()
        await self.bybit.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.bingx.__aexit__(exc_type, exc_val, exc_tb)
        await self.bybit.__aexit__(exc_type, exc_val, exc_tb)

    async def verify_user(self, exchange: str, uid: int) -> dict[str, Any]:
        match exchange.lower():
            case "bingx":
                return await self.bingx.verify_uid(uid)
            case "bybit":
                return await self.bybit.verify_uid(uid)
            case _:
                raise ValueError(f"Unsupported exchange: {exchange}")
