'use client';

import { cn } from '@/lib/utils';

interface FilePaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const navButtonClass =
  'flex size-9 items-center justify-center rounded-lg border-2 border-ink bg-white text-ink transition-all duration-100 hover:-translate-y-0.5 hover:shadow-brutal-xs disabled:pointer-events-none disabled:opacity-30';

export function FilePagination({ page, totalPages, onPageChange }: FilePaginationProps) {
  return (
    <div className="flex items-center justify-between gap-3 border-t-2 border-ink px-5 py-3.5">
      <span className="font-mono text-[11px] font-bold uppercase tracking-[0.15em] text-ink/60">
        Страница {page} / {totalPages}
      </span>

      <div className="flex items-center gap-2">
        <button
          type="button"
          aria-label="Назад"
          disabled={page <= 1}
          onClick={() => onPageChange(Math.max(1, page - 1))}
          className={navButtonClass}
        >
          <svg viewBox="0 0 20 20" fill="currentColor" className="size-4" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M12.78 5.22a.75.75 0 010 1.06L9.06 10l3.72 3.72a.75.75 0 11-1.06 1.06L7.44 10.53a.75.75 0 010-1.06l4.28-4.28a.75.75 0 011.06 0z"
              clipRule="evenodd"
            />
          </svg>
        </button>

        <div className="flex items-center gap-2">
          {[page - 1, page, page + 1]
            .filter((p) => p >= 1 && p <= totalPages)
            .map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => onPageChange(p)}
                aria-current={p === page ? 'page' : undefined}
                className={cn(
                  'flex size-9 items-center justify-center rounded-lg border-2 border-ink font-mono text-sm font-bold transition-all duration-100',
                  p === page
                    ? 'bg-ink text-paper shadow-brutal-xs'
                    : 'bg-white text-ink hover:-translate-y-0.5 hover:shadow-brutal-xs',
                )}
              >
                {p}
              </button>
            ))}
        </div>

        <button
          type="button"
          aria-label="Вперёд"
          disabled={page >= totalPages}
          onClick={() => onPageChange(Math.min(totalPages, page + 1))}
          className={navButtonClass}
        >
          <svg viewBox="0 0 20 20" fill="currentColor" className="size-4" aria-hidden="true">
            <path
              fillRule="evenodd"
              d="M8.22 5.22a.75.75 0 011.06 0l4.28 4.28a.75.75 0 010 1.06l-4.28 4.28a.75.75 0 11-1.06-1.06L11.94 10 8.22 6.28a.75.75 0 010-1.06z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
