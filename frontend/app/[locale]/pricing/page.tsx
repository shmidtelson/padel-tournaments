import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';
import { ProCheckoutButton } from './ProCheckoutButton';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('pricing');
  return buildMetadata({
    title: t('title'),
    description: t('description'),
    locale,
    path: 'pricing',
  });
}

export default async function PricingPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('pricing');

  return (
    <div className="mx-auto max-w-5xl px-4 py-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900">{t('title')}</h1>
        <p className="mt-4 text-lg text-neutral-600">{t('description')}</p>
      </header>

      <div className="mt-16 grid gap-8 sm:grid-cols-2">
        <article
          className="rounded-2xl border border-neutral-200 bg-white p-8 shadow-sm"
          aria-labelledby="plan-free"
        >
          <h2 id="plan-free" className="text-xl font-semibold text-neutral-900">
            {t('freeTitle')}
          </h2>
          <p className="mt-4">
            <span className="text-3xl font-bold text-neutral-900">{t('freePrice')}</span>
            <span className="text-neutral-600"> {t('freePeriod')}</span>
          </p>
          <ul className="mt-6 space-y-3 text-neutral-600" role="list">
            {(
              [
                'freeFeature1',
                'freeFeature2',
                'freeFeature3',
                'freeFeature4',
                'freeFeature5',
              ] as const
            ).map((key, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-green-600" aria-hidden>
                  ✓
                </span>
                <span>{t(key)}</span>
              </li>
            ))}
          </ul>
          <div className="mt-8">
            <Link
              href={`/${locale}/register`}
              className="block w-full rounded-lg border-2 border-neutral-900 py-3 text-center font-medium text-neutral-900 hover:bg-neutral-50"
            >
              {t('ctaFree')}
            </Link>
          </div>
        </article>

        <article
          className="rounded-2xl border-2 border-neutral-900 bg-neutral-50 p-8 shadow-sm"
          aria-labelledby="plan-pro"
        >
          <h2 id="plan-pro" className="text-xl font-semibold text-neutral-900">
            {t('proTitle')}
          </h2>
          <p className="mt-4">
            <span className="text-2xl font-bold text-neutral-900">{t('proPrice')}</span>
            {t('proPeriod') && <span className="text-neutral-600"> {t('proPeriod')}</span>}
          </p>
          <ul className="mt-6 space-y-3 text-neutral-600" role="list">
            {(['proFeature1', 'proFeature2', 'proFeature3', 'proFeature4'] as const).map(
              (key, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-green-600" aria-hidden>
                    ✓
                  </span>
                  <span>{t(key)}</span>
                </li>
              )
            )}
          </ul>
          <div className="mt-8">
            <ProCheckoutButton locale={locale} ctaText={t('ctaProSubscribe')} />
            <p className="mt-2 text-center text-sm text-neutral-500">
              <Link href={`/${locale}/contact`} className="hover:underline">
                {t('ctaPro')}
              </Link>
            </p>
          </div>
        </article>
      </div>
    </div>
  );
}
