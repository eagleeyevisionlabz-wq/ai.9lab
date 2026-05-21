import { promises as fs } from "node:fs";
import path from "node:path";
import {
  ObsidianNoteSummary,
  ObsidianSnapshot,
} from "./types";

// Obsidian adapter.
//
// When OBSIDIAN_VAULT_PATH is set and points to a readable directory, we walk
// the vault (bounded) and compute READ-ONLY stats: note count, total bytes,
// top tags from #tag tokens inside .md files, and the most recently modified
// notes. We never write to the vault from this adapter.
//
// When OBSIDIAN_VAULT_PATH is unset, we return deterministic mock data.

const MAX_FILES = 5000;
const MAX_BYTES_PER_FILE = 200_000;

function nowIso(): string {
  return new Date().toISOString();
}

async function walk(root: string, out: string[], depth = 0): Promise<void> {
  if (out.length >= MAX_FILES) return;
  if (depth > 8) return;
  let entries;
  try {
    entries = await fs.readdir(root, { withFileTypes: true });
  } catch {
    return;
  }
  for (const e of entries) {
    if (out.length >= MAX_FILES) return;
    if (e.name.startsWith(".")) continue; // skip .obsidian, .git, etc.
    const full = path.join(root, e.name);
    if (e.isDirectory()) {
      await walk(full, out, depth + 1);
    } else if (e.isFile() && e.name.toLowerCase().endsWith(".md")) {
      out.push(full);
    }
  }
}

function extractTags(body: string): string[] {
  const tags = new Set<string>();
  // very simple #tag matcher; not full Obsidian semantics
  const re = /(^|\s)#([A-Za-z0-9_\-/]{1,40})/g;
  let m;
  while ((m = re.exec(body)) !== null) {
    tags.add(m[2].toLowerCase());
  }
  return Array.from(tags);
}

function deriveTitle(filePath: string, body: string): string {
  const firstHeader = body.match(/^#\s+(.+)$/m);
  if (firstHeader) return firstHeader[1].trim();
  return path.basename(filePath, path.extname(filePath));
}

async function liveSnapshot(vaultPath: string): Promise<ObsidianSnapshot> {
  let resolved: string;
  try {
    const st = await fs.stat(vaultPath);
    if (!st.isDirectory()) throw new Error("not a directory");
    resolved = vaultPath;
  } catch (err) {
    return mockSnapshot(
      `OBSIDIAN_VAULT_PATH set to '${vaultPath}' but unreadable: ${(err as Error).message}`,
    );
  }

  const files: string[] = [];
  await walk(resolved, files);

  const tagCounts = new Map<string, number>();
  const summaries: ObsidianNoteSummary[] = [];
  let totalBytes = 0;

  for (const f of files) {
    let stat;
    try {
      stat = await fs.stat(f);
    } catch {
      continue;
    }
    totalBytes += stat.size;
    let body = "";
    try {
      const fh = await fs.open(f, "r");
      try {
        const buf = Buffer.alloc(Math.min(MAX_BYTES_PER_FILE, stat.size));
        await fh.read(buf, 0, buf.length, 0);
        body = buf.toString("utf8");
      } finally {
        await fh.close();
      }
    } catch {
      // ignore unreadable file
    }
    const tags = extractTags(body);
    for (const t of tags) tagCounts.set(t, (tagCounts.get(t) ?? 0) + 1);
    summaries.push({
      path: path.relative(resolved, f),
      title: deriveTitle(f, body),
      modifiedAt: stat.mtime.toISOString(),
      sizeBytes: stat.size,
      tags,
    });
  }

  summaries.sort((a, b) => (a.modifiedAt < b.modifiedAt ? 1 : -1));
  const topTags = Array.from(tagCounts.entries())
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 12);

  return {
    status: {
      module: "obsidian",
      mode: "live",
      ok: true,
      message: `Indexed ${summaries.length} notes from ${resolved}`,
      checkedAt: nowIso(),
    },
    vaultPath: resolved,
    noteCount: summaries.length,
    totalBytes,
    tagCount: tagCounts.size,
    recent: summaries.slice(0, 8),
    topTags,
    ragReady: summaries.length > 0,
  };
}

function mockSnapshot(reason?: string): ObsidianSnapshot {
  const recent: ObsidianNoteSummary[] = [
    {
      path: "rituals/morning-briefing.md",
      title: "Morning briefing ritual",
      modifiedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
      sizeBytes: 2148,
      tags: ["ritual", "aion"],
    },
    {
      path: "research/sovereign-infra.md",
      title: "Sovereign infra patterns",
      modifiedAt: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
      sizeBytes: 5310,
      tags: ["research", "infra"],
    },
    {
      path: "agents/hermes.md",
      title: "Hermes — orchestrator notes",
      modifiedAt: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
      sizeBytes: 4012,
      tags: ["agent", "hermes"],
    },
    {
      path: "captures/inbox.md",
      title: "Capture inbox",
      modifiedAt: new Date(Date.now() - 1000 * 60 * 60 * 18).toISOString(),
      sizeBytes: 1290,
      tags: ["paperclip", "inbox"],
    },
  ];
  return {
    status: {
      module: "obsidian",
      mode: "mock",
      ok: true,
      message:
        reason ??
        "OBSIDIAN_VAULT_PATH not set; using deterministic mock vault.",
      checkedAt: nowIso(),
    },
    vaultPath: null,
    noteCount: recent.length,
    totalBytes: recent.reduce((s, r) => s + r.sizeBytes, 0),
    tagCount: 6,
    recent,
    topTags: [
      { tag: "ritual", count: 4 },
      { tag: "research", count: 3 },
      { tag: "agent", count: 3 },
      { tag: "hermes", count: 2 },
      { tag: "paperclip", count: 2 },
      { tag: "infra", count: 1 },
    ],
    ragReady: false,
  };
}

export async function getObsidianSnapshot(): Promise<ObsidianSnapshot> {
  const vaultPath = process.env.OBSIDIAN_VAULT_PATH;
  if (!vaultPath) return mockSnapshot();
  return liveSnapshot(vaultPath);
}
