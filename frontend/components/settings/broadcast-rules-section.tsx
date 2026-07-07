import { FormField } from "@/components/ui/form-field";
import { SectionHeading } from "@/components/ui/section-heading";
import type { Integrations } from "@/lib/types";

export function BroadcastRulesSection({ integrations }: { integrations: Integrations }) {
  return (
    <section className="grid gap-5 md:grid-cols-2">
      <SectionHeading title="Правила рассылки" />
      <FormField label="Порядок автовыбора каналов">
        <input name="broadcast_default_channel_order" defaultValue={integrations.broadcast_default_channel_order || "whatsapp,telegram,max,vk"} className="form-input" />
      </FormField>
      <FormField label="Пауза между отправками, мс">
        <input name="broadcast_rate_limit_ms" type="number" min="0" defaultValue={integrations.broadcast_rate_limit_ms || 800} className="form-input" />
      </FormField>
    </section>
  );
}
