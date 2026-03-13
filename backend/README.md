# Padel Tournaments Backend (DDD)

FastAPI backend using **Domain-Driven Design (DDD)**.

## Architecture

```
app/
  domain/                 # Domain layer (no external deps)
    entities.py           # User, Organization, Tournament, Player, Round, Match
    value_objects.py      # TournamentFormat, OrgMemberRole, TournamentStatus
    repositories.py       # Ports (abstract interfaces)
    services.py           # Domain services (e.g. Americano/Mexicano pair generation)

  application/            # Application layer (use cases)
    dto.py                # Commands, DTOs
    auth_service.py       # Auth use cases
    tournament_service.py # Tournament CRUD, rounds, matches, leaderboard

  infrastructure/         # Adapters
    persistence/          # ORM and repository implementations
      models.py           # SQLAlchemy ORM models
      repositories.py     # Repository implementations (ORM <-> domain)
    api/                  # HTTP adapter
      schemas.py          # Pydantic request/response
      dependencies.py     # FastAPI Depends (session, services)
      routes/             # auth, tournaments

  core/                   # Shared (config, database, security)
```

- **Domain**: pure business logic and entities; repository interfaces (ports).
- **Application**: application services depend only on domain ports; no SQL or HTTP.
- **Infrastructure**: implements ports (repositories), exposes HTTP API (FastAPI).

## SSE (обновления в реальном времени)

- **`GET /tournaments/{tournament_id}/stream`** — Server-Sent Events: при обновлении счёта матча (PATCH `/tournaments/matches/{match_id}`) или добавлении раунда (POST `.../rounds/next`) все открытые подключения к потоку этого турнира получают событие (`match_updated` или `rounds_updated`). Так дашборд и экран ТВ могут обновляться без опроса.
- События: `event: match_updated` с `data: {"type":"match_updated","match_id":...}`; `event: rounds_updated` с `data: {"type":"rounds_updated","round_index":...}`. Каждые ~30 сек отправляется `ping` для поддержания соединения.

## Sentry

При заданном **SENTRY_DSN** в `.env` ошибки и трейсы (FastAPI) отправляются в Sentry. Опционально: **SENTRY_ENVIRONMENT** (по умолчанию `development`), **SENTRY_TRACES_SAMPLE_RATE** (по умолчанию `0.1`). Без DSN Sentry не инициализируется.

## OpenAPI / Swagger (приватная документация)

- **GET /docs** — Swagger UI.
- **GET /redoc** — ReDoc.
- **GET /openapi.json** — схема OpenAPI 3.0.

Если в `.env` задан **DOCS_SECRET_KEY**, доступ к этим URL только с ключом:
- в query: `/docs?docs_key=YOUR_SECRET`;
- или в заголовке: `X-Docs-Key: YOUR_SECRET`.
Без ключа возвращается 403. Если `DOCS_SECRET_KEY` не задан, документация открыта без проверки (удобно для локальной разработки).

## Production checklist

Перед выкладкой в прод убедитесь:

- **SECRET_KEY** — задан и не менее 32 символов (при `DEBUG=false` приложение не стартует с дефолтом).
- **CORS_ORIGINS** — задан список разрешённых origin через запятую (например `https://your-frontend.com`).
- **ALLOWED_FRONTEND_BASE_URL** — задан для проверки `success_url`/`cancel_url` Stripe Checkout (защита от open redirect).
- **Миграции** — в деплое перед стартом приложения выполнить `uv run alembic upgrade head`.
- **Health** — использовать `GET /health/ready` для проверки готовности (проверка БД); `GET /health` — только liveness.
- **Логи и мониторинг** — запросы логируются с `X-Request-ID`; настроить Sentry (SENTRY_DSN) и при необходимости ротацию логов.
- **Бэкапы БД** — настроить резервное копирование Postgres (pg_dump по расписанию или бэкапы managed DB).

## Run

**Локальная разработка:** в `.env` задайте **DEBUG=true** (тогда не проверяются SECRET_KEY и CORS_ORIGINS). Для продакшена оставьте DEBUG=false и задайте все переменные из Production checklist.

**Локальная разработка с Docker (Postgres + очереди Procrastinate):**

