# LidraFlow

**LidraFlow** — минималистичный омниканальный AI SDR / CRM для локального B2B.

Стек:

- **Frontend:** Next.js App Router + TypeScript + Tailwind CSS
- **Backend:** FastAPI
- **DB:** SQLite
- **Каналы:** Telegram, WhatsApp Cloud API, MAX Bot API, VK Community API
- **Источники лидов:** CSV, ручной ввод, бесплатный OpenStreetMap Overpass, Yandex Organization Search API или договорной endpoint

## Что умеет MVP

- автосбор организаций из карт по нише, региону, городу, району, координатам и радиусу;
- фильтрация найденных компаний: без сайта / только с контактом;
- дедупликация лидов по source ID, телефону, Telegram и названию + адресу;
- карточка лида с географией: регион, город, район, адрес, координаты;
- каналы в карточке: Telegram, WhatsApp, MAX, VK;
- настройка всех токенов через веб-интерфейс;
- единая история сообщений;
- AI-черновики сообщений;
- рассылки по региону, городу, району, нише, статусу, согласию и каналу;
- dry-run перед реальной отправкой;
- история запусков кампаний;
- светлая/тёмная тема;
- брендированные формы авторизации, регистрации и восстановления пароля в стиле Aeterna SSO;
- локальные сессии пользователей: PBKDF2-хеши паролей, SQLite sessions, signed cookie на Next.js.

## Быстрый запуск

```bash
cp config/secrets.example.env config/secrets.env
cp frontend/.env.example frontend/.env.local
```

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Открыть:

```text
http://127.0.0.1:3000
```

Логин по умолчанию:

```text
admin / change-me-now
# или
admin@lidraflow.local / change-me-now
```


## Авторизация и SSO

В этой версии Basic Auth заменён на брендированный SSO-слой LidraFlow, адаптированный под структуру Aeterna SSO:

```text
/login      — вход
/register   — регистрация
/restore    — восстановление пароля
```

Backend endpoints:

```text
POST /api/auth/login
POST /api/auth/register
GET  /api/auth/me
POST /api/auth/logout
POST /api/auth/forgot
POST /api/auth/reset
```

Первый owner-аккаунт создаётся автоматически при старте backend из переменных:

```env
ADMIN_USER=admin
ADMIN_PASSWORD=change-me-now
```

Секрет подписи frontend-cookie должен быть одинаковым для frontend и backend окружения:

```env
LIDRAFLOW_AUTH_SECRET=change-this-long-random-auth-secret
AUTH_ALLOW_REGISTRATION=true
AUTH_DEBUG_RESET_TOKENS=true
```

В MVP код восстановления пароля показывается на странице `/restore`, чтобы проект работал без SMTP. Для production подключите почтовый сервис и отключите:

```env
AUTH_DEBUG_RESET_TOKENS=false
```

## Где вставлять токены

В веб-интерфейсе:

```text
Настройки → Интеграции и ключи
```

Там доступны:

- Telegram Bot Token / Bot ID;
- OpenStreetMap Overpass / Nominatim endpoints — ключ не нужен;
- Yandex Maps API Key / endpoint — опционально;
- WhatsApp Access Token / Phone Number ID / Business Account ID / Verify Token;
- MAX Bot Token / Bot ID / API Base URL;
- VK Community Token / Group ID / Confirmation Code / Secret Key;
- порядок автовыбора каналов;
- пауза между отправками;
- demo mode;
- разрешение ручного первого касания.

`config/secrets.env` остаётся fallback-файлом для первого запуска и Docker.


## Бесплатный поиск по картам

По умолчанию в `config/secrets.env` выбран провайдер:

```env
MAPS_PROVIDER=openstreetmap_overpass
```

Он использует:

```env
OSM_OVERPASS_ENDPOINT=https://overpass-api.de/api/interpreter
OSM_NOMINATIM_ENDPOINT=https://nominatim.openstreetmap.org/search
```

API-ключ не нужен. В разделе “Поиск” можно искать по категории, региону, городу, району, координатам и радиусу. Для больших объёмов лучше поднять свой Overpass/OSM dump, потому что публичные бесплатные endpoints не рассчитаны на массовую промышленную нагрузку.

## Географические рассылки

Раздел:

```text
Рассылка
```

Фильтры кампании:

- регион;
- город;
- район;
- ниша;
- статус лида;
- статус согласия;
- канал: auto / Telegram / WhatsApp / MAX / VK;
- максимальное количество получателей.

Сначала запускайте с включённым `dry_run`: система покажет, сколько лидов подходит, кого пропустила и по каким каналам будет отправка.

## Webhook endpoints

Для входящих сообщений:

```text
POST /api/webhooks/whatsapp
GET  /api/webhooks/whatsapp
POST /api/webhooks/max
POST /api/webhooks/vk
```

Для frontend → backend используется заголовок:

```text
X-LidraFlow-Key: <FRONTEND_API_KEY>
```

## Docker

```bash
docker compose up --build
```

После запуска:

```text
Frontend: http://127.0.0.1:3000
Backend:  http://127.0.0.1:8000
```

## Проверка

В этой сборке проверено:

- Python compile backend;
- FastAPI smoke-test: health, meta, integrations, demo discovery, geo/channel filter, broadcast dry-run;
- TypeScript typecheck;
- Next.js production build.


## Локальная база данных

Для локального запуска `DATABASE_PATH` должен быть относительным или указывать на доступную папку, например:

```env
DATABASE_PATH=data/lidraflow.sqlite3
```

Если при локальном запуске видите Permission denied для `/app`, значит в `config/secrets.env` остался Docker-путь. Замените его на строку выше или удалите переменную `DATABASE_PATH`, тогда backend использует `lidraflow/data/lidraflow.sqlite3`.
# LidraFlow
