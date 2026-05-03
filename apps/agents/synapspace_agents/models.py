from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    idea: str = Field(min_length=3)


class AgentEvent(BaseModel):
    agent: str
    role: str
    status: str
    message: str
    engine: str = "deterministic"


class EventPlan(BaseModel):
    title: str
    audience: str
    venue: str
    marketing: str
    matching: str
    approvals: list[str]


class RunResponse(BaseModel):
    runId: str
    summary: str
    engine: str
    events: list[AgentEvent]
    plan: EventPlan
    approvalsRequired: bool = True


class CapabilityResponse(BaseModel):
    ag2Installed: bool
    modelConfigured: bool
    engine: str
    patterns: list[str]
