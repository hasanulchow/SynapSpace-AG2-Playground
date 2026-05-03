"use client";

import { FormEvent, useState } from "react";
import { Bot, BrainCircuit, CheckCircle2, Database, Network, Play, ShieldCheck, Sparkles, UsersRound } from "lucide-react";
import type { AgentRunResponse } from "@/lib/types";

const fallbackIdea = "AI networking event in NYC next month for 100 founders, builders, and design leaders";

const agents = [
  ["Master Orchestrator", "Builds the event dependency graph"],
  ["Safety Guardrail", "Reviews risk before external action"],
  ["Venue Scout", "Ranks rooms by capacity, budget, and vibe"],
  ["Vendor Coordinator", "Coordinates food, A/V, photo, and setup"],
  ["Outreach Agent", "Finds speakers and valuable guests"],
  ["Content Agent", "Creates launch copy and reminders"],
  ["Marketing Trust Agent", "Invites high-intent people without spam risk"],
  ["Payments Agent", "Explains revenue and queued payments"],
  ["Timeline Agent", "Sequences deadlines and day-of flow"],
  ["Attendee Matchmaker", "Designs high-value introductions"],
  ["Follow-up Agent", "Turns meetings into next steps"]
];

export default function Home() {
  const [idea, setIdea] = useState(fallbackIdea);
  const [run, setRun] = useState<AgentRunResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function startRun(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("/api/run", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ idea })
      });
      setRun(await response.json());
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow">SynapSpace AG2 Playground</p>
          <h1>Watch agents turn an event idea into an operating plan.</h1>
          <p className="lede">
            A live AG2 beta playground for multi-agent event orchestration: planner, challenger, refiner,
            safety, venue, vendor, outreach, content, social, payments, timeline, matchmaker, and follow-up
            agents coordinate through shared context memory while AG-UI exposes the frontend streaming path.
          </p>
          <div className="pill-row">
            <span className="pill"><Bot size={14} />AG2 beta Agent runtime</span>
            <span className="pill"><BrainCircuit size={14} />Shared context memory</span>
            <span className="pill"><Network size={14} />AG-UI stream endpoint</span>
            <span className="pill"><ShieldCheck size={14} />Human approval checkpoint</span>
          </div>
        </div>

        <form className="panel composer" onSubmit={startRun}>
          <div>
            <p className="eyebrow">Event prompt</p>
            <h2>Start a playground run</h2>
            <p className="small muted">Describe the event. Each beta agent reads shared memory, writes its update, and hands context to the next specialist.</p>
          </div>
          <textarea onChange={(event) => setIdea(event.target.value)} value={idea} />
          <button className="button primary" disabled={loading} type="submit">
            <Play size={16} />
            {loading ? "Agents coordinating..." : "Run AG2 agents"}
          </button>
        </form>
      </section>

      <section className="capability-strip">
        <article>
          <strong>Context memory</strong>
          <span>Each agent reads the run memory, then writes decisions, risks, and handoffs for the next agent.</span>
        </article>
        <article>
          <strong>AG2 beta runtime</strong>
          <span>Python service uses `autogen.beta.Agent` and async `Agent.ask(...)` for specialist orchestration.</span>
        </article>
        <article>
          <strong>AG-UI development path</strong>
          <span>Backend exposes `/ag-ui/chat`; Next.js proxies it through `/api/ag-ui` for streaming clients.</span>
        </article>
        <article>
          <strong>Demo-safe fallback</strong>
          <span>If AG2 credentials are absent, all 11 product agents still run a deterministic judge-friendly workflow.</span>
        </article>
      </section>

      <section className="workspace">
        <aside className="panel">
          <h2>Agent Team</h2>
          <div className="agent-list">
            {agents.map(([name, detail]) => (
              <article className="agent-card" key={name}>
                <span className="agent-icon"><Bot size={18} /></span>
                <div>
                  <strong>{name}</strong>
                  <p className="small muted">{detail}</p>
                </div>
              </article>
            ))}
          </div>
        </aside>

        <section className="panel">
          <div className="event-top">
            <div>
              <p className="eyebrow">Live coordination</p>
              <h2>{run ? run.summary : "No run yet"}</h2>
              {run ? <p className="small muted">Engine: {run.engine}</p> : null}
            </div>
            <span className="status">{run ? "complete" : "waiting"}</span>
          </div>

          <div className="event-log">
            {(run?.events ?? []).map((item, index) => (
              <article className="event-card" key={`${item.agent}-${index}`}>
                <div className="event-top">
                  <strong>{item.agent}</strong>
                  <span className="status">{item.status}</span>
                </div>
                <p className="small muted">{item.role}</p>
                <p>{item.message}</p>
                <div className="memory-meter">
                  <span><Database size={13} />Read {item.memoryReads} memory entries</span>
                  <span>Wrote {item.memoryWrites.join(", ")}</span>
                </div>
                <span className="pill">{item.engine}</span>
              </article>
            ))}
            {!run ? (
              <article className="event-card">
                <strong>Ready</strong>
                <p className="small muted">Start a run to see the AG2-style agent conversation.</p>
              </article>
            ) : null}
          </div>

          {run ? (
            <div className="plan-grid" style={{ marginTop: 14 }}>
              <article className="plan-card">
                <Sparkles size={18} />
                <h3>{run.plan.title}</h3>
                <p className="small muted">{run.plan.audience}</p>
              </article>
              <article className="plan-card">
                <UsersRound size={18} />
                <h3>Matchmaking</h3>
                <p className="small muted">{run.plan.matching}</p>
              </article>
              <article className="plan-card">
                <CheckCircle2 size={18} />
                <h3>Approvals</h3>
                <p className="small muted">{run.plan.approvals.join(", ")}</p>
              </article>
            </div>
          ) : null}
        </section>

        <aside className="panel memory-panel">
          <div>
            <p className="eyebrow">Context memory</p>
            <h2>{run ? "Shared agent memory" : "Memory starts after a run"}</h2>
            <p className="small muted">
              {run ? run.memory.activeBrief : "The first agent writes the plan, then every next agent reads and extends it."}
            </p>
          </div>

          {run ? (
            <>
              <div className="memory-columns">
                <MemoryList title="Decisions" items={run.memory.decisions} />
                <MemoryList title="Risks" items={run.memory.risks} />
                <MemoryList title="Handoffs" items={run.memory.handoffs} />
              </div>

              <div className="memory-timeline">
                {run.memory.entries.map((entry, index) => (
                  <article key={`${entry.agent}-${entry.signal}-${index}`}>
                    <span>{entry.agent}</span>
                    <strong>{entry.signal}</strong>
                    <p className="small muted">{entry.content}</p>
                  </article>
                ))}
              </div>
            </>
          ) : (
            <article className="event-card">
              <strong>Waiting for memory</strong>
              <p className="small muted">Run the agents to see the shared context fill up step by step.</p>
            </article>
          )}
        </aside>
      </section>
    </main>
  );
}

function MemoryList({ title, items }: { title: string; items: string[] }) {
  return (
    <article>
      <strong>{title}</strong>
      {items.length ? (
        items.map((item) => <p className="small muted" key={item}>{item}</p>)
      ) : (
        <p className="small muted">None yet</p>
      )}
    </article>
  );
}
