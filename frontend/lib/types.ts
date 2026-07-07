export type LeadStatus = "new" | "drafted" | "contacted" | "replied" | "qualified" | "closed";
export type ConsentStatus = "pending" | "opted_in" | "opted_out";
export type MessageDirection = "in" | "out" | "draft" | "system";

export type Lead = {
  id: number;
  organization: string;
  contact_name: string;
  niche: string;
  region: string;
  city: string;
  district: string;
  address: string;
  latitude?: number | null;
  longitude?: number | null;
  phone: string;
  telegram_username: string;
  telegram_chat_id: string;
  whatsapp_phone: string;
  max_user_id: string;
  max_chat_id: string;
  vk_user_id: string;
  vk_peer_id: string;
  website: string;
  source_url: string;
  maps_provider: string;
  maps_external_id: string;
  discovered_at: string;
  status: LeadStatus;
  consent_status: ConsentStatus;
  preferred_channel: string;
  notes: string;
  created_at: string;
  updated_at: string;
  last_message_at: string;
  available_channels?: string[];
  last_message?: string;
  message_count?: number;
};

export type Message = {
  id: number;
  lead_id: number;
  direction: MessageDirection;
  channel: string;
  sender_name: string;
  body: string;
  tg_message_id: string;
  external_message_id: string;
  created_at: string;
};

export type Stats = {
  total: number;
  messages: number;
  opted_in: number;
  discovered: number;
  telegram: number;
  whatsapp: number;
  max: number;
  vk: number;
  new: number;
  replied: number;
  qualified: number;
};

export type LabelMap = Record<string, string>;

export type LeadsResponse = {
  items: Lead[];
  stats: Stats;
  status_labels: LabelMap;
  consent_labels: LabelMap;
  channel_labels: LabelMap;
};

export type LeadDetailResponse = {
  lead: Lead;
  messages: Message[];
  status_labels: LabelMap;
  consent_labels: LabelMap;
  channel_labels: LabelMap;
};

export type MetaResponse = {
  app_name: string;
  tagline: string;
  bot_configured: boolean;
  demo_mode: boolean;
  allow_manual_first_contact: boolean;
  status_labels: LabelMap;
  consent_labels: LabelMap;
  channel_labels: LabelMap;
  stats: Stats;
};

export type SettingsResponse = {
  settings: Record<string, string>;
};

export type Integrations = {
  telegram_bot_configured: boolean;
  telegram_bot_token_masked: string;
  telegram_bot_id: string;
  enable_bot_polling: boolean;
  demo_mode: boolean;
  allow_manual_first_contact: boolean;
  maps_provider: string;
  osm_maps_configured: boolean;
  osm_overpass_endpoint: string;
  osm_nominatim_endpoint: string;
  yandex_maps_configured: boolean;
  yandex_maps_api_key_masked: string;
  yandex_maps_endpoint: string;
  whatsapp_configured: boolean;
  whatsapp_access_token_masked: string;
  whatsapp_phone_number_id: string;
  whatsapp_business_account_id: string;
  whatsapp_api_base_url: string;
  whatsapp_api_version: string;
  whatsapp_default_template: string;
  whatsapp_default_language: string;
  whatsapp_verify_token: string;
  max_configured: boolean;
  max_bot_token_masked: string;
  max_bot_id: string;
  max_api_base_url: string;
  vk_configured: boolean;
  vk_community_token_masked: string;
  vk_group_id: string;
  vk_confirmation_code: string;
  vk_secret_key_masked: string;
  vk_api_base_url: string;
  vk_api_version: string;
  broadcast_rate_limit_ms: number;
  broadcast_default_channel_order: string;
};

export type IntegrationsResponse = {
  integrations: Integrations;
  channel_labels: LabelMap;
};

export type DiscoveredLead = Partial<Lead> & {
  lead_id?: number;
  created?: boolean;
  organization: string;
};

export type DiscoveryResponse = {
  provider: string;
  found: number;
  imported: number;
  merged: number;
  skipped: number;
  items: DiscoveredLead[];
  warnings: string[];
  stats: Stats;
};

export type BroadcastResponse = {
  ok: boolean;
  campaign_id?: number;
  dry_run: boolean;
  eligible: number;
  sent: number;
  failed: number;
  skipped_count?: number;
  channel_breakdown?: Record<string, number>;
  skipped?: { organization: string; reason: string }[];
  failures?: { organization: string; reason: string }[];
  stats?: Stats;
};

export type Campaign = {
  id: number;
  name: string;
  channel: string;
  body: string;
  filters_json: string;
  dry_run: number;
  eligible: number;
  sent: number;
  failed: number;
  skipped: number;
  created_at: string;
};

export type CampaignsResponse = {
  items: Campaign[];
};
