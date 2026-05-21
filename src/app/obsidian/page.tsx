import { getObsidianSnapshot } from "@/adapters/obsidian";
import { ObsidianCard } from "@/components/cards/ObsidianCard";
import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";

export default async function ObsidianPage() {
  const snap = await getObsidianSnapshot();
  return (
    <div className="space-y-6">
      <ObsidianCard snap={snap} />

      <Card title="All recent notes" subtitle="Sorted by modification time">
        <ul className="space-y-1 text-xs">
          {snap.recent.map((n) => (
            <li
              key={n.path}
              className="flex items-center justify-between gap-3 rounded-md border border-border bg-elevated px-3 py-1.5"
            >
              <div className="min-w-0">
                <div className="truncate text-text">{n.title}</div>
                <div className="truncate text-faint">{n.path}</div>
              </div>
              <div className="text-right tabular text-faint">
                {new Date(n.modifiedAt).toISOString().slice(0, 16).replace("T", " ")}
              </div>
            </li>
          ))}
        </ul>
      </Card>

      <Card title="Connection" subtitle="How to attach a real vault">
        <pre className="overflow-x-auto rounded-md border border-border bg-bg p-3 font-mono text-[11px] text-muted">
{`# .env.local
OBSIDIAN_VAULT_PATH=/absolute/path/to/your/Vault

# The adapter walks .md files (skips dotfiles like .obsidian / .git),
# computes note count, total bytes, and top tags from #tag tokens.
# It is strictly read-only.`}
        </pre>
      </Card>
    </div>
  );
}
