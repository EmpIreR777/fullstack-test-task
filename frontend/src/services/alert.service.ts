import { apiClient } from '@/lib/api-client';
import type { PaginatedAlertResponse } from '@/types/alert';

export const alertService = {
  list: (params: { page: number; query?: string }) =>
    apiClient
      .get<PaginatedAlertResponse>('/alerts', {
        params: {
          page: params.page,
          query: params.query?.trim() || undefined,
        },
      })
      .then((r) => r.data),

};
