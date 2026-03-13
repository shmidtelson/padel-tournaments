# First MVP Readiness — Padel Tournaments

**Focus:** what is ready for MVP launch, what is missing for the first release, what can be deferred.

---

## MVP summary

**For the first MVP, the main gap is on the frontend:** working login/register pages and a basic organizer area (list of organizations, create tournament, manage participants/rounds). Backend and infrastructure are MVP-ready when the checklist is followed (env, migrations, health).

---

## 1. Ready for MVP ✅

### Backend
- Register/login/refresh via API, JWT, roles (SuperAdmin, Owner, Admin, Player).
- Organizations: create, moderation (superuser), members (Owner adds Admin).
- Tournaments: CRUD, players, rounds, matches, Americano/Mexicano, leaderboard, SSE.
- Billing: Stripe Checkout for Pro, webhook, URL validation.
- Admin: site settings, stats, blog CRUD. Public: post list, post by slug.
- Contact: `POST /contact`, website form submits to API.
- Security: SECRET_KEY/CORS checks when `DEBUG=false`, password and URL validation.
- Health: `/health`, `/health/ready` (DB). Logging and `X-Request-ID`.
- Migrations: Alembic, initial migration. In deploy: `alembic upgrade head`.
- Tests: pytest (health, auth validation, contact, billing 401).

### Frontend
- Marketing: home, how it works, pricing, reviews, collaboration, contact (form works), blog, FAQ.
- SEO, sitemap, robots, i18n (ru/en).
- Admin (stats, settings) and pricing with Stripe button — work when token is in `localStorage`.
- Privacy/Terms — placeholders (“Content to be added”).

### Infrastructure
- Docker Compose (Postgres 5433, Procrastinate worker). Sentry (backend + frontend). Private OpenAPI by key.

---

## 2. Missing for first MVP ❌

| # | Item | Why for MVP |
|---|------|-------------|
| 1 | **Login and Register pages with forms** | Currently placeholders (“coming soon”). Need forms: email + password, call `POST /auth/register` and `POST /auth/login`, store token (e.g. in `localStorage`), redirect to dashboard or organization list. Without this, users cannot sign in and become organizers. |
| 2 | **Organizer dashboard (minimum)** | After login, user should see their organizations and be able to: create organization (API call), open org and create tournament, add players, generate round, enter score. This does not exist on the frontend yet — only marketing and admin. At least: “My organizations” page + “Organization tournaments” + tournament creation form and basic grid/leaderboard. |
| 3 | **TV display page** | Planned “display mode for in-club screen”. Backend provides SSE and tournament data. Need at least one page (e.g. `/[locale]/tournaments/[id]/display`) with large display of current round and score table, subscribed to SSE. Without it, the venue cannot show the grid on screen. |
| 4 | **Minimal Privacy and Terms text** | Currently “Content to be added”. For MVP, one short paragraph each is enough (what data we collect, what we do with it; terms of use), or an explicit “Draft” label and date. Needed for trust and when accepting payments. |

**Summary:** Items **1 and 2** are required (login/register + basic organizer area and tournaments). Items 3 and 4 are recommended for a “full” first launch; 3 can be replaced by a temporary link to a public tournament, 4 by short text or a draft.

---

## 3. Can be deferred until after MVP ⏸

| Area | What | When |
|------|------|------|
| Rate limiting | Throttle `/auth/register`, `/auth/login` | After MVP when load or abuse grows. |
| CI/CD | Automated tests, deploy on commit | When you have a stable release process. |
| Frontend tests | E2E (Playwright) or component tests | After core flows are stable. |
| Full Privacy/Terms | Legally reviewed texts | Before scaling or when required. |
| Production Dockerfile | Backend/frontend image for deploy | If deploying with Docker. |
| Advanced formats | Round Robin, Single/Double Elimination (planned) | After validating Americano/Mexicano in real tournaments. |

---

## 4. Pre-launch MVP checklist

- [ ] **Backend env:** `DEBUG=false`, `SECRET_KEY` (≥32 chars), `CORS_ORIGINS`, `ALLOWED_FRONTEND_BASE_URL` (if Stripe enabled), `DATABASE_URL`, and Stripe/Sentry if needed.
- [ ] **Migrations:** run `uv run alembic upgrade head` in deploy before starting the app.
- [ ] **Health:** orchestrator/load balancer uses `GET /health/ready` for readiness.
- [ ] **Frontend env:** `NEXT_PUBLIC_API_URL` points to production API.
- [ ] **Superuser:** one user in DB has `is_superuser = true` for organization moderation and admin access.
- [ ] **MVP implemented:** Login/Register pages with API calls and token storage; basic organizer area (organizations + tournaments + players + rounds/scores); optionally TV display page and short Privacy/Terms.

---

## 5. Files and roles (summary)

- **Backend README** — Production checklist and DB backup note.
- **Roles:** SuperAdmin (moderation, admin), Owner (adds Admin, Pro subscription), Admin (tournaments, scoring), Player (participate in tournaments).
- **Deploy:** bring up Postgres, run migrations, set env, start API and (separately) frontend; optionally Procrastinate worker.

---

*MVP readiness audit; update as features and requirements change.*
