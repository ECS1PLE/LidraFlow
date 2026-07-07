"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { runDiscovery } from "../api";
import { field, messagePath } from "../utils";
import { checked, numberField, optionalNumber } from "./helpers";

export async function discoverLeadsAction(formData: FormData) {
  let message = "Поиск завершён";
  let level: "ok" | "warn" = "ok";
  try {
    const data = await runDiscovery({
      provider: field(formData, "provider") || "openstreetmap_overpass",
      query: field(formData, "query"),
      region: field(formData, "region"),
      city: field(formData, "city"),
      district: field(formData, "district"),
      latitude: optionalNumber(formData, "latitude"),
      longitude: optionalNumber(formData, "longitude"),
      radius_m: numberField(formData, "radius_m", 5000),
      limit: numberField(formData, "limit", 20),
      require_no_site: checked(formData, "require_no_site"),
      require_contact: checked(formData, "require_contact"),
      import_results: checked(formData, "import_results")
    });
    revalidatePath("/leads");
    revalidatePath("/discover");
    const warningText = data.warnings.length ? ` Предупреждения: ${data.warnings.join(" ")}` : "";
    message = `Найдено: ${data.found}; новых: ${data.imported}; обновлено дублей: ${data.merged}; пропущено фильтрами: ${data.skipped}.${warningText}`;
    level = data.found > 0 ? "ok" : "warn";
  } catch (error) {
    message = error instanceof Error ? error.message : "Поиск по картам не выполнен";
    level = "warn";
  }
  redirect(messagePath("/discover", message, level));
}
