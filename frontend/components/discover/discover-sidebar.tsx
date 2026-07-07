import { StatTile } from "@/components/ui/stat-tile";
import type { Integrations, Stats } from "@/lib/types";

type DiscoverSidebarProps = {
  stats: Stats;
  integrations: Integrations;
};

export function DiscoverSidebar({ stats, integrations }: DiscoverSidebarProps) {
  return (
    <section className="space-y-6">
      <div className="card space-y-4">
        <h2 className="text-lg font-semibold">Как работает география</h2>
        <p className="text-sm leading-6 text-slate-500 dark:text-slate-400">
          Для OpenStreetMap backend сначала определяет bbox через Nominatim по району/городу/региону, затем берёт организации через Overpass. Если заданы координаты, используется поиск в радиусе вокруг точки.
        </p>
        <div className="grid gap-3 sm:grid-cols-3">
          <StatTile label="Найдено из карт" value={stats.discovered} />
          <StatTile label="WhatsApp-ready" value={stats.whatsapp} />
          <StatTile label="Telegram-ready" value={stats.telegram} />
        </div>
      </div>

      <div className="card space-y-4">
        <h2 className="text-lg font-semibold">Статус интеграций</h2>
        <div className="grid gap-3 text-sm text-slate-600 dark:text-slate-300">
          <p><b>Карты:</b> {integrations.maps_provider === "openstreetmap_overpass" ? "OpenStreetMap, ключ не нужен" : (integrations.yandex_maps_configured || integrations.demo_mode ? "готово" : "нужен ключ")}</p>
          <p><b>Demo mode:</b> {integrations.demo_mode ? "включён" : "выключен"}</p>
          <p><b>WhatsApp:</b> {integrations.whatsapp_configured ? "подключён" : "не настроен"}</p>
          <p><b>MAX:</b> {integrations.max_configured ? "подключён" : "не настроен"}</p>
          <p><b>VK:</b> {integrations.vk_configured ? "подключён" : "не настроен"}</p>
        </div>
      </div>
    </section>
  );
}
