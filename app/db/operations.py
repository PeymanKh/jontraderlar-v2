"""Database operations — user registration, account lookups."""
from __future__ import annotations

from typing import Any, TypedDict

from pymongo.errors import DuplicateKeyError, PyMongoError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.db.client import get_client, get_db
from app.db.models import ExchangeAccount, User
from app.logging import get_logger

logger = get_logger(__name__)


class OperationResult(TypedDict, total=False):
    status: str   # "success" | "failed"
    eligible: bool
    msg: str


class AccountLookupResult(TypedDict, total=False):
    status: str
    account: dict[str, Any] | None
    user: dict[str, Any] | None
    msg: str


class UserLookupResult(TypedDict, total=False):
    status: str
    user: dict[str, Any] | None
    exchange_accounts: list[dict[str, Any]]
    msg: str


@retry(
    retry=retry_if_exception_type(PyMongoError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def add_new_user(
    telegram_id: int,
    telegram_username: str,
    telegram_full_name: str,
    exchange_name: str,
    exchange_uid: int,
) -> OperationResult:
    """Atomically insert a brand-new user plus their first exchange account."""
    db = get_db()
    client = get_client()

    user = User(
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        telegram_full_name=telegram_full_name,
    )
    account = ExchangeAccount(
        telegram_id=telegram_id,
        exchange_name=exchange_name,  # type: ignore[arg-type]
        exchange_uid=exchange_uid,
    )

    try:
        async with await client.start_session() as session:
            async with session.start_transaction():
                await db.users.insert_one(user.model_dump(), session=session)
                await db.exchange_accounts.insert_one(account.model_dump(), session=session)
        return {
            "status": "success",
            "eligible": True,
            "msg": "telegram account has been added to the system",
        }

    except DuplicateKeyError as e:
        err = str(e)
        if "index: telegram_id_1" in err:
            return {"status": "failed", "eligible": False, "msg": "telegram account has been verified before"}
        if "index: exchange_name_1_exchange_uid_1" in err:
            return {"status": "failed", "eligible": False, "msg": "exchange account is already verified for another user"}
        logger.error("Unexpected DuplicateKeyError: %s", e)
        return {"status": "failed", "eligible": False, "msg": "database error occurred"}

    except PyMongoError as e:
        logger.error("Database error in add_new_user: %s", e)
        return {"status": "failed", "eligible": False, "msg": "database error occurred"}


async def add_exchange_account(
    telegram_id: int,
    exchange_name: str,
    exchange_uid: int,
) -> OperationResult:
    """Link an additional exchange account to an already-existing user."""
    db = get_db()
    account = ExchangeAccount(
        telegram_id=telegram_id,
        exchange_name=exchange_name,  # type: ignore[arg-type]
        exchange_uid=exchange_uid,
    )
    try:
        await db.exchange_accounts.insert_one(account.model_dump())
        return {"status": "success", "msg": "New exchange account added"}
    except DuplicateKeyError:
        return {"status": "failed", "msg": "exchange account is already verified for another user"}
    except PyMongoError as e:
        logger.error("Database error in add_exchange_account: %s", e)
        return {"status": "failed", "msg": "database error occurred"}


async def get_user_with_accounts(telegram_id: int) -> UserLookupResult:
    db = get_db()
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        return {"status": "failed", "user": None, "exchange_accounts": [], "msg": "user not found"}

    accounts = await db.exchange_accounts.find(
        {"telegram_id": telegram_id}, {"_id": 0}
    ).to_list(None)
    return {"status": "success", "user": user, "exchange_accounts": accounts}


async def get_account_by_uid(exchange_uid: int, exchange_name: str) -> AccountLookupResult:
    db = get_db()
    account = await db.exchange_accounts.find_one(
        {"exchange_uid": exchange_uid, "exchange_name": exchange_name},
        {"_id": 0},
    )
    if not account:
        return {"status": "failed", "account": None, "user": None, "msg": "exchange account not found"}

    user = await db.users.find_one({"telegram_id": account["telegram_id"]}, {"_id": 0})
    return {"status": "success", "account": account, "user": user}
