import { importLeadsAction } from "@/lib/actions";

type LeadsFilterPanelProps = {
  searchParams: {
    q?: string;
    region_filter?: string;
    city_filter?: string;
    district_filter?: string;
    niche_filter?: string;
    channel_filter?: string;
  };
};

export function LeadsFilterPanel({ searchParams }: LeadsFilterPanelProps) {
  return (
    <section className="mb-6 grid gap-4 rounded-3xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
      <form className="grid gap-3 md:grid-cols-4 lg:grid-cols-8">
        <input name="q" defaultValue={searchParams.q ?? ""} className="form-input md:col-span-2" placeholder="Поиск по названию, телефону, адресу" />
        <input name="region_filter" defaultValue={searchParams.region_filter ?? ""} className="form-input" placeholder="Регион" />
        <input name="city_filter" defaultValue={searchParams.city_filter ?? ""} className="form-input" placeholder="Город" />
        <input name="district_filter" defaultValue={searchParams.district_filter ?? ""} className="form-input" placeholder="Район" />
        <input name="niche_filter" defaultValue={searchParams.niche_filter ?? ""} className="form-input" placeholder="Ниша" />
        <select name="channel_filter" defaultValue={searchParams.channel_filter ?? ""} className="form-input">
          <option value="">Любой канал</option>
          <option value="telegram">Telegram</option>
          <option value="whatsapp">WhatsApp</option>
          <option value="max">MAX</option>
          <option value="vk">VK</option>
        </select>
        <button className="btn-primary" type="submit">Фильтр</button>
      </form>
      <div className="flex flex-col gap-3 border-t border-slate-100 pt-4 dark:border-slate-800 md:flex-row md:items-center md:justify-between">
        <form action={importLeadsAction} className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input name="file" type="file" accept=".csv,text/csv" className="text-sm" />
          <button className="btn-secondary !py-2" type="submit">Импорт CSV</button>
        </form>
        <a href="/sample_leads.csv" className="text-sm font-medium text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white">Скачать CSV-шаблон</a>
      </div>
    </section>
  );
}
