import { HTMLAttributes, ReactNode } from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  title?: ReactNode;
  subtitle?: ReactNode;
  right?: ReactNode;
  glow?: boolean;
};

export function Card({
  title,
  subtitle,
  right,
  glow,
  className = "",
  children,
  ...rest
}: CardProps) {
  return (
    <section
      className={`rounded-xl border border-border bg-surface ${
        glow ? "shadow-glow" : ""
      } ${className}`}
      {...rest}
    >
      {(title || right) && (
        <header className="flex items-start justify-between gap-4 border-b border-border px-4 py-3">
          <div className="min-w-0">
            {title ? (
              <h2 className="truncate text-sm font-semibold tracking-wide text-text">
                {title}
              </h2>
            ) : null}
            {subtitle ? (
              <p className="mt-0.5 text-xs text-muted">{subtitle}</p>
            ) : null}
          </div>
          {right ? <div className="shrink-0">{right}</div> : null}
        </header>
      )}
      <div className="p-4">{children}</div>
    </section>
  );
}
