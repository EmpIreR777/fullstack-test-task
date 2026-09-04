from enum import StrEnum


class ProcessingStatus(StrEnum):
    """Статус обработки файла."""

    UPLOADED = 'uploaded'
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    FAILED = 'failed'


class ScanStatus(StrEnum):
    """Результат сканирования файла."""

    CLEAN = 'clean'
    SUSPICIOUS = 'suspicious'
    FAILED = 'failed'


class AlertLevel(StrEnum):
    """Уровень алерта, который генерирует celery-таск."""

    CRITICAL = 'critical'
    WARNING = 'warning'
    INFO = 'info'
