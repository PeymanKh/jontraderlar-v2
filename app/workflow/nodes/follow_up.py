"""Follow-up node — handles "Evet/Hayır" responses to a pending confirmation."""
from __future__ import annotations

from app.bot.operations import send_admin_notification
from app.db.operations import add_exchange_account
from app.logging import get_logger
from app.messages import Errors, Info, map_database_error
from app.workflow.state import WorkflowState

logger = get_logger(__name__)

_AFFIRMATIVE = {"evet", "evet.", "evet!", "evet?", "e"}


async def follow_up_node(state: WorkflowState) -> WorkflowState:
    logger.info("follow_up_node start")
    response = state.user_message.strip().lower()

    if response in _AFFIRMATIVE:
        data = state.pending_action_data
        if not data:
            logger.error("Pending action data is missing.")
            return state.model_copy(update={
                "pending_confirmation": False,
                "response_message": Errors.UNEXPECTED,
            })

        result = await add_exchange_account(
            telegram_id=state.user_metadata.telegram_id,
            exchange_name=data["exchange_name"],
            exchange_uid=data["exchange_uid"],
        )

        if result.get("status") == "success":
            try:
                admin_msg = (
                    f"🔄 <b>Yeni Borsa Hesabı Eklendi</b>\n\n"
                    f"🏦 <b>Borsa:</b> {data['exchange_name'].title()} "
                    f"UID <code>{data['exchange_uid']}</code>\n\n"
                    f"👤 <b>Telegram Kullanıcı Adı:</b> @{state.user_metadata.telegram_username}\n"
                    f"📛 <b>Görünen İsim:</b> {state.user_metadata.telegram_full_name}"
                )
                await send_admin_notification(admin_msg)
            except Exception as e:
                logger.warning("Admin notification failed: %s", e)

            return state.model_copy(update={
                "pending_confirmation": False,
                "pending_action_data": None,
                "response_message": Info.ACCOUNT_ADDED.format(
                    exchange_name=data["exchange_name"].title(),
                    exchange_uid=data["exchange_uid"],
                ),
            })

        return state.model_copy(update={
            "pending_confirmation": False,
            "pending_action_data": None,
            "response_message": map_database_error(result.get("msg")),
        })

    # Anything else cancels the pending action.
    return state.model_copy(update={
        "pending_confirmation": False,
        "pending_action_data": None,
        "response_message": Info.ACTION_CANCELLED,
    })
