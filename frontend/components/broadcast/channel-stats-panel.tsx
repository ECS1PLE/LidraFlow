import type { Stats } from "@/lib/types";

export function ChannelStatsPanel({ stats }: { stats: Stats }) {
  return (
    <div className="card space-y-4">
      <h2 className="text-lg font-semibold">Доступные каналы в базе</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        {[
          ["Telegram", stats.telegram],
          ["WhatsApp", stats.whatsapp],
          ["MAX", stats.max],
          ["VK", stats.vk]
        ].map(([label, count]) => (
          <div key={label} className="rounded-3xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950/50">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{label}</p>
            <p className="mt-2 text-3xl font-semibold">{count}</p>
          </div>
        ))}
      </div>
      <p className="text-sm leading-6 text-slate-500 dark:text-slate-400">
        Если у лида несколько каналов, режим “Автовыбор” использует порядок из настроек: WhatsApp, Telegram, MAX, VK.
      </p>
    </div>
  );
}
