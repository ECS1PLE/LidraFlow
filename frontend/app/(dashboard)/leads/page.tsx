export const dynamic = "force-dynamic";

import Link from "next/link";
import { BackendError } from "@/components/backend-error";
import { LeadListItem } from "@/components/leads/lead-list-item";
import { LeadsFilterPanel } from "@/components/leads/leads-filter-panel";
import { StatCard } from "@/components/stat-card";
import { PageHeader } from "@/components/ui/page-header";
import { Toast } from "@/components/toast";
import { getLeads, getMeta } from "@/lib/api";

type SearchParams = {
  q?: string;
  status_filter?: string;
  consent_filter?: string;
  city_filter?: string;
  region_filter?: string;
  district_filter?: string;
  niche_filter?: string;
  channel_filter?: string;
  msg?: string;
  level?: string;
};

export default async function LeadsPage({ searchParams }: { searchParams: SearchParams }) {
  try {
    const [meta, data] = await Promise.all([
      getMeta(),
      getLeads({
        q: searchParams.q,
        status_filter: searchParams.status_filter,
        consent_filter: searchParams.consent_filter,
        city_filter: searchParams.city_filter,
        region_filter: searchParams.region_filter,
        district_filter: searchParams.district_filter,
        niche_filter: searchParams.niche_filter,
        channel_filter: searchParams.channel_filter
      })
    ]);

    return (
      <div>
        <Toast message={searchParams.msg} level={searchParams.level} />
        <PageHeader
          eyebrow="Leads"
          title="База лидов"
          description="Организации из карт, входящих сообщений и CSV. Фильтруй по географии, нише и доступному каналу."
          actions={
            <div className="flex flex-wrap gap-3">
              <Link href="/discover" className="btn-secondary">Автопоиск</Link>
              <Link href="/leads/new" className="btn-primary">Новый лид</Link>
            </div>
          }
        />

        <div className="mb-6 grid gap-4 md:grid-cols-4">
          <StatCard label="Всего" value={meta.stats.total} hint="в CRM" />
          <StatCard label="Из карт" value={meta.stats.discovered} hint="автосбор" />
          <StatCard label="Opt-in" value={meta.stats.opted_in} hint="можно отвечать" />
          <StatCard label="Каналы" value={`TG ${meta.stats.telegram} · WA ${meta.stats.whatsapp}`} hint="готовы к отправке" />
        </div>

        <LeadsFilterPanel searchParams={searchParams} />

        <div className="grid gap-4">
          {data.items.length === 0 ? (
            <div className="card text-center text-sm text-slate-500 dark:text-slate-400">Лидов по этим фильтрам нет.</div>
          ) : (
            data.items.map((lead) => (
              <LeadListItem
                key={lead.id}
                lead={lead}
                statusLabels={data.status_labels}
                consentLabels={data.consent_labels}
              />
            ))
          )}
        </div>
      </div>
    );
  } catch (error) {
    return <BackendError error={error} />;
  }
}