Postgres в контейнере слушает на хосте порт **5433** (чтобы не конфликтовать с локальным Postgres на 5432). В `.env` укажите `DATABASE_URL=...@localhost:5433/...`.

```bash
# В корне проекта
docker compose up -d postgres
# Опционально воркер очередей:
docker compose up -d worker

cd backend
cp ../.env.example .env   # в примере уже порт 5433 для docker compose
uv run pip install -e .
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

Воркер Procrastinate можно запускать и локально (нужен sync URL в `.env`):

```bash
cd backend
procrastinate --app=app.queues:app worker
```

**Без Docker** — подставьте свои параметры БД в `DATABASE_URL`.

## Роли пользователей

| Роль | Описание | Где хранится |
|------|----------|--------------|
| **SuperAdmin** | Глобальный администратор: подтверждает/отклоняет организации. | `User.is_superuser = True` |
| **Owner (организации)** | Владелец организации. Один пользователь может быть Owner нескольких организаций. Может добавлять в организацию **Admin** и других **Owner**. | `OrganizationMember.role = "owner"` |
| **Admin (организации)** | Администратор организации; добавляется только **Owner**. Может управлять турнирами и вводить счёт наравне с Owner. | `OrganizationMember.role = "admin"` |
| **Player** | Игрок. Любой залогиненный пользователь может регистрироваться в турнирах; отдельной сущности «роль Player» нет. | — |

- **Добавление участников организации**: только **Owner** может вызывать `POST /organizations/{org_id}/members` (тело: `{"user_id": <id>, "role": "admin"}` или `"owner"`). Список участников: `GET /organizations/{org_id}/members` (доступен любому члену организации).

## Подтверждение организаций (суперпользователь)

- При создании организация получает статус **pending**; создавать турниры может только организация со статусом **approved**.
- Подтвердить или отклонить организацию может только **суперпользователь** (`User.is_superuser = True`):
  - `GET /organizations/pending` — список организаций на подтверждении (только суперпользователь);
  - `PATCH /organizations/{id}/approval` — тело `{"approved": true}` или `{"approved": false}` (только суперпользователь).
- Назначить суперпользователя: обновить в БД у нужного пользователя поле `is_superuser = true` (или добавить отдельный endpoint/скрипт при первом запуске).

## Панель суперадмина (SuperAdmin)

- **GET /admin/stats** — статистика: пользователи (всего / суперпользователи), организации (всего / на модерации / одобрено / отклонено), турниры, игроки, раунды, матчи. Только SuperAdmin (Bearer token).
- **GET /admin/settings** — настройки сайта (key-value). Рекомендуемые ключи: `maintenance_mode`, `registration_enabled`, `default_locale`, `max_tournaments_per_month_free`, `max_organizations_per_user`, `site_name`, `contact_email`.
- **PATCH /admin/settings** — обновить настройки (тело: `{"settings": {"key": "value", ...}}`). Только SuperAdmin.
- **GET/POST/PATCH/DELETE /admin/blog** — CRUD постов блога (только SuperAdmin). Публичный список: **GET /blog**, пост по slug: **GET /blog/{slug}**.

## Stripe (оплата тарифа Pro для организаций)

- В `.env` задайте: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_PRO` (Price ID рекуррентного тарифа в Stripe).
- **POST /billing/create-checkout-session** — тело: `{"organization_id": int, "success_url": str, "cancel_url": str}`. Только Owner организации. Возвращает `{ "url": "https://checkout.stripe.com/..." }` — редирект на оплату.
- **POST /billing/webhook** — webhook Stripe (подпись проверяется по `STRIPE_WEBHOOK_SECRET`). События: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`. В метаданных подписки передаётся `organization_id`; у организации обновляются `plan` (free/pro) и `stripe_subscription_id`.

## Migrations

Alembic uses `app.infrastructure.persistence.models` and `app.core.database.Base` for schema.

```bash
uv run alembic upgrade head
```

Новые таблицы/колонки: `site_settings`, `blog_posts`, у `organizations` — `created_at`, `updated_at`, `stripe_customer_id`, `stripe_subscription_id`, `plan`. При необходимости создайте миграцию вручную или через `alembic revision --autogenerate`.
