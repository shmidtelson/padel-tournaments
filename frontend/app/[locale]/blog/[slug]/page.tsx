import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { buildMetadata } from '@/lib/seo';
import { Link } from '@/components/Link';
import { notFound } from 'next/navigation';

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

type Props = { params: Promise<{ locale: string; slug: string }> };

async function getPost(slug: string): Promise<BlogPost | null> {
  try {
    const res = await fetch(`${API_URL}/blog/${encodeURIComponent(slug)}`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export async function generateMetadata({ params }: Props) {
  const { locale, slug } = await params;
  const post = await getPost(slug);
  if (!post) return { title: 'Post' };
  return buildMetadata({
    title: post.title,
    description: post.body.replace(/<[^>]*>/g, '').slice(0, 160),
    locale,
    path: `blog/${slug}`,
  });
}

export default async function BlogPostPage({ params }: Props) {
  const { locale, slug } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('blog');
  const post = await getPost(slug);
  if (!post) notFound();

  return (
    <article className="mx-auto max-w-3xl px-4 py-16">
      <Link href={`/${locale}/blog`} className="text-sm text-neutral-500 hover:text-neutral-900">
        ← {t('backToList')}
      </Link>
      <header className="mt-6">
        <h1 className="text-3xl font-bold text-neutral-900">{post.title}</h1>
        <p className="mt-2 text-sm text-neutral-500">
          {post.published_at ? new Date(post.published_at).toLocaleDateString(locale) : ''}
        </p>
      </header>
      <div
        className="prose prose-neutral mt-8 max-w-none"
        dangerouslySetInnerHTML={{ __html: post.body }}
      />
    </article>
  );
}
