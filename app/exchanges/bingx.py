"""BingX API client — affiliate UID verification."""
from __future__ import annotations

import hmac
import time
from hashlib import sha256
from typing import Any

from app.config import settings
from app.exchanges.base import BaseClientConfig, BaseExchangeClient


class BingXClient(BaseExchangeClient):
    BASE_URL = "https://open-api.bingx.com"

    def __init__(self) -> None:
        super().__init__(
            BaseClientConfig(
                base_url=self.BASE_URL,
                api_key=settings.bingx.api_key,
                secret_key=settings.bingx.secret_key,
                timeout=10,
                max_retries=3,
            )
        )

    async def __aenter__(self) -> "BingXClient":
        await super().__aenter__()
        assert self.session is not None
        self.session.headers.update(
            {"X-BX-APIKEY": self.config.api_key.get_secret_value()}
        )
        return self

    def _sign(self, params: dict[str, Any]) -> tuple[str, str]:
        params = {k: v for k, v in params.items() if k != "timestamp"}
        keys = sorted(params.keys())
        body = "&".join(f"{k}={params[k]}" for k in keys)
        timestamp = str(int(time.time() * 1000))
        body = f"{body}&timestamp={timestamp}" if body else f"timestamp={timestamp}"

        signature = hmac.new(
            self.config.secret_key.get_secret_value().encode("utf-8"),
            body.encode("utf-8"),
            sha256,
        ).hexdigest()
        return signature, timestamp

    async def verify_uid(self, uid: int) -> dict[str, Any]:
        params = {"uid": str(uid)}
        signature, timestamp = self._sign(params)
        final = {"uid": str(uid), "timestamp": timestamp, "signature": signature}

        response = await self._request(
            "GET",
            "/openApi/agent/v1/account/inviteRelationCheck",
            params=final,
        )

        data = response.get("data")
        if not data:
            return {"status": "success", "eligible": False, "msg": "invalid uid"}

        if "kycResult" not in data:
            return {"status": "success", "eligible": False, "msg": "wrong referral"}

        if not data.get("kycResult"):
            return {"status": "success", "eligible": False, "msg": "kyc not complete"}

        if not data.get("trade"):
            return {"status": "success", "eligible": False, "msg": "no deposit"}

        return {"status": "success", "eligible": True, "msg": "user is eligible"}
