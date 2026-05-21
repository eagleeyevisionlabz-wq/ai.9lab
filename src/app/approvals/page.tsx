import { getHermesSnapshot } from "@/adapters/hermes";
import { Card } from "@/components/ui/Card";
import { Pill } from "@/components/ui/Pill";

export const dynamic = "force-dynamic";

export default async function ApprovalsPage() {
  const snap = await getHermesSnapshot();
  const pending = snap.tasks.filter((t) => t.approval === "required");
  return (
    <div className="space-y-6">
      <Card
        title="Approval inbox"
        subtitle="Irreversible or risky actions wait here until a human approves."
        right={<Pill tone={pending.length ? "warn" : "ok"}>{pending.length} pending</Pill>}
      >
        {pending.length === 0 ? (
          <p className="text-sm text-muted">Nothing waiting. Sovereign loop is idle.</p>
        ) : (
          <ul className="space-y-3">
            {pending.map((t) => (
              <li
                key={t.id}
                className="rounded-md border border-warn/40 bg-warn/5 px-3 py-2"
              >
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm text-text">{t.title}</div>
                    <div className="text-xs text-faint">agent {t.agentId} · {t.state}</div>
                  </div>
                  <div className="flex gap-1">
                    <button
                      disabled
                      title="Approval write side not yet implemented"
                      className="rounded-md border border-ok/40 bg-ok/10 px-3 py-1 text-xs font-medium text-ok opacity-60"
                    >
                      approve
                    </button>
                    <button
                      disabled
                      className="rounded-md border border-border bg-elevated px-3 py-1 text-xs font-medium text-muted opacity-60"
                    >
                      modify
                    </button>
                    <button
                      disabled
                      className="rounded-md border border-danger/40 bg-danger/10 px-3 py-1 text-xs font-medium text-danger opacity-60"
                    >
                      reject
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
