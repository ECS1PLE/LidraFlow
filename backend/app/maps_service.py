from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import httpx

from .config import settings
from .db import create_or_update_discovered_lead, normalize_phone, normalize_username, utc_now
from .runtime_config import (
    get_maps_provider,
    get_osm_nominatim_endpoint,
    get_osm_overpass_endpoint,
    get_yandex_maps_api_key,
    get_yandex_maps_endpoint,
    is_demo_mode,
)

TG_RE = re.compile(r"(?:https?://)?(?:t\.me|telegram\.me)/([A-Za-z0-9_]{5,32})|@([A-Za-z0-9_]{5,32})", re.IGNORECASE)
VK_RE = re.compile(r"(?:https?://)?(?:vk\.com|vkontakte\.ru)/([A-Za-z0-9_.-]{3,80})", re.IGNORECASE)
YANDEX_ORG_SEARCH_ENDPOINT = "https://search-maps.yandex.ru/v1/"
OSM_OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"
OSM_NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
OSM_ATTRIBUTION = "© OpenStreetMap contributors, ODbL"


OSM_CATEGORY_MAP: list[tuple[tuple[str, ...], list[tuple[str, str]]]] = [
    (("салон красоты", "beauty", "красот", "косметолог"), [("shop", "beauty"), ("shop", "hairdresser")]),
    (("барб", "парикмах", "hairdresser"), [("shop", "hairdresser")]),
    (("стомат", "dentist", "зуб"), [("amenity", "dentist")]),
    (("коф", "coffee", "кофей"), [("amenity", "cafe")]),
    (("кафе", "cafe"), [("amenity", "cafe")]),
    (("ресторан", "restaurant"), [("amenity", "restaurant")]),
    (("бар", "pub"), [("amenity", "bar"), ("amenity", "pub")]),
    (("аптек", "pharmacy"), [("amenity", "pharmacy")]),
    (("автосервис", "сто", "ремонт авто", "car repair"), [("shop", "car_repair")]),
    (("шиномонтаж", "tyres", "шины"), [("shop", "tyres")]),
    (("фитнес", "спортзал", "gym"), [("leisure", "fitness_centre"), ("sport", "fitness")]),
    (("клиник", "clinic"), [("amenity", "clinic"), ("amenity", "doctors")]),
    (("вет", "veterinary"), [("amenity", "veterinary")]),
    (("отель", "гостини", "hotel"), [("tourism", "hotel"), ("tourism", "guest_house")]),
    (("цвет", "flowers", "florist"), [("shop", "florist")]),
    (("пекар", "bakery"), [("shop", "bakery")]),
    (("магазин", "shop"), [("shop", "")]),
]


def normalize_yandex_endpoint(endpoint: str) -> tuple[str, str]:
    raw = str(endpoint or "").strip()
    if not raw:
        return YANDEX_ORG_SEARCH_ENDPOINT, ""
    parsed = urlparse(raw)
    host = parsed.netloc.lower()
    path = parsed.path.rstrip("/").lower()
    if "api-maps.yandex" in host or path == "/v3":
        return (
            YANDEX_ORG_SEARCH_ENDPOINT,
            "Endpoint карт был исправлен: для поиска организаций используется https://search-maps.yandex.ru/v1/, а не Maps JavaScript API v3.",
        )
    if not raw.startswith(("http://", "https://")):
        return "https://" + raw.strip("/") + "/", ""
    return raw, ""


def _normalize_http_endpoint(value: str, fallback: str) -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    if not text.startswith(("http://", "https://")):
        return "https://" + text.strip("/")
    return text


def _safe_http_error_message(response: httpx.Response, provider: str = "Maps API") -> str:
    status = response.status_code
    reason = response.reason_phrase
    body = response.text[:700].strip()
    if not body:
        body = "пустой ответ"
    return f"{provider} вернул {status} {reason}. Ответ: {body}"


