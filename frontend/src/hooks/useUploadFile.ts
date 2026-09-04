import { useMutation, useQueryClient } from '@tanstack/react-query';
import { fileService } from '@/services/file.service';
import { FILES_QUERY_KEY } from './useFiles';
import { ALERTS_QUERY_KEY } from './useAlerts';

export function useUploadFile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ title, file }: { title: string; file: File }) =>
      fileService.upload(title, file),
    onSuccess: () => {
      // Важно: никаких await/долгих ожиданий, чтобы модалка не "держалась".
      void queryClient.invalidateQueries({ queryKey: FILES_QUERY_KEY });

      // Алерты появляются асинхронно (Celery скан).
      // Запускаем несколько инвалидирований без ожидания.
      void queryClient.invalidateQueries({ queryKey: ALERTS_QUERY_KEY });

      setTimeout(() => {
        void queryClient.invalidateQueries({ queryKey: ALERTS_QUERY_KEY });
      }, 1200);

      setTimeout(() => {
        void queryClient.invalidateQueries({ queryKey: ALERTS_QUERY_KEY });
      }, 3000);
    },
  });
}
