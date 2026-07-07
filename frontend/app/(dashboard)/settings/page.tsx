export const dynamic = "force-dynamic";

import { BackendError } from "@/components/backend-error";
import { IntegrationsForm } from "@/components/settings/integrations-form";
import { ProductSettingsForm } from "@/components/settings/product-settings-form";
import { PageHeader } from "@/components/ui/page-header";
import { Toast } from "@/components/toast";
import { getIntegrations, getSettings } from "@/lib/api";

export default async function SettingsPage({ searchParams }: { searchParams: { msg?: string; level?: string } }) {
  try {
    const [{ settings }, { integrations }] = await Promise.all([getSettings(), getIntegrations()]);

    return (
      <div className="mx-auto max-w-6xl">
        <Toast message={searchParams.msg} level={searchParams.level} />
        <PageHeader
          eyebrow="Workspace"
          title="Настройки продукта"
          description="Здесь задаются токены каналов, карты, порядок автовыбора, лимит рассылки и шаблоны сообщений."
        />
        <div className="grid gap-6">
          <IntegrationsForm integrations={integrations} />
          <ProductSettingsForm settings={settings} />
        </div>
      </div>
    );
  } catch (error) {
    return <BackendError error={error} />;
  }
}
