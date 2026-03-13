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

## Pairing strategies (round generation)

When generating the next round (Americano/Mexicano), teams can be formed in three ways (optional `pairing_strategy` on tournament; default by format):

| Strategy | Description |
|----------|-------------|
| **random** | Full random shuffle; consecutive groups of 4 become one match (team1 = first two, team2 = last two). |
| **by_ranking** | Weak+strong vs weak+strong: players ordered by points; in each group of 4, team1 = 1st+3rd, team2 = 2nd+4th. |
| **similar_points_avoid_rematch** | Group by similar points (consecutive quartets by ranking); for each quartet, choose the 2v2 split that minimizes how often those two pairs have already been in the same match. |

- Create tournament: optional `pairing_strategy` in body (`"random"`, `"by_ranking"`, `"similar_points_avoid_rematch"`). If omitted: Americano → random, Mexicano → by_ranking.
- Round generation uses the tournament’s effective strategy (explicit or default).

## SSE (real-time updates)

- **`GET /tournaments/{tournament_id}/stream`** — Server-Sent Events: when a match score is updated (PATCH `/tournaments/matches/{match_id}`) or a round is added (POST `.../rounds/next`), all open connections to that tournament’s stream receive an event (`match_updated` or `rounds_updated`). The dashboard and TV screen can update without polling.
- Events: `event: match_updated` with `data: {"type":"match_updated","match_id":...}`; `event: rounds_updated` with `data: {"type":"rounds_updated","round_index":...}`. A `ping` is sent every ~30s to keep the connection alive.

## Sentry

When **SENTRY_DSN** is set in `.env`, errors and traces (FastAPI) are sent to Sentry. Optional: **SENTRY_ENVIRONMENT** (default `development`), **SENTRY_TRACES_SAMPLE_RATE** (default `0.1`). Without DSN, Sentry is not initialized.

## OpenAPI / Swagger (private docs)

- **GET /docs** — Swagger UI.
- **GET /redoc** — ReDoc.
- **GET /openapi.json** — OpenAPI 3.0 schema.

If **DOCS_SECRET_KEY** is set in `.env`, these URLs are only accessible with the key:
- query: `/docs?docs_key=YOUR_SECRET`;
- or header: `X-Docs-Key: YOUR_SECRET`.
Without the key, 403 is returned. If `DOCS_SECRET_KEY` is not set, docs are open (handy for local development).

## Production checklist

Before going to production:

- **SECRET_KEY** — set and at least 32 characters (with `DEBUG=false` the app will not start with the default).
- **CORS_ORIGINS** — set allowed frontend origin(s), comma-separated (e.g. `https://your-frontend.com`).
- **ALLOWED_FRONTEND_BASE_URL** — set for Stripe Checkout `success_url`/`cancel_url` validation (open redirect protection).
- **Migrations** — in deploy, run `uv run alembic upgrade head` before starting the app.
- **Health** — use `GET /health/ready` for readiness (DB check); `GET /health` for liveness only.
- **Logging and monitoring** — requests are logged with `X-Request-ID`; configure Sentry (SENTRY_DSN) and log rotation if needed.
- **DB backups** — set up Postgres backups (scheduled pg_dump or managed DB backups).

## Lint and format

Install dev deps: `uv sync --extra dev` or `pip install -e ".[dev]"`.

- **Format:** `black app tests` and `isort app tests`
- **Check only:** `black --check app tests`, `isort --check-only app tests`
- **Lint:** `ruff check app tests` (add `--fix` to auto-fix)

CI runs black --check, isort --check-only, and ruff check before tests.

## Run

**Local development:** set **DEBUG=true** in `.env` (then SECRET_KEY and CORS_ORIGINS are not enforced). For production leave DEBUG=false and set all variables from the Production checklist.

**Local development with Docker (Postgres + Procrastinate queues):**

Postgres in the container listens on host port **5433** (to avoid conflict with local Postgres on 5432). In `.env` use `DATABASE_URL=...@localhost:5433/...`.

```bash
# From project root
docker compose up -d postgres
# Optional queue worker:
docker compose up -d worker

cd backend
cp ../.env.example .env   # example already uses port 5433 for docker compose
uv run pip install -e .
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

The Procrastinate worker can also run locally (sync URL required in `.env`):

```bash
cd backend
procrastinate --app=app.queues:app worker
```

**Without Docker** — put your DB parameters in `DATABASE_URL`.

## User roles

| Role | Description | Stored in |
|------|-------------|-----------|
| **SuperAdmin** | Global admin: approves/rejects organizations. | `User.is_superuser = True` |
| **Owner (organization)** | Organization owner. One user can be Owner of multiple organizations. Can add **Admin** and other **Owner** to the organization. | `OrganizationMember.role = "owner"` |
| **Admin (organization)** | Organization admin; added only by **Owner**. Can manage tournaments and enter scores like Owner. | `OrganizationMember.role = "admin"` |
| **Player** | Player. Any logged-in user can register for tournaments; there is no separate “Player” entity. | — |

- **Adding organization members:** only **Owner** can call `POST /organizations/{org_id}/members` (body: `{"user_id": <id>, "role": "admin"}` or `"owner"`). List members: `GET /organizations/{org_id}/members` (available to any org member).

## Organization approval (superuser)

- On creation, an organization gets status **pending**; only **approved** organizations can create tournaments.
- Only a **superuser** (`User.is_superuser = True`) can approve or reject:
  - `GET /organizations/pending` — list of organizations pending approval (superuser only);
  - `PATCH /organizations/{id}/approval` — body `{"approved": true}` or `{"approved": false}` (superuser only).
- To assign a superuser: set `is_superuser = true` in the DB for the desired user (or add a dedicated endpoint/script on first run).

## SuperAdmin panel

- **GET /admin/stats** — stats: users (total / superusers), organizations (total / pending / approved / rejected), tournaments, players, rounds, matches. SuperAdmin only (Bearer token).
- **GET /admin/settings** — site settings (key-value). Suggested keys: `maintenance_mode`, `registration_enabled`, `default_locale`, `max_tournaments_per_month_free`, `max_organizations_per_user`, `site_name`, `contact_email`.
- **PATCH /admin/settings** — update settings (body: `{"settings": {"key": "value", ...}}`). SuperAdmin only.
- **GET/POST/PATCH/DELETE /admin/blog** — blog post CRUD (SuperAdmin only). Public list: **GET /blog**, post by slug: **GET /blog/{slug}**.

## Stripe (Pro plan for organizations)

- In `.env` set: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_PRO` (Stripe recurring price ID).
- **POST /billing/create-checkout-session** — body: `{"organization_id": int, "success_url": str, "cancel_url": str}`. Organization Owner only. Returns `{ "url": "https://checkout.stripe.com/..." }` for redirect to checkout.
- **POST /billing/webhook** — Stripe webhook (signature verified with `STRIPE_WEBHOOK_SECRET`). Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`. Subscription metadata must include `organization_id`; organization’s `plan` (free/pro) and `stripe_subscription_id` are updated.

## Migrations

Alembic uses `app.infrastructure.persistence.models` and `app.core.database.Base` for the schema.

```bash
uv run alembic upgrade head
```

New tables/columns: `site_settings`, `blog_posts`; on `organizations`: `created_at`, `updated_at`, `stripe_customer_id`, `stripe_subscription_id`, `plan`. Create migrations manually or with `alembic revision --autogenerate` as needed.
