"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { apiFetch } from "../api";
import { field, messagePath } from "../utils";
import { checked, numberField } from "./helpers";

export async function saveSettingsAction(formData: FormData) {
  const payload = {
    workspace_name: field(formData, "workspace_name"),
    client_company_name: field(formData, "client_company_name"),
    client_offer: field(formData, "client_offer"),
    client_site: field(formData, "client_site"),
    manager_name: field(formData, "manager_name"),
    default_goal: field(formData, "default_goal"),
    default_template: field(formData, "default_template"),
    bot_welcome: field(formData, "bot_welcome"),
    bot_ack: field(formData, "bot_ack"),
    bot_stop: field(formData, "bot_stop")
  };
  await apiFetch("/api/settings", { method: "PUT", body: JSON.stringify(payload) });
  revalidatePath("/settings");
  redirect(messagePath("/settings", "Настройки сохранены"));
}

export async function saveIntegrationSettingsAction(formData: FormData) {
  const payload = {
    telegram_bot_token: field(formData, "telegram_bot_token"),
    telegram_bot_id: field(formData, "telegram_bot_id"),
    enable_bot_polling: checked(formData, "enable_bot_polling"),
    demo_mode: checked(formData, "demo_mode"),
    allow_manual_first_contact: checked(formData, "allow_manual_first_contact"),
    maps_provider: field(formData, "maps_provider") || "openstreetmap_overpass",
    yandex_maps_api_key: field(formData, "yandex_maps_api_key"),
    yandex_maps_endpoint: field(formData, "yandex_maps_endpoint") || "https://search-maps.yandex.ru/v1/",
    osm_overpass_endpoint: field(formData, "osm_overpass_endpoint") || "https://overpass-api.de/api/interpreter",
    osm_nominatim_endpoint: field(formData, "osm_nominatim_endpoint") || "https://nominatim.openstreetmap.org/search",
    whatsapp_access_token: field(formData, "whatsapp_access_token"),
    whatsapp_phone_number_id: field(formData, "whatsapp_phone_number_id"),
    whatsapp_business_account_id: field(formData, "whatsapp_business_account_id"),
    whatsapp_api_base_url: field(formData, "whatsapp_api_base_url") || "https://graph.facebook.com",
    whatsapp_api_version: field(formData, "whatsapp_api_version") || "v23.0",
    whatsapp_default_template: field(formData, "whatsapp_default_template"),
    whatsapp_default_language: field(formData, "whatsapp_default_language") || "ru",
    whatsapp_verify_token: field(formData, "whatsapp_verify_token"),
    max_bot_token: field(formData, "max_bot_token"),
    max_bot_id: field(formData, "max_bot_id"),
    max_api_base_url: field(formData, "max_api_base_url") || "https://platform-api2.max.ru",
    vk_community_token: field(formData, "vk_community_token"),
    vk_group_id: field(formData, "vk_group_id"),
    vk_confirmation_code: field(formData, "vk_confirmation_code"),
    vk_secret_key: field(formData, "vk_secret_key"),
    vk_api_base_url: field(formData, "vk_api_base_url") || "https://api.vk.com/method",
    vk_api_version: field(formData, "vk_api_version") || "5.199",
    broadcast_rate_limit_ms: numberField(formData, "broadcast_rate_limit_ms", 800),
    broadcast_default_channel_order: field(formData, "broadcast_default_channel_order") || "whatsapp,telegram,max,vk"
  };
  await apiFetch("/api/integrations", { method: "PUT", body: JSON.stringify(payload) });
  revalidatePath("/settings");
  revalidatePath("/discover");
  revalidatePath("/broadcast");
  redirect(messagePath("/settings", "Интеграции сохранены"));
}
