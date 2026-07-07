import { directionLabels } from "@/lib/labels";
import type { LabelMap, Message } from "@/lib/types";
import { formatDate } from "@/lib/utils";

type MessageThreadProps = {
  messages: Message[];
  channelLabels: LabelMap;
};

export function MessageThread({ messages, channelLabels }: MessageThreadProps) {
  return (
    <section className="card">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Диалог</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Входящие и исходящие из Telegram, WhatsApp, MAX, VK, черновики и заметки.</p>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">{messages.length}</span>
      </div>

      <div className="max-h-[520px] space-y-3 overflow-auto pr-1">
        {messages.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500 dark:border-slate-800 dark:text-slate-400">Сообщений пока нет.</div>
        ) : (
          messages.map((message) => {
            const align = message.direction === "out" ? "ml-auto" : "";
            const tone =
              message.direction === "draft"
                ? "border-amber-200 bg-amber-50 dark:border-amber-900/60 dark:bg-amber-950/30"
                : message.direction === "out"
                  ? "border-slate-900 bg-slate-950 text-white dark:border-slate-100 dark:bg-white dark:text-slate-950"
                  : "border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-950";
            return (
              <article key={message.id} className={`max-w-[92%] rounded-3xl border p-4 ${align} ${tone}`}>
                <div className="mb-2 flex flex-wrap items-center gap-2 text-xs opacity-70">
                  <span className="font-semibold">{directionLabels[message.direction] ?? message.direction}</span>
                  <span>·</span>
                  <span>{channelLabels[message.channel] ?? message.channel}</span>
                  <span>·</span>
                  <span>{formatDate(message.created_at)}</span>
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6">{message.body}</p>
              </article>
            );
          })
        )}
      </div>
    </section>
  );
}
