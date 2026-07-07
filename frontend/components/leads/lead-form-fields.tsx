import { FormField } from "@/components/ui/form-field";
import type { Lead } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { ChannelSelect } from "./channel-select";

type LeadFormFieldsProps = {
  lead?: Lead;
  mode: "create" | "edit";
};

export function LeadFormFields({ lead, mode }: LeadFormFieldsProps) {
  const isEdit = mode === "edit";

  return (
    <>
      <FormField label="Организация *" className="md:col-span-2">
        <input name="organization" defaultValue={lead?.organization} required className="form-input" placeholder={isEdit ? undefined : "Например, Клиника Север"} />
      </FormField>
      <FormField label="Контакт">
        <input name="contact_name" defaultValue={lead?.contact_name} className="form-input" placeholder={isEdit ? undefined : "Имя, если известно"} />
      </FormField>
      <FormField label="Ниша">
        <input name="niche" defaultValue={lead?.niche} className="form-input" placeholder={isEdit ? undefined : "Кафе, клиника, салон"} />
      </FormField>
      <FormField label="Регион">
        <input name="region" defaultValue={lead?.region} className="form-input" placeholder={isEdit ? undefined : "Московская область"} />
      </FormField>
      <FormField label="Город">
        <input name="city" defaultValue={lead?.city} className="form-input" placeholder={isEdit ? undefined : "Москва"} />
      </FormField>
      <FormField label="Район">
        <input name="district" defaultValue={lead?.district} className="form-input" placeholder={isEdit ? undefined : "Тверской"} />
      </FormField>
      <FormField label="Адрес">
        <input name="address" defaultValue={lead?.address} className="form-input" placeholder={isEdit ? undefined : "ул. Примерная, 1"} />
      </FormField>
      {isEdit ? (
        <>
          <FormField label="Широта">
            <input name="latitude" defaultValue={lead?.latitude ?? ""} className="form-input" />
          </FormField>
          <FormField label="Долгота">
            <input name="longitude" defaultValue={lead?.longitude ?? ""} className="form-input" />
          </FormField>
        </>
      ) : null}
      <FormField label="Телефон">
        <input name="phone" defaultValue={lead?.phone} className="form-input" placeholder={isEdit ? undefined : "+79990000000"} />
      </FormField>
      <FormField label="WhatsApp phone">
        <input name="whatsapp_phone" defaultValue={lead?.whatsapp_phone} className="form-input" placeholder={isEdit ? undefined : "79990000000"} />
      </FormField>
      <FormField label="Telegram username">
        <input name="telegram_username" defaultValue={lead?.telegram_username} className="form-input" placeholder={isEdit ? undefined : "company_tg без @"} />
      </FormField>
      <FormField label="Telegram chat_id">
        <input name="telegram_chat_id" defaultValue={lead?.telegram_chat_id} className="form-input" placeholder={isEdit ? undefined : "обычно появляется после /start"} />
      </FormField>
      <FormField label="MAX user_id">
        <input name="max_user_id" defaultValue={lead?.max_user_id} className="form-input" />
      </FormField>
      <FormField label="MAX chat_id">
        <input name="max_chat_id" defaultValue={lead?.max_chat_id} className="form-input" />
      </FormField>
      <FormField label="VK user_id">
        <input name="vk_user_id" defaultValue={lead?.vk_user_id} className="form-input" />
      </FormField>
      <FormField label="VK peer_id">
        <input name="vk_peer_id" defaultValue={lead?.vk_peer_id} className="form-input" />
      </FormField>
      <FormField label="Предпочтительный канал">
        <ChannelSelect name="preferred_channel" defaultValue={lead?.preferred_channel || "auto"} />
      </FormField>
      <FormField label="Сайт">
        <input name="website" defaultValue={lead?.website} className="form-input" placeholder={isEdit ? undefined : "https://example.com или пусто"} />
      </FormField>
      <FormField label="Источник" className="md:col-span-2">
        <input name="source_url" defaultValue={lead?.source_url} className="form-input" placeholder={isEdit ? undefined : "Ссылка на карточку, сайт или внутренний источник"} />
      </FormField>
      {isEdit && lead ? (
        <div className="md:col-span-2 rounded-3xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500 dark:border-slate-800 dark:bg-slate-950/50 dark:text-slate-400">
          <p><b>Карты:</b> {lead.maps_provider || "—"}</p>
          <p className="mt-1"><b>ID источника:</b> {lead.maps_external_id || "—"}</p>
          <p className="mt-1"><b>Найдено:</b> {lead.discovered_at ? formatDate(lead.discovered_at) : "—"}</p>
        </div>
      ) : null}
      <FormField label="Заметки" className="md:col-span-2">
        <textarea name="notes" defaultValue={lead?.notes} rows={4} className="form-input" placeholder={isEdit ? undefined : "Почему лид подходит, какие есть детали"} />
      </FormField>
    </>
  );
}
