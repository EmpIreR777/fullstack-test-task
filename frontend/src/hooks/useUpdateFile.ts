import { useMutation, useQueryClient } from '@tanstack/react-query';
import { fileService } from '@/services/file.service';
import { FILES_QUERY_KEY } from './useFiles';

export function useUpdateFile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, title }: { id: string; title: string }) =>
      fileService.update(id, { title }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: FILES_QUERY_KEY });
    },
  });
}
