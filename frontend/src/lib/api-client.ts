import axios from 'axios';

const rawApiUrl = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const normalizedApiUrl = rawApiUrl.replace(/\/+$/, '');

export const API_BASE_URL = normalizedApiUrl.endsWith('/api/v1')
  ? normalizedApiUrl
  : normalizedApiUrl.endsWith('/api')
    ? `${normalizedApiUrl}/v1`
    : `${normalizedApiUrl}/api/v1`;

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      if (status === 500) {
        console.error('[API] Внутренняя ошибка сервера:', error.response?.data);
      }
    }
    return Promise.reject(error);
  },
);
