from __future__ import annotations

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
    engine: str


def runtime_status() -> RuntimeStatus:
    return RuntimeStatus(
        ag2_installed=_can_import_ag2(),
        model_configured=bool(os.environ.get("OPENAI_API_KEY")),
        engine="ag2-live" if _can_import_ag2() and os.environ.get("OPENAI_API_KEY") else "deterministic-fallback",
    )


def _can_import_ag2() -> bool:
    try:
        import autogen  # noqa: F401
    except Exception:
        return False
    return True


def run_live_ag2(idea: str) -> RunResponse:
    """Run the actual AG2 ConversableAgent workflow.

    This uses AG2's ConversableAgent + initiate_chat flow. It is intentionally
    sequential for demo legibility: each specialist receives the original event
    idea plus the prior agents' outputs, then contributes its own result.
    """

    try:
        from autogen import ConversableAgent, LLMConfig
    except Exception as exc:  # pragma: no cover - exercised when dependency missing
        raise RuntimeError("AG2 is not installed. Run: pip install -e apps/agents") from exc

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for live AG2 execution")

    model = os.environ.get("AG2_MODEL", "gpt-4o-mini")
    llm_config = LLMConfig(
        {
            "api_type": "openai",
            "model": model,
            "api_key": api_key,
        },
        cache_seed=None,
    )

    events: list[AgentEvent] = []
    shared_context = f"Original organizer idea: {idea}\n\n"

    with llm_config:
        user_proxy = ConversableAgent(
            name="human_approval_proxy",
            system_message="You represent the organizer. Do not invent approvals; ask agents for concise output.",
            llm_config=False,
            human_input_mode="NEVER",
            default_auto_reply="Continue.",
        )

        for name, role, instruction, status in AGENT_SPECS:
            agent = ConversableAgent(
                name=_agent_name(name),
                system_message=(
                    f"You are {name}, role: {role}. {instruction} "
                    "Reply in 2-4 concise sentences. Do not use markdown tables."
                ),
                human_input_mode="NEVER",
            )

            result = user_proxy.initiate_chat(
                recipient=agent,
                message=(
                    f"{shared_context}\n"
                    "Contribute your specialist update for the SynapSpace event plan."
                ),
                max_turns=1,
                silent=True,
            )
            message = _extract_message(result)
            shared_context += f"{name}: {message}\n\n"
            events.append(
                AgentEvent(
                    agent=name,
                    role=role,
                    status=status,
                    message=message,
                    engine="ag2-live",
                )
            )

    return RunResponse(
        runId="ag2-live-run",
        summary="Live AG2 multi-agent run complete",
        engine="ag2-live",
        events=events,
        plan=_plan_from_events(idea, events),
    )


def _agent_name(label: str) -> str:
    return label.lower().replace(" ", "_")


def _extract_message(result: Any) -> str:
    summary = getattr(result, "summary", None)
    if isinstance(summary, str) and summary.strip():
        return summary.strip()

    chat_history = getattr(result, "chat_history", None)
    if isinstance(chat_history, list):
        for item in reversed(chat_history):
            if isinstance(item, dict):
                content = item.get("content")
                if isinstance(content, str) and content.strip():
                    return content.strip()

    return "Agent completed its step and passed context to the next specialist."


def _plan_from_events(idea: str, events: list[AgentEvent]) -> EventPlan:
    social = _find_event(events, "Social Agent")
    matchmaker = _find_event(events, "Matchmaker Agent")
    governance = _find_event(events, "Governance Agent")

    return EventPlan(
        title="AG2-orchestrated SynapSpace Event",
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
