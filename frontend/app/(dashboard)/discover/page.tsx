export const dynamic = "force-dynamic";

import Link from "next/link";
import { BackendError } from "@/components/backend-error";
import { DiscoverForm } from "@/components/discover/discover-form";
import { DiscoverSidebar } from "@/components/discover/discover-sidebar";
import { PageHeader } from "@/components/ui/page-header";
import { Toast } from "@/components/toast";
import { getIntegrations, getMeta } from "@/lib/api";

export default async function DiscoverPage({ searchParams }: { searchParams: { msg?: string; level?: string } }) {
  try {
    const [meta, { integrations }] = await Promise.all([getMeta(), getIntegrations()]);

    return (
      <div className="mx-auto max-w-6xl">
        <Toast message={searchParams.msg} level={searchParams.level} />
        <PageHeader
          eyebrow="Maps discovery"
          title="Автосбор лидов из карт"
          description="Ищи организации по нише, региону, городу и району. По умолчанию используется бесплатный OpenStreetMap Overpass. Найденные карточки попадают в CRM с адресом, источником и доступными каналами связи."
          actions={<Link href="/settings" className="btn-secondary">Настроить ключи</Link>}
        />

        <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <DiscoverForm integrations={integrations} />
          <DiscoverSidebar stats={meta.stats} integrations={integrations} />
        </div>
      </div>
    );
  } catch (error) {
    return <BackendError error={error} />;
  }
}
