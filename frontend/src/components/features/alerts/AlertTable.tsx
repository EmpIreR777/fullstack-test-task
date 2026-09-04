'use client';

import { useAlerts } from '@/hooks/useAlerts';
import { Badge } from '@/components/ui/Badge';
import { Spinner } from '@/components/ui/Spinner';
import { Button } from '@/components/ui/Button';
import { formatDate } from '@/lib/utils';
import { AlertSearchBar } from './AlertSearchBar';
import { FilePagination } from '@/components/features/files/FilePagination';
import { useEffect, useState } from 'react';

function getLevelVariant(level: string): 'danger' | 'warning' | 'success' | 'default' {
  if (level === 'critical') return 'danger';
  if (level === 'warning') return 'warning';
  if (level === 'info') return 'success';
  return 'default';
}

const COLUMNS = ['ID', 'File ID', 'Уровень', 'Сообщение', 'Дата'];

export function AlertTable() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);

  const normalizedQuery = query.trim();

  const { data, isLoading, isError, refetch } = useAlerts({
    page,
    query: normalizedQuery || undefined,
  });

  const searchedAlerts = data?.items ?? [];
  const totalPages = data?.total_pages ?? 1;

  useEffect(() => {
    if (!isLoading && searchedAlerts.length === 0 && page > 1) {
      setPage(1);
    }
  }, [isLoading, searchedAlerts.length, page]);

  return (
    <section className="overflow-hidden rounded-2xl border-2 border-ink bg-white shadow-brutal">
      <div className="flex flex-col gap-4 border-b-2 border-ink px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <h2 className="font-display text-lg font-extrabold uppercase tracking-tight">
            Алерты безопасности
          </h2>
          <span className="rounded-full border-2 border-ink bg-coral px-2.5 py-0.5 font-mono text-xs font-bold shadow-brutal-xs">
            {data?.total ?? 0}
          </span>
        </div>

        <AlertSearchBar
          value={query}
          onChange={(v) => {
            setQuery(v);
            setPage(1);
          }}
          onClear={() => {
            setQuery('');
            setPage(1);
          }}
          count={searchedAlerts.length}
        />

        <div className="flex items-center gap-2 lg:justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => void refetch()}
            title="Обновить список алертов"
          >
            <svg viewBox="0 0 20 20" fill="currentColor" className="size-4" aria-hidden="true">
              <path
                fillRule="evenodd"
                d="M15.312 11.424a5.5 5.5 0 01-9.201 2.466l-.312-.311h2.433a.75.75 0 000-1.5H3.989a.75.75 0 00-.75.75v4.242a.75.75 0 001.5 0v-2.43l.31.31a7 7 0 0011.712-3.138.75.75 0 00-1.449-.39zm1.23-3.723a.75.75 0 00.219-.53V2.929a.75.75 0 00-1.5 0V5.36l-.31-.31A7 7 0 003.239 8.188a.75.75 0 101.448.389A5.5 5.5 0 0113.89 6.11l.311.31h-2.432a.75.75 0 000 1.5h4.243a.75.75 0 00.53-.219z"
                clipRule="evenodd"
              />
            </svg>
            Обновить
          </Button>
        </div>
      </div>

      {isError && (
        <div className="px-5 pt-4">
          <p className="rounded-xl border-2 border-ink bg-coral/30 px-4 py-3 text-sm font-bold">
            ⚠ Не удалось загрузить алерты
          </p>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full min-w-[600px] text-sm">
          <thead>
            <tr className="border-b-2 border-ink bg-ink text-paper">
              {COLUMNS.map((col) => (
                <th
                  key={col}
                  className="px-4 py-3 text-left font-mono text-[11px] font-bold uppercase tracking-[0.15em]"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={5} className="py-14 text-center">
                  <Spinner />
                </td>
              </tr>
            ) : searchedAlerts.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-14">
                  <div className="flex flex-col items-center gap-3">
                    <span className="rotate-2 rounded-lg border-2 border-ink bg-bubble px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider shadow-brutal-xs">
                      0 алертов
                    </span>
                    <p className="font-bold text-ink/50">Алертов пока нет</p>
                  </div>
                </td>
              </tr>
            ) : (
              searchedAlerts.map((alert) => (
                <tr
                  key={alert.id}
                  className="border-b-2 border-ink/10 transition-colors last:border-b-0 hover:bg-lime/25"
                >
                  <td className="px-4 py-3.5">
                    <span className="rounded-md bg-paper-deep px-2 py-0.5 font-mono text-xs font-bold">
                      #{alert.id}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 font-mono text-[11px] text-ink/50">{alert.file_id}</td>
                  <td className="px-4 py-3.5">
                    <Badge variant={getLevelVariant(alert.level)}>{alert.level}</Badge>
                  </td>
                  <td className="px-4 py-3.5 text-sm font-semibold text-ink/80">{alert.message}</td>
                  <td className="whitespace-nowrap px-4 py-3.5 font-mono text-xs text-ink/60">
                    {formatDate(alert.created_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <FilePagination page={page} totalPages={totalPages} onPageChange={setPage} />
    </section>
  );
}
