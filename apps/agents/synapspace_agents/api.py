from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .ag2_runtime import runtime_status
from .models import CapabilityResponse, RunRequest, RunResponse
from .orchestrator import run_event_playground


app = FastAPI(title="SynapSpace AG2 Agent Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "synapspace-ag2-agents"}


@app.get("/capabilities", response_model=CapabilityResponse)
def capabilities() -> CapabilityResponse:
    status = runtime_status()
    return CapabilityResponse(
        ag2Installed=status.ag2_installed,
        modelConfigured=status.model_configured,
        engine=status.engine,
        patterns=[
            "ConversableAgent",
            "initiate_chat",
            "sequential specialist pipeline",
            "human approval checkpoint",
            "deterministic fallback",
        ],
    )


@app.post("/run", response_model=RunResponse)
def run_agents(request: RunRequest) -> RunResponse:
    return run_event_playground(request.idea)
