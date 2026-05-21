import { getHermesSnapshot } from "@/adapters/hermes";
import { HermesCard } from "@/components/cards/HermesCard";
import { Card } from "@/components/ui/Card";
import { Pill } from "@/components/ui/Pill";

export const dynamic = "force-dynamic";

export default async function HermesPage() {
  const snap = await getHermesSnapshot();
  return (
    <div className="space-y-6">
      <HermesCard snap={snap} />

      <Card title="Tasks" subtitle="Open work managed by the orchestrator">
        <ul className="space-y-2 text-sm">
          {snap.tasks.map((t) => (
            <li
              key={t.id}
              className="flex items-center justify-between gap-3 rounded-md border border-border bg-elevated px-3 py-2"
            >
              <div className="min-w-0">
                <div className="truncate text-text">{t.title}</div>
                <div className="text-xs text-faint">agent {t.agentId} · {t.state}</div>
              </div>
              {t.approval === "required" ? (
                <Pill tone="warn">approval required</Pill>
              ) : (
                <Pill>{t.approval}</Pill>
              )}
            </li>
          ))}
        </ul>
      </Card>

      <Card title="Trace" subtitle="Recent orchestrator log entries">
        <ul className="space-y-1 font-mono text-[11px]">
          {snap.logs.map((l) => (
            <li key={l.id} className="flex gap-2 text-muted">
              <span className="tabular text-faint">{l.ts.slice(11, 19)}</span>
              <span
                className={
                  l.level === "warn"
                    ? "text-warn"
                    : l.level === "error"
                    ? "text-danger"
                    : l.level === "trace"
                    ? "text-violet"
                    : "text-accent"
                }
              >
                {l.level}
              </span>
              <span className="text-faint">{l.agentId ?? "—"}</span>
              <span className="text-text">{l.message}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
