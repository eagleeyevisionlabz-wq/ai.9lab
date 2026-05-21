import { promises as fs } from "node:fs";
import path from "node:path";
import {
  CaptureKind,
  PaperclipCapture,
  PaperclipSnapshot,
} from "./types";

// Paperclip adapter.
//
// In-process store of captures, optionally persisted as JSONL to
// PAPERCLIP_STORE. The store is intentionally simple: append-only, one JSON
// object per line. The dashboard reads via getPaperclipSnapshot() and writes
// via addCapture(). Real Hermes-memory / Obsidian routing is mocked here as a
// metadata field — the actual write side will be implemented by the Hermes
// memory router once it exists.

function nowIso(): string {
  return new Date().toISOString();
}

const MEMORY: PaperclipCapture[] = [
  {
    id: "cap-001",
    kind: "research",
    title: "Sovereign infra patterns",
    source: "https://example.com/sovereign-infra",
    body: "Notes on running your own model + memory stack with OrbStack and Docker.",
    tags: ["research", "infra"],
    capturedAt: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    routedTo: ["obsidian", "hermes-memory"],
  },
  {
    id: "cap-002",
    kind: "snippet",
    title: "shell: lock files audit",
    source: "terminal",
    body: "lsof /tmp/m3ta.lock — quick way to find stale lock holders.",
    tags: ["snippet", "ops"],
    capturedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    routedTo: ["hermes-memory"],
  },
  {
    id: "cap-003",
    kind: "link",
    title: "Hermes capability test (M3ta pack)",
    source: "internal://pack/HERMES-CAPABILITY-TEST.md",
    body: "Reference scorecard for comparing agents against Hermes-style capabilities.",
    tags: ["reference", "hermes"],
    capturedAt: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
    routedTo: ["obsidian"],
  },
];

async function persist(c: PaperclipCapture): Promise<void> {
  const store = process.env.PAPERCLIP_STORE;
  if (!store) return;
  try {
    await fs.mkdir(path.dirname(store), { recursive: true });
    await fs.appendFile(store, JSON.stringify(c) + "\n", "utf8");
  } catch {
    // ignore — capture stays in memory
  }
}

export async function addCapture(
  input: Omit<PaperclipCapture, "id" | "capturedAt">,
): Promise<PaperclipCapture> {
  const capture: PaperclipCapture = {
    id: `cap-${Math.random().toString(36).slice(2, 8)}`,
    capturedAt: nowIso(),
    ...input,
  };
  MEMORY.unshift(capture);
  await persist(capture);
  return capture;
}

export async function getPaperclipSnapshot(): Promise<PaperclipSnapshot> {
  const byKind: Record<CaptureKind, number> = {
    clip: 0,
    doc: 0,
    snippet: 0,
    research: 0,
    link: 0,
  };
  for (const c of MEMORY) byKind[c.kind]++;

  return {
    status: {
      module: "paperclip",
      mode: process.env.PAPERCLIP_STORE ? "live" : "mock",
      ok: true,
      message: process.env.PAPERCLIP_STORE
        ? `Captures persisted as JSONL at ${process.env.PAPERCLIP_STORE}`
        : "In-memory captures only. Set PAPERCLIP_STORE to persist.",
      checkedAt: nowIso(),
    },
    recent: MEMORY.slice(0, 10),
    totalCount: MEMORY.length,
    byKind,
  };
}
