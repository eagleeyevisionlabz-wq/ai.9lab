# Architecture

## Layers

```
contracts.py      ── Pydantic schemas (Action, Plan, Task, ...)
config.py         ── env-driven Settings
audit.py          ── append-only JSONL writer
safety/governor.py── pure policy checker (no I/O)
providers/
  base.py         ── Provider ABC: observe / plan / act
  mock.py         ── deterministic in-memory
  local_uitars.py ── HTTP bridge to UI-TARS Desktop (stub contract)
  remote_operator ── HTTP client for hosted operators
engine.py         ── orchestrator: state machine, gate, audit
server/
  mcp_server.py   ── MCP tools surface
  http_app.py     ── FastAPI webhook surface
sdk/
  client.py       ── InProcessClient + HTTPClient
```

## Task state machine

```
   submit_task
       │
       ▼
   pending ──► planning ──► awaiting_confirmation
                  │              │
                  ▼              ▼
                running ◄── (with confirmation_token)
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
   succeeded  failed   cancelled / timed_out
```

Every transition writes one or more entries to `<audit_dir>/<task_id>.jsonl`.

## Why three surfaces?

- **MCP** is the right shape for native agent toolchains.
- **HTTP webhooks** are how n8n, OpenClaw, and Apple Shortcuts will call us.
- **SDK** lets in-process agents (Hermes, Metatron) skip the network entirely.

All three reduce to the same `Engine` + capability contract, so behavior and
audit semantics match across surfaces.
