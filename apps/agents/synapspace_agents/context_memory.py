from .models import ContextMemory, MemoryEntry


class SharedContextMemory:
    """Run-scoped memory that agents read from and write to during orchestration."""

    def __init__(self, idea: str):
        self.idea = idea
        self.entries: list[MemoryEntry] = [
            MemoryEntry(
                agent="Organizer",
                signal="event-intent",
                content=f"Original organizer idea: {idea}",
            )
        ]
        self.decisions: list[str] = []
        self.risks: list[str] = []
        self.handoffs: list[str] = []

    def read_count(self) -> int:
        return len(self.entries)

    def prompt(self) -> str:
        timeline = "\n".join(
            f"- {entry.agent} [{entry.signal}]: {entry.content}" for entry in self.entries[-8:]
        )
        decisions = _format_list(self.decisions, "No decisions captured yet.")
        risks = _format_list(self.risks, "No risks captured yet.")
        handoffs = _format_list(self.handoffs, "No handoffs captured yet.")
        return (
            "Shared context memory for this event run:\n"
            f"{timeline}\n\n"
            f"Decisions:\n{decisions}\n\n"
            f"Risks:\n{risks}\n\n"
            f"Handoffs:\n{handoffs}\n\n"
            "Use this memory to build on prior agents. Do not restart from scratch."
        )

    def record(self, agent: str, role: str, message: str) -> list[str]:
        signal = _signal_for_role(role)
        short_message = _shorten(message)
        writes = [signal]

        self.entries.append(MemoryEntry(agent=agent, signal=signal, content=short_message))

        if role == "Orchestrator":
            decision = "Event dependency graph drafted"
            self.decisions.append(decision)
            writes.append(decision)
        elif role == "Safety reviewer":
            risk = "Policy, permit, spend, and outbound risks reviewed"
            self.risks.append(risk)
            writes.append(risk)
        elif role == "Venue specialist":
            decision = "Venue requirements and shortlist criteria captured"
            self.decisions.append(decision)
            writes.append(decision)
        elif role == "Logistics specialist":
            handoff = "Vendor quote and setup dependencies captured"
            self.handoffs.append(handoff)
            writes.append(handoff)
        elif role == "Speaker and guest scout":
            handoff = "Speaker and guest outreach inputs prepared for content"
            self.handoffs.append(handoff)
            writes.append(handoff)
        elif role == "Marketing producer":
            decision = "Launch content direction prepared"
            self.decisions.append(decision)
            writes.append(decision)
        elif role == "Growth operator":
            handoff = "Marketing Trust Agent should invite only high-intent people with safe consent, location fit, availability, and low spam risk"
            self.handoffs.append(handoff)
            writes.append(handoff)
        elif role == "Money operator":
            risk = "Revenue, platform fee, reserve, and vendor payment flow reviewed"
            self.risks.append(risk)
            writes.append(risk)
        elif role == "Schedule operator":
            handoff = "Timeline now controls launch, setup, reminders, and day-of sequence"
            self.handoffs.append(handoff)
            writes.append(handoff)
        elif role == "Network strategist":
            handoff = "Matchmaking graph feeds intro prompts and follow-up windows"
            self.handoffs.append(handoff)
            writes.append(handoff)
        elif role == "Post-event operator":
            decision = "Final external actions require organizer approval"
            self.decisions.append(decision)
            writes.append(decision)

        return writes

    def snapshot(self) -> ContextMemory:
        return ContextMemory(
            activeBrief=(
                f"{len(self.entries)} memory entries connect the agent team around: {self.idea}"
            ),
            entries=self.entries,
            decisions=self.decisions,
            risks=self.risks,
            handoffs=self.handoffs,
        )


def _format_list(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items[-5:])


def _signal_for_role(role: str) -> str:
    signals = {
        "Orchestrator": "dependency-graph",
        "Safety reviewer": "safety",
        "Venue specialist": "venue",
        "Logistics specialist": "vendors",
        "Speaker and guest scout": "outreach",
        "Marketing producer": "content",
        "Growth operator": "trust-marketing",
        "Money operator": "money",
        "Schedule operator": "timeline",
        "Network strategist": "matching",
        "Post-event operator": "follow-up",
    }
    return signals.get(role, "update")


def _shorten(text: str, limit: int = 260) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[: limit - 3]}..."
