from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .ag_ui_runtime import ag_ui_available, dispatch_ag_ui
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
        agUiAvailable=status.ag_ui_available,
        engine=status.engine,
        patterns=[
            "AG2 beta Agent",
            "Agent.ask",
            "AG-UI streaming",
            "sequential specialist pipeline",
            "human approval checkpoint",
            "deterministic fallback",
        ],
    )


@app.post("/run", response_model=RunResponse)
def run_agents(request: RunRequest) -> RunResponse:
    return run_event_playground(request.idea)


@app.post("/ag-ui/chat")
async def ag_ui_chat(message: dict, accept: str | None = Header(None)):
    if not ag_ui_available():
        return JSONResponse(
            {
                "error": "AG-UI is not available. Install ag2[ag-ui,openai] on Python 3.10-3.13 and set OPENAI_API_KEY.",
                "engine": "deterministic-fallback",
            },
            status_code=503,
        )
    return await dispatch_ag_ui(message, accept=accept)
