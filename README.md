# SynapSpace AG2 Beta Playground

A hackathon-ready multi-agent event operating system built around AG2 beta and AG-UI.

Users enter an event idea and watch specialized agents coordinate:

- Planner Agent turns the idea into a concrete event plan.
- Challenger Agent finds risks, gaps, and budget problems.
- Refiner Agent improves attendee experience.
- Social Agent creates launch content and market strategy.
- Matchmaker Agent designs high-value networking.
- Governance Agent summarizes what needs human approval.

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
  "engine": "deterministic-fallback"
}
```
