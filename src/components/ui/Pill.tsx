import { ReactNode } from "react";

type Tone = "default" | "accent" | "violet" | "warn" | "danger" | "ok";

const toneClass: Record<Tone, string> = {
  default: "border-border bg-elevated text-muted",
  accent: "border-accent/40 bg-accent/10 text-accent",
  violet: "border-violet/40 bg-violet/10 text-violet",
  warn: "border-warn/40 bg-warn/10 text-warn",
  danger: "border-danger/40 bg-danger/10 text-danger",
  ok: "border-ok/40 bg-ok/10 text-ok",
};

export function Pill({
  children,
  tone = "default",
}: {
  children: ReactNode;
  tone?: Tone;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider ${toneClass[tone]}`}
    >
      {children}
    </span>
  );
}
