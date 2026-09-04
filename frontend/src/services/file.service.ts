import { API_BASE_URL, apiClient } from '@/lib/api-client';
import type { FileItem, FileUpdate, PaginatedFileResponse } from '@/types/file';

export const fileService = {
  list: (params: { page: number; query?: string }) =>
    apiClient
      .get<PaginatedFileResponse>('/files', {
        params: {
          page: params.page,
          query: params.query?.trim() || undefined,
        },
      })
      .then((r) => r.data),



  getById: (id: string) =>
    apiClient.get<FileItem>(`/files/${id}`).then((r) => r.data),

  upload: (title: string, file: File) => {
    const form = new FormData();
    form.append('title', title);
    form.append('file', file);
    return apiClient
      .post<FileItem>('/files', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },

  update: (id: string, payload: FileUpdate) =>
    apiClient.patch<FileItem>(`/files/${id}`, payload).then((r) => r.data),

  remove: (id: string) =>
    apiClient.delete(`/files/${id}`),

  downloadUrl: (id: string) =>
    `${API_BASE_URL}/files/${id}/download`,
};