def extract_telegram_username(*values: str) -> str:
    for value in values:
        if not value:
            continue
        match = TG_RE.search(value)
        if match:
            return normalize_username(match.group(1) or match.group(2) or "")
    return ""


def extract_vk_id(*values: str) -> str:
    for value in values:
        if not value:
            continue
        match = VK_RE.search(value)
        if match:
            return match.group(1).strip()
    return ""


def _join_text(*values: Any) -> str:
    parts: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, list):
            parts.extend(str(v) for v in value if v)
        elif isinstance(value, dict):
            for item in value.values():
                if isinstance(item, (dict, list)):
                    parts.append(_join_text(item))
                elif item:
                    parts.append(str(item))
        else:
            parts.append(str(value))
    return "\n".join(p for p in parts if p)


def _phone_from_meta(meta: dict[str, Any]) -> str:
    phones = meta.get("Phones") or meta.get("phones") or []
    if isinstance(phones, list):
        for phone in phones:
            if isinstance(phone, dict):
                value = phone.get("formatted") or phone.get("number") or phone.get("value")
                if value:
                    return str(value).strip()
            elif phone:
                return str(phone).strip()
    return ""


def _website_from_meta(meta: dict[str, Any], props: dict[str, Any]) -> str:
    for key in ["url", "site", "website"]:
        value = str(meta.get(key) or props.get(key) or "").strip()
        if value and not any(domain in value.lower() for domain in ["t.me/", "telegram.me/", "vk.com/"]):
            return value
    links = meta.get("Links") or meta.get("links") or props.get("links") or []
    if isinstance(links, list):
        for link in links:
            if isinstance(link, dict):
                href = str(link.get("href") or link.get("url") or "").strip()
                if href and not any(domain in href.lower() for domain in ["t.me/", "telegram.me/", "vk.com/"]):
                    return href
    return ""


def _links_as_text(meta: dict[str, Any], props: dict[str, Any]) -> str:
    links = meta.get("Links") or meta.get("links") or props.get("links") or []
    parts: list[str] = []
    if isinstance(links, list):
        for link in links:
            if isinstance(link, dict):
                parts.extend(str(link.get(k) or "") for k in ["href", "url", "name", "type"])
            elif link:
                parts.append(str(link))
    return "\n".join(p for p in parts if p)


def _categories(meta: dict[str, Any]) -> str:
    categories = meta.get("Categories") or meta.get("categories") or []
    names: list[str] = []
    if isinstance(categories, list):
        for item in categories:
            if isinstance(item, dict):
                name = item.get("name") or item.get("class")
                if name:
                    names.append(str(name))
            elif item:
                names.append(str(item))
    return ", ".join(dict.fromkeys(names))


def _admin_area(meta: dict[str, Any], fallback_region: str, fallback_city: str, fallback_district: str) -> tuple[str, str, str]:
    address_details = meta.get("Address") or meta.get("addressDetails") or {}
    components = address_details.get("Components") or address_details.get("components") or []
    region = fallback_region
    city = fallback_city
    district = fallback_district
    if isinstance(components, list):
        for component in components:
            if not isinstance(component, dict):
                continue
            name = str(component.get("name") or "").strip()
            kind = str(component.get("kind") or component.get("type") or "").lower()
            if not name:
                continue
            if kind in {"province", "area", "region"} and not region:
                region = name
            elif kind in {"locality", "city"} and not city:
                city = name
            elif kind in {"district", "metro", "street"} and not district:
                district = name if "район" in name.lower() or not district else district
    return region, city, district


