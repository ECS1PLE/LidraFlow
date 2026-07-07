import Link from "next/link";
import { ConsentBadge, StatusBadge } from "@/components/badge";
import { deleteLeadAction } from "@/lib/actions";
import type { LabelMap, Lead } from "@/lib/types";

type LeadHeaderProps = {
  lead: Lead;
  statusLabels: LabelMap;
  consentLabels: LabelMap;
  channelLabels: LabelMap;
};

export function LeadHeader({ lead, statusLabels, consentLabels, channelLabels }: LeadHeaderProps) {
  const channels = lead.available_channels ?? [];
  const deleteLead = deleteLeadAction.bind(null, lead.id);

  return (
    <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <Link href="/leads" className="text-sm font-medium text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">← К лидам</Link>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 dark:text-white">{lead.organization}</h1>
        <div className="mt-3 flex flex-wrap gap-2">
          <StatusBadge value={lead.status} label={statusLabels[lead.status] ?? lead.status} />
          <ConsentBadge value={lead.consent_status} label={consentLabels[lead.consent_status] ?? lead.consent_status} />
          {channels.map((channel) => (
            <span key={channel} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {channelLabels[channel] ?? channel}
            </span>
          ))}
        </div>
      </div>
      <form action={deleteLead}>
        <button className="btn-danger" type="submit">Удалить лид</button>
      </form>
    </div>
  );
}
