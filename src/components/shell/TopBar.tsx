import { Pill } from "../ui/Pill";

export function TopBar() {
  return (
    <header className="flex items-center justify-between border-b border-border bg-surface/80 px-6 py-3 backdrop-blur">
      <div className="flex items-center gap-3">
        <span className="text-sm font-semibold tracking-wide text-text">
          Mission Control
        </span>
        <Pill tone="accent">m3ta-0s · sovereign</Pill>
        <Pill tone="violet">hermes hybrid</Pill>
      </div>
      <div className="flex items-center gap-2 text-xs text-muted">
        <span className="tabular">{new Date().toUTCString().slice(5, 22)} UTC</span>
        <Pill tone="ok">/health</Pill>
      </div>
    </header>
  );
}
