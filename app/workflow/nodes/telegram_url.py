"""Invite-link node — generates a single-use group link and notifies the admin."""
from __future__ import annotations

from app.bot.operations import generate_invite_link, send_admin_notification
from app.logging import get_logger
from app.messages import Errors, verification_success_message
from app.workflow.state import InviteLinkResult, WorkflowState

logger = get_logger(__name__)


async def telegram_url_node(state: WorkflowState) -> WorkflowState:
    logger.info("telegram_url_node start")

    try:
        invite = await generate_invite_link(expire_minutes=1440, member_limit=1)
        if invite.get("status") != "success" or not invite.get("group_url"):
            return state.model_copy(update={
                "invite_link_result": InviteLinkResult(
                    is_successful=False,
                    error_message="Link generation returned failed status",
                ),
                "response_message": Errors.INVITE_LINK_FAILED,
            })

        url = invite["group_url"]
        success_message = verification_success_message(url)

        assert state.router is not None
        admin_msg = (
            f"✅ <b>Yeni Hesap Doğrulandı</b>\n\n"
            f"🏦 <b>Borsa:</b> {(state.router.exchange or '').title()} "
            f"UID <code>{state.router.uid}</code>\n\n"
            f"👤 <b>Telegram Kullanıcı Adı:</b> @{state.user_metadata.telegram_username}\n"
            f"📛 <b>Görünen İsim:</b> {state.user_metadata.telegram_full_name}"
        )
        await send_admin_notification(admin_msg)

        return state.model_copy(update={
            "invite_link_result": InviteLinkResult(is_successful=True, group_invitation_url=url),
            "response_message": success_message,
        })

    except Exception as e:
        logger.error("telegram_url_node unexpected error: %s", e, exc_info=True)
        return state.model_copy(update={
            "invite_link_result": InviteLinkResult(is_successful=False, error_message=str(e)),
            "response_message": Errors.UNEXPECTED,
        })
