import { NextResponse } from "next/server";

const AGENT_SERVICE_URL = process.env.AGENT_SERVICE_URL ?? "http://127.0.0.1:8000/run";

export async function POST(request: Request) {
  const body = await request.json();

  try {
    const response = await fetch(AGENT_SERVICE_URL, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body)
    });

    if (!response.ok) throw new Error("Agent service failed");
    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json(localFallback(body.idea));
  }
}

function localFallback(rawIdea: unknown) {
  const idea = String(rawIdea ?? "AI networking event");
  return {
    runId: "local-demo-run",
    summary: "Local fallback run complete",
    events: [
      {
        agent: "Planner Agent",
        role: "Proposer",
        status: "thinking",
        message: `Drafted a first event plan from: ${idea}.`,
        engine: "web-local-fallback"
      },
      {
        agent: "Challenger Agent",
        role: "Critic",
        status: "challenging",
        message: "Flagged budget, venue availability, audience quality, and approval timing as key risks.",
        engine: "web-local-fallback"
      },
      {
        agent: "Refiner Agent",
        role: "Experience designer",
        status: "refining",
        message: "Improved the plan with curated intros, speaker moments, and a smaller approval queue.",
        engine: "web-local-fallback"
      },
      {
        agent: "Governance Agent",
        role: "Human approval",
        status: "approval",
        message: "Prepared final decisions: venue, social audience, budget ceiling, and outreach tone.",
        engine: "web-local-fallback"
      }
    ],
    engine: "web-local-fallback",
    plan: {
      title: "Agentic Networking Night",
      audience: "100 qualified founders, builders, and design leaders",
      venue: "Flexible loft or enterprise partner space",
      marketing: "Intent-based social campaign plus partner community posts",
      matching: "Rank attendee fit and generate warm intro prompts",
      approvals: ["Venue", "Budget", "Audience", "Outreach tone"]
    },
    approvalsRequired: true
  };
}
