# SynapSpace AG2 Playground

A hackathon-ready multi-agent event operating system built around AG2 Playground concepts.

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

## AG2 Notes

The service is structured for AG2:

- Round-robin proposer/challenger/refiner style collaboration.
- Sequential event-building pipeline.
- Human approval checkpoint at the end.
- Deterministic fallback so the demo runs even without model credentials.

To enable live AG2/OpenAI behavior, add your model provider variables in `apps/agents/.env`.

