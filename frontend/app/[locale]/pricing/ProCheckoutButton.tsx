'use client';

import { useState, useEffect } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Org = { id: number; name: string; slug: string; status: string; plan: string };

export function ProCheckoutButton({ locale, ctaText }: { locale: string; ctaText: string }) {
  const [orgs, setOrgs] = useState<Org[]>([]);
  const [selectedId, setSelectedId] = useState<number | ''>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) return;
    fetch(`${API_URL}/organizations`, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => (r.ok ? r.json() : []))
      .then((list: Org[]) => {
        setOrgs(list);
        if (list.length && !selectedId) setSelectedId(list[0].id);
      })
      .catch(() => setOrgs([]));
  }, [selectedId]);

  const handleSubscribe = async () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (!token) {
      setError(locale === 'ru' ? 'Войдите в аккаунт' : 'Please log in');
      return;
    }
    const orgId = selectedId || orgs[0]?.id;
    if (!orgId) {
      setError(locale === 'ru' ? 'Создайте организацию' : 'Create an organization first');
      return;
    }
    setLoading(true);
    setError(null);
    const base = typeof window !== 'undefined' ? window.location.origin : '';
    try {
      const res = await fetch(`${API_URL}/billing/create-checkout-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          organization_id: Number(orgId),
          success_url: `${base}/${locale}/pricing?success=1`,
          cancel_url: `${base}/${locale}/pricing`,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || res.status);
      if (data.url) window.location.href = data.url;
      else throw new Error('No redirect URL');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-8 space-y-3">
      {orgs.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-neutral-700">
            {locale === 'ru' ? 'Организация' : 'Organization'}
          </label>
          <select
            value={selectedId}
            onChange={(e) => setSelectedId(e.target.value ? Number(e.target.value) : '')}
            className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-neutral-900"
          >
            {orgs.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name} {o.plan === 'pro' ? '(Pro)' : ''}
              </option>
            ))}
          </select>
        </div>
      )}
      <button
        type="button"
        onClick={handleSubscribe}
        disabled={loading}
        className="block w-full rounded-lg bg-neutral-900 py-3 text-center font-medium text-white hover:bg-neutral-800 disabled:opacity-50"
      >
        {loading ? (locale === 'ru' ? 'Перенаправление…' : 'Redirecting…') : ctaText}
      </button>
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
}
