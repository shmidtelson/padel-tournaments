import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';
import { ContactForm } from './ContactForm';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('contact');
  return buildMetadata({
    title: t('title'),
    description: t('description'),
    locale,
    path: 'contact',
  });
}

export default async function ContactPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('contact');

  return (
    <div className="mx-auto max-w-2xl px-4 py-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900">{t('title')}</h1>
        <p className="mt-4 text-neutral-600">{t('description')}</p>
      </header>
      <div className="mt-10">
        <ContactForm />
      </div>
      <p className="mt-8 text-center text-sm text-neutral-500">
        <Link href={`/${locale}`} className="hover:text-neutral-700">
          ← {locale === 'ru' ? 'На главную' : 'Back to home'}
        </Link>
      </p>
    </div>
  );
}
