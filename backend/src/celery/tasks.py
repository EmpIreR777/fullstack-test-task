import logging
from pathlib import Path

from redis.exceptions import RedisError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from src.core.config import STORAGE_DIR
from src.db.enums import AlertLevel, ProcessingStatus, ScanStatus
from src.db.models import Alert, StoredFile
from src.db.session_make import SyncSession

from celery import Task

from .celery import celery_app
from .constants import (
    FILE_ALLOWED_PDF_MIME_TYPES,
    FILE_MAX_SIZE_BYTES,
    FILE_SUSPICIOUS_EXTENSIONS,
    PDF_MIME_TYPE,
    PDF_PAGE_PATTERN,
    SCAN_CHUNK_SIZE,
)

logger = logging.getLogger(__name__)


def _scan_file_for_threats(file_item: StoredFile) -> None:
    """Вычисляет статус сканирования и обновляет поля объекта."""
    file_item.processing_status = ProcessingStatus.PROCESSING
    reasons: list[str] = []
    extension = Path(file_item.original_name).suffix.lower()

    if extension in FILE_SUSPICIOUS_EXTENSIONS:
        reasons.append(f'suspicious extension {extension}')

    if file_item.size > FILE_MAX_SIZE_BYTES:
        reasons.append('file is larger than allowed size')

    if extension == '.pdf' and file_item.mime_type not in FILE_ALLOWED_PDF_MIME_TYPES:
        reasons.append('pdf extension does not match mime type')

    file_item.scan_status = ScanStatus.SUSPICIOUS if reasons else ScanStatus.CLEAN
    file_item.scan_details = ', '.join(reasons) if reasons else 'no threats found'
    file_item.requires_attention = bool(reasons)


def _count_text_lines_and_chars(stored_path: Path) -> tuple[int, int]:
    """Считает строки и символы текстового файла, читая его построчно (без загрузки в ОЗУ)."""
    line_count = 0
    char_count = 0
    with stored_path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_count += 1
            char_count += len(line)
    return line_count, char_count


def _count_pdf_page_marks(stored_path: Path) -> int:
    """Ищет маркеры страниц по чанкам с перекрытием (без загрузки файла в ОЗУ)."""
    occurrences = 0
    tail = b''
    with stored_path.open('rb') as f:
        while chunk := f.read(SCAN_CHUNK_SIZE):
            window = tail + chunk
            occurrences += window.count(PDF_PAGE_PATTERN)
            tail = window[-(len(PDF_PAGE_PATTERN) - 1) :]
    return max(occurrences, 1)


def _extract_file_metadata(file_item: StoredFile) -> None:
    """Извлекает метаданные с диска и обновляет поля объекта."""
    stored_path = STORAGE_DIR / file_item.stored_name
    if not stored_path.exists():
        file_item.processing_status = ProcessingStatus.FAILED
        file_item.scan_status = file_item.scan_status or ScanStatus.FAILED
        file_item.scan_details = 'stored file not found during metadata extraction'
        return

    metadata: dict[str, object] = {
        'extension': Path(file_item.original_name).suffix.lower(),
        'size_bytes': file_item.size,
        'mime_type': file_item.mime_type,
    }

    if file_item.mime_type.startswith('text/'):
        line_count, char_count = _count_text_lines_and_chars(stored_path)
        metadata['line_count'] = line_count
        metadata['char_count'] = char_count
    elif file_item.mime_type == PDF_MIME_TYPE:
        metadata['approx_page_count'] = _count_pdf_page_marks(stored_path)

    file_item.metadata_json = metadata
    file_item.processing_status = ProcessingStatus.PROCESSED


def _send_file_alert(session: Session, file_item: StoredFile) -> None:
    """Создаёт алерт по итогам обработки."""
    existing = session.query(Alert).filter(Alert.file_id == file_item.id).first()
    if existing is not None:
        logger.info(f'Алерт для файла {file_item.id} уже существует, повторное создание пропущено.')
        return

    if file_item.processing_status == ProcessingStatus.FAILED:
        alert = Alert(file_id=file_item.id, level=AlertLevel.CRITICAL, message='File processing failed')
        logger.error(f'File processing failed: {file_item.id}')
    elif file_item.requires_attention:
        alert = Alert(
            file_id=file_item.id,
            level=AlertLevel.WARNING,
            message=f'File requires attention: {file_item.scan_details}',
        )
    else:
        alert = Alert(file_id=file_item.id, level=AlertLevel.INFO, message='File processed successfully')

    session.add(alert)


class ScanFileTask(Task):  # type: ignore[misc]
    """Базовый класс задачи сканирования с обработкой окончательного провала."""

    def on_failure(
        self,
        exc: Exception,  # noqa: ARG002
        task_id: str,  # noqa: ARG002
        args: tuple[object, ...],
        kwargs: dict[str, object],
        einfo: object,  # noqa: ARG002
    ) -> None:
        """При окончательном провале таска помечаем файл как failed, чтобы он не висел в 'processing'."""
        file_id = args[0] if args else kwargs.get('file_id')
        if not file_id:
            return
        try:
            with SyncSession() as session:
                file_item = session.get(StoredFile, file_id)
                if file_item and file_item.processing_status == ProcessingStatus.PROCESSING:
                    file_item.processing_status = ProcessingStatus.FAILED
                    file_item.scan_status = file_item.scan_status or ScanStatus.FAILED
                    file_item.scan_details = 'scan task failed after retries'
                    session.commit()
        except Exception as e:
            logger.error(f'Не удалось пометить файл {file_id} как failed после провала таска: {e}')


@celery_app.task(
    bind=True,
    base=ScanFileTask,
    autoretry_for=(OperationalError, RedisError),
    retry_backoff=True,
    retry_backoff_max=60,
    max_retries=3,
)
def scan_file_for_threats(self: Task, file_id: str) -> None:
    """Сканирует файл и запускает цепочку обработки: scan -> extract_metadata -> send_alert."""
    with SyncSession() as session:
        file_item = session.get(StoredFile, file_id)
        if not file_item:
            logger.warning(f'Файл {file_id} не найден при сканировании')
            return

        _scan_file_for_threats(file_item)
        session.commit()

        _extract_file_metadata(file_item)
        session.commit()

        _send_file_alert(session, file_item)
        session.commit()
