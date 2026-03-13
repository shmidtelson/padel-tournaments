import { getTranslations } from 'next-intl/server';
import { setRequestLocale } from 'next-intl/server';
import { AdminSettingsBlock } from '../AdminSettingsBlock';

type Props = { params: Promise<{ locale: string }> };

export default async function AdminSettingsPage({ params }: Props) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations('admin');
  return (
    <div>
      <h1 className="text-2xl font-bold text-neutral-900">{t('settings')}</h1>
      <p className="mt-2 text-neutral-600">
        Настройки сайта (только SuperAdmin). / Site options (SuperAdmin only).
      </p>
      <AdminSettingsBlock />
    </div>
  );
}
