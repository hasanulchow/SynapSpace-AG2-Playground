from uuid import uuid4

from .ag2_runtime import AGENT_SPECS, run_live_ag2, runtime_status
from .context_memory import SharedContextMemory
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

    memory = SharedContextMemory(idea)
    events = []

    for agent, role, _instruction, status in AGENT_SPECS:
        message = _fallback_message(agent, idea)
        memory_reads = memory.read_count()
        memory_writes = memory.record(agent, role, message)
        events.append(
            AgentEvent(
                agent=agent,
                role=role,
                status=status,
                message=message,
                engine="deterministic-fallback",
                memoryReads=memory_reads,
                memoryWrites=memory_writes,
            )
        )

    plan = EventPlan(
        title="SynapSpace Agentic Event",
        audience="Founders, builders, operators, and community leaders with shared intent",
        venue="Venue shortlist selected after safety, capacity, budget, contract, and vibe checks",
        marketing="Content Agent and Marketing Trust Agent coordinate reputation-safe intent-based launch campaigns",
        matching="Pre-event attendee graph with warm intro prompts and meeting windows",
        approvals=["Venue", "Audience", "Budget", "Outreach tone", "Vendor payments"],
    )

    return RunResponse(
        runId=f"run-{uuid4()}",
        summary=reason,
        engine="deterministic-fallback",
        events=events,
        plan=plan,
        memory=memory.snapshot(),
    )


def _fallback_message(agent: str, idea: str) -> str:
    messages = {
        "Master Orchestrator": f"Built the event dependency graph from: {idea}. Routed safety, venue, vendors, outreach, content, social, money, timeline, matchmaking, and follow-up as connected workstreams.",
        "Safety Guardrail": "Read the organizer intent and dependency graph, then flagged permit, spend, outbound messaging, and human approval checks before any external action.",
        "Venue Scout": "Used the safety memory to define venue requirements around capacity, budget, vibe, availability, and cancellation risk.",
        "Vendor Coordinator": "Used the venue memory to prepare catering, A/V, photography, signage, setup windows, and vendor quote dependencies.",
        "Outreach Agent": "Used the audience and venue memory to shortlist speakers and high-value guests with approval-ready invite tones.",
        "Content Agent": "Used speaker, venue, and audience memory to draft launch copy, reminder content, partner blurbs, and recap angles.",
        "Marketing Trust Agent": "Used public intent, location, availability, consent, and fatigue signals to prepare only high-fit invite drafts while suppressing spam-risk outreach.",
        "Payments Agent": "Used vendor and ticketing memory to explain revenue, platform fee, reserve, host payout, and queued vendor payments.",
        "Timeline Agent": "Used all prior dependencies to sequence approvals, content drops, vendor deadlines, reminders, setup, and day-of run of show.",
        "Attendee Matchmaker": "Used audience and social intent memory to design attendee fit scoring, warm intro prompts, and meeting windows.",
        "Follow-up Agent": "Read the full memory and prepared post-event drafts, action items, CRM export notes, and final organizer approval checkpoints.",
    }
    return messages.get(agent, "Read shared memory, added its specialist update, and passed context forward.")
