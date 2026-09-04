import uuid

import pytest
from src.celery.tasks import _extract_file_metadata, _scan_file_for_threats, _send_file_alert
from src.core.config import STORAGE_DIR
from src.db.enums import AlertLevel, ProcessingStatus, ScanStatus
from src.db.models import Alert, StoredFile
from src.db.session_make import SyncSession


def _create_file_row(
    file_id: str,
    original_name: str,
    stored_name: str,
    mime_type: str,
    size: int,
    processing_status: ProcessingStatus = ProcessingStatus.UPLOADED,
    requires_attention: bool = False,
) -> None:
    """Создаёт запись файла напрямую через SyncSession (коммит в реальную БД)."""
    with SyncSession() as session:
        session.add(
            StoredFile(
                id=file_id,
                title='Scan Test',
                original_name=original_name,
                stored_name=stored_name,
                mime_type=mime_type,
                size=size,
                processing_status=processing_status,
                requires_attention=requires_attention,
            )
        )
        session.commit()


def _get_file(file_id: str) -> StoredFile:
    """Возвращает свежий объект файла из БД в отдельной сессии."""
    with SyncSession() as session:
        file_item = session.get(StoredFile, file_id)
        assert file_item is not None
        return file_item


def _cleanup(file_id: str, stored_name: str) -> None:
    """Удаляет тестовые данные и файл на диске."""
    with SyncSession() as session:
        session.query(Alert).filter(Alert.file_id == file_id).delete()
        file = session.get(StoredFile, file_id)
        if file is not None:
            session.delete(file)
        session.commit()
    stored_path = STORAGE_DIR / stored_name
    if stored_path.exists():
        stored_path.unlink()


