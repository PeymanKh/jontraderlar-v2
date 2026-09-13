"""General-purpose node — answers free-form Turkish questions via the LLM."""
from __future__ import annotations

from app.logging import get_logger
from app.messages import Errors
from app.workflow.llm import create_chat_model, general_messages
from app.workflow.state import WorkflowState

logger = get_logger(__name__)


async def general_node(state: WorkflowState) -> WorkflowState:
    logger.info("general_node start")

    try:
        model = create_chat_model()
        response = await model.ainvoke(general_messages(state))

        # Newer Gemini models return content as a list of blocks;
        # older ones return a plain string. Handle both.
        raw = response.content
        if isinstance(raw, list):
            raw = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in raw
            )
        content = (raw or "").strip()

        if not content:
            logger.warning("general_node: empty LLM response, using fallback")
            content = Errors.UNEXPECTED

        return state.model_copy(update={"response_message": content})

    except Exception as e:
        logger.error("general_node unexpected error: %s", e, exc_info=True)
        return state.model_copy(update={"response_message": Errors.UNEXPECTED})
