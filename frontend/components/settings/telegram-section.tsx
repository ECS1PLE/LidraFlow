import { FormField } from "@/components/ui/form-field";
import { IntegrationStatus } from "@/components/ui/integration-status";
import { SectionHeading } from "@/components/ui/section-heading";
import type { Integrations } from "@/lib/types";

export function TelegramSection({ integrations }: { integrations: Integrations }) {
  return (
    <section className="grid gap-5 md:grid-cols-2">
      <SectionHeading title="Telegram" status={<IntegrationStatus ok={integrations.telegram_bot_configured} />} />
      <FormField label="Telegram Bot Token">
        <input name="telegram_bot_token" type="password" className="form-input" placeholder={integrations.telegram_bot_token_masked || "123456:ABC..."} />
      </FormField>
      <FormField label="Telegram Bot ID">
        <input name="telegram_bot_id" defaultValue={integrations.telegram_bot_id} className="form-input" placeholder="ID бота" />
      </FormField>
    </section>
  );
}
