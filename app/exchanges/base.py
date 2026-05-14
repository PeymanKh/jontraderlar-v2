"""Base async HTTP client for exchange APIs.

Provides retry, rate limiting, session management, and a normalized
response envelope ({status, eligible, msg}) for callers.
"""
from __future__ import annotations

from typing import Any

import aiohttp
from aiohttp import ClientTimeout
from aiolimiter import AsyncLimiter
from pydantic import BaseModel, SecretStr
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.logging import get_logger

logger = get_logger(__name__)


class APIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(APIError):
    pass


class AuthError(APIError):
    pass


class BaseClientConfig(BaseModel):
    base_url: str
    api_key: SecretStr
    secret_key: SecretStr
    timeout: int = 10
    max_retries: int = 3


class BaseExchangeClient:
    """Async context-manager HTTP client shared by all exchange implementations."""

    def __init__(self, config: BaseClientConfig):
        self.config = config
        self.session: aiohttp.ClientSession | None = None
        self.limiter = AsyncLimiter(7, time_period=1.0)

    async def __aenter__(self) -> "BaseExchangeClient":
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "JonTraderlar/2.0",
                "Accept": "application/json",
            },
            timeout=ClientTimeout(total=self.config.timeout),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session is not None:
            await self.session.close()

    @staticmethod
    def _log_retry(state: RetryCallState) -> None:
        logger.warning(
            "Retrying %s: attempt %d (%s)",
            state.fn.__name__ if state.fn else "<unknown>",
            state.attempt_number,
            state.outcome.exception() if state.outcome else None,
        )

    async def _raw_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self.session is None:
            raise RuntimeError("Client session is not initialized — use 'async with'.")

        url = f"{self.config.base_url}{endpoint}"
        async with self.limiter:
            try:
                async with self.session.request(method, url, params=params, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ContentTypeError as e:
                raise APIError(f"Invalid API response format: {e}") from e
            except aiohttp.ClientError as e:
                raise APIError(f"Network failure: {e}") from e

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Authenticated request with exponential-backoff retry on transient errors."""
        retryer = retry(
            stop=stop_after_attempt(self.config.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=(
                retry_if_exception_type(aiohttp.ClientConnectionError)
                | retry_if_exception_type(aiohttp.ClientError)
                | retry_if_exception_type(RateLimitError)
            ),
            before_sleep=self._log_retry,
        )
        wrapped = retryer(self._raw_request)
        try:
            return await wrapped(method, endpoint, params)
        except Exception as e:
            logger.error("API request failed for %s: %s", endpoint, e, exc_info=True)
            return {"status": "failed", "eligible": False, "msg": "Internal server error"}