def _feature_to_lead(feature: dict[str, Any], provider: str, payload: dict[str, Any]) -> dict[str, Any]:
    props = feature.get("properties") or {}
    meta = props.get("CompanyMetaData") or props.get("companyMetaData") or props.get("BusinessMetaData") or {}
    geometry = feature.get("geometry") or {}
    coords = geometry.get("coordinates") or []

    fallback_region = str(payload.get("region") or "").strip()
    fallback_city = str(payload.get("city") or "").strip()
    fallback_district = str(payload.get("district") or "").strip()
    region, city, district = _admin_area(meta, fallback_region, fallback_city, fallback_district)

    name = meta.get("name") or props.get("name") or feature.get("name") or "Без названия"
    address = meta.get("address") or props.get("description") or ""
    phone = _phone_from_meta(meta)
    website = _website_from_meta(meta, props)
    links_text = _links_as_text(meta, props)
    description_text = _join_text(address, props.get("description"), props.get("text"), meta, links_text)
    telegram = extract_telegram_username(links_text, website, description_text)
    vk_id = extract_vk_id(links_text, website, description_text)
    source_url = str(props.get("uri") or props.get("href") or props.get("permalink") or "").strip()
    external_id = str(meta.get("id") or props.get("id") or feature.get("id") or source_url or "").strip()
    niche = _categories(meta) or str(props.get("category") or "").strip()

    latitude = None
    longitude = None
    geo_note = ""
    if isinstance(coords, list) and len(coords) >= 2:
        longitude = float(coords[0])
        latitude = float(coords[1])
        geo_note = f"Координаты: {latitude}, {longitude}"

    notes = [
        "Найдено через автопоиск по картам.",
        f"Адрес: {address}" if address else "",
        f"Регион: {region}" if region else "",
        f"Город: {city}" if city else "",
        f"Район: {district}" if district else "",
        geo_note,
        f"Источник: {source_url}" if source_url else "",
    ]

    return {
        "organization": str(name).strip() or "Без названия",
        "contact_name": "",
        "niche": niche,
        "region": region,
        "city": city,
        "district": district,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "phone": phone,
        "telegram_username": telegram,
        "telegram_chat_id": "",
        "whatsapp_phone": normalize_phone(phone),
        "max_user_id": "",
        "max_chat_id": "",
        "vk_user_id": vk_id,
        "vk_peer_id": "",
        "website": website,
        "source_url": source_url,
        "maps_provider": provider,
        "maps_external_id": external_id,
        "discovered_at": utc_now(),
        "notes": "\n".join(p for p in notes if p),
    }


def _demo_features() -> list[dict[str, Any]]:
    return [
        {
            "properties": {
                "name": "Demo Coffee Point",
                "description": "Москва, Тверской район, ул. Примерная, 1, Telegram @demo_coffee_point, vk.com/demo_coffee_point",
                "uri": "demo://maps/org/coffee-point",
                "CompanyMetaData": {
                    "id": "demo-coffee-point",
                    "name": "Demo Coffee Point",
                    "address": "Москва, Тверской район, ул. Примерная, 1",
                    "Phones": [{"formatted": "+7 900 000-00-01"}],
                    "Categories": [{"name": "Кофейня"}],
                },
            },
            "geometry": {"coordinates": [37.62, 55.75]},
        },
        {
            "properties": {
                "name": "Demo Beauty Studio",
                "description": "Санкт-Петербург, Центральный район, Telegram: https://t.me/demo_beauty_studio",
                "uri": "demo://maps/org/beauty-studio",
                "CompanyMetaData": {
                    "id": "demo-beauty-studio",
                    "name": "Demo Beauty Studio",
                    "address": "Санкт-Петербург, Центральный район, Невский проспект, 10",
                    "Phones": [{"formatted": "+7 900 000-00-02"}],
                    "Categories": [{"name": "Салон красоты"}],
                },
            },
            "geometry": {"coordinates": [30.31, 59.93]},
        },
    ]


