import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { AdminStatsBlock } from '../AdminStatsBlock';

type Props = { params: Promise<{ locale: string }> };

export default async function AdminStatsPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('admin');
  return (
    <div>
      <h1 className="text-2xl font-bold text-neutral-900">{t('stats')}</h1>
      <p className="mt-2 text-neutral-600">
        Доступ только для суперпользователя. Требуется авторизация (Bearer token). / Superuser only.
        Auth required.
      </p>
      <AdminStatsBlock />
    </div>
  );
}
