import asyncio
import os
from dataclasses import dataclass
from typing import Any

from .models import AgentEvent, EventPlan, RunResponse


AGENT_SPECS = [
    (
        "Planner Agent",
        "Proposer",
        "Create a practical event operating plan. Include venue, audience, schedule, budget, and success metric.",
        "thinking",
    ),
    (
        "Challenger Agent",
        "Critic",
        "Challenge the plan. Find risks, missing constraints, safety issues, budget gaps, and assumptions.",
        "challenging",
    ),
    (
        "Refiner Agent",
        "Experience designer",
        "Improve the plan so attendees meet the right people and the organizer has fewer decisions.",
        "refining",
    ),
    (
        "Social Agent",
        "Growth operator",
        "Create audience targeting, social posts, ad angles, and community-safe outreach strategy.",
        "refining",
    ),
    (
        "Matchmaker Agent",
        "Network strategist",
        "Design attendee matching, intro logic, and follow-up flow for high-value relationships.",
        "complete",
    ),
    (
        "Governance Agent",
        "Human approval",
        "Summarize final approvals needed before external actions happen. Keep this short and explicit.",
        "approval",
    ),
]


@dataclass(frozen=True)
class RuntimeStatus:
    ag2_installed: bool
    model_configured: bool
    ag_ui_available: bool
    engine: str


def runtime_status() -> RuntimeStatus:
    ag2_installed = _can_import_ag2_beta()
    model_configured = bool(os.environ.get("OPENAI_API_KEY"))
    ag_ui_ready = _can_import_ag_ui() and model_configured
    return RuntimeStatus(
        ag2_installed=ag2_installed,
        model_configured=model_configured,
        ag_ui_available=ag_ui_ready,
        engine="ag2-beta-live" if ag2_installed and model_configured else "deterministic-fallback",
    )


def _can_import_ag2_beta() -> bool:
    try:
        from autogen.beta import Agent  # noqa: F401
        from autogen.beta.config import OpenAIConfig  # noqa: F401
    except Exception:
        return False
    return True


def _can_import_ag_ui() -> bool:
    try:
        from autogen.beta.ag_ui import AGUIStream  # noqa: F401
    except Exception:
        return False
    return True


def run_live_ag2(idea: str) -> RunResponse:
    """Run the AG2 beta Agent workflow."""

    try:
        from autogen.beta import Agent
        from autogen.beta.config import OpenAIConfig
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("AG2 beta is not installed. Run: pip install -e apps/agents") from exc

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for live AG2 beta execution")

    config = OpenAIConfig(
        model=os.environ.get("AG2_MODEL", "gpt-4o-mini"),
        api_key=api_key,
        streaming=True,
    )
    return asyncio.run(_run_live_ag2_async(idea, Agent, config))


async def _run_live_ag2_async(idea: str, agent_cls: Any, config: Any) -> RunResponse:
    events: list[AgentEvent] = []
    shared_context = f"Original organizer idea: {idea}\n\n"

    for name, role, instruction, status in AGENT_SPECS:
        agent = agent_cls(
            _agent_name(name),
            prompt=(
                f"You are {name}, role: {role}. {instruction} "
                "Reply in 2-4 concise sentences. Do not use markdown tables."
            ),
            config=config,
        )

        reply = await agent.ask(
            f"{shared_context}\nContribute your specialist update for the SynapSpace event plan."
        )
        message = _extract_message(reply)
        shared_context += f"{name}: {message}\n\n"
        events.append(
            AgentEvent(
                agent=name,
                role=role,
                status=status,
                message=message,
                engine="ag2-beta-live",
            )
        )

    return RunResponse(
        runId="ag2-beta-live-run",
        summary="Live AG2 beta multi-agent run complete",
        engine="ag2-beta-live",
        events=events,
        plan=_plan_from_events(idea, events),
    )


def _agent_name(label: str) -> str:
    return label.lower().replace(" ", "_")


def _extract_message(result: Any) -> str:
    body = getattr(result, "body", None)
    if isinstance(body, str) and body.strip():
        return body.strip()

    summary = getattr(result, "summary", None)
    if isinstance(summary, str) and summary.strip():
        return summary.strip()

    return "Agent completed its step and passed context to the next specialist."


def _plan_from_events(idea: str, events: list[AgentEvent]) -> EventPlan:
    social = _find_event(events, "Social Agent")
    matchmaker = _find_event(events, "Matchmaker Agent")
    governance = _find_event(events, "Governance Agent")

    return EventPlan(
        title="AG2 beta-orchestrated SynapSpace Event",
        audience=f"Qualified audience inferred from: {idea}",
        venue="Venue choice is routed through the Planner and Challenger recommendations.",
        marketing=social.message if social else "Social Agent prepares intent-based launch content.",
        matching=matchmaker.message if matchmaker else "Matchmaker Agent designs high-value attendee introductions.",
        approvals=_approval_list(governance.message if governance else ""),
    )


def _find_event(events: list[AgentEvent], agent: str) -> AgentEvent | None:
    return next((event for event in events if event.agent == agent), None)


def _approval_list(text: str) -> list[str]:
    normalized = text.lower()
    defaults = ["Venue", "Budget", "Audience", "Outreach tone"]
    approvals = [item for item in defaults if item.lower().split()[0] in normalized]
    return approvals or defaults
