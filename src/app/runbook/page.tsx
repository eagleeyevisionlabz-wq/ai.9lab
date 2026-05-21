import { Card } from "@/components/ui/Card";

export const dynamic = "force-dynamic";

export default function RunbookPage() {
  return (
    <div className="space-y-6">
      <Card title="M3ta-0S runbook" subtitle="How the modules are wired, what is real, what is mocked.">
        <div className="prose prose-invert max-w-none text-sm">
          <h3 className="text-text">Architecture</h3>
          <ul className="text-muted">
            <li>
              <strong className="text-text">Hermes</strong> — orchestrator. Mock today; live adapter
              will replace <code>src/adapters/hermes.ts</code> when <code>HERMES_URL</code> is set.
            </li>
            <li>
              <strong className="text-text">Obsidian</strong> — read-only vault adapter. Set
              <code> OBSIDIAN_VAULT_PATH</code> to walk a real vault and compute note count, top tags,
              and recent files. Never writes.
            </li>
            <li>
              <strong className="text-text">Aion</strong> — chronos / scheduler. Mock today; design
              keeps automations, events, and rituals separate so a durable cron runner can attach.
            </li>
            <li>
              <strong className="text-text">Paperclip</strong> — capture endpoint
              (<code>POST /api/paperclip/capture</code>). In-memory by default; set
              <code> PAPERCLIP_STORE</code> to persist as JSONL.
            </li>
            <li>
              <strong className="text-text">Claude Code</strong> — workspace panel reads
              <code> .git/HEAD</code> and surfaces suggested prompts + implementation status. No
              shelling out.
            </li>
          </ul>

          <h3 className="text-text">Environment variables</h3>
          <pre className="rounded-md border border-border bg-bg p-3 font-mono text-[11px]">
{`OBSIDIAN_VAULT_PATH=        # absolute path; enables live Obsidian stats
HERMES_URL=                 # reserved; live orchestrator endpoint
HERMES_API_KEY=             # reserved
AION_URL=                   # reserved; live scheduler endpoint
PAPERCLIP_STORE=            # file path; enables JSONL persistence
CLAUDE_CODE_WORKSPACE=      # workspace path to report on
M3TA_REQUIRE_APPROVALS=1    # gate write-side actions
`}
          </pre>

          <h3 className="text-text">Running locally</h3>
          <pre className="rounded-md border border-border bg-bg p-3 font-mono text-[11px]">
{`npm install
cp .env.example .env.local   # optional
npm run dev                  # http://localhost:3030
npm run typecheck
npm run lint
npm run build`}
          </pre>

          <h3 className="text-text">What is real vs mocked</h3>
          <ul className="text-muted">
            <li><span className="text-ok">real</span> — Obsidian vault stats when path is set, Paperclip capture endpoint, Claude Code branch/workspace report.</li>
            <li><span className="text-warn">mock</span> — Hermes agents/tasks/logs, Aion automations/events, Claude Code recent runs.</li>
          </ul>

          <h3 className="text-text">Next integration steps</h3>
          <ol className="text-muted">
            <li>Replace <code>getHermesSnapshot()</code> with an HTTP client against a live Hermes deployment.</li>
            <li>Back Aion with a durable scheduler (Railway worker or container cron).</li>
            <li>Build the Hermes memory router on top of Obsidian and Postgres.</li>
            <li>Wire Firecrawl into the Paperclip card for URL captures.</li>
            <li>Stand up the approval write-side (approve/modify/reject endpoints).</li>
            <li>Deploy to Railway per <code>m3ta-agent-os-claude-code-pack/integrations/RAILWAY.md</code>.</li>
          </ol>
        </div>
      </Card>
    </div>
  );
}
