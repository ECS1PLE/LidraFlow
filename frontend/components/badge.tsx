import { consentTone, statusTone } from "@/lib/labels";

export function StatusBadge({ value, label }: { value: string; label: string }) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusTone(value)}`}>{label}</span>;
}

export function ConsentBadge({ value, label }: { value: string; label: string }) {
  return <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${consentTone(value)}`}>{label}</span>;
}
