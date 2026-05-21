import { ReactNode } from "react";

export function Metric({
  label,
  value,
  hint,
  tone = "default",
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: "default" | "accent" | "warn" | "danger" | "ok";
}) {
  const toneClass: Record<string, string> = {
    default: "text-text",
    accent: "text-accent",
    warn: "text-warn",
    danger: "text-danger",
    ok: "text-ok",
  };
  return (
    <div className="rounded-lg border border-border bg-elevated px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-faint">
        {label}
      </div>
      <div className={`tabular text-xl font-semibold ${toneClass[tone]}`}>
        {value}
      </div>
      {hint ? <div className="text-xs text-muted">{hint}</div> : null}
    </div>
  );
}
