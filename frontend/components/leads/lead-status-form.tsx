import { updateStatusAction } from "@/lib/actions";
import type { LabelMap, Lead } from "@/lib/types";

type LeadStatusFormProps = {
  lead: Lead;
  statusLabels: LabelMap;
  consentLabels: LabelMap;
};

export function LeadStatusForm({ lead, statusLabels, consentLabels }: LeadStatusFormProps) {
  const updateStatus = updateStatusAction.bind(null, lead.id);

  return (
    <form action={updateStatus} className="card grid gap-4 md:grid-cols-[1fr_1fr_auto] md:items-end">
      <label>
        <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Статус</span>
        <select name="status" defaultValue={lead.status} className="form-input">
          {Object.entries(statusLabels).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </label>
      <label>
        <span className="mb-2 block text-sm font-medium text-slate-700 dark:text-slate-300">Согласие</span>
        <select name="consent_status" defaultValue={lead.consent_status} className="form-input">
          {Object.entries(consentLabels).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </label>
      <button className="btn-secondary" type="submit">Обновить</button>
    </form>
  );
}
