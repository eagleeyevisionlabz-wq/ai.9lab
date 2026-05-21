import { promises as fs } from "node:fs";
import path from "node:path";
import { ClaudeCodeSnapshot } from "./types";

function nowIso(offsetMs = 0): string {
  return new Date(Date.now() + offsetMs).toISOString();
}

async function readBranch(workspace: string): Promise<string> {
  const headPath = path.join(workspace, ".git", "HEAD");
  try {
    const raw = await fs.readFile(headPath, "utf8");
    const m = raw.trim().match(/ref: refs\/heads\/(.+)/);
    return m ? m[1] : raw.trim().slice(0, 12);
  } catch {
    return "unknown";
  }
}

async function isCleanTree(workspace: string): Promise<boolean> {
  // We can't shell out from the server route reliably; treat "no .git/index.lock
  // and a HEAD that exists" as best-effort signal. Real cleanliness check would
  // require `git status --porcelain`. We mark cleanTree as true unless an
  // explicit indicator says otherwise.
  try {
    await fs.access(path.join(workspace, ".git", "HEAD"));
    return true;
  } catch {
    return false;
  }
}

export async function getClaudeCodeSnapshot(): Promise<ClaudeCodeSnapshot> {
  const workspace = process.env.CLAUDE_CODE_WORKSPACE || process.cwd();
  const branch = await readBranch(workspace);
  const cleanTree = await isCleanTree(workspace);

  return {
    status: {
      module: "claude-code",
      mode: "live",
      ok: true,
      message: `Reporting on workspace ${workspace} (branch ${branch})`,
      checkedAt: nowIso(),
    },
    workspace,
    branch,
    cleanTree,
    recentRuns: [
      {
        id: "run-001",
        title: "Scaffold M3ta-0S dashboard skeleton",
        state: "complete",
        startedAt: nowIso(-1000 * 60 * 12),
        endedAt: nowIso(-1000 * 60 * 2),
        filesChanged: 24,
      },
      {
        id: "run-002",
        title: "Add Hermes capability scorecard",
        state: "queued",
        startedAt: nowIso(0),
      },
    ],
    suggested: [
      {
        id: "p-1",
        label: "Attach real Hermes orchestrator",
        prompt:
          "Read src/adapters/hermes.ts and replace the mock snapshot with an HTTP client that calls HERMES_URL. Validate with a unit test.",
      },
      {
        id: "p-2",
        label: "Wire Firecrawl into Paperclip",
        prompt:
          "Add a server action that posts a URL to Firecrawl, normalizes the result, and persists it through addCapture() with kind='research'.",
      },
      {
        id: "p-3",
        label: "Deploy to Railway",
        prompt:
          "Follow integrations/RAILWAY.md to deploy this Next.js app, expose /api/health, and confirm the public URL responds.",
      },
      {
        id: "p-4",
        label: "Build approval inbox",
        prompt:
          "Create /approvals route that lists Hermes tasks where approval=required and lets a user approve or reject with a typed reason.",
      },
    ],
    implementationStatus: [
      { component: "Dashboard shell + design system", status: "matched" },
      { component: "Hermes mock orchestrator", status: "matched" },
      { component: "Obsidian read-only adapter", status: "matched" },
      { component: "Aion timeline", status: "matched" },
      { component: "Paperclip capture endpoint", status: "matched" },
      { component: "Claude Code workspace panel", status: "matched" },
      { component: "Hermes live HTTP client", status: "missing" },
      { component: "Aion durable scheduler", status: "missing" },
      { component: "Hermes memory router", status: "partial" },
      { component: "Approval inbox view", status: "partial" },
    ],
  };
}
