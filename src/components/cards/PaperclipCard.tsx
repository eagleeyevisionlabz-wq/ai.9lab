"use client";

import { useState, useTransition } from "react";
import { CaptureKind, PaperclipSnapshot } from "@/adapters/types";
import { Card } from "../ui/Card";
import { Pill } from "../ui/Pill";
import { Metric } from "../ui/Metric";

const KINDS: CaptureKind[] = ["clip", "doc", "snippet", "research", "link"];

export function PaperclipCard({ initial }: { initial: PaperclipSnapshot }) {
  const [snap, setSnap] = useState(initial);
  const [pending, start] = useTransition();
  const [form, setForm] = useState({
    kind: "clip" as CaptureKind,
    title: "",
    source: "",
    body: "",
    tags: "",
    routeObsidian: true,
    routeHermes: true,
  });

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.title.trim() || !form.body.trim()) return;
    start(async () => {
      const res = await fetch("/api/paperclip/capture", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          kind: form.kind,
          title: form.title,
          source: form.source || undefined,
          body: form.body,
          tags: form.tags
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean),
          routedTo: [
            ...(form.routeObsidian ? ["obsidian"] : []),
            ...(form.routeHermes ? ["hermes-memory"] : []),
          ],
        }),
      });
      if (res.ok) {
        const next: PaperclipSnapshot = await (
          await fetch("/api/paperclip", { cache: "no-store" })
        ).json();
        setSnap(next);
        setForm({ ...form, title: "", source: "", body: "", tags: "" });
      }
    });
  }

  return (
    <Card
      title="Paperclip — capture"
      subtitle={snap.status.message}
      right={<Pill tone={snap.status.mode === "live" ? "ok" : "default"}>{snap.status.mode}</Pill>}
    >
      <div className="grid grid-cols-5 gap-2">
        {KINDS.map((k) => (
          <Metric key={k} label={k} value={snap.byKind[k]} />
        ))}
      </div>

      <form onSubmit={submit} className="mt-4 space-y-2">
        <div className="flex gap-2">
          <select
            value={form.kind}
            onChange={(e) => setForm({ ...form, kind: e.target.value as CaptureKind })}
            className="rounded-md border border-border bg-elevated px-2 py-1 text-xs text-text"
          >
            {KINDS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
          <input
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="title"
            className="flex-1 rounded-md border border-border bg-elevated px-2 py-1 text-xs text-text placeholder:text-faint"
          />
          <input
            value={form.source}
            onChange={(e) => setForm({ ...form, source: e.target.value })}
            placeholder="source (url or path)"
            className="flex-1 rounded-md border border-border bg-elevated px-2 py-1 text-xs text-text placeholder:text-faint"
          />
        </div>
        <textarea
          value={form.body}
          onChange={(e) => setForm({ ...form, body: e.target.value })}
          placeholder="body / notes"
          rows={3}
          className="w-full rounded-md border border-border bg-elevated px-2 py-1 font-mono text-xs text-text placeholder:text-faint"
        />
        <div className="flex flex-wrap items-center gap-2">
          <input
            value={form.tags}
            onChange={(e) => setForm({ ...form, tags: e.target.value })}
            placeholder="tags, comma separated"
            className="flex-1 rounded-md border border-border bg-elevated px-2 py-1 text-xs text-text placeholder:text-faint"
          />
          <label className="flex items-center gap-1 text-xs text-muted">
            <input
              type="checkbox"
              checked={form.routeObsidian}
              onChange={(e) => setForm({ ...form, routeObsidian: e.target.checked })}
            />
            obsidian
          </label>
          <label className="flex items-center gap-1 text-xs text-muted">
            <input
              type="checkbox"
              checked={form.routeHermes}
              onChange={(e) => setForm({ ...form, routeHermes: e.target.checked })}
            />
            hermes-memory
          </label>
          <button
            type="submit"
            disabled={pending}
            className="rounded-md border border-accent/40 bg-accent/10 px-3 py-1 text-xs font-medium text-accent hover:bg-accent/20 disabled:opacity-50"
          >
            {pending ? "capturing…" : "capture"}
          </button>
        </div>
      </form>

      <div className="mt-4">
        <div className="mb-2 text-[10px] uppercase tracking-wider text-faint">
          Recent captures
        </div>
        <ul className="space-y-1 text-xs">
          {snap.recent.slice(0, 6).map((c) => (
            <li
              key={c.id}
              className="flex items-start gap-2 rounded-md border border-border bg-elevated px-2 py-1.5"
            >
              <Pill tone="violet">{c.kind}</Pill>
              <div className="min-w-0 flex-1">
                <div className="truncate text-text">{c.title}</div>
                {c.source ? (
                  <div className="truncate text-[11px] text-faint">{c.source}</div>
                ) : null}
              </div>
              <div className="flex flex-col items-end gap-0.5 text-[10px] text-faint">
                {c.routedTo.map((r) => (
                  <span key={r}>→ {r}</span>
                ))}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}
