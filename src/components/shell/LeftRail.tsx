import Link from "next/link";

const NAV = [
  { href: "/", label: "Mission Control", group: "control" },
  { href: "/hermes", label: "Hermes", group: "control" },
  { href: "/obsidian", label: "Obsidian", group: "control" },
  { href: "/aion", label: "Aion", group: "control" },
  { href: "/paperclip", label: "Paperclip", group: "control" },
  { href: "/claude-code", label: "Claude Code", group: "control" },
  { href: "/capabilities", label: "Hermes Scorecard", group: "ops" },
  { href: "/approvals", label: "Approvals", group: "ops" },
  { href: "/runbook", label: "Runbook", group: "ops" },
];

export function LeftRail() {
  return (
    <aside className="flex h-screen flex-col border-r border-border bg-surface px-3 py-4">
      <Link href="/" className="mb-6 block px-2">
        <div className="text-xs uppercase tracking-[0.3em] text-faint">
          M3ta-0S
        </div>
        <div className="text-base font-semibold text-text">Mission Control</div>
      </Link>

      <nav className="flex flex-1 flex-col gap-6 text-sm">
        <div>
          <div className="px-2 text-[10px] uppercase tracking-wider text-faint">
            Modules
          </div>
          <ul className="mt-2 space-y-1">
            {NAV.filter((n) => n.group === "control").map((n) => (
              <li key={n.href}>
                <Link
                  href={n.href}
                  className="block rounded-md px-2 py-1.5 text-muted hover:bg-elevated hover:text-text"
                >
                  {n.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <div className="px-2 text-[10px] uppercase tracking-wider text-faint">
            Ops
          </div>
          <ul className="mt-2 space-y-1">
            {NAV.filter((n) => n.group === "ops").map((n) => (
              <li key={n.href}>
                <Link
                  href={n.href}
                  className="block rounded-md px-2 py-1.5 text-muted hover:bg-elevated hover:text-text"
                >
                  {n.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </nav>

      <div className="mt-auto rounded-md border border-border bg-elevated p-3 text-xs text-muted">
        <div className="text-[10px] uppercase tracking-wider text-faint">
          Build
        </div>
        <div className="mt-1 text-text">dashboard-skeleton</div>
        <div className="mt-1">design: M3ta DS v0.1</div>
      </div>
    </aside>
  );
}
