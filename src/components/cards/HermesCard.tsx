import { HermesSnapshot } from "@/adapters/types";
import { Card } from "../ui/Card";
import { Metric } from "../ui/Metric";
import { Pill } from "../ui/Pill";
import { Status, StatusDot } from "../ui/StatusDot";

function agentStateToStatus(s: string): Status {
  if (s === "idle" || s === "complete" || s === "acting" || s === "planning")
    return s as Status;
  if (s === "waiting") return "waiting";
  if (s === "blocked") return "blocked";
  if (s === "failed") return "failed";
  return "idle";
}

export function HermesCard({ snap }: { snap: HermesSnapshot }) {
  const active = snap.agents.filter((a) => a.state !== "idle").length;
  const matched = snap.capabilities.filter((c) => c.status === "matched").length;
  return (
    <Card
      title="Hermes — orchestrator"
      subtitle={snap.status.message}
      right={<Pill tone={snap.status.mode === "live" ? "ok" : "default"}>{snap.status.mode}</Pill>}
    >
      <div className="grid grid-cols-3 gap-3">
        <Metric label="Active agents" value={active} hint={`${snap.agents.length} total`} tone="accent" />
        <Metric label="Open tasks" value={snap.tasks.length} />
        <Metric label="Capabilities matched" value={`${matched}/${snap.capabilities.length}`} tone="ok" />
      </div>

      <div className="mt-4">
        <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">Agents</div>
        <ul className="space-y-2">
          {snap.agents.map((a) => (
            <li
              key={a.id}
              className="flex items-start justify-between gap-3 rounded-md border border-border bg-elevated px-3 py-2"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2 text-sm text-text">
                  <span className="font-medium">{a.name}</span>
                  <span className="text-xs text-faint">{a.role}</span>
                </div>
                {a.currentTask ? (
                  <div className="mt-0.5 truncate text-xs text-muted">{a.currentTask}</div>
                ) : null}
                {a.nextAction ? (
                  <div className="mt-0.5 truncate text-[11px] text-faint">next: {a.nextAction}</div>
                ) : null}
              </div>
              <StatusDot status={agentStateToStatus(a.state)} label={a.state} />
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