@pytest.mark.asyncio
class TestScanTask:
    """Тесты логики сканирования файлов (celery task) без брокера."""

    async def test_scan_clean_file(self) -> None:
        """Чистый .txt файл помечается как clean и не требует внимания."""
        file_id = str(uuid.uuid4())
        stored_name = f'{file_id}.txt'
        _create_file_row(file_id, 'clean.txt', stored_name, 'text/plain', 10)
        (STORAGE_DIR / stored_name).write_bytes(b'hello world')
        try:
            with SyncSession() as session:
                file_item = session.get(StoredFile, file_id)
                assert file_item is not None
                _scan_file_for_threats(file_item)
                _extract_file_metadata(file_item)
                session.commit()

            refreshed = _get_file(file_id)
            assert refreshed is not None
            assert refreshed.scan_status == ScanStatus.CLEAN
            assert refreshed.requires_attention is False
            assert refreshed.processing_status == ProcessingStatus.PROCESSED
            assert refreshed.metadata_json is not None
            assert refreshed.metadata_json.get('extension') == '.txt'
        finally:
            _cleanup(file_id, stored_name)

    async def test_scan_suspicious_extension(self) -> None:
        """Файл с подозрительным расширением (.exe) помечается как suspicious."""
        file_id = str(uuid.uuid4())
        stored_name = f'{file_id}.exe'
        _create_file_row(file_id, 'malware.exe', stored_name, 'application/x-msdownload', 10)
        (STORAGE_DIR / stored_name).write_bytes(b'MZ binary content')
        try:
            with SyncSession() as session:
                file_item = session.get(StoredFile, file_id)
                assert file_item is not None
                _scan_file_for_threats(file_item)
                _extract_file_metadata(file_item)
                session.commit()

            refreshed = _get_file(file_id)
            assert refreshed is not None
            assert refreshed.scan_status == ScanStatus.SUSPICIOUS
            assert refreshed.requires_attention is True
            assert 'suspicious extension' in (refreshed.scan_details or '')
        finally:
            _cleanup(file_id, stored_name)

    async def test_scan_oversized_file(self) -> None:
        """Слишком большой файл помечается как suspicious."""
        from src.celery.constants import FILE_MAX_SIZE_BYTES

        file_id = str(uuid.uuid4())
        stored_name = f'{file_id}.bin'
        _create_file_row(file_id, 'big.bin', stored_name, 'application/octet-stream', FILE_MAX_SIZE_BYTES + 1)
        (STORAGE_DIR / stored_name).write_bytes(b'x')
        try:
            with SyncSession() as session:
                file_item = session.get(StoredFile, file_id)
                assert file_item is not None
                _scan_file_for_threats(file_item)
                _extract_file_metadata(file_item)
                session.commit()

            refreshed = _get_file(file_id)
            assert refreshed is not None
            assert refreshed.scan_status == ScanStatus.SUSPICIOUS
            assert 'larger than allowed size' in (refreshed.scan_details or '')
        finally:
            _cleanup(file_id, stored_name)

    async def test_metadata_extraction_failure_marks_failed(self) -> None:
        """Если файл отсутствует на диске — _extract_file_metadata помечает обработку как failed."""
        file_id = str(uuid.uuid4())
        stored_name = f'{file_id}.pdf'
        _create_file_row(file_id, 'missing.pdf', stored_name, 'application/pdf', 10)
        # File is intentionally NOT written to disk
        try:
            with SyncSession() as session:
                file_item = session.get(StoredFile, file_id)
                assert file_item is not None
                _extract_file_metadata(file_item)
                session.commit()

            refreshed = _get_file(file_id)
            assert refreshed is not None
            assert refreshed.processing_status == ProcessingStatus.FAILED
            assert refreshed.scan_status == ScanStatus.FAILED
            assert 'stored file not found' in (refreshed.scan_details or '')
        finally:
            _cleanup(file_id, stored_name)

    async def test_scan_task_creates_critical_alert_on_missing_file(self) -> None:
        """Оркестратор scan_file_for_threats создаёт critical алерт при отсутствии файла на диске."""
        from src.celery.tasks import scan_file_for_threats

        file_id = str(uuid.uuid4())
        stored_name = f'{file_id}.pdf'
        _create_file_row(file_id, 'missing.pdf', stored_name, 'application/pdf', 10)
        # File is intentionally NOT written to disk
        try:
            scan_file_for_threats(file_id)

            refreshed = _get_file(file_id)
            assert refreshed is not None
            assert refreshed.processing_status == ProcessingStatus.FAILED

            with SyncSession() as session:
                alert = session.query(Alert).filter(Alert.file_id == file_id).first()
                assert alert is not None
                assert alert.level == AlertLevel.CRITICAL
        finally:
            _cleanup(file_id, stored_name)

    async def test_send_alert_for_clean_file(self) -> None:
        """Для обработанного чистого файла создаётся info-алерт."""
        file_id = str(uuid.uuid4())
        stored_name = f'{file_id}.txt'
        _create_file_row(file_id, 'ok.txt', stored_name, 'text/plain', 10, processing_status=ProcessingStatus.PROCESSED)
        try:
            with SyncSession() as session:
                file_item = session.get(StoredFile, file_id)
                assert file_item is not None
                _send_file_alert(session, file_item)
                session.commit()

            with SyncSession() as session:
                alert = session.query(Alert).filter(Alert.file_id == file_id).first()
                assert alert is not None
                assert alert.level == AlertLevel.INFO
        finally:
            _cleanup(file_id, stored_name)

    async def test_send_alert_is_idempotent(self) -> None:
        """Повторный вызов _send_file_alert не создаёт дублирующий алерт (защита при ретрае)."""
        file_id = str(uuid.uuid4())
        stored_name = f'{file_id}.txt'
        _create_file_row(file_id, 'ok.txt', stored_name, 'text/plain', 10, processing_status=ProcessingStatus.PROCESSED)
        try:
            with SyncSession() as session:
                file_item = session.get(StoredFile, file_id)
                assert file_item is not None
                _send_file_alert(session, file_item)
                _send_file_alert(session, file_item)  # повторный вызов, как при ретрае
                session.commit()  # оркестратор владеет транзакцией, коммитим явно

            with SyncSession() as session:
                alerts = session.query(Alert).filter(Alert.file_id == file_id).all()
                assert len(alerts) == 1
                assert alerts[0].level == AlertLevel.INFO
        finally:
            _cleanup(file_id, stored_name)
