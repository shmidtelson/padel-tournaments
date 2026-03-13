import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('home');
  return buildMetadata({
    title: t('title'),
    description: t('description'),
    locale,
  });
}

export default async function HomePage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('home');

  return (
    <div className="mx-auto max-w-6xl px-4 py-16">
      <section className="text-center" aria-labelledby="hero-heading">
        <h1
          id="hero-heading"
          className="text-4xl font-bold tracking-tight text-neutral-900 sm:text-5xl md:text-6xl"
        >
          {t('title')}
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-neutral-600">{t('description')}</p>
        <div className="mt-10">
          <Link
            href={`/${locale}/register`}
            className="inline-flex rounded-lg bg-neutral-900 px-6 py-3 text-base font-medium text-white hover:bg-neutral-800 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:ring-offset-2"
          >
            {t('cta')}
          </Link>
        </div>
      </section>

      <section className="mt-24" aria-labelledby="features-heading">
        <h2 id="features-heading" className="text-center text-2xl font-semibold text-neutral-900">
          {t('featuresTitle')}
        </h2>
        <ul className="mx-auto mt-12 grid max-w-4xl gap-8 sm:grid-cols-3">
          <li className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
            <h3 className="font-semibold text-neutral-900">{t('feature1Title')}</h3>
            <p className="mt-2 text-sm text-neutral-600">{t('feature1Text')}</p>
          </li>
          <li className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
            <h3 className="font-semibold text-neutral-900">{t('feature2Title')}</h3>
            <p className="mt-2 text-sm text-neutral-600">{t('feature2Text')}</p>
          </li>
          <li className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
            <h3 className="font-semibold text-neutral-900">{t('feature3Title')}</h3>
            <p className="mt-2 text-sm text-neutral-600">{t('feature3Text')}</p>
          </li>
        </ul>
      </section>
    </div>
  );
}
