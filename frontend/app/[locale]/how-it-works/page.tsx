import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('howItWorks');
  return buildMetadata({
    title: t('title'),
    description: t('description'),
    locale,
    path: 'how-it-works',
  });
}

export default async function HowItWorksPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('howItWorks');

  const steps = [
    { key: 'step1', num: 1 },
    { key: 'step2', num: 2 },
    { key: 'step3', num: 3 },
    { key: 'step4', num: 4 },
    { key: 'step5', num: 5 },
  ] as const;

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900">{t('title')}</h1>
        <p className="mt-4 text-lg text-neutral-600">{t('description')}</p>
      </header>

      <ol className="mt-16 space-y-12" aria-label={t('title')}>
        {steps.map(({ key, num }) => (
          <li key={key} className="relative flex gap-6">
            <span
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-neutral-900 text-sm font-semibold text-white"
              aria-hidden
            >
              {num}
            </span>
            <div>
              <h2 className="text-xl font-semibold text-neutral-900">{t(`${key}Title`)}</h2>
              <p className="mt-2 text-neutral-600">{t(`${key}Text`)}</p>
            </div>
          </li>
        ))}
      </ol>

      <p className="mt-12 text-center">
        <Link
          href={`/${locale}/register`}
          className="rounded-lg bg-neutral-900 px-6 py-3 text-white hover:bg-neutral-800"
        >
          {locale === 'ru' ? 'Начать бесплатно' : 'Get started for free'}
        </Link>
      </p>
    </div>
  );
}
