import { ClaudeCodeSnapshot } from "@/adapters/types";
import { Card } from "../ui/Card";
import { Pill } from "../ui/Pill";

export function ClaudeCodeCard({ snap }: { snap: ClaudeCodeSnapshot }) {
  return (
    <Card
      title="Claude Code — implementation agent"
      subtitle={
        <span className="font-mono">
          {snap.branch} · {snap.workspace}
        </span>
      }
      right={
        <Pill tone={snap.cleanTree ? "ok" : "warn"}>
          {snap.cleanTree ? "tree ok" : "tree dirty"}
        </Pill>
      }
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">
            Suggested prompts
          </div>
          <ul className="space-y-2">
            {snap.suggested.map((s) => (
              <li
                key={s.id}
                className="rounded-md border border-border bg-elevated px-3 py-2"
              >
                <div className="text-sm text-text">{s.label}</div>
                <div className="mt-1 font-mono text-[11px] text-muted">{s.prompt}</div>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">
            Implementation status
          </div>
          <ul className="space-y-1 text-xs">
            {snap.implementationStatus.map((c) => (
              <li key={c.component} className="flex items-center justify-between gap-2">
                <span className="truncate text-text">{c.component}</span>
                <Pill
                  tone={
                    c.status === "matched"
                      ? "ok"
                      : c.status === "partial"
                      ? "warn"
                      : "danger"
                  }
                >
                  {c.status}
                </Pill>
              </li>
            ))}
          </ul>

          <div className="mb-2 mt-4 text-[10px] uppercase tracking-wider text-faint">
            Recent runs
          </div>
          <ul className="space-y-1 text-xs">
            {snap.recentRuns.map((r) => (
              <li
                key={r.id}
                className="flex items-center justify-between gap-2 rounded-md border border-border bg-elevated px-3 py-1.5"
              >
                <span className="truncate text-text">{r.title}</span>
                <Pill
                  tone={
                    r.state === "complete"
                      ? "ok"
                      : r.state === "failed"
                      ? "danger"
                      : r.state === "running"
                      ? "accent"
                      : "default"
                  }
                >
                  {r.state}
                </Pill>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}
