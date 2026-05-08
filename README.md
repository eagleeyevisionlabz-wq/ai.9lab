# ai.9lab — M3ta-0S UI-TARS Integration

A careful, production-minded integration layer that brings UI-TARS-style
visual computer/browser control into the M3ta-0S ecosystem (Qu3bii, Hermes,
Metatron, and related agents) as a first-class capability.

It exposes one capability contract through three surfaces:

- **MCP server** — tools callable from any MCP client (Claude Desktop, OpenClaw, etc.)
- **HTTP webhook surface** — n8n / OpenClaw friendly REST endpoints
- **Agent SDK** — in-process or HTTP client for Qu3bii, Hermes, Metatron

> Status: **scaffold + mock provider work end-to-end.** Concrete UI-TARS
> Desktop control is gated behind a documented bridge contract — the
> `local_uitars` provider will fail loudly until that bridge exists. See
> [Limitations](#limitations).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# 1. Run the validation script (no external deps)
python -m scripts.validate

# 2. Run the test suite
pytest

# 3. Start the HTTP/webhook surface
m3ta-uitars-server     # or: python -m m3ta_uitars.server.http_app

# 4. Start the MCP server (requires `pip install m3ta-uitars[mcp]`)
m3ta-uitars-mcp        # or: python -m m3ta_uitars.server.mcp_server
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ Agents: Qu3bii · Hermes · Metatron · M3ta-0S · n8n · OpenClaw   │
└─────────────────────────────────────────────────────────────────┘
            │                │                  │
            ▼                ▼                  ▼
      ┌──────────┐    ┌──────────────┐    ┌──────────────┐
      │ Agent SDK│    │ MCP server   │    │ HTTP webhooks│
      └──────────┘    └──────────────┘    └──────────────┘
            └────────────────┴───────────────────┘
                             ▼
                      ┌──────────────┐
                      │   Engine     │  ← orchestrates the contract
                      └──────────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
          Governor      AuditLogger    Provider
          (safety)      (JSONL)        ├── mock
                                       ├── local_uitars (bridge stub)
                                       └── remote_operator (HF / Doubao)
```

## Capability contract

`src/m3ta_uitars/contracts.py` defines the durable types every surface speaks:

| Method        | Behavior                                                 |
|---------------|----------------------------------------------------------|
| `observe`     | Capture a single screen / page state                     |
| `plan`        | Produce an action plan (no side effects)                 |
| `act`         | Execute one action and return the new observation        |
| `run_task`    | Submit + drive a task to a terminal status               |
| `cancel_task` | Cancel an in-flight task                                 |
| `status`      | Return the current `Task` record                         |
| `audit_log`   | Return the JSONL audit trail for a task                  |

`TaskStatus` ∈ `pending · planning · awaiting_confirmation · running · succeeded · failed · cancelled · timed_out`.

## Provider abstraction

| Provider          | Use                                                   | State                |
|-------------------|-------------------------------------------------------|----------------------|
| `mock`            | tests, dry-runs, CI                                    | works                |
| `local_uitars`    | UI-TARS Desktop on macOS via local bridge              | bridge stub — see TODO |
| `remote_operator` | Hosted (HF UI-TARS-1.5, VolcEngine Doubao, custom)     | wired, untested in this repo without credentials |

Switch providers via `M3TA_UITARS_PROVIDER`. See [.env.example](./.env.example).

## Surfaces

### MCP server

Tools exposed:
- `m3ta_uitars_run_task`
- `m3ta_uitars_observe`
- `m3ta_uitars_status`
- `m3ta_uitars_cancel`
- `m3ta_uitars_audit_log`

Each tool ships an input schema with safe descriptions. The MCP runtime
itself is an optional dependency (`pip install m3ta-uitars[mcp]`); the tool
dispatcher in `m3ta_uitars.server.mcp_server` is exported as plain async
functions for testing and embedding.

### HTTP / webhook surface

| Method | Path                              | Purpose                              |
|--------|-----------------------------------|--------------------------------------|
| GET    | `/v1/health`                      | health (unauthenticated)             |
| POST   | `/v1/tasks`                       | submit + run (sync)                  |
| POST   | `/v1/tasks/submit`                | submit only                          |
| POST   | `/v1/tasks/{id}/run`              | drive a previously submitted task    |
| GET    | `/v1/tasks/{id}`                  | status                               |
| POST   | `/v1/tasks/{id}/cancel`           | cancel                               |
| GET    | `/v1/tasks/{id}/audit`            | JSONL audit entries                  |
| POST   | `/v1/observe`                     | one-shot observation                 |
| POST   | `/v1/events`                      | callback sink for n8n/OpenClaw       |

Auth: when `M3TA_UITARS_API_TOKEN` is set, every non-health request must
present the token via `Authorization: Bearer <token>` or `X-M3TA-Token: <token>`.

See [`examples/openclaw_webhook.md`](./examples/openclaw_webhook.md) and
[`examples/n8n_workflow.json`](./examples/n8n_workflow.json).

### Agent SDK

```python
from m3ta_uitars.sdk import InProcessClient

sdk = InProcessClient()
task = await sdk.run_computer_task(
    instruction="Open the Eagle Eye dashboard and screenshot the latest run",
    agent_id="hermes",
    starting_url="https://dash.example.com",
    dry_run=True,
    confirmation_token="operator-approved-2026-05-08",
)
print(task.status, task.plan, task.result)
```

For agents running outside the host process:

```python
from m3ta_uitars.sdk import HTTPClient

sdk = HTTPClient(base_url="http://m3ta-uitars.local:8765",
                 api_token=os.environ["M3TA_UITARS_API_TOKEN"])
```

Both clients implement the same `M3taUITARSClient` Protocol.

## Safety model

- **Default-dry-run.** `M3TA_UITARS_DEFAULT_DRY_RUN=true` makes every task
  plan-only unless the caller explicitly opts in.
- **Action allowlist.** Only types in `M3TA_UITARS_ACTION_ALLOWLIST` (or
  in the confirmation list with a token) are runnable.
- **Confirmation gate.** Risky action types
  (`navigate,type,click,key,scroll`) require `confirmation_token` in the
  request. Without it, the task halts in `awaiting_confirmation` and the
  plan is preserved for human review.
- **Host allowlist.** When `M3TA_UITARS_ENFORCE_HOST_ALLOWLIST=true`,
  any `navigate` target or `starting_url` must match a host in
  `M3TA_UITARS_HOST_ALLOWLIST` (suffix-matching for subdomains).
- **Audit log.** Every task gets an append-only JSONL file at
  `<audit_dir>/<task_id>.jsonl` with task creation, plan, every action
  attempt/completion/block, screenshot refs, and terminal status.
- **Timeouts.** `M3TA_UITARS_TASK_TIMEOUT_SECONDS` caps wall-clock time per
  task.
- **No secrets in code.** All endpoints, tokens, and keys are env-driven.

## Hybrid runtime

| Runtime          | Host                            | Provider             |
|------------------|----------------------------------|----------------------|
| `macos_local`    | macOS host + UI-TARS Desktop    | `local_uitars`       |
| `docker_server`  | Linux container, headless       | `remote_operator`    |
| `hybrid`         | Both sides reachable            | per-task selection   |

Set `M3TA_UITARS_RUNTIME` to advertise the deployment. The provider is the
ultimate switch; `runtime` is metadata for clients and the `/v1/health`
response.

## Configuration

See [.env.example](./.env.example) for the full set. Highlights:

| Var                                      | Purpose                              |
|------------------------------------------|--------------------------------------|
| `M3TA_UITARS_PROVIDER`                   | `mock` / `local_uitars` / `remote_operator` |
| `M3TA_UITARS_API_TOKEN`                  | Webhook bearer token                 |
| `M3TA_UITARS_LOCAL_BRIDGE_URL`           | URL of the (future) UI-TARS bridge   |
| `M3TA_UITARS_REMOTE_BASE_URL`            | Hosted operator base URL             |
| `M3TA_UITARS_HOST_ALLOWLIST`             | Allowed nav hosts (CSV)              |
| `M3TA_UITARS_DEFAULT_DRY_RUN`            | Default dry-run posture              |
| `M3TA_UITARS_AUDIT_DIR`                  | Where JSONL audit goes               |

## Tests / validation

```bash
pytest                       # full suite
python -m scripts.validate   # standalone smoke check (no test framework needed)
```

## Limitations

1. **No real UI-TARS Desktop control yet.** UI-TARS Desktop does not ship a
   documented external automation API. `LocalUITARSProvider` defines the
   bridge contract (`/observe`, `/plan`, `/act`) and will raise loudly until
   that bridge is implemented. See `TODO(uitars-bridge)` in
   `src/m3ta_uitars/providers/local_uitars.py`.
2. **`RemoteOperatorProvider` is wired but unverified** in this repo
   without credentials and a reachable hosted endpoint.
3. **In-memory task store.** Tasks live in process memory. If the server
   restarts, in-flight task IDs are lost. Audit logs persist on disk.
4. **No screenshot persistence beyond ref strings.** The schema carries a
   `screenshot_ref`; storing the actual image bytes is up to the provider /
   bridge.
5. **No multi-tenant isolation yet.** A single `agent_id` is captured in the
   audit log but not used to scope task access.

## Follow-up tasks

- [ ] Implement the UI-TARS Desktop bridge (`/observe`, `/plan`, `/act`)
      against a real ByteDance / community automation surface.
- [ ] Add a persistent task store (SQLite / Redis) so tasks survive restarts.
- [ ] Add screenshot byte storage with content-addressed refs.
- [ ] Add per-`agent_id` ACLs and rate limits.
- [ ] Provide example MCP client config snippets for Claude Desktop.
- [ ] Add an n8n custom node wrapping the SDK directly.
