"""LangGraph workflow state and shared enums."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Route(str, Enum):
    general = "general"
    verification = "verification"
    error = "error"


class EligibilityStatus(str, Enum):
    eligible = "eligible"
    not_eligible = "not_eligible"


class UserMetadata(BaseModel):
    telegram_id: int
    telegram_username: str
    telegram_full_name: str


class RouterOutput(BaseModel):
    route: Route
    exchange: str | None = None
    uid: int | None = Field(default=None, gt=0)
    missing_data: bool = False
    unsupported_exchange: bool = False
    invalid_uid_format: bool = False


class ExchangeVerificationResult(BaseModel):
    eligibility_status: EligibilityStatus
    is_successful: bool
    error_message: str | None = None


class DatabaseOperationResult(BaseModel):
    eligibility_status: EligibilityStatus
    is_successful: bool
    error_message: str | None = None


class InviteLinkResult(BaseModel):
    is_successful: bool
    group_invitation_url: str | None = None
    error_message: str | None = None


class WorkflowState(BaseModel):
    """LangGraph state — passed unchanged between every node."""

    user_metadata: UserMetadata
    user_message: str
    response_message: str | None = None

    router: RouterOutput | None = None
    exchange_verification_result: ExchangeVerificationResult | None = None
    database_operation_result: DatabaseOperationResult | None = None
    invite_link_result: InviteLinkResult | None = None

    pending_confirmation: bool = False
    pending_action_data: dict[str, Any] | None = None
