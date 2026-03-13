'use client';

import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type Stats = {
  users_total: number;
  users_superusers: number;
  organizations_total: number;
  organizations_pending: number;
  organizations_approved: number;
  organizations_rejected: number;
  tournaments_total: number;
  players_total: number;
  rounds_total: number;
  matches_total: number;
};

export function AdminStatsBlock() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    fetch(`${API_URL}/admin/stats`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((r) => {
        if (!r.ok)
          throw new Error(r.status === 403 ? 'Forbidden (need SuperAdmin)' : ` ${r.status}`);
        return r.json();
      })
      .then(setStats)
      .catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-6 text-amber-800">
        {error}. Войдите как суперпользователь и обновите страницу. / Log in as superuser and
        refresh.
      </div>
    );
  }
  if (!stats) {
    return <div className="mt-6 text-neutral-500">Загрузка… / Loading…</div>;
  }

  const t = {
    usersTotal: 'Пользователей всего',
    usersSuperusers: 'Суперпользователей',
    organizationsTotal: 'Организаций всего',
    organizationsPending: 'На модерации',
    organizationsApproved: 'Одобрено',
    organizationsRejected: 'Отклонено',
    tournamentsTotal: 'Турниров',
    playersTotal: 'Участников',
    roundsTotal: 'Раундов',
    matchesTotal: 'Матчей',
  };

  return (
    <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <StatCard label={t.usersTotal} value={stats.users_total} />
      <StatCard label={t.usersSuperusers} value={stats.users_superusers} />
      <StatCard label={t.organizationsTotal} value={stats.organizations_total} />
      <StatCard label={t.organizationsPending} value={stats.organizations_pending} />
      <StatCard label={t.organizationsApproved} value={stats.organizations_approved} />
      <StatCard label={t.organizationsRejected} value={stats.organizations_rejected} />
      <StatCard label={t.tournamentsTotal} value={stats.tournaments_total} />
      <StatCard label={t.playersTotal} value={stats.players_total} />
      <StatCard label={t.roundsTotal} value={stats.rounds_total} />
      <StatCard label={t.matchesTotal} value={stats.matches_total} />
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-neutral-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-neutral-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-neutral-900">{value}</p>
    </div>
  );
}
