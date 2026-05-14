"""Command handlers.

Trivial commands reply inline. Commands that need DB access are enqueued
onto ARQ so the webhook returns immediately.
"""
from __future__ import annotations

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.db.operations import get_user_with_accounts
from app.logging import get_logger
from app.messages import Info

logger = get_logger(__name__)

router = Router(name="commands")


# Only ever respond to private chats. Belt and braces — the gateway also
# filters group updates upstream.
def _is_private(message: Message) -> bool:
    return message.chat.type == ChatType.PRIVATE


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    if not _is_private(message):
        return
    user = message.from_user
    logger.info("/start from user_id=%s username=@%s", user.id if user else None, user.username if user else None)
    await message.answer(Info.WELCOME)


@router.message(Command("destek"))
async def support_cmd(message: Message) -> None:
    if not _is_private(message):
        return
    await message.answer(Info.SUPPORT)


@router.message(Command("bingx_kimlik_tasima"))
async def bingx_kyc_cmd(message: Message) -> None:
    if not _is_private(message):
        return
    await message.answer(Info.BINGX_KYC_CHANGE_1)
    await message.answer(Info.BINGX_KYC_CHANGE_2)


@router.message(Command("bybit_kimlik_tasima"))
async def bybit_kyc_cmd(message: Message) -> None:
    if not _is_private(message):
        return
    await message.answer(Info.BYBIT_KYC_CHANGE_1)
    await message.answer(Info.BYBIT_KYC_CHANGE_2)


@router.message(Command("hesaplarim"))
async def profile_cmd(message: Message) -> None:
    """Profile lookup — hits MongoDB but is fast enough to handle inline."""
    if not _is_private(message):
        return
    user = message.from_user
    if user is None:
        return

    try:
        result = await get_user_with_accounts(user.id)
        if result["status"] == "failed":
            await message.answer(Info.PROFILE_NOT_FOUND)
            return

        accounts = result.get("exchange_accounts") or []
        if not accounts:
            account_list = Info.NO_ACCOUNTS
        else:
            parts = []
            for acc in accounts:
                parts.append(Info.ACCOUNT_DETAIL.format(
                    exchange_name=acc["exchange_name"].upper(),
                    exchange_uid=acc["exchange_uid"],
                    account_date=acc["account_added_date"].strftime("%d.%m.%Y %H:%M"),
                ))
            account_list = "".join(parts)

        await message.answer(Info.PROFILE.format(account_list=account_list))

    except Exception as e:
        logger.error("/hesaplarim failed for user %s: %s", user.id, e, exc_info=True)
        await message.answer(Info.PROFILE_ERROR)
