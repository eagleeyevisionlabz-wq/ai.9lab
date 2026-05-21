# ai.9lab — M3ta-0S Dashboard

Sovereign, self-hosted AI operating system dashboard.
Unifies **Hermes** (orchestrator), **Obsidian** (knowledge / RAG), **Aion** (chronos / scheduler), **Paperclip** (capture), and **Claude Code** (implementation agent) into one mission-control surface.

> Built against the M3ta agent OS protocol and design system. See
> `m3ta-agent-os-claude-code-pack/CLAUDE.md` and `DESIGN-SYSTEM.md` for the
> architecture and visual language this dashboard implements.

## Quick start

```bash
npm install
cp .env.example .env.local       # optional — all modules run with mock data by default
npm run dev                      # http://localhost:3030

# checks
npm run typecheck
npm run lint
npm run build
```

The dashboard runs as a Next.js 14 app (App Router + React Server Components + Tailwind). No database, no external services are required to see the full UI — every adapter ships with a deterministic mock backend.

## Modules

| Module        | Page              | API                          | Real or mocked                                                                  |
| ------------- | ----------------- | ---------------------------- | ------------------------------------------------------------------------------- |
| Hermes        | `/hermes`         | `GET /api/hermes`            | mock (agent registry, tasks, logs, capability scorecard)                        |
| Obsidian      | `/obsidian`       | `GET /api/obsidian`          | **real read-only** when `OBSIDIAN_VAULT_PATH` is set; mock otherwise            |
| Aion          | `/aion`           | `GET /api/aion`              | mock (automations, event stream)                                                |
| Paperclip     | `/paperclip`      | `POST /api/paperclip/capture` | **real** in-process; persists to JSONL when `PAPERCLIP_STORE` is set            |
| Claude Code   | `/claude-code`    | `GET /api/claude-code`       | **real** branch + workspace from `.git/HEAD`; suggested prompts are mocked      |
| Capabilities  | `/capabilities`   | —                            | Hermes capability scorecard, sourced from the m3ta pack                          |
| Approvals     | `/approvals`      | —                            | UI present; approve/reject write-side not implemented                            |
| Runbook       | `/runbook`        | —                            | this doc, rendered inside the dashboard                                          |
| Health        | —                 | `GET /api/health`            | always real                                                                     |

## Architecture

```
src/
  adapters/                # typed module adapters — single source of truth
    types.ts               # shared types: Agent, HermesTask, ObsidianSnapshot, ...
    hermes.ts              # mock orchestrator (HERMES_URL reserved)
    obsidian.ts            # filesystem-based read-only vault adapter + mock
    aion.ts                # mock chronos timeline
    paperclip.ts           # in-process + optional JSONL persistence
    claudeCode.ts          # reads .git/HEAD; surfaces suggested prompts
  app/
    layout.tsx             # shell: left rail + top bar
    page.tsx               # unified mission-control dashboard
    hermes|obsidian|aion|paperclip|claude-code|capabilities|approvals|runbook/
    api/                   # one route per adapter
  components/
    shell/                 # LeftRail, TopBar
    ui/                    # Card, Pill, Metric, StatusDot (design-system primitives)
    cards/                 # one card per module — consumed by both unified and per-module pages
```

The dashboard reads only through `src/adapters/*`. Swapping a mock backend for a live one is one file change per module — no other code needs to move.

## Environment variables

See `.env.example`. All variables are optional. Nothing falls back to insecure defaults.

- `OBSIDIAN_VAULT_PATH` — absolute path to an Obsidian vault. When set, the adapter walks `.md` files (skipping dotfiles), and computes note count, total bytes, top `#tag` counts, and recent files. Strictly read-only.
- `HERMES_URL`, `HERMES_API_KEY` — reserved for a future live orchestrator HTTP client.
- `AION_URL` — reserved for a future durable scheduler.
- `PAPERCLIP_STORE` — file path. When set, captures are appended as JSONL.
- `CLAUDE_CODE_WORKSPACE` — directory to introspect for branch + clean-tree status. Defaults to the Next.js process cwd.
- `M3TA_REQUIRE_APPROVALS` — when truthy, write-side actions require explicit approval through the approval inbox.

## Hermes capability scorecard

`/capabilities` renders the Hermes-style scorecard from the m3ta pack. Statuses today:

- **matched** — auto-generated skills, subagent delegation, approval gates.
- **partial** — channels (web only), memory (Obsidian + Claude Code memory dir, no unified router), scheduling (mock Aion), sandboxing (worktrees, no container sandbox), web (Firecrawl documented, not wired), observability (in-memory logs).
- **missing** — multi-model routing, multimodal, deployment persistence.

Update `CAPABILITIES` in `src/adapters/hermes.ts` as the system grows.

## What is real today

- Dashboard shell, navigation, design system primitives, all module pages.
- Obsidian read-only vault stats when `OBSIDIAN_VAULT_PATH` points to a real vault.
- Paperclip capture endpoint with input validation and optional JSONL persistence.
- Claude Code workspace introspection (branch from `.git/HEAD`, workspace path).
- `/api/health` for deploy probes.

## What is intentionally mocked

- Hermes agent registry, task queue, logs.
- Aion automations and event stream.
- Approval write-side (UI is present but disabled).
- Claude Code recent runs and suggested prompts.

Each mock is deterministic (no random data between renders) so you can wire up real backends one at a time without losing visual stability.

## Next integration steps

See `/runbook` in the running app, or:

1. Replace `getHermesSnapshot()` with an HTTP client against a real Hermes deployment.
2. Back Aion with a durable cron runner (Railway worker, container scheduler).
3. Build the Hermes memory router on top of Obsidian + Postgres.
4. Wire Firecrawl into the Paperclip card for URL captures.
5. Implement the approval write-side (`approve` / `modify` / `reject` endpoints with audit trail).
6. Deploy to Railway per `m3ta-agent-os-claude-code-pack/integrations/RAILWAY.md`.
