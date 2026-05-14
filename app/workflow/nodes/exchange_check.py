"""Exchange-check node — calls the appropriate exchange API to verify UID + referral + KYC + deposit."""
from __future__ import annotations

from app.config import settings
from app.exchanges.facade import ExchangeClient
from app.logging import get_logger
from app.messages import Errors, map_exchange_error
from app.workflow.state import (
    EligibilityStatus,
    ExchangeVerificationResult,
    WorkflowState,
)

logger = get_logger(__name__)


def _failed(reason: str, response: str) -> dict:
    return {
        "exchange_verification_result": ExchangeVerificationResult(
            is_successful=False,
            eligibility_status=EligibilityStatus.not_eligible,
            error_message=reason,
        ),
        "response_message": response,
    }


async def exchange_check_node(state: WorkflowState) -> WorkflowState:
    logger.info("exchange_check_node start")

    assert state.router is not None
    exchange = state.router.exchange
    uid = state.router.uid

    if not exchange or not uid:
        logger.error("Missing exchange data — exchange=%s uid=%s", exchange, uid)
        return state.model_copy(update=_failed("Missing exchange or UID data", Errors.UNEXPECTED))

    if uid in settings.blocked_uids:
        logger.info("Blocked UID provided: %s", uid)
        return state.model_copy(update=_failed("Blocked UID", Errors.BLOCKED_UID))

    logger.info("Verifying %s account UID=%s", exchange, uid)

    try:
        async with ExchangeClient() as client:
            verification = await client.verify_user(exchange=exchange, uid=uid)

        if verification.get("eligible"):
            return state.model_copy(update={
                "exchange_verification_result": ExchangeVerificationResult(
                    is_successful=True,
                    eligibility_status=EligibilityStatus.eligible,
                )
            })

        api_msg = verification.get("msg")
        user_msg = map_exchange_error(api_msg, exchange)
        return state.model_copy(update=_failed(api_msg or "unknown", user_msg))

    except ValueError as e:
        logger.error("Unsupported exchange %s: %s", exchange, e, exc_info=True)
        return state.model_copy(update=_failed(f"Unsupported exchange: {exchange}", Errors.UNSUPPORTED_EXCHANGE))

    except (ConnectionError, TimeoutError) as e:
        logger.error("Exchange API connection error for %s: %s", exchange, e, exc_info=True)
        return state.model_copy(update=_failed("Exchange API connection failed", Errors.EXCHANGE_UNKNOWN))

    except Exception as e:
        logger.error("exchange_check_node unexpected error: %s", e, exc_info=True)
        return state.model_copy(update=_failed(f"Unexpected error: {e}", Errors.UNEXPECTED))
