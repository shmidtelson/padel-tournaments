import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('collaboration');
  return buildMetadata({
    title: t('title'),
    description: t('description'),
    locale,
    path: 'collaboration',
  });
}

export default async function CollaborationPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('collaboration');

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900">{t('title')}</h1>
        <p className="mt-4 text-lg text-neutral-600">{t('description')}</p>
      </header>

      <div className="mt-16 space-y-12">
        <section aria-labelledby="collab-clubs">
          <h2 id="collab-clubs" className="text-xl font-semibold text-neutral-900">
            {t('clubsTitle')}
          </h2>
          <p className="mt-3 text-neutral-600">{t('clubsText')}</p>
        </section>
        <section aria-labelledby="collab-federations">
          <h2 id="collab-federations" className="text-xl font-semibold text-neutral-900">
            {t('federationsTitle')}
          </h2>
          <p className="mt-3 text-neutral-600">{t('federationsText')}</p>
        </section>
        <section aria-labelledby="collab-sponsors">
          <h2 id="collab-sponsors" className="text-xl font-semibold text-neutral-900">
            {t('sponsorsTitle')}
          </h2>
          <p className="mt-3 text-neutral-600">{t('sponsorsText')}</p>
        </section>
      </div>

      <p className="mt-16 text-center">
        <Link
          href={`/${locale}/contact`}
          className="inline-flex rounded-lg bg-neutral-900 px-6 py-3 font-medium text-white hover:bg-neutral-800"
        >
          {t('cta')}
        </Link>
      </p>
    </div>
  );
}
