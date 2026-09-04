'use client';

import { FileSearchBar } from './FileSearchBar';
import { Button } from '@/components/ui/Button';

interface FileToolbarProps {
  query: string;
  fileCount: number;
  onQueryChange: (value: string) => void;
  onQueryClear: () => void;
  onRefresh: () => void;
  onUploadOpen: () => void;
}

export function FileToolbar({
  query,
  fileCount,
  onQueryChange,
  onQueryClear,
  onRefresh,
  onUploadOpen,
}: FileToolbarProps) {
  return (
    <div className="flex flex-col gap-4 border-b-2 border-ink px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
      <div className="flex items-center gap-3">
        <h2 className="font-display text-lg font-extrabold uppercase tracking-tight">
          Файлы
        </h2>
        <span className="rounded-full border-2 border-ink bg-lime px-2.5 py-0.5 font-mono text-xs font-bold shadow-brutal-xs">
          {fileCount}
        </span>
      </div>

      <FileSearchBar
        value={query}
        onChange={onQueryChange}
        onClear={onQueryClear}
        count={fileCount}
      />

      <div className="flex items-center gap-2 lg:justify-end">
        <Button size="sm" onClick={onUploadOpen}>
          <svg viewBox="0 0 20 20" fill="currentColor" className="size-4" aria-hidden="true">
            <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
          </svg>
          Загрузить файл
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onRefresh}
          title="Обновить список файлов"
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
  );
}
