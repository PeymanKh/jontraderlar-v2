"""Pydantic models for MongoDB collections."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(BaseModel):
    """One record per Telegram user."""

    telegram_id: int = Field(..., gt=0)
    telegram_username: str = Field(..., min_length=1, max_length=64)
    telegram_full_name: str = Field(..., min_length=1, max_length=128)
    warnings: int = Field(default=0, ge=0)
    join_date: datetime = Field(default_factory=_utcnow)
    edited_at: datetime = Field(default_factory=_utcnow)


class ExchangeAccount(BaseModel):
    """One record per (user, exchange UID) pair."""

    telegram_id: int = Field(..., gt=0)
    exchange_name: Literal["bingx", "bybit"]
    exchange_uid: int
    account_added_date: datetime = Field(default_factory=_utcnow)
