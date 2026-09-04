export interface FileItem {
  id: string;
  title: string;
  original_name: string;
  mime_type: string;
  size: number;
  processing_status: string;
  scan_status: string | null;
  scan_details: string | null;
  metadata_json: Record<string, unknown> | null;
  requires_attention: boolean;
  created_at: string;
  updated_at: string;
}

export interface FileUpdate {
  title: string;
}

export interface PaginatedFileResponse {
  items: FileItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}
