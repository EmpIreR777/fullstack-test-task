FILE_MAX_SIZE_BYTES: int = 10 * 1024 * 1024
FILE_SUSPICIOUS_EXTENSIONS: list[str] = ['.exe', '.bat', '.cmd', '.sh', '.js']
FILE_ALLOWED_PDF_MIME_TYPES: list[str] = ['application/pdf', 'application/octet-stream']
PDF_MIME_TYPE: str = 'application/pdf'
SCAN_CHUNK_SIZE: int = 1024 * 1024
PDF_PAGE_PATTERN: bytes = b'/Type /Page'
