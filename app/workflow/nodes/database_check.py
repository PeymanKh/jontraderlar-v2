"""Database-check node — register new users or ask for confirmation on a 2nd account."""
from __future__ import annotations

from app.db.operations import add_new_user, get_account_by_uid, get_user_with_accounts
from app.logging import get_logger
from app.messages import Errors, Info, map_database_error
from app.workflow.state import (
    DatabaseOperationResult,
    EligibilityStatus,
    Route,
    WorkflowState,
)

logger = get_logger(__name__)


def _failed(reason: str, response: str) -> dict:
    return {
        "database_operation_result": DatabaseOperationResult(
            is_successful=False,
            eligibility_status=EligibilityStatus.not_eligible,
            error_message=reason,
        ),
        "response_message": response,
        "router": None,  # placeholder so the conditional edge still routes via state
    }


async def database_check_node(state: WorkflowState) -> WorkflowState:
    logger.info("database_check_node start")

    assert state.router is not None
    telegram_id = state.user_metadata.telegram_id
    exchange_name = state.router.exchange
    exchange_uid = state.router.uid
    assert exchange_name is not None and exchange_uid is not None

    try:
        existing_account = await get_account_by_uid(exchange_uid, exchange_name)

        if existing_account.get("account"):
            owner_id = existing_account["account"]["telegram_id"]

            if owner_id != telegram_id:
                # UID is owned by someone else.
                return state.model_copy(update={
                    "response_message": Errors.EXCHANGE_ACCOUNT_ALREADY_USED,
                    "database_operation_result": DatabaseOperationResult(
                        is_successful=False,
                        eligibility_status=EligibilityStatus.not_eligible,
                        error_message="Exchange account already used by another user.",
                    ),
                })

            # This UID belongs to the current user already.
            return state.model_copy(update={
                "response_message": Errors.USER_ALREADY_VERIFIED,
                "database_operation_result": DatabaseOperationResult(
                    is_successful=False,
                    eligibility_status=EligibilityStatus.not_eligible,
                    error_message="User already verified.",
                ),
            })

        # UID is brand new in the system.
        existing_user = await get_user_with_accounts(telegram_id)

        if existing_user.get("user") is not None:
            # Known user adding an additional account → ask for confirmation.
            message = Info.CONFIRM_SECOND_ACCOUNT.format(
                exchange_name=exchange_name.title(),
                exchange_uid=exchange_uid,
            )
            return state.model_copy(update={
                "pending_confirmation": True,
                "pending_action_data": {
                    "exchange_name": exchange_name,
                    "exchange_uid": exchange_uid,
                },
                "response_message": message,
            })

        # First-time user.
        result = await add_new_user(
            telegram_id=telegram_id,
            telegram_username=state.user_metadata.telegram_username,
            telegram_full_name=state.user_metadata.telegram_full_name,
            exchange_name=exchange_name,
            exchange_uid=exchange_uid,
        )

        if not result.get("eligible"):
            return state.model_copy(update={
                "response_message": map_database_error(result.get("msg")),
                "database_operation_result": DatabaseOperationResult(
                    is_successful=False,
                    eligibility_status=EligibilityStatus.not_eligible,
                ),
            })

        return state.model_copy(update={
            "database_operation_result": DatabaseOperationResult(
                is_successful=True,
                eligibility_status=EligibilityStatus.eligible,
            )
        })

    except Exception as e:
        logger.error("database_check_node unexpected error: %s", e, exc_info=True)
        return state.model_copy(update={
            "response_message": Errors.UNEXPECTED,
            "database_operation_result": DatabaseOperationResult(
                is_successful=False,
                eligibility_status=EligibilityStatus.not_eligible,
            ),
        })
