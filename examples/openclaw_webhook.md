# OpenClaw / generic webhook example

The HTTP surface is intentionally small — any system that can sign and POST
JSON can drive a task.

## Submit a task

```http
POST /v1/tasks HTTP/1.1
Host: m3ta-uitars.local:8765
Authorization: Bearer ${M3TA_UITARS_API_TOKEN}
Content-Type: application/json

{
  "instruction": "Open the Eagle Eye dashboard and screenshot the latest run",
  "agent_id": "hermes",
  "surface": "browser",
  "starting_url": "https://dash.example.com",
  "dry_run": true,
  "confirmation_token": "operator-approved-2026-05-08",
  "metadata": { "trace_id": "oc_4f81..." }
}
```

The response is the full `Task` record, including `id`, `status`, `plan`,
`result`, and `audit_log_path`. OpenClaw should persist `task.id` so it can
poll status or cancel later.

## Poll status

```http
GET /v1/tasks/{task_id} HTTP/1.1
Authorization: Bearer ${M3TA_UITARS_API_TOKEN}
```

## Cancel

```http
POST /v1/tasks/{task_id}/cancel HTTP/1.1
Authorization: Bearer ${M3TA_UITARS_API_TOKEN}
Content-Type: application/json

{ "task_id": "{task_id}", "reason": "user aborted from Apple Watch" }
```

## Event callback (n8n / OpenClaw → M3ta-0S)

Use `/v1/events` as a sink for upstream notifications. The engine logs them
without acting; wire policy on top once the contract is agreed.

```http
POST /v1/events HTTP/1.1
Authorization: Bearer ${M3TA_UITARS_API_TOKEN}
Content-Type: application/json

{ "source": "openclaw", "kind": "task.handoff", "data": { ... } }
```
