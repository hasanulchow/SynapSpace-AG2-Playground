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
  const memory = createLocalMemory(idea);
  const events = [
    createEvent(
      memory,
      "Master Orchestrator",
      "Orchestrator",
      "thinking",
      `Built the event dependency graph from: ${idea}. Routed the full SynapSpace agent team as connected workstreams.`
    ),
    createEvent(
      memory,
      "Safety Guardrail",
      "Safety reviewer",
      "challenging",
      "Read the organizer intent and dependency graph, then flagged permit, spend, outbound messaging, and human approval checks."
    ),
    createEvent(
      memory,
      "Venue Scout",
      "Venue specialist",
      "refining",
      "Used the safety memory to define venue requirements around capacity, budget, vibe, availability, and cancellation risk."
    ),
    createEvent(
      memory,
      "Vendor Coordinator",
      "Logistics specialist",
      "refining",
      "Used the venue memory to prepare catering, A/V, photography, signage, setup windows, and vendor quote dependencies."
    ),
    createEvent(
      memory,
      "Outreach Agent",
      "Speaker and guest scout",
      "refining",
      "Used the audience and venue memory to shortlist speakers and high-value guests with approval-ready invite tones."
    ),
    createEvent(
      memory,
      "Content Agent",
      "Marketing producer",
      "refining",
      "Used speaker, venue, and audience memory to draft launch copy, reminder content, partner blurbs, and recap angles."
    ),
    createEvent(
      memory,
      "Marketing Trust Agent",
      "Growth operator",
      "refining",
      "Used public intent, location, availability, consent, and fatigue signals to prepare only high-fit invite drafts while suppressing spam-risk outreach."
    ),
    createEvent(
      memory,
      "Payments Agent",
      "Money operator",
      "refining",
      "Used vendor and ticketing memory to explain revenue, platform fee, reserve, host payout, and queued vendor payments."
    ),
    createEvent(
      memory,
      "Timeline Agent",
      "Schedule operator",
      "refining",
      "Used all prior dependencies to sequence approvals, content drops, vendor deadlines, reminders, setup, and day-of run of show."
    ),
    createEvent(
      memory,
      "Attendee Matchmaker",
      "Network strategist",
      "complete",
      "Used the social and audience memory to rank attendee fit and generate warm intro prompts."
    ),
    createEvent(
      memory,
      "Follow-up Agent",
      "Post-event operator",
      "approval",
      "Read the full memory and prepared post-event drafts, action items, CRM export notes, and final organizer approval checkpoints."
    )
  ];

  return {
    runId: "local-demo-run",
    summary: "Local fallback run complete with shared context memory",
    events,
    engine: "web-local-fallback",
    plan: {
      title: "Agentic Networking Night",
      audience: "100 qualified founders, builders, and design leaders",
      venue: "Venue shortlist selected after safety, capacity, budget, contract, and vibe checks",
      marketing: "Content Agent and Marketing Trust Agent coordinate reputation-safe intent-based launch campaigns",
      matching: "Rank attendee fit and generate warm intro prompts",
      approvals: ["Venue", "Budget", "Audience", "Outreach tone", "Vendor payments"]
    },
    memory: {
      activeBrief: `${memory.entries.length} memory entries connect the agent team around: ${idea}`,
      entries: memory.entries,
      decisions: memory.decisions,
      risks: memory.risks,
      handoffs: memory.handoffs
    },
    approvalsRequired: true
  };
}

type LocalMemory = {
  entries: Array<{ agent: string; signal: string; content: string }>;
  decisions: string[];
  risks: string[];
  handoffs: string[];
};

function createLocalMemory(idea: string): LocalMemory {
  return {
    entries: [{ agent: "Organizer", signal: "event-intent", content: `Original organizer idea: ${idea}` }],
    decisions: [],
    risks: [],
    handoffs: []
  };
}

function createEvent(memory: LocalMemory, agent: string, role: string, status: string, message: string) {
  const memoryReads = memory.entries.length;
  const signal = signalForRole(role);
  const memoryWrites = [signal];
  memory.entries.push({ agent, signal, content: message });

  if (role === "Orchestrator") {
    memory.decisions.push("Event dependency graph drafted");
    memoryWrites.push("Event dependency graph drafted");
  } else if (role === "Safety reviewer") {
    memory.risks.push("Policy, permit, spend, and outbound risks reviewed");
    memoryWrites.push("Policy, permit, spend, and outbound risks reviewed");
  } else if (role === "Venue specialist") {
    memory.decisions.push("Venue requirements and shortlist criteria captured");
    memoryWrites.push("Venue requirements and shortlist criteria captured");
  } else if (role === "Logistics specialist") {
    memory.handoffs.push("Vendor quote and setup dependencies captured");
    memoryWrites.push("Vendor quote and setup dependencies captured");
  } else if (role === "Speaker and guest scout") {
    memory.handoffs.push("Speaker and guest outreach inputs prepared for content");
    memoryWrites.push("Speaker and guest outreach inputs prepared for content");
  } else if (role === "Marketing producer") {
    memory.decisions.push("Launch content direction prepared");
    memoryWrites.push("Launch content direction prepared");
  } else if (role === "Growth operator") {
    memory.handoffs.push("Marketing Trust Agent should invite only high-intent people with safe consent, location fit, availability, and low spam risk");
    memoryWrites.push("Marketing Trust Agent should invite only high-intent people with safe consent, location fit, availability, and low spam risk");
  } else if (role === "Money operator") {
    memory.risks.push("Revenue, platform fee, reserve, and vendor payment flow reviewed");
    memoryWrites.push("Revenue, platform fee, reserve, and vendor payment flow reviewed");
  } else if (role === "Schedule operator") {
    memory.handoffs.push("Timeline now controls launch, setup, reminders, and day-of sequence");
    memoryWrites.push("Timeline now controls launch, setup, reminders, and day-of sequence");
  } else if (role === "Network strategist") {
    memory.handoffs.push("Matchmaking graph feeds intro prompts and follow-up windows");
    memoryWrites.push("Matchmaking graph feeds intro prompts and follow-up windows");
  } else if (role === "Post-event operator") {
    memory.decisions.push("Final external actions require organizer approval");
    memoryWrites.push("Final external actions require organizer approval");
  }

  return {
    agent,
    role,
    status,
    message,
    engine: "web-local-fallback",
    memoryReads,
    memoryWrites
  };
}

function signalForRole(role: string) {
  const signals: Record<string, string> = {
    Orchestrator: "dependency-graph",
    "Safety reviewer": "safety",
    "Venue specialist": "venue",
    "Logistics specialist": "vendors",
    "Speaker and guest scout": "outreach",
    "Marketing producer": "content",
    "Growth operator": "trust-marketing",
    "Money operator": "money",
    "Schedule operator": "timeline",
    "Network strategist": "matching",
    "Post-event operator": "follow-up"
  };
  return signals[role] ?? "update";
}
