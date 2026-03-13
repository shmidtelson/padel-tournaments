import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type BlogPost = {
  id: number;
  slug: string;
  title: string;
  body: string;
  locale: string;
  published_at: string | null;
  created_at: string;
  updated_at: string;
};

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('blog');
  return buildMetadata({
    title: t('title'),
    description: t('description'),
    locale,
    path: 'blog',
  });
}

async function getPosts(locale: string): Promise<BlogPost[]> {
  try {
    const res = await fetch(`${API_URL}/blog?locale=${locale}`, { next: { revalidate: 60 } });
    if (!res.ok) return [];
    return res.json();
  } catch {
    return [];
  }
}

export default async function BlogPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('blog');
  const posts = await getPosts(locale);

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <header className="text-center">
        <h1 className="text-3xl font-bold text-neutral-900">{t('title')}</h1>
        <p className="mt-4 text-lg text-neutral-600">{t('description')}</p>
      </header>
      <ul className="mt-12 space-y-8">
        {posts.length === 0 && (
          <li className="rounded-xl border border-neutral-200 bg-neutral-50 p-8 text-center text-neutral-500">
            Пока нет записей. / No posts yet.
          </li>
        )}
        {posts.map((post) => (
          <li key={post.id} className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-neutral-900">
              <Link href={`/${locale}/blog/${post.slug}`}>{post.title}</Link>
            </h2>
            <p className="mt-2 text-sm text-neutral-500">
              {post.published_at ? new Date(post.published_at).toLocaleDateString(locale) : ''}
            </p>
            <p className="mt-3 line-clamp-2 text-neutral-600">
              {post.body.replace(/<[^>]*>/g, '').slice(0, 200)}…
            </p>
            <Link
              href={`/${locale}/blog/${post.slug}`}
              className="mt-4 inline-block font-medium text-neutral-900 hover:underline"
            >
              {t('readMore')}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
