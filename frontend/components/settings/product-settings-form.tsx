import { FormField } from "@/components/ui/form-field";
import { saveSettingsAction } from "@/lib/actions";
import { WORKSPACE_FIELDS } from "./constants";

type ProductSettingsFormProps = {
  settings: Record<string, string>;
};

export function ProductSettingsForm({ settings }: ProductSettingsFormProps) {
  return (
    <form action={saveSettingsAction} className="grid gap-6">
      <section className="card grid gap-5 md:grid-cols-2">
        {WORKSPACE_FIELDS.map(([name, label, placeholder]) => (
          <FormField key={name} label={label}>
            <input name={name} defaultValue={settings[name] ?? ""} placeholder={placeholder} className="form-input" />
          </FormField>
        ))}
      </section>

      <section className="card space-y-5">
        <div>
          <h2 className="text-lg font-semibold">Шаблон AI-сообщения</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Доступные переменные: organization, contact_name, niche, region, city, district, phone, telegram_username, website, source_url, client_company_name, client_offer, client_site, manager_name, default_goal, extra_context.
          </p>
        </div>
        <textarea name="default_template" rows={7} defaultValue={settings.default_template ?? ""} className="form-input font-mono text-xs" />
      </section>

      <section className="card grid gap-5">
        <div>
          <h2 className="text-lg font-semibold">Ответы Telegram-бота</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Используются при /start, /stop и обычном входящем сообщении.</p>
        </div>
        <FormField label="/start">
          <textarea name="bot_welcome" rows={3} defaultValue={settings.bot_welcome ?? ""} className="form-input" />
        </FormField>
        <FormField label="Автоответ">
          <textarea name="bot_ack" rows={3} defaultValue={settings.bot_ack ?? ""} className="form-input" />
        </FormField>
        <FormField label="/stop">
          <textarea name="bot_stop" rows={3} defaultValue={settings.bot_stop ?? ""} className="form-input" />
        </FormField>
      </section>

      <div className="flex justify-end">
        <button className="btn-primary" type="submit">Сохранить настройки</button>
      </div>
    </form>
  );
}
