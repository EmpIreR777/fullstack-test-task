import { useMutation, useQueryClient } from '@tanstack/react-query';
import { fileService } from '@/services/file.service';
import { FILES_QUERY_KEY } from './useFiles';
import { ALERTS_QUERY_KEY } from './useAlerts';

export function useDeleteFile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => fileService.remove(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: FILES_QUERY_KEY });
      void queryClient.invalidateQueries({ queryKey: ALERTS_QUERY_KEY });
    },
  });
}
