# M3ta-OS Execution Backbone

This directory defines the first operational contract between Qu3bii, Grokky/GrokBot, ODS, BB, Omarchy, Mac M5, Argus, Sentinel, and Archivist.

## Included foundations

1. `ods/job-schema.yaml` — canonical ODS job lifecycle, mission schema, policy gates, and node/model routing fields.
2. `templates/qu3bii-mission-packet.yaml` — the compact task capsule Qu3bii uses before dispatching technical work.
3. `bb/AGENTS.md` — BB software-factory operating protocol, isolation rules, verification contract, and completion record.

## Flow

`M3ta/Hermes → Qu3bii → ODS → BB/Omarchy/Mac M5 → Argus → ODS → Qu3bii → M3ta`

## Safety baseline

- GrokBot coordinates business-facing work; it is not the default code, terminal, artifact, or local-model environment.
- ODS assigns immutable job IDs and records routing, execution, evidence, and approval state.
- BB must only execute technical work that includes a valid ODS mission ID and acceptance criteria.
- Production deployment, external communication, credential changes, destructive operations, payments, and data migrations require explicit M3ta approval.