async def _fetch_yandex_features(payload: dict[str, Any]) -> list[dict[str, Any]]:
    api_key = get_yandex_maps_api_key()
    endpoint, endpoint_warning = normalize_yandex_endpoint(get_yandex_maps_endpoint() or settings.yandex_maps_endpoint)
    if not api_key or "PASTE_" in api_key:
        if is_demo_mode():
            return _demo_features()
        raise RuntimeError("YANDEX_MAPS_API_KEY не настроен. Вставьте ключ на странице Настройки → Интеграции или выберите OpenStreetMap Overpass.")

    query = str(payload.get("query") or "").strip()
    region = str(payload.get("region") or "").strip()
    city = str(payload.get("city") or "").strip()
    district = str(payload.get("district") or "").strip()
    if not query:
        raise RuntimeError("Укажите поисковый запрос: например, 'кофейни', 'стоматологии', 'салоны красоты'.")

    text = " ".join(part for part in [query, district, city, region] if part).strip()
    limit = max(1, min(int(payload.get("limit") or 20), settings.max_discovery_limit))
    params: dict[str, Any] = {
        "apikey": api_key,
        "text": text,
        "type": "biz",
        "lang": "ru_RU",
        "results": limit,
    }

    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    if latitude is not None and longitude is not None:
        params["ll"] = f"{float(longitude)},{float(latitude)}"
        radius_m = max(250, min(int(payload.get("radius_m") or 5000), 50000))
        degree_span = radius_m / 111_000
        params["spn"] = f"{degree_span},{degree_span}"
        params["rspn"] = 1

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(endpoint, params=params)
        if response.status_code >= 400:
            raise RuntimeError(_safe_http_error_message(response, "Yandex Maps API"))
        data = response.json()

    if endpoint_warning:
        payload.setdefault("_warnings", []).append(endpoint_warning)

    features = data.get("features") or data.get("FeatureCollection", {}).get("features") or []
    if not isinstance(features, list):
        return []
    return [feature for feature in features if isinstance(feature, dict)]


def _osm_escape(value: str) -> str:
    return str(value or "").replace('\\', '\\\\').replace('"', '\\"').replace("\n", " ").strip()


def _osm_tags_for_query(query: str) -> list[tuple[str, str]]:
    lowered = (query or "").strip().lower()
    tags: list[tuple[str, str]] = []
    for keywords, mapped_tags in OSM_CATEGORY_MAP:
        if any(keyword in lowered for keyword in keywords):
            tags.extend(mapped_tags)
    seen: set[tuple[str, str]] = set()
    unique: list[tuple[str, str]] = []
    for tag in tags:
        if tag not in seen:
            unique.append(tag)
            seen.add(tag)
    return unique


def _osm_selector_lines(tags: list[tuple[str, str]], scope: str, query: str) -> list[str]:
    lines: list[str] = []
    for key, value in tags:
        key_escaped = _osm_escape(key)
        if value:
            value_escaped = _osm_escape(value)
            for element_type in ["node", "way", "relation"]:
                lines.append(f'  {element_type}["{key_escaped}"="{value_escaped}"]{scope};')
        else:
            for element_type in ["node", "way", "relation"]:
                lines.append(f'  {element_type}["{key_escaped}"]{scope};')
    if not lines and query:
        needle = _osm_escape(query)
        for element_type in ["node", "way", "relation"]:
            lines.append(f'  {element_type}["name"~"{needle}", i]{scope};')
    return lines


def _bbox_from_nominatim_item(item: dict[str, Any]) -> tuple[float, float, float, float] | None:
    bbox = item.get("boundingbox") or []
    if not isinstance(bbox, list) or len(bbox) != 4:
        return None
    try:
        south = float(bbox[0])
        north = float(bbox[1])
        west = float(bbox[2])
        east = float(bbox[3])
        return south, west, north, east
    except (TypeError, ValueError):
        return None


