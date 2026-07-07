import { sendMessageAction } from "@/lib/actions";
import type { Lead } from "@/lib/types";
import { ChannelSelect } from "./channel-select";

type SendMessageFormProps = {
  lead: Lead;
  lastDraft: string;
};

export function SendMessageForm({ lead, lastDraft }: SendMessageFormProps) {
  const sendMessage = sendMessageAction.bind(null, lead.id);

  return (
    <form action={sendMessage} className="card space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Отправить сообщение</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Выбери канал или оставь автовыбор. Для WhatsApp можно указать approved template.</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <ChannelSelect name="channel" defaultValue={lead.preferred_channel || "auto"} />
        <input name="whatsapp_template_name" className="form-input" placeholder="WA template" />
        <input name="whatsapp_language" defaultValue="ru" className="form-input" />
      </div>
      <textarea name="body" rows={6} defaultValue={lastDraft} className="form-input" placeholder="Текст сообщения" />
      <button className="btn-primary" type="submit">Отправить</button>
    </form>
  );
}
