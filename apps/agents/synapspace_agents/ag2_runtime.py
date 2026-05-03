import asyncio
import os
from dataclasses import dataclass
from typing import Any

from .context_memory import SharedContextMemory
from .models import AgentEvent, EventPlan, RunResponse


AGENT_SPECS = [
    (
        "Master Orchestrator",
        "Orchestrator",
        "Build the event dependency graph, decide which specialist should act next, and surface only organizer decisions.",
        "thinking",
    ),
    (
        "Safety Guardrail",
        "Safety reviewer",
        "Screen policy, permits, spending risk, outbound communication risk, and anything that needs human review.",
        "challenging",
    ),
    (
        "Venue Scout",
        "Venue specialist",
        "Find venue options that match capacity, budget, vibe, location, availability, and contract risk.",
        "refining",
    ),
    (
        "Vendor Coordinator",
        "Logistics specialist",
        "Coordinate food, A/V, photo, signage, setup windows, vendor quotes, and operational tradeoffs.",
        "refining",
    ),
    (
        "Outreach Agent",
        "Speaker and guest scout",
        "Find speakers and guests worth inviting, draft personalized pitches, and sequence follow-ups after approval.",
        "refining",
    ),
    (
        "Content Agent",
        "Marketing producer",
        "Create launch copy, email reminders, partner blurbs, recap content, and platform-specific variants.",
        "refining",
    ),
    (
        "Marketing Trust Agent",
        "Growth operator",
        "Use public social intent, location, availability, and consent signals to invite only people likely to want this event. Suppress broad blasts, spam-like outreach, phishing-like language, unknown-consent targets, and recently-contacted people so AG2 protects site reputation and acquisition cost.",
        "refining",
    ),
    (
        "Payments Agent",
        "Money operator",
        "Prepare checkout, reconcile revenue, model platform fees, queue vendor payments, and explain the money flow.",
        "refining",
    ),
    (
        "Timeline Agent",
        "Schedule operator",
        "Coordinate deadlines, reminders, content drops, setup windows, day-of run of show, and delayed decisions.",
        "refining",
    ),
    (
        "Attendee Matchmaker",
        "Network strategist",
        "Score attendee fit, explain why each introduction matters, and design warm intro moments.",
        "complete",
    ),
    (
        "Follow-up Agent",
        "Post-event operator",
        "Turn event conversations into follow-up drafts, action items, CRM exports, and relationship loops.",
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
    model_configured = bool(_api_key())
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

    api_key = _api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for live AG2 beta execution")

    config = _openai_config(OpenAIConfig, api_key)
    return asyncio.run(_run_live_ag2_async(idea, Agent, config))


async def _run_live_ag2_async(idea: str, agent_cls: Any, config: Any) -> RunResponse:
    events: list[AgentEvent] = []
    memory = SharedContextMemory(idea)

    for name, role, instruction, status in AGENT_SPECS:
        memory_reads = memory.read_count()
        agent = agent_cls(
            _agent_name(name),
            prompt=(
                f"You are {name}, role: {role}. {instruction} "
                "Read the shared context memory before acting, then add one useful update for the next agent. "
                "Reply in 2-4 concise sentences. Do not use markdown tables."
            ),
            config=config,
        )

        reply = await agent.ask(
            f"{memory.prompt()}\n\nContribute your specialist update for the SynapSpace event plan."
        )
        message = _extract_message(reply)
        memory_writes = memory.record(name, role, message)
        events.append(
            AgentEvent(
                agent=name,
                role=role,
                status=status,
                message=message,
                engine="ag2-beta-live",
                memoryReads=memory_reads,
                memoryWrites=memory_writes,
            )
        )

    return RunResponse(
        runId="ag2-beta-live-run",
        summary="Live AG2 beta multi-agent run complete",
        engine="ag2-beta-live",
        events=events,
        plan=_plan_from_events(idea, events),
        memory=memory.snapshot(),
    )


def _agent_name(label: str) -> str:
    return label.lower().replace(" ", "_")


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


def _extract_message(result: Any) -> str:
    body = getattr(result, "body", None)
    if isinstance(body, str) and body.strip():
        return body.strip()

    summary = getattr(result, "summary", None)
    if isinstance(summary, str) and summary.strip():
        return summary.strip()

    return "Agent completed its step and passed context to the next specialist."


def _plan_from_events(idea: str, events: list[AgentEvent]) -> EventPlan:
    venue = _find_event(events, "Venue Scout")
    content = _find_event(events, "Content Agent")
    social = _find_event(events, "Marketing Trust Agent")
    matchmaker = _find_event(events, "Attendee Matchmaker")
    followup = _find_event(events, "Follow-up Agent")

    return EventPlan(
        title="AG2 beta-orchestrated SynapSpace Event OS",
        audience=f"Qualified audience inferred from: {idea}",
        venue=venue.message if venue else "Venue Scout ranks venue options after safety and budget checks.",
        marketing=(
            f"{content.message if content else 'Content Agent prepares launch copy.'} "
            f"{social.message if social else 'Marketing Trust Agent targets expressed event intent without spam risk.'}"
        ),
        matching=matchmaker.message if matchmaker else "Attendee Matchmaker designs high-value attendee introductions.",
        approvals=_approval_list(followup.message if followup else ""),
    )


def _find_event(events: list[AgentEvent], agent: str) -> AgentEvent | None:
    return next((event for event in events if event.agent == agent), None)


def _approval_list(text: str) -> list[str]:
    normalized = text.lower()
    defaults = ["Venue", "Budget", "Audience", "Outreach tone"]
    approvals = [item for item in defaults if item.lower().split()[0] in normalized]
    return approvals or defaults
