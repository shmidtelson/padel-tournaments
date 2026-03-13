# Padel Tournaments — Frontend

Next.js 14 (App Router), Tailwind CSS, next-intl (ru/en).

## Pages

- **Home** (`/[locale]`) — hero, benefits block, CTA.
- **Contact** (`/[locale]/contact`) — contact form.
- **How it works** (`/[locale]/how-it-works`) — step-by-step description.
- **Pricing** (`/[locale]/pricing`) — Free and Pro plans.
- **Reviews** (`/[locale]/reviews`) — quotes from clubs and federations.
- **Collaboration** (`/[locale]/collaboration`) — partnership with clubs, federations, sponsors.
- Placeholders: **Login**, **Register**, **Privacy**, **Terms of use**.

## SEO

- Each page has its own `generateMetadata`: `title`, `description`, `canonical`, `alternates.languages` (ru/en), **Open Graph** and **Twitter**.
- Shared helpers in `lib/seo.ts` and env var `NEXT_PUBLIC_SITE_URL`.
- **Sitemap** (`/sitemap.xml`) and **robots** (`/robots.txt`).
- Semantics: one `h1` per page, sections with `aria-labelledby`, lists and quotes used meaningfully.

## Run

```bash
cd frontend
npm install
npm run dev
```

By default: `http://localhost:3000` redirects to `/ru`.

## Sentry

When **NEXT_PUBLIC_SENTRY_DSN** is set in `.env.local`, errors and traces (client and server) are sent to Sentry. Optional: **NEXT_PUBLIC_SENTRY_ENVIRONMENT**. Setup: client — `sentry.client.config.ts`, server and edge — `instrumentation.ts`. Global render errors are caught in `app/global-error.tsx`. For source map upload on build, set **SENTRY_AUTH_TOKEN** (and **SENTRY_ORG**, **SENTRY_PROJECT** if needed).

## TypeScript, ESLint, Prettier

- **TypeScript** — enabled (`tsconfig.json`, `strict: true`). All components and pages in `.ts`/`.tsx`.
- **ESLint** — config in `.eslintrc.json`: `next/core-web-vitals`, `next/typescript`, `prettier` (disables conflicting rules).
  - `npm run lint` — check
  - `npm run lint:fix` — auto-fix
- **Prettier** — config in `.prettierrc` (single quotes, trailing comma, print width 100).
  - `npm run format` — format all files
  - `npm run format:check` — check without writing (handy for CI)
