import { getHermesSnapshot } from "@/adapters/hermes";
import { getObsidianSnapshot } from "@/adapters/obsidian";
import { getAionSnapshot } from "@/adapters/aion";
import { getPaperclipSnapshot } from "@/adapters/paperclip";
import { getClaudeCodeSnapshot } from "@/adapters/claudeCode";
import { HermesCard } from "@/components/cards/HermesCard";
import { ObsidianCard } from "@/components/cards/ObsidianCard";
import { AionCard } from "@/components/cards/AionCard";
import { PaperclipCard } from "@/components/cards/PaperclipCard";
import { ClaudeCodeCard } from "@/components/cards/ClaudeCodeCard";
import { Card } from "@/components/ui/Card";
import { Metric } from "@/components/ui/Metric";
import { Pill } from "@/components/ui/Pill";

export const dynamic = "force-dynamic";

export default async function MissionControlPage() {
  const [hermes, obsidian, aion, paperclip, claude] = await Promise.all([
    getHermesSnapshot(),
    getObsidianSnapshot(),
    getAionSnapshot(),
    getPaperclipSnapshot(),
    getClaudeCodeSnapshot(),
  ]);

  const activeAgents = hermes.agents.filter((a) => a.state !== "idle").length;
  const pendingApprovals = hermes.tasks.filter((t) => t.approval === "required").length;
  const matchedCaps = hermes.capabilities.filter((c) => c.status === "matched").length;

  return (
    <div className="space-y-6">
      <section className="grid grid-cols-2 gap-3 md:grid-cols-5">
        <Metric label="Active agents" value={activeAgents} hint={`${hermes.agents.length} total`} tone="accent" />
        <Metric label="Open tasks" value={hermes.tasks.length} />
        <Metric label="Approvals" value={pendingApprovals} tone={pendingApprovals ? "warn" : "ok"} />
        <Metric
          label="Vault notes"
          value={obsidian.noteCount}
          hint={obsidian.vaultPath ? "live" : "mock"}
        />
        <Metric label="Hermes match" value={`${matchedCaps}/${hermes.capabilities.length}`} tone="ok" />
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <HermesCard snap={hermes} />
        <ObsidianCard snap={obsidian} />
        <AionCard snap={aion} />
        <PaperclipCard initial={paperclip} />
        <div className="xl:col-span-2">
          <ClaudeCodeCard snap={claude} />
        </div>
      </section>

      <Card
        title="Module status"
        subtitle="Every adapter reports its mode (mock vs live) and last check."
        right={<Pill tone="accent">m3ta protocol</Pill>}
      >
        <ul className="grid grid-cols-1 gap-2 text-xs md:grid-cols-2 lg:grid-cols-3">
          {[hermes.status, obsidian.status, aion.status, paperclip.status, claude.status].map((s) => (
            <li
              key={s.module}
              className="flex items-start justify-between gap-2 rounded-md border border-border bg-elevated px-3 py-2"
            >
              <div>
                <div className="text-text">{s.module}</div>
                <div className="text-faint">{s.message}</div>
              </div>
              <Pill tone={s.mode === "live" ? "ok" : "default"}>{s.mode}</Pill>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
