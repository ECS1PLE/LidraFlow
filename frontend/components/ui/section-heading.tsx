import type { ReactNode } from "react";

type SectionHeadingProps = {
  title: string;
  subtitle?: string;
  status?: ReactNode;
  className?: string;
};

export function SectionHeading({ title, subtitle, status, className = "md:col-span-2" }: SectionHeadingProps) {
  return (
    <div className={className}>
      <h3 className="text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{title}</h3>
      {status ? <p className="mt-1 text-xs text-slate-400">Статус: {status}</p> : null}
      {subtitle ? <p className="mt-1 text-xs text-slate-400">{subtitle}</p> : null}
    </div>
  );
}
