import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const title = locale === 'ru' ? 'Конфиденциальность' : 'Privacy';
  return buildMetadata({
    title,
    description:
      locale === 'ru'
        ? 'Политика конфиденциальности Padel Tournaments'
        : 'Padel Tournaments privacy policy',
    locale,
    path: 'privacy',
  });
}

export default async function PrivacyPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);

  return (
    <div className="mx-auto max-w-2xl px-4 py-16">
      <h1 className="text-3xl font-bold text-neutral-900">
        {locale === 'ru' ? 'Конфиденциальность' : 'Privacy Policy'}
      </h1>
      <p className="mt-6 text-neutral-600">
        {locale === 'ru' ? 'Содержимое страницы будет добавлено.' : 'Content to be added.'}
      </p>
      <p className="mt-8">
        <Link href={`/${locale}`} className="text-neutral-900 underline hover:no-underline">
          ← {locale === 'ru' ? 'На главную' : 'Back'}
        </Link>
      </p>
    </div>
  );
}
