import { FormField } from "@/components/ui/form-field";
import { IntegrationStatus } from "@/components/ui/integration-status";
import { SectionHeading } from "@/components/ui/section-heading";
import type { Integrations } from "@/lib/types";

export function WhatsappSection({ integrations }: { integrations: Integrations }) {
  return (
    <section className="grid gap-5 md:grid-cols-2">
      <SectionHeading title="WhatsApp Cloud API" status={<IntegrationStatus ok={integrations.whatsapp_configured} />} />
      <FormField label="Access Token">
        <input name="whatsapp_access_token" type="password" className="form-input" placeholder={integrations.whatsapp_access_token_masked || "EAAG..."} />
      </FormField>
      <FormField label="Phone Number ID">
        <input name="whatsapp_phone_number_id" defaultValue={integrations.whatsapp_phone_number_id} className="form-input" />
      </FormField>
      <FormField label="Business Account ID">
        <input name="whatsapp_business_account_id" defaultValue={integrations.whatsapp_business_account_id} className="form-input" />
      </FormField>
      <FormField label="Verify Token для webhook">
        <input name="whatsapp_verify_token" defaultValue={integrations.whatsapp_verify_token} className="form-input" />
      </FormField>
      <FormField label="API Base URL">
        <input name="whatsapp_api_base_url" defaultValue={integrations.whatsapp_api_base_url || "https://graph.facebook.com"} className="form-input" />
      </FormField>
      <FormField label="API Version">
        <input name="whatsapp_api_version" defaultValue={integrations.whatsapp_api_version || "v23.0"} className="form-input" />
      </FormField>
      <FormField label="Default template">
        <input name="whatsapp_default_template" defaultValue={integrations.whatsapp_default_template} className="form-input" placeholder="approved_template_name" />
      </FormField>
      <FormField label="Default language">
        <input name="whatsapp_default_language" defaultValue={integrations.whatsapp_default_language || "ru"} className="form-input" />
      </FormField>
    </section>
  );
}
