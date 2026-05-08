# Safety model

The integration assumes UI-TARS-style providers can take real, irreversible
action on a user's machine or browser. Defaults err on the side of "do
nothing without explicit consent."

## Layers (in order of evaluation)

1. **Request gate** (`Governor.evaluate_request`)
   - Validates `starting_url` against `M3TA_UITARS_HOST_ALLOWLIST` if
     `M3TA_UITARS_ENFORCE_HOST_ALLOWLIST=true`.
2. **Plan gate** (`Governor.evaluate_plan`)
   - Every step must be in `M3TA_UITARS_ACTION_ALLOWLIST` or
     `M3TA_UITARS_CONFIRM_REQUIRED`.
   - Any step in the confirm list flips the plan to `requires_confirmation=true`
     unless a `confirmation_token` accompanies the request.
   - Any `navigate` step's target host must satisfy the host allowlist.
3. **Per-action gate** (`Governor.evaluate_action`)
   - Re-evaluated immediately before each action runs — defends against
     providers that ignore plans or that mutate plans during execution.
4. **Dry-run gate**
   - When `dry_run` is true, the engine never calls `provider.act`. The
     plan and audit log are still produced.
5. **Audit log**
   - Every event (created, plan, attempt, completion, block, screenshot,
     terminal) is JSONL-appended to `<audit_dir>/<task_id>.jsonl`.

## Confirmation tokens

`confirmation_token` is treated as opaque. It is the caller's
responsibility to bind it to a specific user authorization (e.g. an
out-of-band Apple Watch tap, a Slack approval, a Hermes UI confirm). The
engine simply requires its presence for risky actions.

## What this does NOT do

- It does not authenticate users. Authentication is the responsibility of
  the caller; the webhook layer only checks the shared `M3TA_UITARS_API_TOKEN`.
- It does not sandbox the provider. If the provider is a local desktop
  bridge, OS-level permissions still apply.
- It does not store screenshots. The audit log carries `screenshot_ref`
  strings; persistence is the provider's job.
