# Padel Tournaments

A **SaaS platform** for padel clubs and federations to run tournaments: organizations, tournaments, rounds, matches, live leaderboards, and optional Pro subscriptions via Stripe.

---

## Tech stack

| Layer        | Stack |
|-------------|--------|
| **Backend** | FastAPI, SQLAlchemy 2 (async), PostgreSQL, Alembic, JWT auth, Stripe, Procrastinate (queues), Sentry |
| **Frontend**| Next.js 14 (App Router), Tailwind CSS, next-intl (ru/en), Sentry |
| **Infra**   | Docker Compose (Postgres, optional worker), private OpenAPI docs |

Backend follows **Domain-Driven Design (DDD)**: domain → application (use cases) → infrastructure (HTTP, persistence).

---

## Repository structure

```
PadelTournaments/
├── backend/           # FastAPI app (DDD, auth, orgs, tournaments, billing, admin, blog)
│   ├── app/
│   │   ├── domain/     # Entities, value objects, repository ports
│   │   ├── application/ # Auth, tournament services (use cases)
│   │   ├── infrastructure/ # Persistence, API routes, schemas
│   │   └── core/      # Config, database, security
│   ├── alembic/       # DB migrations
│   └── tests/
├── frontend/          # Next.js app (marketing, i18n, SEO, future: login, org dashboard)
├── docs/              # Production readiness audit, MVP notes
├── docker-compose.yml # Postgres (port 5433), Procrastinate worker
├── .env.example       # Shared env template (copy to .env)
└── README.md          # This file
```

---

## Quick start

**1. Environment**

```bash
cp .env.example .env
# Edit .env: set DEBUG=true for local dev; set DATABASE_URL (port 5433 if using Docker Postgres).
```

**2. Database (Docker)**

```bash
docker compose up -d postgres
```

**3. Backend**

```bash
cd backend
uv run pip install -e .
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

API: `http://localhost:8000`. Health: `GET /health`, readiness: `GET /health/ready`.

**4. Frontend**

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:3000` (redirects to `/ru` or `/en`).

**Optional:** Procrastinate worker (if you use background jobs):

```bash
docker compose up -d worker
# or locally: procrastinate --app=app.queues:app worker
```

---

## Features

- **Auth:** Register, login, refresh; JWT; roles: SuperAdmin, Organization Owner/Admin, Player.
- **Organizations:** Create org (pending); SuperAdmin approves; Owner adds Admin; Pro plan via Stripe.
- **Tournaments:** CRUD, add players, Americano/Mexicano formats, rounds, matches, leaderboard; **SSE stream** for live updates (`GET /tournaments/{id}/stream`).
- **Billing:** Stripe Checkout for Pro subscription; webhook; URL validation for success/cancel.
- **Admin:** SuperAdmin stats, site settings, blog CRUD; public blog list and post by slug.
- **Contact:** `POST /contact` from website form; backend logs (plug mailer if needed).
- **Security:** SECRET_KEY and CORS enforced when `DEBUG=false`; password and billing URL validation; request logging with `X-Request-ID`.
- **Ops:** Liveness `/health`, readiness `/health/ready` (DB); Alembic migrations; optional Sentry.

See **backend/README.md** for API details, roles, Stripe, OpenAPI docs, and production checklist.

---

## Configuration

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Async Postgres URL for FastAPI (e.g. `postgresql+asyncpg://...`) |
| `DATABASE_URL_SYNC` | Sync URL for Procrastinate worker |
| `SECRET_KEY` | JWT signing (≥32 chars in production) |
| `CORS_ORIGINS` | Allowed frontend origins (comma-separated) |
| `ALLOWED_FRONTEND_BASE_URL` | Allowed base for Stripe checkout URLs |
| `DEBUG` | If `true`, skips SECRET_KEY/CORS checks (local only) |
| `STRIPE_*`, `SENTRY_*`, `DOCS_SECRET_KEY` | Optional; see `.env.example` and backend README |

Frontend: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SITE_URL`, `NEXT_PUBLIC_SENTRY_DSN` — see **frontend/.env.example**.

---

## Plans and status

### Current status (pre-MVP)

- **Backend:** Feature-complete for MVP: auth, organizations, tournaments (Americano/Mexicano), billing, admin, blog, contact, health, migrations, tests.
- **Frontend:** Marketing site ready (home, pricing, contact, blog, FAQ, i18n, SEO). Login/Register and organizer dashboard are **placeholders** (“coming soon”).
- **Infrastructure:** Docker Compose, Sentry, private docs. Production checklist and DB backup note in backend README.

### Missing for first MVP

1. **Login & Register pages** — Real forms calling `POST /auth/register` and `POST /auth/login`, storing token (e.g. in `localStorage`), redirect to dashboard.
2. **Organizer dashboard** — After login: list “My organizations”, create org, open org → create tournament, add players, generate round, enter scores. Backend supports it; frontend UI is missing.
3. **TV display page** (optional for MVP) — A page (e.g. `/[locale]/tournaments/[id]/display`) that shows current round and leaderboard with SSE for in-club screens.
4. **Privacy & Terms** — Minimal text or “Draft” instead of “Content to be added” (needed for trust and payments).

### After MVP

- Rate limiting on auth endpoints.
- CI/CD (lint, tests, deploy).
- Frontend E2E or component tests.
- Full Privacy/Terms and production Dockerfiles if deploying with Docker.
- Additional tournament formats (Round Robin, Single/Double Elimination) once Americano/Mexicano are validated in production.

Detailed audit: **docs/PRODUCTION_READINESS_AUDIT.md** (in Russian; summarizes MVP readiness and checklist).

---

## Scripts and tools

- **Backend:** `uv run pytest` (tests), `uv run alembic upgrade head` (migrations), `uv run uvicorn app.main:app`.
- **Frontend:** `npm run dev` / `build` / `start`, `npm run lint`, `npm run format`.
- **Root:** `.gitignore` and `.dockerignore` (root + backend) for clean repos and smaller Docker context.

---

## Docs

- **Backend:** [backend/README.md](backend/README.md) — architecture, SSE, Sentry, OpenAPI, production checklist, roles, Stripe, migrations.
- **Frontend:** [frontend/README.md](frontend/README.md) — pages, SEO, Sentry, TypeScript/ESLint/Prettier.
- **MVP audit:** [docs/PRODUCTION_READINESS_AUDIT.md](docs/PRODUCTION_READINESS_AUDIT.md) — what’s done, what’s missing for first release, what to defer.

---

*Padel Tournaments — tournament management for padel clubs and federations.*
