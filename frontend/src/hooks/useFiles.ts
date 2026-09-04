import { useQuery } from '@tanstack/react-query';
import { fileService } from '@/services/file.service';

export const FILES_QUERY_KEY = ['files'] as const;

export function useFiles(params: { page: number; query?: string }) {
  const { page, query } = params;
  return useQuery({
    queryKey: [...FILES_QUERY_KEY, page, query ?? ''] as const,
    queryFn: () => fileService.list({ page, query }),
    staleTime: 1000 * 30,
  });
}
