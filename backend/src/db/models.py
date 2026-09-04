from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from src.db.enums import ProcessingStatus


class Base(DeclarativeBase):
    """Базовый класс модели с общими полями."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    __abstract__ = True


class StoredFile(Base):
    __tablename__ = 'stored_files'
    __table_args__ = (
        Index(
            'ix_files_stored_files_title_trgm',
            'title',
            postgresql_using='gin',
            postgresql_ops={'title': 'gin_trgm_ops'},
        ),
        Index(
            'ix_files_stored_files_original_name_trgm',
            'original_name',
            postgresql_using='gin',
            postgresql_ops={'original_name': 'gin_trgm_ops'},
        ),
        {'schema': 'files'},
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_status: Mapped[str] = mapped_column(String(50), nullable=False, default=ProcessingStatus.UPLOADED)
    scan_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    scan_details: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    requires_attention: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Alert(Base):
    __tablename__ = 'alerts'
    __table_args__ = {'schema': 'files'}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(String(36), ForeignKey('files.stored_files.id'), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
