import logging
import mimetypes
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import STORAGE_DIR, settings
from src.dao import AlertDAO, StoredFileDAO
from src.db.enums import ProcessingStatus
from src.db.models import StoredFile

logger = logging.getLogger(__name__)

UPLOAD_CHUNK_SIZE: int = 1024 * 1024  # 1 MiB


class StoredFileService:
    """Сервис для работы с файлами (CRUD)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_files(
        self,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
        query: str | None = None,
    ) -> tuple[list[StoredFile], int]:
        """Возвращает пагинированный список файлов. Поиск по title и original_name."""
        query = query.strip() if query else None

        logger.info(f'Получение списка файлов. page={page}, page_size={page_size}, query={query!r}')

        search_filter = None
        if query:
            search_filter = or_(
                StoredFile.id == query,
                StoredFile.title.ilike(f'%{query}%'),
                StoredFile.original_name.ilike(f'%{query}%'),
            )

        files, total = await StoredFileDAO.paginate(
            self.session,
            page=page,
            page_size=page_size,
            filters=search_filter,
            order_by=StoredFile.created_at.desc(),
        )

        logger.info(f'Найдено {len(files)} файлов, всего: {total}')
        return files, total

    async def get_file(self, file_id: str) -> StoredFile:
        """Возвращает файл по его ID или выбрасывает 404."""
        logger.info(f'Поиск файла с ID: {file_id}')
        file_item = await StoredFileDAO.find_one_or_none(session=self.session, filters={'id': file_id})
        if not file_item:
            logger.warning(f'Файл с ID {file_id} не найден')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found')
        logger.info(f'Файл с ID {file_id} найден: {file_item.original_name}')
        return file_item

    async def create_file(self, title: str, upload_file: UploadFile) -> StoredFile:
        """Создаёт файл: стриминговая запись на диск чанками, затем запись в БД."""
        logger.info(f'Загрузка файла: title={title}, filename={upload_file.filename}')
        file_id = str(uuid4())
        suffix = Path(upload_file.filename or '').suffix
        stored_name = f'{file_id}{suffix}'
        stored_path = STORAGE_DIR / stored_name

        # 1. Проверяем первый чанк, чтобы отсечь пустые файлы до создания артефактов
        first_chunk = await upload_file.read(UPLOAD_CHUNK_SIZE)
        if not first_chunk:
            logger.warning(f'Попытка загрузить пустой файл: {upload_file.filename}')
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='File is empty')

        # 2. Стримим файл на диск чанками, не читая его целиком в ОЗУ  # noqa: RUF003
        size = len(first_chunk)
        try:
            async with aiofiles.open(stored_path, 'wb') as out:
                await out.write(first_chunk)
                while chunk := await upload_file.read(UPLOAD_CHUNK_SIZE):
                    size += len(chunk)
                    await out.write(chunk)
        except OSError as e:
            logger.error(f'Ошибка записи файла на диск: {e}')
            stored_path.unlink(missing_ok=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to save file')

        # 3. Создаём запись в БД; при сбое БД удаляем уже записанный файл  # noqa: RUF003
        try:
            file_item = await StoredFileDAO.add(
                session=self.session,
                values={
                    'id': file_id,
                    'title': title,
                    'original_name': upload_file.filename or stored_name,
                    'stored_name': stored_name,
                    'mime_type': upload_file.content_type
                    or mimetypes.guess_type(stored_name)[0]
                    or 'application/octet-stream',
                    'size': size,
                    'processing_status': ProcessingStatus.UPLOADED,
                },
            )
            await self.session.refresh(file_item)
        except Exception:
            logger.exception(f'Ошибка создания записи в БД для файла {file_id}, удаляю файл с диска')
            stored_path.unlink(missing_ok=True)
            raise

        logger.info(f'Файл успешно загружен. ID: {file_id}, размер: {size} байт')
        return file_item

    async def update_file(self, file_id: str, title: str) -> StoredFile:
        """Обновляет название файла."""
        logger.info(f'Обновление файла с ID: {file_id}, новое название: {title}')
        file_item = await StoredFileDAO.find_one_or_none(session=self.session, filters={'id': file_id})
        if not file_item:
            logger.warning(f'Файл с ID {file_id} не найден для обновления')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found')
        file_item.title = title
        await self.session.flush()
        await self.session.refresh(file_item)
        logger.info(f'Файл с ID {file_id} успешно обновлен')
        return file_item

    async def delete_file(self, file_id: str) -> None:
        """Удаляет файл: сначала коммитит удаление из БД, и только потом удаляет файл с диска."""
        logger.info(f'Удаление файла с ID: {file_id}')
        file_item = await StoredFileDAO.find_one_or_none(session=self.session, filters={'id': file_id})
        if not file_item:
            logger.warning(f'Файл с ID {file_id} не найден для удаления')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='File not found')
        stored_path = STORAGE_DIR / file_item.stored_name

        # 1. Удаляем связанные алерты
        alerts_deleted = await AlertDAO.delete(session=self.session, filters={'file_id': file_id})
        logger.info(f'Удалено {alerts_deleted} алертов для файла {file_id}')

        # 2. Удаляем запись из БД и коммитим транзакцию ДО удаления файла с диска:
        await self.session.delete(file_item)
        await self.session.commit()

        # 3. Только после успешного коммита удаляем файл с диска
        try:
            stored_path.unlink(missing_ok=True)
            logger.info(f'Файл {stored_path.name} удалён с диска')
        except OSError as e:
            logger.error(f'Не удалось удалить файл {stored_path.name} с диска: {e}')

        logger.info(f'Файл с ID {file_id} удалён из БД')

    async def get_file_storage_path(self, file_id: str) -> tuple[StoredFile, Path]:
        """Возвращает файл и путь к нему на диске для скачивания."""
        file_item = await self.get_file(file_id)
        stored_path = STORAGE_DIR / file_item.stored_name
        if not stored_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Stored file not found')
        return file_item, stored_path
