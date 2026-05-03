import os
from typing import Any

from fastapi import Header
from fastapi.responses import StreamingResponse


def ag_ui_available() -> bool:
    try:
        from autogen.beta import Agent  # noqa: F401
        from autogen.beta.ag_ui import AGUIStream  # noqa: F401
        from autogen.beta.config import OpenAIConfig  # noqa: F401
    except Exception:
        return False
    return bool(_api_key())


def build_ag_ui_stream() -> Any:
    try:
        from autogen.beta import Agent
        from autogen.beta.ag_ui import AGUIStream
        from autogen.beta.config import OpenAIConfig
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("AG2 beta AG-UI dependencies are not installed") from exc

    api_key = _api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for AG-UI streaming")

    agent = Agent(
        "synapspace_ag_ui_agent",
        prompt=(
            "You are SynapSpace AG2 Playground, an agentic event operating system. "
            "Help organizers create events, coordinate specialist agents, explain approvals, "
            "and produce concise plans. Surface human approval checkpoints before external actions."
        ),
        config=_openai_config(OpenAIConfig, api_key),
    )
    return AGUIStream(agent)


async def dispatch_ag_ui(message: Any, accept: str | None = Header(None)) -> StreamingResponse:
    stream = build_ag_ui_stream()
    return StreamingResponse(
        stream.dispatch(message, accept=accept),
        media_type=accept or "text/event-stream",
    )


def _api_key() -> str | None:
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("AG2_API_KEY")


def _base_url() -> str | None:
    return os.environ.get("AG2_BASE_URL") or os.environ.get("OPENAI_BASE_URL")


def _openai_config(config_cls: Any, api_key: str) -> Any:
    kwargs = {
        "model": os.environ.get("AG2_MODEL", "gpt-4o-mini"),
        "api_key": api_key,
        "streaming": True,
    }
    base_url = _base_url()
    if base_url:
        kwargs["base_url"] = base_url
    return config_cls(**kwargs)
