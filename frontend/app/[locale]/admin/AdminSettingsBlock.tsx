'use client';

import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const KEYS = [
  'maintenance_mode',
  'registration_enabled',
  'default_locale',
  'max_tournaments_per_month_free',
  'max_organizations_per_user',
  'site_name',
  'contact_email',
];

export function AdminSettingsBlock() {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    fetch(`${API_URL}/admin/settings`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((r) => {
        if (!r.ok) throw new Error(r.status === 403 ? 'Forbidden' : `${r.status}`);
        return r.json();
      })
      .then((data: { settings: Record<string, string> }) => setSettings(data.settings || {}))
      .catch((e) => setError(e.message));
  }, []);

  const handleSave = () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    fetch(`${API_URL}/admin/settings`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ settings }),
    })
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status}`);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      })
      .catch((e) => setError(e.message));
  };

  if (error) {
    return (
      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-800">
        {error}. Войдите как суперпользователь. / Log in as superuser.
      </div>
    );
  }

  return (
    <div className="mt-6 rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
      <div className="space-y-4">
        {KEYS.map((key) => (
          <div key={key} className="flex flex-col gap-1">
            <label className="text-sm font-medium text-neutral-700">{key}</label>
            <input
              type="text"
              value={settings[key] ?? ''}
              onChange={(e) => setSettings((s) => ({ ...s, [key]: e.target.value }))}
              className="rounded border border-neutral-300 px-3 py-2 text-neutral-900"
            />
          </div>
        ))}
      </div>
      <div className="mt-6 flex items-center gap-4">
        <button
          type="button"
          onClick={handleSave}
          className="rounded-lg bg-neutral-900 px-4 py-2 text-white hover:bg-neutral-800"
        >
          Сохранить / Save
        </button>
        {saved && <span className="text-green-600">Сохранено / Saved</span>}
      </div>
    </div>
  );
}
