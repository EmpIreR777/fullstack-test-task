import { useQuery } from '@tanstack/react-query';
import { alertService } from '@/services/alert.service';

export const ALERTS_QUERY_KEY = ['alerts'] as const;

export function useAlerts(params: { page: number; query?: string }) {
  return useQuery({
    queryKey: [...ALERTS_QUERY_KEY, params] as const,
    queryFn: () => alertService.list(params),
    staleTime: 1000 * 30,
  });
}
