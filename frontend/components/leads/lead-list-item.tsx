import Link from "next/link";
import { ConsentBadge, StatusBadge } from "@/components/badge";
import type { LabelMap, Lead } from "@/lib/types";
import { clip, formatDate } from "@/lib/utils";

type LeadListItemProps = {
  lead: Lead;
  statusLabels: LabelMap;
  consentLabels: LabelMap;
};

export function LeadListItem({ lead, statusLabels, consentLabels }: LeadListItemProps) {
  return (
    <Link href={`/leads/${lead.id}`} className="card block transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-semibold text-slate-950 dark:text-white">{lead.organization}</h2>
            <StatusBadge value={lead.status} label={statusLabels[lead.status] ?? lead.status} />
            <ConsentBadge value={lead.consent_status} label={consentLabels[lead.consent_status] ?? lead.consent_status} />
          </div>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            {[lead.niche, lead.region, lead.city, lead.district].filter(Boolean).join(" · ") || "Без географии"}
          </p>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{clip(lead.last_message || lead.notes, 150) || "Сообщений пока нет"}</p>
        </div>
        <div className="min-w-[240px] text-sm text-slate-500 dark:text-slate-400 lg:text-right">
          <p>{lead.phone || lead.whatsapp_phone || "телефон не указан"}</p>
          <p className="mt-1">Каналы: {(lead.available_channels ?? []).join(", ") || "—"}</p>
          <p className="mt-1">Обновлено: {formatDate(lead.updated_at)}</p>
        </div>
      </div>
    </Link>
  );
}
