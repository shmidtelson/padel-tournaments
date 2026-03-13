'use client';

type Item = { q: string; a: string };

export function FaqAccordion({ items, className = '' }: { items: Item[]; className?: string }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {items.map((item, i) => (
        <details key={i} className="group rounded-xl border border-neutral-200 bg-white shadow-sm">
          <summary className="cursor-pointer list-none px-6 py-4 font-medium text-neutral-900 hover:bg-neutral-50 [&::-webkit-details-marker]:hidden">
            <span className="flex items-center justify-between gap-2">
              {item.q}
              <span className="text-neutral-400 transition group-open:rotate-180">▼</span>
            </span>
          </summary>
          <div className="border-t border-neutral-100 px-6 py-4 text-neutral-600">{item.a}</div>
        </details>
      ))}
    </div>
  );
}
