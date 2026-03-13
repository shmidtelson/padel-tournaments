import { getTranslations } from 'next-intl/server';
import { Link } from '@/components/Link';

type Props = { children: React.ReactNode; params: Promise<{ locale: string }> };

export default async function AdminLayout({ children, params }: Props) {
  const { locale } = await params;
  const tAdmin = await getTranslations('admin');

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <nav className="mb-8 flex gap-4 border-b border-neutral-200 pb-4">
        <Link href={`/${locale}/admin`} className="font-medium text-neutral-900 hover:underline">
          {tAdmin('title')}
        </Link>
        <Link href={`/${locale}/admin/stats`} className="text-neutral-600 hover:text-neutral-900">
          {tAdmin('stats')}
        </Link>
        <Link
          href={`/${locale}/admin/settings`}
          className="text-neutral-600 hover:text-neutral-900"
        >
          {tAdmin('settings')}
        </Link>
      </nav>
      {children}
    </div>
  );
}
