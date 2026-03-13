import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('nav');
  return buildMetadata({
    title: t('login'),
    description:
      locale === 'ru' ? 'Вход в аккаунт Padel Tournaments' : 'Log in to Padel Tournaments',
    locale,
    path: 'login',
  });
}

export default async function LoginPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('nav');

  return (
    <div className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold text-neutral-900">{t('login')}</h1>
      <p className="mt-4 text-neutral-600">
        {locale === 'ru' ? 'Страница входа (в разработке).' : 'Login page (coming soon).'}
      </p>
      <p className="mt-6">
        <Link href={`/${locale}`} className="text-neutral-900 underline hover:no-underline">
          ← {locale === 'ru' ? 'На главную' : 'Back'}
        </Link>
      </p>
    </div>
  );
}
