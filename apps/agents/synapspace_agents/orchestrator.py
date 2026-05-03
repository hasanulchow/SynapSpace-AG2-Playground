from uuid import uuid4

from .ag2_runtime import run_live_ag2, runtime_status
from .models import AgentEvent, EventPlan, RunResponse


def run_event_playground(idea: str) -> RunResponse:
    """Run live AG2 when configured, otherwise keep the demo reliable."""

    status = runtime_status()
    if status.engine == "ag2-beta-live":
        try:
            return run_live_ag2(idea)
        except Exception:
            # Keep the hackathon demo working even if a provider request fails.
            return run_deterministic_playground(idea, reason="AG2 beta live run failed; using fallback")

    return run_deterministic_playground(idea, reason="AG2 beta or model credentials not configured")


def run_deterministic_playground(idea: str, reason: str) -> RunResponse:
    """Deterministic fallback for local demos and CI."""

    events = [
        AgentEvent(
            agent="Planner Agent",
            role="Proposer",
            status="thinking",
            message=f"Created the first event operating plan from: {idea}.",
            engine="deterministic-fallback",
        ),
        AgentEvent(
            agent="Challenger Agent",
            role="Critic",
            status="challenging",
            message="Challenged the plan on budget, venue constraints, audience quality, and approval timing.",
            engine="deterministic-fallback",
        ),
        AgentEvent(
            agent="Refiner Agent",
            role="Experience designer",
            status="refining",
            message="Refined the event around curated intros, practical talks, and fewer organizer decisions.",
            engine="deterministic-fallback",
        ),
        AgentEvent(
            agent="Social Agent",
            role="Growth operator",
            status="refining",
            message="Prepared a demand-led launch using people already searching for related events.",
            engine="deterministic-fallback",
        ),
        AgentEvent(
            agent="Matchmaker Agent",
            role="Network strategist",
            status="complete",
            message="Designed a matching graph so attendees meet the right people, not just more people.",
            engine="deterministic-fallback",
        ),
        AgentEvent(
            agent="Governance Agent",
            role="Human approval",
            status="approval",
            message="Reduced the final handoff to four approvals: venue, audience, budget, and outreach tone.",
            engine="deterministic-fallback",
        ),
    ]

    plan = EventPlan(
        title="SynapSpace Agentic Event",
        audience="Founders, builders, operators, and community leaders with shared intent",
        venue="Flexible venue selected after capacity, budget, and vibe checks",
        marketing="Intent-based social campaign plus partner community distribution",
        matching="Pre-event attendee graph with warm intro prompts and meeting windows",
        approvals=["Venue", "Audience", "Budget", "Outreach tone"],
    )

    return RunResponse(
        runId=f"run-{uuid4()}",
        summary=reason,
        engine="deterministic-fallback",
        events=events,
        plan=plan,
    )
