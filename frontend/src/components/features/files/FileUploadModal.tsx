'use client';

import { useState, type FormEvent } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { useUploadFile } from '@/hooks/useUploadFile';

interface FileUploadModalProps {
  open: boolean;
  onClose: () => void;
}

export function FileUploadModal({ open, onClose }: FileUploadModalProps) {
  const [title, setTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { mutateAsync, isPending } = useUploadFile();

  const handleClose = () => {
    setTitle('');
    setFile(null);
    setError(null);
    onClose();
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!title.trim() || !file) {
      setError('Укажите название и выберите файл');
      return;
    }
    setError(null);
    try {
      await mutateAsync({ title: title.trim(), file });
      handleClose();
    } catch {
      setError('Не удалось загрузить файл. Попробуйте снова.');
    }
  };

  return (
    <Modal open={open} onClose={handleClose} title="Загрузить файл">
      <form onSubmit={(e) => void handleSubmit(e)} className="flex flex-col gap-4">
        {error && (
          <p className="rounded-xl border-2 border-ink bg-coral/30 px-4 py-3 text-sm font-bold">
            {error}
          </p>
        )}

        <div className="flex flex-col gap-1.5">
          <label htmlFor="file-title" className="font-mono text-[11px] font-bold uppercase tracking-wider text-ink/60">
            Название
          </label>
          <input
            id="file-title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Введите название файла"
            className="rounded-xl border-2 border-ink bg-white px-3.5 py-2.5 text-sm font-medium outline-none transition-all duration-100 placeholder:text-ink/30 focus:shadow-brutal-xs"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="file-input" className="font-mono text-[11px] font-bold uppercase tracking-wider text-ink/60">
            Файл
          </label>
          <label
            htmlFor="file-input"
            className="group flex cursor-pointer flex-col items-center justify-center gap-1.5 rounded-xl border-2 border-dashed border-ink/50 bg-paper-deep/50 px-4 py-7 text-center transition-all duration-100 hover:border-ink hover:bg-lime/25"
          >
            {file ? (
              <>
                <span className="flex max-w-full items-center gap-2 rounded-lg border-2 border-ink bg-white px-3 py-1.5 font-mono text-xs font-bold shadow-brutal-xs">
                  <svg viewBox="0 0 20 20" fill="currentColor" className="size-3.5 shrink-0" aria-hidden="true">
                    <path d="M3 3.5A1.5 1.5 0 014.5 2h6.879a1.5 1.5 0 011.06.44l4.122 4.12A1.5 1.5 0 0117 7.622V16.5a1.5 1.5 0 01-1.5 1.5h-11A1.5 1.5 0 013 16.5v-13z" />
                  </svg>
                  <span className="truncate">{file.name}</span>
                </span>
                <span className="font-mono text-[10px] uppercase tracking-wider text-ink/50">
                  Нажмите, чтобы заменить
                </span>
              </>
            ) : (
              <>
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="mb-1 size-8 text-ink/40 transition-colors group-hover:text-ink"
                  aria-hidden="true"
                >
                  <path d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
                <span className="text-sm font-bold">Нажмите для выбора файла</span>
                <span className="font-mono text-[10px] uppercase tracking-wider text-ink/40">
                  любой формат
                </span>
              </>
            )}
            <input
              id="file-input"
              type="file"
              className="sr-only"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button type="button" variant="secondary" onClick={handleClose}>
            Отмена
          </Button>
          <Button type="submit" loading={isPending}>
            Загрузить
          </Button>
        </div>
      </form>
    </Modal>
  );
}
