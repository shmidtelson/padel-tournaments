# Padel Tournaments — Frontend

Next.js 14 (App Router), Tailwind CSS, next-intl (ru/en).

## Страницы

- **Главная** (`/[locale]`) — герой, блок преимуществ, CTA.
- **Связаться с нами** (`/[locale]/contact`) — форма обратной связи.
- **Как это работает** (`/[locale]/how-it-works`) — пошаговое описание.
- **Тарифы** (`/[locale]/pricing`) — бесплатный и Pro.
- **Отзывы** (`/[locale]/reviews`) — цитаты клубов и федераций.
- **Коллаборация** (`/[locale]/collaboration`) — партнёрство с клубами, федерациями, спонсорами.
- Заглушки: **Вход**, **Регистрация**, **Конфиденциальность**, **Условия использования**.

## SEO

- У каждой страницы свой `generateMetadata`: `title`, `description`, `canonical`, `alternates.languages` (ru/en), **Open Graph** и **Twitter**.
- Единая база в `lib/seo.ts` и переменная окружения `NEXT_PUBLIC_SITE_URL`.
- **Sitemap** (`/sitemap.xml`) и **robots** (`/robots.txt`).
- Семантика: один `h1` на страницу, секции с `aria-labelledby`, списки и цитаты по смыслу.

## Запуск

```bash
cd frontend
npm install
npm run dev
```

По умолчанию: `http://localhost:3000` → редирект на `/ru`.

## Sentry

При заданном **NEXT_PUBLIC_SENTRY_DSN** в `.env.local` ошибки и трейсы (клиент и сервер) отправляются в Sentry. Опционально: **NEXT_PUBLIC_SENTRY_ENVIRONMENT**. Инициализация: клиент — `sentry.client.config.ts`, сервер и edge — `instrumentation.ts`. Глобальные ошибки рендера перехватывает `app/global-error.tsx`. Для загрузки source maps при сборке задайте **SENTRY_AUTH_TOKEN** (и при необходимости **SENTRY_ORG**, **SENTRY_PROJECT**).

## TypeScript, ESLint, Prettier

- **TypeScript** — включён (`tsconfig.json`, `strict: true`). Все компоненты и страницы в `.ts`/`.tsx`.
- **ESLint** — конфиг в `.eslintrc.json`: `next/core-web-vitals`, `next/typescript`, `prettier` (отключает конфликтующие правила).
  - `npm run lint` — проверка
  - `npm run lint:fix` — автоисправление
- **Prettier** — настройки в `.prettierrc` (single quotes, trailing comma, print width 100).
  - `npm run format` — форматировать все файлы
  - `npm run format:check` — проверить без изменений (удобно для CI)
