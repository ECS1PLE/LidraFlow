export const dynamic = "force-dynamic";

import Link from "next/link";
import { BackendError } from "@/components/backend-error";
import { BroadcastForm } from "@/components/broadcast/broadcast-form";
import { CampaignHistory } from "@/components/broadcast/campaign-history";
import { ChannelStatsPanel } from "@/components/broadcast/channel-stats-panel";
import { PageHeader } from "@/components/ui/page-header";
import { Toast } from "@/components/toast";
import { getCampaigns, getLeads, getMeta } from "@/lib/api";

export default async function BroadcastPage({ searchParams }: { searchParams: { msg?: string; level?: string } }) {
  try {
    const [meta, leads, campaigns] = await Promise.all([getMeta(), getLeads({}), getCampaigns()]);
    const channelLabels = meta.channel_labels ?? { auto: "Автовыбор", telegram: "Telegram", whatsapp: "WhatsApp", max: "MAX", vk: "VK" };

    return (
      <div className="mx-auto max-w-6xl">
        <Toast message={searchParams.msg} level={searchParams.level} />
        <PageHeader
          eyebrow="Campaigns"
          title="Рассылка по географии и каналам"
          description="Запускай кампании по региону, городу, району, нише, статусу и каналу связи. Dry-run показывает охват без отправки."
          actions={<Link href="/leads" className="btn-secondary">База лидов</Link>}
        />

        <div className="grid gap-6 xl:grid-cols-[1fr_0.75fr]">
          <BroadcastForm channelLabels={channelLabels} statusLabels={meta.status_labels} />
          <section className="space-y-6">
            <ChannelStatsPanel stats={leads.stats} />
            <CampaignHistory campaigns={campaigns.items} channelLabels={channelLabels} />
          </section>
        </div>
      </div>
    );
  } catch (error) {
    return <BackendError error={error} />;
  }
}
