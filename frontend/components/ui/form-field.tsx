import type { ReactNode } from "react";

type FormFieldProps = {
  label: string;
  name?: string;
  className?: string;
  hint?: ReactNode;
  children?: ReactNode;
};

export function FormField({ label, name, className = "", hint, children }: FormFieldProps) {
  return (
    <label className={className}>
      <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">{label}</span>
      {children ?? (name ? <input name={name} className="form-input" /> : null)}
      {hint ? <span className="mt-1 block text-xs text-slate-400">{hint}</span> : null}
    </label>
  );
}