async def _geocode_osm_bbox(payload: dict[str, Any]) -> tuple[float, float, float, float] | None:
    parts = [str(payload.get(k) or "").strip() for k in ["district", "city", "region"]]
    query = ", ".join(part for part in parts if part)
    if not query:
        return None
    endpoint = _normalize_http_endpoint(get_osm_nominatim_endpoint(), OSM_NOMINATIM_ENDPOINT)
    headers = {"User-Agent": "LidraFlow/0.1 local-mvp (OpenStreetMap discovery; contact: admin@localhost)"}
    params = {"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1}
    try:
        async with httpx.AsyncClient(timeout=20, headers=headers) as client:
            response = await client.get(endpoint, params=params)
            if response.status_code >= 400:
                return None
            data = response.json()
    except Exception:
        return None
    if not isinstance(data, list) or not data:
        return None
    return _bbox_from_nominatim_item(data[0])


def _osm_area_query(payload: dict[str, Any], selector_lines: list[str], limit: int) -> str:
    area_name = str(payload.get("district") or payload.get("city") or payload.get("region") or "").strip()
    if not area_name:
        raise RuntimeError("Для OpenStreetMap укажите город/район или координаты с радиусом.")
    escaped_area = _osm_escape(area_name)
    scoped = []
    for line in selector_lines:
        scoped.append(line.replace("__SCOPE__", "(area.searchArea)"))
    return "\n".join(
        [
            "[out:json][timeout:25];",
            f'area["name"="{escaped_area}"]["boundary"="administrative"]->.searchArea;',
            "(",
            *scoped,
            ");",
            f"out tags center qt {limit};",
        ]
    )


def _osm_bbox_query(bbox: tuple[float, float, float, float], selector_lines: list[str], limit: int) -> str:
    south, west, north, east = bbox
    scope = f"({south},{west},{north},{east})"
    scoped = [line.replace("__SCOPE__", scope) for line in selector_lines]
    return "\n".join(["[out:json][timeout:25];", "(", *scoped, ");", f"out tags center qt {limit};"])


def _osm_around_query(latitude: float, longitude: float, radius_m: int, selector_lines: list[str], limit: int) -> str:
    scope = f"(around:{radius_m},{latitude},{longitude})"
    scoped = [line.replace("__SCOPE__", scope) for line in selector_lines]
    return "\n".join(["[out:json][timeout:25];", "(", *scoped, ");", f"out tags center qt {limit};"])


def _address_from_osm_tags(tags: dict[str, Any]) -> str:
    city = str(tags.get("addr:city") or "").strip()
    street = str(tags.get("addr:street") or "").strip()
    house = str(tags.get("addr:housenumber") or "").strip()
    full = str(tags.get("addr:full") or "").strip()
    if full:
        return full
    line = " ".join(part for part in [street, house] if part).strip()
    return ", ".join(part for part in [city, line] if part)


def _osm_website(tags: dict[str, Any]) -> str:
    for key in ["contact:website", "website", "url", "contact:facebook", "contact:instagram"]:
        value = str(tags.get(key) or "").strip()
        if value and not any(domain in value.lower() for domain in ["t.me/", "telegram.me/", "vk.com/", "vkontakte.ru/"]):
            return value
    return ""


def _osm_phone(tags: dict[str, Any]) -> str:
    for key in ["contact:phone", "phone", "mobile", "contact:mobile"]:
        value = str(tags.get(key) or "").strip()
        if value:
            return value
    return ""


def _osm_niche(tags: dict[str, Any], fallback_query: str) -> str:
    parts: list[str] = []
    for key in ["amenity", "shop", "tourism", "leisure", "office", "craft", "healthcare", "sport"]:
        value = str(tags.get(key) or "").strip()
        if value:
            parts.append(f"{key}={value}")
    return ", ".join(dict.fromkeys(parts)) or fallback_query


def _osm_element_to_lead(element: dict[str, Any], provider: str, payload: dict[str, Any]) -> dict[str, Any]:
    tags = element.get("tags") or {}
    if not isinstance(tags, dict):
        tags = {}
    element_type = str(element.get("type") or "node")
    element_id = str(element.get("id") or "")
    center = element.get("center") or {}

    lat = element.get("lat") if element.get("lat") is not None else center.get("lat")
    lon = element.get("lon") if element.get("lon") is not None else center.get("lon")
    latitude = float(lat) if lat is not None else None
    longitude = float(lon) if lon is not None else None

    name = str(tags.get("name") or tags.get("brand") or "Без названия").strip()
    phone = _osm_phone(tags)
    website = _osm_website(tags)
    all_tags_text = _join_text(tags)
    telegram = normalize_username(str(tags.get("contact:telegram") or tags.get("telegram") or "").strip()) or extract_telegram_username(all_tags_text)
    vk_id = str(tags.get("contact:vk") or tags.get("vk") or "").strip() or extract_vk_id(all_tags_text)
    address = _address_from_osm_tags(tags)
    city = str(tags.get("addr:city") or payload.get("city") or "").strip()
    region = str(tags.get("addr:region") or payload.get("region") or "").strip()
    district = str(tags.get("addr:district") or payload.get("district") or "").strip()
    source_url = f"https://www.openstreetmap.org/{element_type}/{element_id}" if element_id else "https://www.openstreetmap.org/"
    external_id = f"{element_type}/{element_id}" if element_id else source_url
    niche = _osm_niche(tags, str(payload.get("query") or "").strip())

    notes = [
        "Найдено через бесплатный источник OpenStreetMap Overpass.",
        OSM_ATTRIBUTION,
        f"Адрес: {address}" if address else "",
        f"Регион: {region}" if region else "",
        f"Город: {city}" if city else "",
        f"Район: {district}" if district else "",
        f"Координаты: {latitude}, {longitude}" if latitude is not None and longitude is not None else "",
        f"OSM: {source_url}",
    ]

    return {
        "organization": name or "Без названия",
        "contact_name": "",
        "niche": niche,
        "region": region,
        "city": city,
        "district": district,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "phone": phone,
        "telegram_username": telegram,
        "telegram_chat_id": "",
        "whatsapp_phone": normalize_phone(phone),
        "max_user_id": "",
        "max_chat_id": "",
        "vk_user_id": vk_id,
        "vk_peer_id": "",
        "website": website,
        "source_url": source_url,
        "maps_provider": provider,
        "maps_external_id": external_id,
        "discovered_at": utc_now(),
        "notes": "\n".join(p for p in notes if p),
    }


async def _fetch_osm_elements(payload: dict[str, Any]) -> list[dict[str, Any]]:
    query = str(payload.get("query") or "").strip()
    if not query:
        raise RuntimeError("Укажите поисковый запрос: например, 'кофейни', 'стоматологии', 'салоны красоты'.")

    limit = max(1, min(int(payload.get("limit") or 20), settings.max_discovery_limit))
    tags = _osm_tags_for_query(query)
    selector_template = _osm_selector_lines(tags, "__SCOPE__", query)
    if not selector_template:
        raise RuntimeError("Не удалось построить OSM-запрос. Уточните категорию или укажите более конкретный текст.")

    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    radius_m = max(250, min(int(payload.get("radius_m") or 5000), 50000))
    warnings = payload.setdefault("_warnings", [])

    if latitude is not None and longitude is not None:
        overpass_query = _osm_around_query(float(latitude), float(longitude), radius_m, selector_template, limit)
    else:
        bbox = await _geocode_osm_bbox(payload)
        if bbox:
            overpass_query = _osm_bbox_query(bbox, selector_template, limit)
            warnings.append("География найдена через Nominatim, затем организации взяты из OpenStreetMap Overpass.")
        else:
            overpass_query = _osm_area_query(payload, selector_template, limit)
            warnings.append("Nominatim не вернул bbox; использован fallback по административной области Overpass.")

    endpoint = _normalize_http_endpoint(get_osm_overpass_endpoint(), OSM_OVERPASS_ENDPOINT)
    headers = {"User-Agent": "LidraFlow/0.1 local-mvp (OpenStreetMap discovery; contact: admin@localhost)"}
    async with httpx.AsyncClient(timeout=45, headers=headers) as client:
        response = await client.post(endpoint, data={"data": overpass_query})
        if response.status_code >= 400:
            raise RuntimeError(_safe_http_error_message(response, "OpenStreetMap Overpass"))
        data = response.json()

    elements = data.get("elements") or []
    if not isinstance(elements, list):
        return []
    return [element for element in elements if isinstance(element, dict)]


async def discover_leads(payload: dict[str, Any]) -> dict[str, Any]:
    provider = str(payload.get("provider") or get_maps_provider() or "openstreetmap_overpass").strip().lower()
    supported = {"yandex", "custom_yandex_contract", "openstreetmap_overpass", "osm_overpass", "osm"}
    if provider not in supported:
        raise RuntimeError("Поддерживаемые провайдеры: openstreetmap_overpass, yandex, custom_yandex_contract.")
    if provider in {"osm_overpass", "osm"}:
        provider = "openstreetmap_overpass"

    require_no_site = bool(payload.get("require_no_site", True))
    require_contact = bool(payload.get("require_contact", True))
    import_results = bool(payload.get("import_results", True))

    if provider in {"yandex", "custom_yandex_contract"}:
        raw_items = await _fetch_yandex_features(payload)
        leads = [_feature_to_lead(feature, provider=provider, payload=payload) for feature in raw_items]
    elif is_demo_mode():
        raw_items = _demo_features()
        leads = [_feature_to_lead(feature, provider=provider, payload=payload) for feature in raw_items]
        payload.setdefault("_warnings", []).append("Demo mode включён: показаны тестовые лиды вместо запроса к OpenStreetMap.")
    else:
        raw_items = await _fetch_osm_elements(payload)
        leads = [_osm_element_to_lead(element, provider=provider, payload=payload) for element in raw_items]

    parsed: list[dict[str, Any]] = []
    skipped = 0
    warnings: list[str] = list(payload.get("_warnings") or [])

    for lead in leads:
        has_site = bool(str(lead.get("website") or "").strip())
        has_contact = any(
            str(lead.get(key) or "").strip()
            for key in ["phone", "telegram_username", "whatsapp_phone", "vk_user_id", "max_user_id"]
        )

        if require_no_site and has_site:
            skipped += 1
            continue
        if require_contact and not has_contact:
            skipped += 1
            continue

        if import_results:
            lead_id, created = create_or_update_discovered_lead(lead)
            lead["lead_id"] = lead_id
            lead["created"] = created
        parsed.append(lead)

    imported = sum(1 for item in parsed if item.get("created") is True)
    merged = sum(1 for item in parsed if item.get("created") is False)
    if provider == "openstreetmap_overpass":
        warnings.append("Источник OpenStreetMap бесплатный, но контакты организаций заполнены не всегда; для теста можно отключить фильтр 'только с контактом'.")
        warnings.append(OSM_ATTRIBUTION)
    if not parsed:
        warnings.append("По заданным фильтрам ничего не найдено. Попробуйте расширить запрос, увеличить радиус или отключить фильтр 'без сайта/с контактом'.")

    return {
        "provider": provider,
        "found": len(parsed),
        "imported": imported,
        "merged": merged,
        "skipped": skipped,
        "items": parsed,
        "warnings": warnings,
    }


async def test_maps_connection() -> dict[str, Any]:
    data = await discover_leads(
        {
            "provider": get_maps_provider(),
            "query": "кофейня",
            "city": "Москва",
            "limit": 1,
            "require_no_site": False,
            "require_contact": False,
            "import_results": False,
        }
    )
    return {"ok": True, "provider": data["provider"], "sample_count": data["found"]}
