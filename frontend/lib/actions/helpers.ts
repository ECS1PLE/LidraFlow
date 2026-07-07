import { field } from "../utils";

export function checked(formData: FormData, name: string): boolean {
  const value = formData.get(name);
  return value === "on" || value === "true" || value === "1";
}

export function numberField(formData: FormData, name: string, fallback: number): number {
  const value = Number(field(formData, name));
  return Number.isFinite(value) && value > 0 ? value : fallback;
}

export function optionalNumber(formData: FormData, name: string): number | null {
  const raw = field(formData, name);
  if (!raw) return null;
  const value = Number(raw);
  return Number.isFinite(value) ? value : null;
}

export function leadPayload(formData: FormData) {
  return {
    organization: field(formData, "organization"),
    contact_name: field(formData, "contact_name"),
    niche: field(formData, "niche"),
    region: field(formData, "region"),
    city: field(formData, "city"),
    district: field(formData, "district"),
    address: field(formData, "address"),
    latitude: optionalNumber(formData, "latitude"),
    longitude: optionalNumber(formData, "longitude"),
    phone: field(formData, "phone"),
    telegram_username: field(formData, "telegram_username"),
    telegram_chat_id: field(formData, "telegram_chat_id"),
    whatsapp_phone: field(formData, "whatsapp_phone"),
    max_user_id: field(formData, "max_user_id"),
    max_chat_id: field(formData, "max_chat_id"),
    vk_user_id: field(formData, "vk_user_id"),
    vk_peer_id: field(formData, "vk_peer_id"),
    website: field(formData, "website"),
    source_url: field(formData, "source_url"),
    preferred_channel: field(formData, "preferred_channel") || "auto",
    notes: field(formData, "notes")
  };
}
