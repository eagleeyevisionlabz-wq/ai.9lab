# M3ta-0S Dashboard — Runbook

This runbook covers how Paperclip, Aion, Hermes, Obsidian, Claude Code, and the
dashboard are wired together; what is real vs mocked; environment variables;
and recommended next integration steps.

## Layered architecture

Per the M3ta agent OS protocol, the system is divided into:

1. **Interface layer** — Next.js App Router pages and the design-system
   primitives in `src/components/ui`.
2. **Orchestration layer** — Hermes is the planner / dispatcher. Today it is
   mocked in `src/adapters/hermes.ts`; the live HTTP adapter will read from
   `HERMES_URL`.
3. **Capability layer** — Aion (chronos), Paperclip (capture), Claude Code
   (implementation), plus reserved Firecrawl / browser slots.
4. **Memory layer** — Obsidian vault (durable, file-based) plus the Paperclip
   JSONL store. A unified memory router is the highest-leverage missing piece.
5. **Deployment layer** — Next.js dev server today. Railway / Docker overlays
   live in `m3ta-agent-os-claude-code-pack/integrations/`.

## Module wiring

```
                    +------------------+
                    |    Dashboard     |
                    | (Next.js / App)  |
                    +---------+--------+
                              |
              +---------------+----------------+
              |               |                |
        +-----v-----+   +-----v------+   +-----v------+
        |  Hermes   |   |  Obsidian  |   |    Aion    |
        |  mock     |   |  fs read   |   |    mock    |
        +-----+-----+   +-----+------+   +-----+------+
              ^               ^                ^
              |               |                |
        +-----+-----+         |          +-----+------+
        | Paperclip |---------+----------|Claude Code |
        | capture   |  routes captures   | workspace  |
        +-----------+   to vault/memory  +------------+
```

- Paperclip captures land in process memory, and optionally a JSONL file.
  Each capture carries `routedTo: ("obsidian" | "hermes-memory")[]` so the
  routing intent is durable even before the write side is implemented.
- Hermes orchestrates: the scorecard at `/capabilities` is the source of
  truth for what is matched, partial, or missing.
- Aion holds the schedule and the event stream.
- Claude Code reports on the workspace it was launched from.

## Environment variables

| Var | Purpose | Default behavior |
| --- | --- | --- |
| `OBSIDIAN_VAULT_PATH` | Absolute path to a real Obsidian vault | Mock vault |
| `HERMES_URL` | Future live orchestrator endpoint | Mock orchestrator |
| `HERMES_API_KEY` | Auth for `HERMES_URL` | — |
| `AION_URL` | Future durable scheduler endpoint | Mock chronos |
| `PAPERCLIP_STORE` | JSONL persistence path for captures | In-memory only |
| `CLAUDE_CODE_WORKSPACE` | Workspace to introspect | `process.cwd()` |
| `M3TA_REQUIRE_APPROVALS` | Gate write-side actions | `1` (require) |

No secret is committed. `.env.example` is the canonical list.

## Local development

```bash
npm install
npm run dev           # http://localhost:3030
npm run typecheck
npm run lint
npm run build
```

The build is fully self-contained — no external services required.

## Smoke tests

| Surface | Check |
| --- | --- |
| `/` | All five module cards render with deterministic mock data |
| `/api/health` | Returns `{ ok: true, service: "m3ta-os-dashboard" }` |
| `/api/hermes` | Returns full snapshot with agents, tasks, logs, capabilities |
| `/api/obsidian` | Returns mock snapshot; or live stats if `OBSIDIAN_VAULT_PATH` is set |
| `/api/paperclip/capture` | `POST` with title + body returns a 201 + capture |
| `/capabilities` | Renders the Hermes scorecard table |
| `/approvals` | Renders any task with `approval=required` |

## What is real vs mocked

| Real | Mocked |
| --- | --- |
| Dashboard shell, design system, all routes | Hermes agents / tasks / logs |
| Obsidian fs read when path set | Hermes capability scorecard text (sourced from m3ta pack) |
| Paperclip capture endpoint + validation | Aion automations + events |
| Paperclip JSONL persistence when configured | Approval write-side |
| Claude Code branch + workspace from `.git/HEAD` | Claude Code recent runs + suggested prompts |
| `/api/health` | — |

## Recommended next integration order

1. **Hermes live adapter** — replace `getHermesSnapshot()` body with an HTTP
   client against `HERMES_URL`. Keep the same return shape; nothing else
   moves. Validate with a unit test that hits a recorded fixture.
2. **Aion durable scheduler** — Railway worker or container cron emitting
   into the same `AionEvent` stream the mock uses.
3. **Memory router** — sit between Paperclip and Obsidian / Postgres,
   honoring `routedTo`.
4. **Firecrawl in Paperclip** — server action that takes a URL, fetches via
   Firecrawl, normalizes, and calls `addCapture()` with `kind="research"`.
5. **Approval write-side** — `POST /api/approvals/:id` with `approve`,
   `modify`, `reject` actions, audit-logged to Hermes.
6. **Multi-channel surface** — Slack + Telegram inbound, both routed to the
   same Paperclip endpoint.
7. **Multi-model routing** — tool router beneath Hermes that can dispatch to
   Claude, OpenAI, Gemini, or local models per skill.
8. **Deployment persistence** — Railway deploy per the pack overlay so the
   dashboard runs when the laptop is closed.

## Design system

All visual choices follow `m3ta-agent-os-claude-code-pack/DESIGN-SYSTEM.md`:

- Dark default palette (`#0B0F14` background, `#00D1B2` primary accent).
- Tabular numerics in metrics.
- Status dots with reduced-motion fallback.
- Calm power: motion only reveals state, never decorates.
- Mission-control layout: left rail + top bar + main canvas.

If you change the palette, update `tailwind.config.ts` and `globals.css` in
the same change so the system remains coherent.
