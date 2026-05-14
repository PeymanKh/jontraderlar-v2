"""LLM model factory and message helpers."""
from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import LLMProvider, settings
from app.workflow.prompts import GENERAL_SYSTEM, ROUTER_SYSTEM
from app.workflow.state import WorkflowState


def create_chat_model():
    """Build a LangChain chat model from the configured provider."""
    if settings.model.provider == LLMProvider.google:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.model.model_name,
            api_key=settings.model.api_key.get_secret_value(),
            temperature=settings.model.temperature,
        )

    if settings.model.provider == LLMProvider.openai:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.model.model_name,
            api_key=settings.model.api_key.get_secret_value(),
            temperature=settings.model.temperature,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.model.provider}")


def router_messages(state: WorkflowState) -> list:
    return [
        SystemMessage(content=ROUTER_SYSTEM),
        HumanMessage(content=state.user_message),
    ]


def general_messages(state: WorkflowState) -> list:
    return [
        SystemMessage(content=GENERAL_SYSTEM),
        HumanMessage(content=state.user_message),
    ]
