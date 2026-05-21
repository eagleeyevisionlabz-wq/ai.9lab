import { AionSnapshot } from "@/adapters/types";
import { Card } from "../ui/Card";
import { Pill } from "../ui/Pill";

function relative(ts: string): string {
  const diff = new Date(ts).getTime() - Date.now();
  const abs = Math.abs(diff);
  const mins = Math.round(abs / 60000);
  if (mins < 1) return diff >= 0 ? "now" : "just now";
  if (mins < 60) return diff >= 0 ? `in ${mins}m` : `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 48) return diff >= 0 ? `in ${hours}h` : `${hours}h ago`;
  const days = Math.round(hours / 24);
  return diff >= 0 ? `in ${days}d` : `${days}d ago`;
}

export function AionCard({ snap }: { snap: AionSnapshot }) {
  return (
    <Card
      title="Aion — chronos"
      subtitle={snap.status.message}
      right={<Pill tone={snap.status.mode === "live" ? "ok" : "default"}>{snap.status.mode}</Pill>}
    >
      <div>
        <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">Automations</div>
        <ul className="space-y-2">
          {snap.automations.map((a) => (
            <li
              key={a.id}
              className="flex items-start justify-between gap-3 rounded-md border border-border bg-elevated px-3 py-2"
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-text">{a.name}</span>
                  <Pill tone="violet">{a.category}</Pill>
                  {!a.enabled ? <Pill tone="warn">disabled</Pill> : null}
                </div>
                <div className="mt-0.5 text-xs text-muted">{a.cadence}</div>
              </div>
              <div className="text-right text-xs">
                <div className="tabular text-text">{relative(a.nextRunAt)}</div>
                {a.lastRunAt ? (
                  <div className="tabular text-faint">last {relative(a.lastRunAt)}</div>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-4">
        <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">Event stream</div>
        <ul className="space-y-1 font-mono text-[11px]">
          {snap.events.map((e) => (
            <li key={e.id} className="flex gap-2 text-muted">
              <span className="tabular text-faint">{relative(e.ts)}</span>
              <span
                className={
                  e.kind === "failed"
                    ? "text-danger"
                    : e.kind === "completed"
                    ? "text-ok"
                    : "text-text"
                }
              >
                [{e.kind}]
              </span>
              <span className="truncate">{e.message}</span>
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
