export type Status =
  | "idle"
  | "planning"
  | "acting"
  | "waiting"
  | "blocked"
  | "failed"
  | "complete"
  | "ok"
  | "partial"
  | "missing"
  | "matched"
  | "na";

const colorMap: Record<Status, string> = {
  idle: "bg-faint",
  planning: "bg-accent pulse-soft",
  acting: "bg-violet pulse-soft",
  waiting: "bg-warn pulse-soft",
  blocked: "bg-warn",
  failed: "bg-danger",
  complete: "bg-ok",
  ok: "bg-ok",
  partial: "bg-warn",
  missing: "bg-danger",
  matched: "bg-ok",
  na: "bg-faint",
};

export function StatusDot({
  status,
  label,
}: {
  status: Status;
  label?: string;
}) {
  return (
    <span className="inline-flex items-center gap-2 text-xs text-muted">
      <span
        aria-label={status}
        className={`inline-block h-2 w-2 rounded-full ${colorMap[status]}`}
      />
      {label ?? status}
    </span>
  );
}
