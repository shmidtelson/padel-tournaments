import { MetadataRoute } from 'next';
import { routing } from '@/i18n/routing';

const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://padel-tournaments.example.com';

const paths = [
  '',
  'contact',
  'how-it-works',
  'pricing',
  'blog',
  'faq',
  'reviews',
  'collaboration',
  'login',
  'register',
  'privacy',
  'terms',
];

export default function sitemap(): MetadataRoute.Sitemap {
  const entries: MetadataRoute.Sitemap = [];
  for (const locale of routing.locales) {
    for (const path of paths) {
      entries.push({
        url: path ? `${baseUrl}/${locale}/${path}` : `${baseUrl}/${locale}`,
        lastModified: new Date(),
        changeFrequency: path === '' ? 'weekly' : 'monthly',
        priority: path === '' ? 1 : 0.8,
      });
    }
  }
  return entries;
}
