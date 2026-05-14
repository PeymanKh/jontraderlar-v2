"""ByBit API client — affiliate UID verification."""
from __future__ import annotations

import hmac
import time
from hashlib import sha256
from typing import Any

from app.config import settings
from app.exchanges.base import BaseClientConfig, BaseExchangeClient
from app.logging import get_logger

logger = get_logger(__name__)


class ByBitClient(BaseExchangeClient):
    BASE_URL = "https://api.bybit.com"
    RECV_WINDOW = "5000"

    def __init__(self) -> None:
        super().__init__(
            BaseClientConfig(
                base_url=self.BASE_URL,
                api_key=settings.bybit.api_key,
                secret_key=settings.bybit.secret_key,
                timeout=10,
                max_retries=3,
            )
        )

    def _sign(self, uid: str) -> tuple[str, str]:
        timestamp = str(int(time.time() * 1000))
        api_key = self.config.api_key.get_secret_value()
        pre_sign = f"{timestamp}{api_key}{self.RECV_WINDOW}uid={uid}&timestamp={timestamp}"
        signature = hmac.new(
            self.config.secret_key.get_secret_value().encode("utf-8"),
            pre_sign.encode("utf-8"),
            sha256,
        ).hexdigest()
        return signature, timestamp

    async def verify_uid(self, uid: int) -> dict[str, Any]:
        if self.session is None:
            raise RuntimeError("Client session is not initialized — use 'async with'.")

        uid_str = str(uid)
        signature, timestamp = self._sign(uid_str)
        params = {"uid": uid_str, "timestamp": timestamp}
        headers = {
            "X-BAPI-SIGN": signature,
            "X-BAPI-API-KEY": self.config.api_key.get_secret_value(),
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": self.RECV_WINDOW,
        }

        try:
            async with self.session.request(
                "GET",
                f"{self.config.base_url}/v5/user/aff-customer-info",
                params=params,
                headers=headers,
            ) as response:
                response.raise_for_status()
                body = await response.json()
        except Exception as e:
            logger.error("ByBit verify_uid failed: %s", e, exc_info=True)
            return {"status": "failed", "eligible": False, "msg": "Internal server error"}

        result = body.get("result")
        if not result:
            return {"status": "success", "eligible": False, "msg": "wrong referral"}

        kyc_level = int(result.get("KycLevel") or 0)
        if kyc_level == 0:
            return {"status": "success", "eligible": False, "msg": "kyc not complete"}

        deposit_amount = float(result.get("depositAmount365Day") or 0.0)
        if deposit_amount < 1:
            return {"status": "success", "eligible": False, "msg": "no deposit"}

        return {"status": "success", "eligible": True, "msg": "user is eligible"}
