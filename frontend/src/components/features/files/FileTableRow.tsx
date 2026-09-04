'use client';

import { useState, type FormEvent } from 'react';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { useDeleteFile } from '@/hooks/useDeleteFile';
import { useUpdateFile } from '@/hooks/useUpdateFile';
import { fileService } from '@/services/file.service';
import { formatDate, formatSize } from '@/lib/utils';
import type { FileItem } from '@/types/file';

interface FileTableRowProps {
  file: FileItem;
}

function getProcessingBadgeVariant(status: string): 'success' | 'warning' | 'danger' | 'default' {
  if (status === 'processed') return 'success';
  if (status === 'processing') return 'warning';
  if (status === 'failed') return 'danger';
  return 'default';
}

function getScanBadgeVariant(status: string | null, requiresAttention: boolean): 'success' | 'warning' | 'danger' | 'default' {
  if (requiresAttention) return 'danger';
  if (status === 'clean') return 'success';
  if (status === 'pending' || status === null) return 'default';
  return 'warning';
}

export function FileTableRow({ file }: FileTableRowProps) {
  const { mutate: deleteFile, isPending: isDeleting } = useDeleteFile();
  const { mutateAsync: updateFile, isPending: isUpdating } = useUpdateFile();

  const [editOpen, setEditOpen] = useState(false);
  const [editTitle, setEditTitle] = useState(file.title);
  const [editError, setEditError] = useState<string | null>(null);

  const handleEdit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!editTitle.trim()) {
      setEditError('Название не может быть пустым');
      return;
    }
    setEditError(null);
    try {
      await updateFile({ id: file.id, title: editTitle.trim() });
      setEditOpen(false);
    } catch {
      setEditError('Не удалось обновить название');
    }
  };

  return (
    <>
      <tr className="border-b-2 border-ink/10 transition-colors last:border-b-0 hover:bg-lime/25">
        <td className="px-4 py-3.5">
          <div className="font-bold">{file.title}</div>
          <div className="mt-0.5 font-mono text-[10px] text-ink/40">{file.id}</div>
        </td>
        <td className="px-4 py-3.5 text-sm font-semibold text-ink/75">{file.original_name}</td>
        <td className="px-4 py-3.5">
          <span className="rounded-md border border-ink/20 bg-paper px-1.5 py-0.5 font-mono text-[11px] text-ink/60">
            {file.mime_type}
          </span>
        </td>
        <td className="whitespace-nowrap px-4 py-3.5 font-mono text-xs font-bold text-ink/75">
          {formatSize(file.size)}
        </td>
        <td className="px-4 py-3.5">
          <Badge variant={getProcessingBadgeVariant(file.processing_status)}>
            {file.processing_status}
          </Badge>
        </td>
        <td className="px-4 py-3.5">
          <div className="flex flex-col items-start gap-1">
            <Badge variant={getScanBadgeVariant(file.scan_status, file.requires_attention)}>
              {file.scan_status ?? 'pending'}
            </Badge>
            {file.scan_details && (
              <span className="text-xs font-medium text-ink/50">{file.scan_details}</span>
            )}
          </div>
        </td>
        <td className="whitespace-nowrap px-4 py-3.5 font-mono text-xs text-ink/60">
          {formatDate(file.created_at)}
        </td>
        <td className="px-4 py-3.5">
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={() => window.open(fileService.downloadUrl(file.id), '_blank')}
              title="Скачать файл"
              aria-label="Скачать файл"
              className="flex size-9 items-center justify-center rounded-lg border-2 border-ink bg-white shadow-brutal-xs transition-all duration-100 hover:-translate-y-0.5 hover:bg-lime hover:shadow-brutal-sm"
            >
              <svg viewBox="0 0 20 20" fill="currentColor" className="size-4" aria-hidden="true">
                <path d="M10.75 2.75a.75.75 0 00-1.5 0v8.614L6.295 8.235a.75.75 0 10-1.09 1.03l4.25 4.5a.75.75 0 001.09 0l4.25-4.5a.75.75 0 00-1.09-1.03l-2.955 3.129V2.75z" />
                <path d="M3.5 12.75a.75.75 0 00-1.5 0v2.5A2.75 2.75 0 004.75 18h10.5A2.75 2.75 0 0018 15.25v-2.5a.75.75 0 00-1.5 0v2.5c0 .69-.56 1.25-1.25 1.25H4.75c-.69 0-1.25-.56-1.25-1.25v-2.5z" />
              </svg>
            </button>
            <button
              type="button"
              onClick={() => { setEditTitle(file.title); setEditOpen(true); }}
              title="Переименовать файл"
              aria-label="Переименовать файл"
              className="flex size-9 items-center justify-center rounded-lg border-2 border-ink bg-white shadow-brutal-xs transition-all duration-100 hover:-translate-y-0.5 hover:bg-sun hover:shadow-brutal-sm"
            >
              <svg viewBox="0 0 20 20" fill="currentColor" className="size-4" aria-hidden="true">
                <path d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" />
                <path d="M3.5 5.75c0-.69.56-1.25 1.25-1.25H10A.75.75 0 0010 3H4.75A2.75 2.75 0 002 5.75v9.5A2.75 2.75 0 004.75 18h9.5A2.75 2.75 0 0017 15.25V10a.75.75 0 00-1.5 0v5.25c0 .69-.56 1.25-1.25 1.25h-9.5c-.69 0-1.25-.56-1.25-1.25v-9.5z" />
              </svg>
            </button>
            <button
              type="button"
              disabled={isDeleting}
              onClick={() => deleteFile(file.id)}
              title="Удалить файл"
              aria-label="Удалить файл"
              className="flex size-9 items-center justify-center rounded-lg border-2 border-ink bg-coral shadow-brutal-xs transition-all duration-100 hover:-translate-y-0.5 hover:shadow-brutal-sm disabled:pointer-events-none disabled:opacity-40"
            >
              {isDeleting ? (
                <svg className="size-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4l3-3-3-3v4a10 10 0 100 10l-2-2a8 8 0 01-6-8z"
                  />
                </svg>
              ) : (
                <svg viewBox="0 0 20 20" fill="currentColor" className="size-4" aria-hidden="true">
                  <path
                    fillRule="evenodd"
                    d="M8.75 1A2.75 2.75 0 006 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 10.23 1.482l.149-.022.841 10.518A2.75 2.75 0 007.596 19h4.807a2.75 2.75 0 002.742-2.53l.841-10.52.149.023a.75.75 0 00.23-1.482A41.03 41.03 0 0014 4.193V3.75A2.75 2.75 0 0011.25 1h-2.5zM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4zM8.58 7.72a.75.75 0 00-1.5.06l.3 7.5a.75.75 0 101.5-.06l-.3-7.5zm4.34.06a.75.75 0 10-1.5-.06l-.3 7.5a.75.75 0 101.5.06l.3-7.5z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
          </div>
        </td>
      </tr>

      <Modal open={editOpen} onClose={() => setEditOpen(false)} title="Переименовать файл">
        <form onSubmit={(e) => void handleEdit(e)} className="flex flex-col gap-4">
          {editError && (
            <p className="rounded-xl border-2 border-ink bg-coral/30 px-4 py-3 text-sm font-bold">
              {editError}
            </p>
          )}
          <div className="flex flex-col gap-1.5">
            <label htmlFor="edit-title" className="font-mono text-[11px] font-bold uppercase tracking-wider text-ink/60">
              Новое название
            </label>
            <input
              id="edit-title"
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="rounded-xl border-2 border-ink bg-white px-3.5 py-2.5 text-sm font-medium outline-none transition-all duration-100 placeholder:text-ink/30 focus:shadow-brutal-xs"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setEditOpen(false)}>
              Отмена
            </Button>
            <Button type="submit" loading={isUpdating}>
              Сохранить
            </Button>
          </div>
        </form>
      </Modal>

    </>
  );
}
