export interface AlertItem {
  id: number;
  file_id: string;
  level: string;
  message: string;
  created_at: string;
}

export interface PaginatedAlertResponse {
  items: AlertItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}
