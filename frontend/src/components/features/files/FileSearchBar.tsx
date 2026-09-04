'use client';

import { useMemo } from 'react';
import { Button } from '@/components/ui/Button';

interface FileSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onClear: () => void;
  count: number;
}

export function FileSearchBar({ value, onChange, onClear, count }: FileSearchBarProps) {
  const isEmpty = useMemo(() => value.trim().length === 0, [value]);

  return (
    <div className="flex flex-wrap items-center gap-2.5">
      <div className="relative">
        <svg
          viewBox="0 0 20 20"
          fill="currentColor"
          className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-ink/40"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
            clipRule="evenodd"
          />
        </svg>
        <input
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Поиск по id/названию/имени"
          className="w-full min-w-[220px] rounded-full border-2 border-ink bg-white py-2 pl-9 pr-3 text-sm font-medium outline-none transition-all duration-100 placeholder:text-ink/40 focus:shadow-brutal-xs sm:w-[320px]"
        />
      </div>
      <span className="font-mono text-xs font-bold text-ink/50">Найдено: {count}</span>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={onClear}
        disabled={isEmpty}
      >
        Очистить
      </Button>
    </div>
  );
}
