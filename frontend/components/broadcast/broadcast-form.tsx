import { FormField } from "@/components/ui/form-field";
import { broadcastAction } from "@/lib/actions";
import type { LabelMap } from "@/lib/types";

type BroadcastFormProps = {
  channelLabels: LabelMap;
  statusLabels: LabelMap;
};

export function BroadcastForm({ channelLabels, statusLabels }: BroadcastFormProps) {
  return (
    <form action={broadcastAction} className="card grid gap-5">
      <div className="grid gap-5 md:grid-cols-2">
        <FormField label="Название кампании">
          <input name="name" className="form-input" placeholder="Москва · салоны · WhatsApp" />
        </FormField>
        <FormField label="Канал">
          <select name="channel" defaultValue="auto" className="form-input">
            {Object.entries(channelLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </FormField>
      </div>

      <FormField label="Текст сообщения *">
        <textarea name="body" required rows={7} className="form-input" placeholder="Короткое сообщение для получателей" />
      </FormField>

      <div className="grid gap-5 md:grid-cols-4">
        <FormField label="Регион">
          <input name="region_filter" className="form-input" placeholder="Московская область" />
        </FormField>
        <FormField label="Город">
          <input name="city_filter" className="form-input" placeholder="Москва" />
        </FormField>
        <FormField label="Район">
          <input name="district_filter" className="form-input" placeholder="Тверской" />
        </FormField>
        <FormField label="Ниша">
          <input name="niche_filter" className="form-input" placeholder="кофейня" />
        </FormField>
      </div>

      <div className="grid gap-5 md:grid-cols-4">
        <FormField label="Согласие">
          <select name="consent_filter" defaultValue="opted_in" className="form-input">
            <option value="opted_in">Только opt-in</option>
            <option value="pending">Pending</option>
            <option value="">Любой, кроме отказов</option>
          </select>
        </FormField>
        <FormField label="Статус">
          <select name="status_filter" defaultValue="" className="form-input">
            <option value="">Любой</option>
            {Object.entries(statusLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </FormField>
        <FormField label="Максимум">
          <input name="max_recipients" type="number" min="1" max="500" defaultValue="50" className="form-input" />
        </FormField>
        <FormField label="WhatsApp language">
          <input name="whatsapp_language" defaultValue="ru" className="form-input" />
        </FormField>
      </div>

      <FormField
        label="WhatsApp template, если нужен"
        hint="Если указать шаблон, WhatsApp отправит template-сообщение вместо свободного текста."
      >
        <input name="whatsapp_template_name" className="form-input" placeholder="approved_template_name" />
      </FormField>

      <label className="flex items-start gap-3 rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700 dark:border-slate-800 dark:bg-slate-950/60 dark:text-slate-300">
        <input name="dry_run" type="checkbox" defaultChecked className="mt-1" />
        <span><b>Сначала только проверить.</b> Покажет количество подходящих получателей и разбивку по каналам без отправки.</span>
      </label>

      <button className="btn-primary" type="submit">Запустить кампанию</button>
    </form>
  );
}
