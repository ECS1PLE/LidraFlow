import { CheckboxField } from "@/components/ui/checkbox-field";
import type { Integrations } from "@/lib/types";

export function IntegrationToggles({ integrations }: { integrations: Integrations }) {
  return (
    <div className="grid gap-3 rounded-3xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950/60">
      <CheckboxField
        name="enable_bot_polling"
        defaultChecked={integrations.enable_bot_polling}
        title="Включить Telegram polling."
        description="Бот будет принимать входящие сообщения."
      />
      <CheckboxField
        name="demo_mode"
        defaultChecked={integrations.demo_mode}
        title="Demo mode."
        description="Тестирует интерфейс без реальной отправки и без ключа карт."
      />
      <CheckboxField
        name="allow_manual_first_contact"
        defaultChecked={integrations.allow_manual_first_contact}
        title="Разрешить ручное первое касание."
        description="Используйте, когда у вас есть основание для контакта и настроен официальный канал."
      />
    </div>
  );
}
