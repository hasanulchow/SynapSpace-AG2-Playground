"use client";

import { FormEvent, useState } from "react";
import { Bot, CheckCircle2, Network, Play, ShieldCheck, Sparkles, UsersRound } from "lucide-react";
import type { AgentRunResponse } from "@/lib/types";

const fallbackIdea = "AI networking event in NYC next month for 100 founders, builders, and design leaders";

const agents = [
  ["Planner Agent", "Creates the first event plan"],
  ["Challenger Agent", "Finds risks and missing constraints"],
  ["Refiner Agent", "Improves attendee experience"],
  ["Social Agent", "Builds audience and content strategy"],
  ["Matchmaker Agent", "Designs high-value introductions"],
  ["Governance Agent", "Prepares human approval checkpoint"]
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
            A live AG2-style playground for multi-agent event orchestration: planner, challenger, refiner,
            social, matchmaker, and governance agents coordinate while the human approves the final plan.
          </p>
          <div className="pill-row">
            <span className="pill"><Bot size={14} />AG2 multi-agent workflows</span>
            <span className="pill"><Network size={14} />Round robin and sequential patterns</span>
            <span className="pill"><ShieldCheck size={14} />Human approval checkpoint</span>
          </div>
        </div>

        <form className="panel composer" onSubmit={startRun}>
          <div>
            <p className="eyebrow">Event prompt</p>
            <h2>Start a playground run</h2>
            <p className="small muted">Describe the event. The agents will coordinate a plan and approval queue.</p>
          </div>
          <textarea onChange={(event) => setIdea(event.target.value)} value={idea} />
          <button className="button primary" disabled={loading} type="submit">
            <Play size={16} />
            {loading ? "Agents coordinating..." : "Run AG2 agents"}
          </button>
        </form>
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
      </section>
    </main>
  );
}

