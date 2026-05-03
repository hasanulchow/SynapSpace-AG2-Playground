from __future__ import annotations

from uuid import uuid4

from .models import AgentEvent, EventPlan, RunResponse


def run_event_playground(idea: str) -> RunResponse:
    """AG2-ready deterministic orchestration.

    This is intentionally deterministic for hackathon demos. The module boundary
    is where live AG2 AssistantAgent / UserProxyAgent / group chat logic can be
    swapped in when model credentials are available.
    """

    events = [
        AgentEvent(
            agent="Planner Agent",
            role="Proposer",
            status="thinking",
            message=f"Created the first event operating plan from: {idea}.",
        ),
        AgentEvent(
            agent="Challenger Agent",
            role="Critic",
            status="challenging",
            message="Challenged the plan on budget, venue constraints, audience quality, and approval timing.",
        ),
        AgentEvent(
            agent="Refiner Agent",
            role="Experience designer",
            status="refining",
            message="Refined the event around curated intros, practical talks, and fewer organizer decisions.",
        ),
        AgentEvent(
            agent="Social Agent",
            role="Growth operator",
            status="refining",
            message="Prepared a demand-led launch using people already searching for related events.",
        ),
        AgentEvent(
            agent="Matchmaker Agent",
            role="Network strategist",
            status="complete",
            message="Designed a matching graph so attendees meet the right people, not just more people.",
        ),
        AgentEvent(
            agent="Governance Agent",
            role="Human approval",
            status="approval",
            message="Reduced the final handoff to four approvals: venue, audience, budget, and outreach tone.",
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
        summary="AG2-style multi-agent run complete",
        events=events,
        plan=plan,
    )

