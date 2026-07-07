import { FormField } from "@/components/ui/form-field";
import { IntegrationStatus } from "@/components/ui/integration-status";
import { SectionHeading } from "@/components/ui/section-heading";
import type { Integrations } from "@/lib/types";

export function VkSection({ integrations }: { integrations: Integrations }) {
  return (
    <section className="grid gap-5 md:grid-cols-2">
      <SectionHeading title="VK" status={<IntegrationStatus ok={integrations.vk_configured} />} />
      <FormField label="VK Community Token">
        <input name="vk_community_token" type="password" className="form-input" placeholder={integrations.vk_community_token_masked || "token"} />
      </FormField>
      <FormField label="VK Group ID">
        <input name="vk_group_id" defaultValue={integrations.vk_group_id} className="form-input" />
      </FormField>
      <FormField label="Confirmation code">
        <input name="vk_confirmation_code" defaultValue={integrations.vk_confirmation_code} className="form-input" />
      </FormField>
      <FormField label="Secret key">
        <input name="vk_secret_key" type="password" className="form-input" placeholder={integrations.vk_secret_key_masked || "secret"} />
      </FormField>
      <FormField label="VK API Base URL">
        <input name="vk_api_base_url" defaultValue={integrations.vk_api_base_url || "https://api.vk.com/method"} className="form-input" />
      </FormField>
      <FormField label="VK API Version">
        <input name="vk_api_version" defaultValue={integrations.vk_api_version || "5.199"} className="form-input" />
      </FormField>
    </section>
  );
}
