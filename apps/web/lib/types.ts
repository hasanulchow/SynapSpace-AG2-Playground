export type AgentRunRequest = {
  idea: string;
};

export type AgentEvent = {
  agent: string;
  role: string;
  status: "thinking" | "challenging" | "refining" | "complete" | "approval";
  message: string;
};

export type AgentRunResponse = {
  runId: string;
  summary: string;
  events: AgentEvent[];
  plan: {
    title: string;
    audience: string;
    venue: string;
    marketing: string;
    matching: string;
    approvals: string[];
  };
};

