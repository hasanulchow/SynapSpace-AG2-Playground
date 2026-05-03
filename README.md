# SynapSpace AG2 Beta Playground

A hackathon-ready multi-agent event operating system built around AG2 beta and AG-UI.

Users enter an event idea and watch the full 11-agent SynapSpace team coordinate:

1. Master Orchestrator builds the dependency graph.
2. Safety Guardrail reviews risk before external action.
3. Venue Scout ranks rooms by capacity, budget, and vibe.
4. Vendor Coordinator handles food, A/V, photo, signage, and setup.
5. Outreach Agent finds speakers and high-value guests.
6. Content Agent creates launch copy and reminders.
7. Marketing Trust Agent invites high-intent people while suppressing spam-risk outreach.
8. Payments Agent explains revenue and queued payments.
9. Timeline Agent sequences deadlines and day-of flow.
10. Attendee Matchmaker designs high-value introductions.
11. Follow-up Agent turns meetings into next steps.

## Stack

- `apps/web`: Next.js playground interface
- `apps/agents`: Python FastAPI service with AG2-ready orchestration
- `packages/shared`: shared schemas and examples

## Quick Start

### Web

```bash
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`.

### Agents

```bash
cd apps/agents
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn synapspace_agents.api:app --reload --port 8000
```

The web app will call `http://localhost:8000/run`.

AG2 requires Python `>=3.10,<3.14`. If your machine only has Python 3.14, use Docker:

```bash
OPENAI_API_KEY="your-key" docker compose up --build agents
```

## AG2 Beta + AG-UI Implementation

The service now has a real AG2 runtime path and a deterministic fallback:

- Uses `autogen.beta.Agent`.
- Uses `autogen.beta.config.OpenAIConfig`.
- Starts each specialist step with async `Agent.ask(...)`.
- Shares a run-scoped context memory across all 11 agents for decisions, risks, handoffs, and timeline entries.
- Exposes an AG-UI endpoint at `/ag-ui/chat` using `AGUIStream`.
- The web app exposes `/api/ag-ui` as a frontend-safe proxy to the AG-UI backend.
- Runs a sequential specialist pipeline inspired by AG2 Playground patterns.
- Ends with a human approval checkpoint.
- Falls back to deterministic orchestration if AG2 or model credentials are missing.

To enable live AG2/OpenAI behavior:

```bash
cd apps/agents
cp .env.example .env
export OPENAI_API_KEY="your-key"
export AG2_MODEL="gpt-4o-mini"
uvicorn synapspace_agents.api:app --reload --port 8000
```

Check the active runtime:

```bash
curl http://127.0.0.1:8000/capabilities
```

Test AG-UI streaming:

```bash
curl -N -X POST http://127.0.0.1:8000/ag-ui/chat \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"thread_id":"t1","run_id":"r1","messages":[{"id":"m1","role":"user","content":"Plan an AI founder dinner in NYC"}],"state":{},"context":[],"tools":[]}'
```

Expected live runtime with dependencies and key:

```json
{
  "ag2Installed": true,
  "modelConfigured": true,
  "agUiAvailable": true,
  "engine": "ag2-beta-live"
}
```

Expected fallback runtime without credentials:

```json
{
  "engine": "deterministic-fallback",
  "events": [
    {
      "agent": "Planner Agent",
      "status": "thinking",
      "memoryReads": 1,
      "memoryWrites": ["plan", "Initial operating plan drafted"]
    }
  ],
  "memory": {
    "activeBrief": "7 memory entries connect the agent team around: ...",
    "decisions": ["Initial operating plan drafted"],
    "risks": ["Budget, venue, audience, and approval risks reviewed"],
    "handoffs": ["Social campaign should target people already showing event intent"]
  }
}
```
