'use client';

import { useEffect, useState } from 'react';
import { useFiles } from '@/hooks/useFiles';
import { FileTableRow } from './FileTableRow';
import { FileUploadModal } from './FileUploadModal';
import { FileToolbar } from './FileToolbar';
import { FilePagination } from './FilePagination';
import { Spinner } from '@/components/ui/Spinner';

const COLUMNS = ['Название', 'Файл', 'MIME', 'Размер', 'Статус', 'Проверка', 'Создан', ''];

export function FileTable() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);
  const [uploadOpen, setUploadOpen] = useState(false);

  const normalizedQuery = query.trim();
  const { data, isLoading, isError, refetch } = useFiles({
    page,
    query: normalizedQuery || undefined,
  });

  const files = data?.items ?? [];
  const totalPages = data?.total_pages ?? 1;

  useEffect(() => {
    if (!isLoading && files.length === 0 && page > 1) {
      setPage(1);
    }
  }, [isLoading, files.length, page]);

  const handleQueryChange = (value: string) => {
    setQuery(value);
    setPage(1);
  };

  const handleQueryClear = () => {
    setQuery('');
    setPage(1);
  };

  return (
    <section className="overflow-hidden rounded-2xl border-2 border-ink bg-white shadow-brutal">
      <FileToolbar
        query={query}
        fileCount={data?.total ?? 0}
        onQueryChange={handleQueryChange}
        onQueryClear={handleQueryClear}
        onRefresh={() => refetch()}
        onUploadOpen={() => setUploadOpen(true)}
      />

      {isError && (
        <div className="px-5 pt-4">
          <p className="rounded-xl border-2 border-ink bg-coral/30 px-4 py-3 text-sm font-bold">
            ⚠ Не удалось загрузить файлы
          </p>
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-sm">
          <thead>
            <tr className="border-b-2 border-ink bg-ink text-paper">
              {COLUMNS.map((col, i) => (
                <th
                  key={`${col}-${i}`}
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
                <td colSpan={8} className="py-14 text-center">
                  <Spinner />
                </td>
              </tr>
            ) : files.length === 0 ? (
              <tr>
                <td colSpan={8} className="py-14">
                  <div className="flex flex-col items-center gap-3">
                    <span className="-rotate-2 rounded-lg border-2 border-ink bg-sun px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider shadow-brutal-xs">
                      0 файлов
                    </span>
                    <p className="font-bold text-ink/50">Файлы пока не загружены</p>
                  </div>
                </td>
              </tr>
            ) : (
              files.map((file) => <FileTableRow key={file.id} file={file} />)
            )}
          </tbody>
        </table>
      </div>

      <FilePagination page={page} totalPages={totalPages} onPageChange={setPage} />

      <FileUploadModal open={uploadOpen} onClose={() => setUploadOpen(false)} />
    </section>
  );
}
