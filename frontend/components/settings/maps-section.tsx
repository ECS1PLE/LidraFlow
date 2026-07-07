import { FormField } from "@/components/ui/form-field";
import { IntegrationStatus } from "@/components/ui/integration-status";
import { SectionHeading } from "@/components/ui/section-heading";
import type { Integrations } from "@/lib/types";

export function MapsSection({ integrations }: { integrations: Integrations }) {
  const mapsOk = integrations.maps_provider === "openstreetmap_overpass" || integrations.yandex_maps_configured || integrations.demo_mode;

  return (
    <section className="grid gap-5 md:grid-cols-2">
      <SectionHeading
        title="Карты"
        status={
          <>
            <IntegrationStatus ok={mapsOk} /> {integrations.maps_provider === "openstreetmap_overpass" ? "ключ не нужен" : ""}
          </>
        }
      />
      <FormField label="Yandex Maps API Key">
        <input name="yandex_maps_api_key" type="password" className="form-input" placeholder={integrations.yandex_maps_api_key_masked || "ключ поиска по организациям"} />
      </FormField>
      <FormField label="Провайдер карт">
        <select name="maps_provider" defaultValue={integrations.maps_provider || "openstreetmap_overpass"} className="form-input">
          <option value="openstreetmap_overpass">OpenStreetMap Overpass — бесплатно</option>
          <option value="yandex">Yandex Organization Search API</option>
          <option value="custom_yandex_contract">Custom Yandex contract endpoint</option>
        </select>
      </FormField>
      <FormField label="Yandex Maps endpoint" className="md:col-span-2">
        <input name="yandex_maps_endpoint" defaultValue={integrations.yandex_maps_endpoint} className="form-input" placeholder="https://search-maps.yandex.ru/v1/" />
      </FormField>
      <FormField
        label="OpenStreetMap Overpass endpoint"
        className="md:col-span-2"
        hint="Бесплатный источник организаций. Для больших объёмов лучше поднять свой Overpass/OSM dump."
      >
        <input name="osm_overpass_endpoint" defaultValue={integrations.osm_overpass_endpoint || "https://overpass-api.de/api/interpreter"} className="form-input" placeholder="https://overpass-api.de/api/interpreter" />
      </FormField>
      <FormField
        label="Nominatim endpoint для географии"
        className="md:col-span-2"
        hint="Используется для определения bbox по городу/району. Координаты + радиус работают без него."
      >
        <input name="osm_nominatim_endpoint" defaultValue={integrations.osm_nominatim_endpoint || "https://nominatim.openstreetmap.org/search"} className="form-input" placeholder="https://nominatim.openstreetmap.org/search" />
      </FormField>
    </section>
  );
}
