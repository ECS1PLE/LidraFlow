import { CheckboxField } from "@/components/ui/checkbox-field";
import { FormField } from "@/components/ui/form-field";
import { discoverLeadsAction } from "@/lib/actions";
import type { Integrations } from "@/lib/types";

export function DiscoverForm({ integrations }: { integrations: Integrations }) {
  return (
    <form action={discoverLeadsAction} className="card grid gap-5">
      <div className="grid gap-5 md:grid-cols-2">
        <FormField label="Что искать *" className="md:col-span-2">
          <input name="query" required className="form-input" placeholder="Например: салоны красоты, стоматологии, кофейни" />
        </FormField>
        <FormField label="Регион">
          <input name="region" className="form-input" placeholder="Московская область" />
        </FormField>
        <FormField label="Город">
          <input name="city" className="form-input" placeholder="Москва" />
        </FormField>
        <FormField label="Район / округ">
          <input name="district" className="form-input" placeholder="Тверской район" />
        </FormField>
        <FormField label="Лимит">
          <input name="limit" type="number" min="1" max="50" defaultValue="20" className="form-input" />
        </FormField>
        <FormField label="Широта, опционально">
          <input name="latitude" className="form-input" placeholder="55.751244" />
        </FormField>
        <FormField label="Долгота, опционально">
          <input name="longitude" className="form-input" placeholder="37.618423" />
        </FormField>
        <FormField label="Радиус, метров">
          <input name="radius_m" type="number" min="250" max="50000" defaultValue="5000" className="form-input" />
        </FormField>
        <FormField label="Провайдер">
          <select name="provider" defaultValue={integrations.maps_provider || "openstreetmap_overpass"} className="form-input">
            <option value="openstreetmap_overpass">OpenStreetMap Overpass — бесплатно</option>
            <option value="yandex">Yandex Organization Search API</option>
            <option value="custom_yandex_contract">Custom Yandex contract</option>
          </select>
        </FormField>
      </div>

      <div className="grid gap-3 rounded-3xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950/60">
        <CheckboxField
          name="require_no_site"
          defaultChecked
          title="Только без сайта."
          description="Полезно, если оффер связан с сайтами, ботами, лидогенерацией или онлайн-записью."
        />
        <CheckboxField
          name="require_contact"
          defaultChecked
          title="Только с контактом."
          description="Оставляет карточки, где найден телефон, Telegram, VK или другой распознанный канал."
        />
        <CheckboxField
          name="import_results"
          defaultChecked
          title="Сразу импортировать."
          description="Новые организации попадут в CRM, дубли будут дополнены пустыми полями."
        />
      </div>

      <button className="btn-primary" type="submit">Найти и импортировать</button>
    </form>
  );
}
