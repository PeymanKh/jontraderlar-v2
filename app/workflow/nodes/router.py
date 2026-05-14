"""Router node — classify user message and extract verification data via LLM."""
from __future__ import annotations

from pydantic import ValidationError

from app.logging import get_logger
from app.messages import Errors
from app.workflow.llm import create_chat_model, router_messages
from app.workflow.state import Route, RouterOutput, WorkflowState

logger = get_logger(__name__)


async def router_node(state: WorkflowState) -> WorkflowState:
    logger.info("router_node start")

    try:
        model = create_chat_model()
        structured = model.with_structured_output(RouterOutput, method="json_mode")
        result: RouterOutput = await structured.ainvoke(router_messages(state))

        updated = state.model_copy(update={"router": result})

        if result.route == Route.verification:
            error_route = result.model_copy(update={"route": Route.error})

            if result.unsupported_exchange:
                return updated.model_copy(update={"router": error_route, "response_message": Errors.UNSUPPORTED_EXCHANGE})
            if result.invalid_uid_format:
                return updated.model_copy(update={"router": error_route, "response_message": Errors.INVALID_UID_FORMAT})
            if result.missing_data:
                return updated.model_copy(update={"router": error_route, "response_message": Errors.MISSING_VERIFICATION_DATA})

        return updated

    except ValidationError as e:
        logger.error("router_node validation failed: %s", e, exc_info=True)
        return state.model_copy(update={
            "router": RouterOutput(route=Route.error),
            "response_message": Errors.UNEXPECTED,
        })
    except Exception as e:
        logger.error("router_node unexpected error: %s", e, exc_info=True)
        return state.model_copy(update={
            "router": RouterOutput(route=Route.error),
            "response_message": Errors.UNEXPECTED,
        })
