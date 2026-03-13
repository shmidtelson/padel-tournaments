import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('reviews');
  return buildMetadata({
    title: t('title'),
    description: t('description'),
    locale,
    path: 'reviews',
  });
}

export default async function ReviewsPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('reviews');

  const reviews = [
    { quote: 'review1Quote', author: 'review1Author' },
    { quote: 'review2Quote', author: 'review2Author' },
    { quote: 'review3Quote', author: 'review3Author' },
  ] as const;

  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900">{t('title')}</h1>
        <p className="mt-4 text-lg text-neutral-600">{t('description')}</p>
      </header>

      <ul className="mt-16 space-y-10" role="list">
        {reviews.map(({ quote, author }, i) => (
          <li key={i} className="rounded-xl border border-neutral-200 bg-white p-8 shadow-sm">
            <blockquote className="text-lg text-neutral-700">«{t(quote)}»</blockquote>
            <cite className="mt-4 block not-italic text-neutral-500">— {t(author)}</cite>
          </li>
        ))}
      </ul>

      <p className="mt-12 text-center">
        <Link href={`/${locale}/contact`} className="text-neutral-900 underline hover:no-underline">
          {locale === 'ru' ? 'Написать отзыв' : 'Submit a review'}
        </Link>
      </p>
    </div>
  );
}
