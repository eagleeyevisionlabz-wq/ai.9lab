import { getHermesSnapshot } from "@/adapters/hermes";
import { Card } from "@/components/ui/Card";
import { Pill } from "@/components/ui/Pill";

export const dynamic = "force-dynamic";

const TONE: Record<string, "ok" | "warn" | "danger" | "default"> = {
  matched: "ok",
  partial: "warn",
  missing: "danger",
  "not-applicable": "default",
};

export default async function CapabilitiesPage() {
  const snap = await getHermesSnapshot();
  const matched = snap.capabilities.filter((c) => c.status === "matched").length;
  const partial = snap.capabilities.filter((c) => c.status === "partial").length;
  const missing = snap.capabilities.filter((c) => c.status === "missing").length;

  return (
    <div className="space-y-6">
      <Card
        title="Hermes capability scorecard"
        subtitle="How M3ta-0S compares against Hermes Agent-style capabilities. Source: m3ta pack."
        right={
          <div className="flex gap-1">
            <Pill tone="ok">{matched} matched</Pill>
            <Pill tone="warn">{partial} partial</Pill>
            <Pill tone="danger">{missing} missing</Pill>
          </div>
        }
      >
        <div className="overflow-hidden rounded-md border border-border">
          <table className="w-full text-sm">
            <thead className="bg-elevated text-[10px] uppercase tracking-wider text-faint">
              <tr>
                <th className="px-3 py-2 text-left">Capability</th>
                <th className="px-3 py-2 text-left">Status</th>
                <th className="px-3 py-2 text-left">Evidence</th>
                <th className="px-3 py-2 text-left">Next upgrade</th>
              </tr>
            </thead>
            <tbody>
              {snap.capabilities.map((c) => (
                <tr key={c.id} className="border-t border-border align-top">
                  <td className="px-3 py-2 text-text">{c.label}</td>
                  <td className="px-3 py-2">
                    <Pill tone={TONE[c.status]}>{c.status}</Pill>
                  </td>
                  <td className="px-3 py-2 text-muted">{c.evidence}</td>
                  <td className="px-3 py-2 text-muted">{c.nextUpgrade}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
