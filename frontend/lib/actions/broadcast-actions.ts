"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { runBroadcast } from "../api";
import { field, messagePath } from "../utils";
import { checked, numberField } from "./helpers";

export async function broadcastAction(formData: FormData) {
  let message = "Рассылка обработана";
  let level: "ok" | "warn" = "ok";
  try {
    const data = await runBroadcast({
      name: field(formData, "name"),
      body: field(formData, "body"),
      channel: field(formData, "channel") || "auto",
      status_filter: field(formData, "status_filter"),
      consent_filter: field(formData, "consent_filter") || "opted_in",
      region_filter: field(formData, "region_filter"),
      city_filter: field(formData, "city_filter"),
      district_filter: field(formData, "district_filter"),
      niche_filter: field(formData, "niche_filter"),
      max_recipients: numberField(formData, "max_recipients", 50),
      dry_run: checked(formData, "dry_run"),
      whatsapp_template_name: field(formData, "whatsapp_template_name"),
      whatsapp_language: field(formData, "whatsapp_language")
    });
    revalidatePath("/leads");
    revalidatePath("/broadcast");
    const breakdown = data.channel_breakdown
      ? Object.entries(data.channel_breakdown).map(([channel, count]) => `${channel}: ${count}`).join(", ")
      : "";
    message = data.dry_run
      ? `Проверка: подходящих получателей: ${data.eligible}; пропущено: ${data.skipped_count ?? 0}${breakdown ? `; каналы: ${breakdown}` : ""}`
      : `Отправлено: ${data.sent}; ошибок: ${data.failed}; подходящих: ${data.eligible}`;
    level = data.failed > 0 || data.eligible === 0 ? "warn" : "ok";
  } catch (error) {
    message = error instanceof Error ? error.message : "Рассылка не выполнена";
    level = "warn";
  }
  redirect(messagePath("/broadcast", message, level));
}
