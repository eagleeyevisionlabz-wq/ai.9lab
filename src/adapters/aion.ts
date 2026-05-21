import { AionAutomation, AionEvent, AionSnapshot } from "./types";

function nowIso(offsetMs = 0): string {
  return new Date(Date.now() + offsetMs).toISOString();
}

const AUTOMATIONS: AionAutomation[] = [
  {
    id: "ritual-morning",
    name: "Morning briefing",
    cadence: "every day at 06:00 local",
    nextRunAt: nowIso(1000 * 60 * 60 * 8),
    lastRunAt: nowIso(-1000 * 60 * 60 * 16),
    enabled: true,
    category: "ritual",
  },
  {
    id: "ritual-evening",
    name: "Evening reflection",
    cadence: "every day at 21:00 local",
    nextRunAt: nowIso(1000 * 60 * 60 * 5),
    lastRunAt: nowIso(-1000 * 60 * 60 * 19),
    enabled: true,
    category: "ritual",
  },
  {
    id: "obsidian-backup",
    name: "Obsidian vault backup",
    cadence: "every Sunday at 03:00",
    nextRunAt: nowIso(1000 * 60 * 60 * 24 * 3),
    lastRunAt: nowIso(-1000 * 60 * 60 * 24 * 4),
    enabled: true,
    category: "backup",
  },
  {
    id: "hermes-healthcheck",
    name: "Hermes /health check",
    cadence: "every 5 minutes",
    nextRunAt: nowIso(1000 * 60 * 3),
    lastRunAt: nowIso(-1000 * 60 * 2),
    enabled: false,
    category: "check",
  },
  {
    id: "paperclip-flush",
    name: "Paperclip inbox flush",
    cadence: "every hour on the :07",
    nextRunAt: nowIso(1000 * 60 * 25),
    lastRunAt: nowIso(-1000 * 60 * 35),
    enabled: true,
    category: "sync",
  },
];

const EVENTS: AionEvent[] = [
  {
    id: "e-1",
    ts: nowIso(-1000 * 60 * 35),
    kind: "completed",
    message: "paperclip-flush moved 3 captures into Obsidian/inbox",
    automationId: "paperclip-flush",
  },
  {
    id: "e-2",
    ts: nowIso(-1000 * 60 * 60 * 16),
    kind: "completed",
    message: "morning briefing assembled — 7 notes, 2 approvals pending",
    automationId: "ritual-morning",
  },
  {
    id: "e-3",
    ts: nowIso(-1000 * 60 * 60 * 24 * 4),
    kind: "completed",
    message: "vault backup written to ~/backups/obsidian-2026-05-17.tar.zst",
    automationId: "obsidian-backup",
  },
  {
    id: "e-4",
    ts: nowIso(-1000 * 60 * 60 * 24 * 2),
    kind: "failed",
    message: "hermes-healthcheck disabled after 3 consecutive failures",
    automationId: "hermes-healthcheck",
  },
];

export async function getAionSnapshot(): Promise<AionSnapshot> {
  return {
    status: {
      module: "aion",
      mode: process.env.AION_URL ? "live" : "mock",
      ok: true,
      message: process.env.AION_URL
        ? "AION_URL set but live adapter not implemented; returning mock timeline."
        : "Mock Aion chronos layer. Configure AION_URL to attach a real scheduler.",
      checkedAt: nowIso(),
    },
    automations: AUTOMATIONS,
    events: EVENTS,
  };
}
