import { saveIntegrationSettingsAction } from "@/lib/actions";
import type { Integrations } from "@/lib/types";
import { BroadcastRulesSection } from "./broadcast-rules-section";
import { IntegrationToggles } from "./integration-toggles";
import { MapsSection } from "./maps-section";
import { MaxSection } from "./max-section";
import { TelegramSection } from "./telegram-section";
import { VkSection } from "./vk-section";
import { WhatsappSection } from "./whatsapp-section";

export function IntegrationsForm({ integrations }: { integrations: Integrations }) {
  return (
    <form action={saveIntegrationSettingsAction} className="card grid gap-7">
      <div>
        <h2 className="text-lg font-semibold">Интеграции и ключи</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Секреты вставляются через веб-приложение и хранятся в SQLite. Пустое поле токена означает “оставить текущий”.
        </p>
      </div>

      <TelegramSection integrations={integrations} />
      <MapsSection integrations={integrations} />
      <WhatsappSection integrations={integrations} />
      <MaxSection integrations={integrations} />
      <VkSection integrations={integrations} />
      <BroadcastRulesSection integrations={integrations} />
      <IntegrationToggles integrations={integrations} />

      <div className="flex justify-end">
        <button className="btn-primary" type="submit">Сохранить интеграции</button>
      </div>
    </form>
  );
}
