import { FormField } from "@/components/ui/form-field";
import { IntegrationStatus } from "@/components/ui/integration-status";
import { SectionHeading } from "@/components/ui/section-heading";
import type { Integrations } from "@/lib/types";

export function MaxSection({ integrations }: { integrations: Integrations }) {
  return (
    <section className="grid gap-5 md:grid-cols-2">
      <SectionHeading title="MAX" status={<IntegrationStatus ok={integrations.max_configured} />} />
      <FormField label="MAX Bot Token">
        <input name="max_bot_token" type="password" className="form-input" placeholder={integrations.max_bot_token_masked || "token"} />
      </FormField>
      <FormField label="MAX Bot ID">
        <input name="max_bot_id" defaultValue={integrations.max_bot_id} className="form-input" />
      </FormField>
      <FormField label="MAX API Base URL" className="md:col-span-2">
        <input name="max_api_base_url" defaultValue={integrations.max_api_base_url || "https://platform-api2.max.ru"} className="form-input" />
      </FormField>
    </section>
  );
}
