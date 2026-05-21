// Shared adapter types for the M3ta-0S dashboard.
// Each module (Hermes, Obsidian, Aion, Paperclip, Claude Code) implements one
// of these interfaces. The dashboard reads through them, never directly from
// implementation modules, so we can swap mock and real backends freely.

export type AdapterMode = "mock" | "live";

export interface AdapterStatus {
  module: string;
  mode: AdapterMode;
  ok: boolean;
  message?: string;
  checkedAt: string; // ISO timestamp
}

// ---- Hermes ----
export type AgentState =
  | "idle"
  | "planning"
  | "acting"
  | "waiting"
  | "blocked"
  | "failed"
  | "complete";

export interface Agent {
  id: string;
  name: string;
  role: string;
  state: AgentState;
  currentTask?: string;
  lastAction?: string;
  nextAction?: string;
  confidence?: number; // 0..1
}

export interface HermesTask {
  id: string;
  title: string;
  agentId: string;
  state: AgentState;
  createdAt: string;
  approval?: "required" | "approved" | "rejected" | "not-required";
}

export interface HermesLogEntry {
  id: string;
  ts: string;
  level: "info" | "warn" | "error" | "trace";
  agentId?: string;
  message: string;
}

export type HermesCapabilityStatus =
  | "matched"
  | "partial"
  | "missing"
  | "not-applicable";

export interface HermesCapability {
  id: string;
  label: string;
  status: HermesCapabilityStatus;
  evidence: string;
  nextUpgrade: string;
}

export interface HermesSnapshot {
  status: AdapterStatus;
  agents: Agent[];
  tasks: HermesTask[];
  logs: HermesLogEntry[];
  capabilities: HermesCapability[];
}

// ---- Obsidian ----
export interface ObsidianNoteSummary {
  path: string;
  title: string;
  modifiedAt: string;
  sizeBytes: number;
  tags: string[];
}

export interface ObsidianSnapshot {
  status: AdapterStatus;
  vaultPath: string | null;
  noteCount: number;
  totalBytes: number;
  tagCount: number;
  recent: ObsidianNoteSummary[];
  topTags: { tag: string; count: number }[];
  ragReady: boolean;
}

// ---- Aion ----
export interface AionAutomation {
  id: string;
  name: string;
  cadence: string; // human-readable cron / schedule
  nextRunAt: string;
  lastRunAt?: string;
  enabled: boolean;
  category: "ritual" | "briefing" | "backup" | "check" | "sync";
}

export interface AionEvent {
  id: string;
  ts: string;
  kind: "fired" | "skipped" | "completed" | "failed" | "note";
  message: string;
  automationId?: string;
}

export interface AionSnapshot {
  status: AdapterStatus;
  automations: AionAutomation[];
  events: AionEvent[];
}

// ---- Paperclip ----
export type CaptureKind = "clip" | "doc" | "snippet" | "research" | "link";

export interface PaperclipCapture {
  id: string;
  kind: CaptureKind;
  title: string;
  source?: string;
  body: string;
  tags: string[];
  capturedAt: string;
  routedTo: ("obsidian" | "hermes-memory")[];
}

export interface PaperclipSnapshot {
  status: AdapterStatus;
  recent: PaperclipCapture[];
  totalCount: number;
  byKind: Record<CaptureKind, number>;
}

// ---- Claude Code ----
export interface ClaudeCodeSuggestedPrompt {
  id: string;
  label: string;
  prompt: string;
}

export interface ClaudeCodeRun {
  id: string;
  title: string;
  state: "queued" | "running" | "complete" | "failed";
  startedAt: string;
  endedAt?: string;
  filesChanged?: number;
}

export interface ClaudeCodeSnapshot {
  status: AdapterStatus;
  workspace: string;
  branch: string;
  cleanTree: boolean;
  recentRuns: ClaudeCodeRun[];
  suggested: ClaudeCodeSuggestedPrompt[];
  implementationStatus: {
    component: string;
    status: "matched" | "partial" | "missing";
  }[];
}
