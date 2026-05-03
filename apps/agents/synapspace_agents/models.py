from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    idea: str = Field(min_length=3)


class AgentEvent(BaseModel):
    agent: str
    role: str
    status: str
    message: str
    engine: str = "deterministic"
    memoryReads: int = 0
    memoryWrites: list[str] = Field(default_factory=list)


class EventPlan(BaseModel):
    title: str
    audience: str
    venue: str
    marketing: str
    matching: str
    approvals: list[str]


class MemoryEntry(BaseModel):
    agent: str
    signal: str
    content: str


class ContextMemory(BaseModel):
    activeBrief: str
    entries: list[MemoryEntry]
    decisions: list[str]
    risks: list[str]
    handoffs: list[str]


class RunResponse(BaseModel):
    runId: str
    summary: str
    engine: str
    events: list[AgentEvent]
    plan: EventPlan
    memory: ContextMemory
    approvalsRequired: bool = True


class CapabilityResponse(BaseModel):
    ag2Installed: bool
    modelConfigured: bool
    agUiAvailable: bool
    engine: str
    patterns: list[str]
