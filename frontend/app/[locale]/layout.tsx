import { Link } from '@/components/Link';
import { getTranslations } from 'next-intl/server';

type Props = { children: React.ReactNode; params: Promise<{ locale: string }> };

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;
  const t = await getTranslations('nav');
  const tFooter = await getTranslations('footer');
  const isEn = locale === 'en';

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-neutral-200 bg-white/95 backdrop-blur">
        <nav
          className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4"
          aria-label="Main"
        >
          <Link href={`/${locale}`} className="text-xl font-semibold text-neutral-900">
            Padel Tournaments
          </Link>
          <ul className="flex flex-wrap items-center gap-6">
            <li>
              <Link href={`/${locale}`} className="text-neutral-600 hover:text-neutral-900">
                {t('home')}
              </Link>
            </li>
            <li>
              <Link
                href={`/${locale}/how-it-works`}
                className="text-neutral-600 hover:text-neutral-900"
              >
                {t('howItWorks')}
              </Link>
            </li>
            <li>
              <Link href={`/${locale}/pricing`} className="text-neutral-600 hover:text-neutral-900">
                {t('pricing')}
              </Link>
            </li>
            <li>
              <Link href={`/${locale}/blog`} className="text-neutral-600 hover:text-neutral-900">
                {t('blog')}
              </Link>
            </li>
            <li>
              <Link href={`/${locale}/faq`} className="text-neutral-600 hover:text-neutral-900">
                {t('faq')}
              </Link>
            </li>
            <li>
              <Link href={`/${locale}/reviews`} className="text-neutral-600 hover:text-neutral-900">
                {t('reviews')}
              </Link>
            </li>
            <li>
              <Link
                href={`/${locale}/collaboration`}
                className="text-neutral-600 hover:text-neutral-900"
              >
                {t('collaboration')}
              </Link>
            </li>
            <li>
              <Link href={`/${locale}/contact`} className="text-neutral-600 hover:text-neutral-900">
                {t('contact')}
              </Link>
            </li>
            <li>
              <Link
                href={`/${locale}/admin`}
                className="text-neutral-500 hover:text-neutral-700 text-sm"
              >
                {t('admin')}
              </Link>
            </li>
            <li className="flex items-center gap-2">
              <Link
                href={isEn ? '/ru' : '/en'}
                className="text-sm text-neutral-500 hover:text-neutral-700"
              >
                {isEn ? 'RU' : 'EN'}
              </Link>
              <span className="text-neutral-300">|</span>
              <Link href={`/${locale}/login`} className="text-neutral-600 hover:text-neutral-900">
                {t('login')}
              </Link>
              <Link
                href={`/${locale}/register`}
                className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm text-white hover:bg-neutral-800"
              >
                {t('register')}
              </Link>
            </li>
          </ul>
        </nav>
      </header>
      <main className="min-h-[calc(100vh-8rem)]">{children}</main>
      <footer className="border-t border-neutral-200 bg-neutral-100">
        <div className="mx-auto max-w-6xl px-4 py-10">
          <div className="grid gap-8 sm:grid-cols-3">
            <div>
              <h3 className="font-semibold text-neutral-900">{tFooter('product')}</h3>
              <ul className="mt-2 space-y-1 text-sm text-neutral-600">
                <li>
                  <Link href={`/${locale}/how-it-works`}>{t('howItWorks')}</Link>
                </li>
                <li>
                  <Link href={`/${locale}/pricing`}>{t('pricing')}</Link>
                </li>
                <li>
                  <Link href={`/${locale}/blog`}>{t('blog')}</Link>
                </li>
                <li>
                  <Link href={`/${locale}/faq`}>{t('faq')}</Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">{tFooter('company')}</h3>
              <ul className="mt-2 space-y-1 text-sm text-neutral-600">
                <li>
                  <Link href={`/${locale}/contact`}>{t('contact')}</Link>
                </li>
                <li>
                  <Link href={`/${locale}/collaboration`}>{t('collaboration')}</Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-neutral-900">{tFooter('legal')}</h3>
              <ul className="mt-2 space-y-1 text-sm text-neutral-600">
                <li>
                  <Link href={`/${locale}/privacy`}>{tFooter('privacy')}</Link>
                </li>
                <li>
                  <Link href={`/${locale}/terms`}>{tFooter('terms')}</Link>
                </li>
              </ul>
            </div>
          </div>
          <p className="mt-8 text-center text-sm text-neutral-500">
            © {new Date().getFullYear()} Padel Tournaments. Open Source.
          </p>
        </div>
      </footer>
    </>
  );
}
