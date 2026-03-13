import type { Metadata } from 'next';

const siteName = 'Padel Tournaments';
const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://padel-tournaments.example.com';

type Params = {
  title: string;
  description: string;
  locale: string;
  path?: string;
  noIndex?: boolean;
};

export function buildMetadata({
  title,
  description,
  locale,
  path = '',
  noIndex,
}: Params): Metadata {
  const url = `${baseUrl}/${locale}${path ? `/${path}` : ''}`;
  const canonical = path ? `${baseUrl}/${locale}/${path}` : `${baseUrl}/${locale}`;

  return {
    title: `${title} | ${siteName}`,
    description,
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: canonical,
      languages: {
        ru: `${baseUrl}/ru${path ? `/${path}` : ''}`,
        en: `${baseUrl}/en${path ? `/${path}` : ''}`,
      },
    },
    openGraph: {
      title: `${title} | ${siteName}`,
      description,
      url,
      siteName,
      locale: locale === 'ru' ? 'ru_RU' : 'en_US',
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: `${title} | ${siteName}`,
      description,
    },
    robots: noIndex ? { index: false, follow: true } : undefined,
  };
}
