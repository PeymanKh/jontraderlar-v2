"""LangGraph state machine — wires the nodes together and adds the Mongo checkpointer."""
from __future__ import annotations

from typing import Any

from langgraph.checkpoint.mongodb import AsyncMongoDBSaver
from langgraph.graph import END, START, StateGraph
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.logging import get_logger
from app.workflow.nodes.database_check import database_check_node
from app.workflow.nodes.exchange_check import exchange_check_node
from app.workflow.nodes.follow_up import follow_up_node
from app.workflow.nodes.general import general_node
from app.workflow.nodes.router import router_node
from app.workflow.nodes.telegram_url import telegram_url_node
from app.workflow.state import EligibilityStatus, Route, WorkflowState

logger = get_logger(__name__)


# ---- routing predicates ----------------------------------------------------

def _entry(state: WorkflowState) -> str:
    return "follow_up" if state.pending_confirmation else "router"


def _after_router(state: WorkflowState) -> str:
    if state.router and state.router.route == Route.verification:
        return "exchange_check"
    if state.router and state.router.route == Route.general:
        return "general"
    return END


def _after_exchange_check(state: WorkflowState) -> str:
    if (
        state.exchange_verification_result
        and state.exchange_verification_result.eligibility_status == EligibilityStatus.eligible
    ):
        return "database_check"
    return END


def _after_database_check(state: WorkflowState) -> str:
    if (
        state.database_operation_result
        and state.database_operation_result.is_successful
        and not state.pending_confirmation
    ):
        return "telegram_url"
    return END


# ---- compilation -----------------------------------------------------------

_workflow: Any | None = None
_checkpoint_client: AsyncIOMotorClient | None = None


def build_graph() -> Any:
    """Build a compiled LangGraph with a fresh Mongo checkpointer client."""
    global _checkpoint_client

    workflow = StateGraph(WorkflowState)
    workflow.add_node("router", router_node)
    workflow.add_node("exchange_check", exchange_check_node)
    workflow.add_node("database_check", database_check_node)
    workflow.add_node("telegram_url", telegram_url_node)
    workflow.add_node("general", general_node)
    workflow.add_node("follow_up", follow_up_node)

    workflow.add_conditional_edges(START, _entry, {"router": "router", "follow_up": "follow_up"})
    workflow.add_conditional_edges("router", _after_router)
    workflow.add_conditional_edges("exchange_check", _after_exchange_check)
    workflow.add_conditional_edges("database_check", _after_database_check)
    workflow.add_edge("general", END)
    workflow.add_edge("telegram_url", END)
    workflow.add_edge("follow_up", END)

    _checkpoint_client = AsyncIOMotorClient(settings.database.uri.get_secret_value())
    checkpoint_db = _checkpoint_client[settings.database.checkpoint_name]
    checkpointer = AsyncMongoDBSaver(checkpoint_db, versions_to_keep=1)

    return workflow.compile(checkpointer=checkpointer)


def get_workflow() -> Any:
    """Singleton accessor — compiles the graph the first time it is called."""
    global _workflow
    if _workflow is None:
        _workflow = build_graph()
        logger.info("LangGraph workflow compiled")
    return _workflow


async def close_workflow() -> None:
    global _workflow, _checkpoint_client
    if _checkpoint_client is not None:
        _checkpoint_client.close()
        logger.info("LangGraph checkpoint client closed")
    _workflow = None
    _checkpoint_client = None
