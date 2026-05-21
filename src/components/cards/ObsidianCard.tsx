import { ObsidianSnapshot } from "@/adapters/types";
import { Card } from "../ui/Card";
import { Metric } from "../ui/Metric";
import { Pill } from "../ui/Pill";

function bytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(2)} MB`;
}

export function ObsidianCard({ snap }: { snap: ObsidianSnapshot }) {
  return (
    <Card
      title="Obsidian — vault"
      subtitle={snap.vaultPath ?? "OBSIDIAN_VAULT_PATH unset (mock vault)"}
      right={
        <div className="flex gap-1">
          <Pill tone={snap.status.mode === "live" ? "ok" : "default"}>{snap.status.mode}</Pill>
          <Pill tone={snap.ragReady ? "ok" : "warn"}>{snap.ragReady ? "RAG ready" : "RAG idle"}</Pill>
        </div>
      }
    >
      <div className="grid grid-cols-3 gap-3">
        <Metric label="Notes" value={snap.noteCount} />
        <Metric label="Bytes" value={bytes(snap.totalBytes)} />
        <Metric label="Tags" value={snap.tagCount} tone="accent" />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">Recent notes</div>
          <ul className="space-y-1 text-xs">
            {snap.recent.slice(0, 6).map((n) => (
              <li key={n.path} className="truncate text-muted">
                <span className="text-text">{n.title}</span>{" "}
                <span className="text-faint">· {n.path}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">Top tags</div>
          <div className="flex flex-wrap gap-1">
            {snap.topTags.slice(0, 10).map((t) => (
              <Pill key={t.tag} tone="violet">
                #{t.tag} · {t.count}
              </Pill>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
