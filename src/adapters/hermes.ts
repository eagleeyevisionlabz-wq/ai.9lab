import {
  Agent,
  HermesCapability,
  HermesLogEntry,
  HermesSnapshot,
  HermesTask,
} from "./types";

// Deterministic seeded agents/tasks so the dashboard never flickers between
// renders. Real Hermes integration would replace getHermesSnapshot with an
// HTTP call to HERMES_URL.

function nowIso(offsetMs = 0): string {
  return new Date(Date.now() + offsetMs).toISOString();
}

const AGENTS: Agent[] = [
  {
    id: "hermes",
    name: "Hermes",
    role: "orchestrator",
    state: "planning",
    currentTask: "Route inbound captures to memory + summarize daily briefing",
    lastAction: "Dispatched 2 subagents",
    nextAction: "Wait for subagent results, then write briefing",
    confidence: 0.84,
  },
  {
    id: "aion",
    name: "Aion",
    role: "chronos / scheduler",
    state: "idle",
    currentTask: "Idle. Watching cron tape.",
    lastAction: "Ran 06:00 morning briefing ritual",
    nextAction: "Next ritual at 18:00",
    confidence: 1,
  },
  {
    id: "obsidian-rag",
    name: "Obsidian RAG",
    role: "knowledge / retrieval",
    state: "acting",
    currentTask: "Re-indexing 17 changed notes",
    lastAction: "Built backlink graph",
    nextAction: "Emit ragReady=true",
    confidence: 0.91,
  },
  {
    id: "paperclip",
    name: "Paperclip",
    role: "capture",
    state: "waiting",
    currentTask: "1 capture pending routing approval",
    lastAction: "Tagged clipping #research",
    nextAction: "Await approval to write to vault",
    confidence: 0.7,
  },
  {
    id: "claude-code",
    name: "Claude Code",
    role: "implementation",
    state: "complete",
    currentTask: "Last run: scaffold dashboard skeleton",
    lastAction: "Committed feat/m3ta-dashboard-skeleton",
    nextAction: "Wait for next task",
    confidence: 0.96,
  },
];

const TASKS: HermesTask[] = [
  {
    id: "t-001",
    title: "Compile evening briefing from today's captures",
    agentId: "hermes",
    state: "planning",
    createdAt: nowIso(-1000 * 60 * 12),
    approval: "not-required",
  },
  {
    id: "t-002",
    title: "Index recently modified Obsidian notes",
    agentId: "obsidian-rag",
    state: "acting",
    createdAt: nowIso(-1000 * 60 * 4),
    approval: "not-required",
  },
  {
    id: "t-003",
    title: "Write captured research clip into vault",
    agentId: "paperclip",
    state: "waiting",
    createdAt: nowIso(-1000 * 60 * 2),
    approval: "required",
  },
];

const LOGS: HermesLogEntry[] = [
  {
    id: "l-1",
    ts: nowIso(-1000 * 60),
    level: "info",
    agentId: "hermes",
    message: "plan: collect-captures -> summarize -> dispatch",
  },
  {
    id: "l-2",
    ts: nowIso(-1000 * 50),
    level: "trace",
    agentId: "obsidian-rag",
    message: "tool: vault.scan(modifiedSince=24h) -> 17 notes",
  },
  {
    id: "l-3",
    ts: nowIso(-1000 * 30),
    level: "info",
    agentId: "paperclip",
    message: "captured 'Sovereign infra patterns' from https://example.com",
  },
  {
    id: "l-4",
    ts: nowIso(-1000 * 10),
    level: "warn",
    agentId: "paperclip",
    message: "vault write requires approval (M3TA_REQUIRE_APPROVALS=1)",
  },
];

const CAPABILITIES: HermesCapability[] = [
  {
    id: "channels",
    label: "Lives where user works (CLI, web, Slack, Discord, Telegram, etc.)",
    status: "partial",
    evidence: "Web dashboard live. CLI + Claude Code attached. Chat surfaces TBD.",
    nextUpgrade: "Add Slack + Telegram adapters wired to Hermes orchestrator",
  },
  {
    id: "memory",
    label: "Persistent memory: user, projects, preferences, decisions",
    status: "partial",
    evidence:
      "Claude Code maintains memory dir; Obsidian vault is durable. No unified memory router yet.",
    nextUpgrade: "Build Hermes memory router on top of Obsidian + Postgres",
  },
  {
    id: "skills",
    label: "Auto-generated reusable skills/procedures",
    status: "matched",
    evidence: "Claude Code skills pack and repo-skills loader present.",
    nextUpgrade: "Expose skills as cards in dashboard with run-once buttons",
  },
  {
    id: "scheduling",
    label: "Scheduled automations + recurring jobs",
    status: "partial",
    evidence: "Aion mock timeline shipped. No durable scheduler attached yet.",
    nextUpgrade: "Back Aion with a cron-based persistent runner (Railway or Docker)",
  },
  {
    id: "delegation",
    label: "Subagent delegation + parallel execution",
    status: "matched",
    evidence: "Claude Code Agent tool supports parallel subagents.",
    nextUpgrade: "Surface subagent fanout traces in Hermes panel",
  },
  {
    id: "sandbox",
    label: "Sandboxed execution for code / risky actions",
    status: "partial",
    evidence: "Claude Code worktrees exist. No container sandbox for arbitrary code.",
    nextUpgrade: "Add Docker-based code sandbox routed through tool router",
  },
  {
    id: "web",
    label: "Web search, scraping, browser control",
    status: "partial",
    evidence: "Firecrawl integration documented; not yet wired to dashboard.",
    nextUpgrade: "Add Firecrawl capture button in Paperclip card",
  },
  {
    id: "routing",
    label: "Multi-model reasoning + routing",
    status: "missing",
    evidence: "Only Claude family attached.",
    nextUpgrade: "Add tool router with OpenAI + local models",
  },
  {
    id: "multimodal",
    label: "Multimodal: voice, image, video, docs, screenshots",
    status: "missing",
    evidence: "Text-only currently.",
    nextUpgrade: "Add voice-in via Whisper + image capture endpoint",
  },
  {
    id: "deployment",
    label: "Deployment persistence (runs when laptop is closed)",
    status: "missing",
    evidence: "Dashboard runs locally only.",
    nextUpgrade: "Deploy to Railway per integrations/RAILWAY.md",
  },
  {
    id: "observability",
    label: "Observability: logs, traces, audit trail",
    status: "partial",
    evidence: "In-memory log panel shipped. No persistent trace store.",
    nextUpgrade: "Persist traces to SQLite or Postgres",
  },
  {
    id: "approvals",
    label: "Approval gates for irreversible actions",
    status: "matched",
    evidence:
      "M3TA_REQUIRE_APPROVALS gates writes; Paperclip routes require approval.",
    nextUpgrade: "Build approval inbox view with diff preview",
  },
];

export async function getHermesSnapshot(): Promise<HermesSnapshot> {
  // Live mode would dispatch to HERMES_URL here. We keep this synchronous in
  // mock mode but return a Promise so the API contract is stable.
  return {
    status: {
      module: "hermes",
      mode: process.env.HERMES_URL ? "live" : "mock",
      ok: true,
      message: process.env.HERMES_URL
        ? "Live Hermes endpoint configured but adapter not yet implemented; returning mock snapshot."
        : "Mock Hermes orchestrator. Set HERMES_URL to attach a real backend.",
      checkedAt: nowIso(),
    },
    agents: AGENTS,
    tasks: TASKS,
    logs: LOGS,
    capabilities: CAPABILITIES,
  };
}
