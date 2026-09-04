from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.celery.tasks import scan_file_for_threats
from src.core.config import settings
from src.db.session_make import get_db_session
from src.schemas import FileItem, FileUpdate, PaginatedFileResponse
from src.services.stored_file_service import StoredFileService
from starlette import status

router = APIRouter(tags=['Files'])


@router.get('/files', response_model=PaginatedFileResponse, summary='Пагинированный список файлов')
async def list_files_view(
    page: int = 1,
    query: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedFileResponse:
    effective_page_size = settings.DEFAULT_PAGE_SIZE
    service = StoredFileService(session)

    items, total = await service.list_files(
        page=page,
        page_size=effective_page_size,
        query=query,
    )

    total_pages = (total + effective_page_size - 1) // effective_page_size

    return PaginatedFileResponse(
        items=[FileItem.model_validate(file) for file in items],
        page=page,
        page_size=effective_page_size,
        total=total,
        total_pages=total_pages,
    )


@router.post('/files', response_model=FileItem, status_code=status.HTTP_201_CREATED, summary='Загрузить файл')
async def create_file_view(
    title: str = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> FileItem:
    service = StoredFileService(session)
    file_item = await service.create_file(title=title, upload_file=file)
    scan_file_for_threats.delay(file_item.id)
    return FileItem.model_validate(file_item)


@router.get('/files/{file_id}', response_model=FileItem, summary='Получить файл по ID')
async def get_file_view(file_id: str, session: AsyncSession = Depends(get_db_session)) -> FileItem:
    service = StoredFileService(session)
    file_item = await service.get_file(file_id)
    return FileItem.model_validate(file_item)


@router.patch('/files/{file_id}', response_model=FileItem, summary='Обновить название файла')
async def update_file_view(
    file_id: str,
    payload: FileUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> FileItem:
    service = StoredFileService(session)
    file_item = await service.update_file(file_id=file_id, title=payload.title)
    return FileItem.model_validate(file_item)


@router.get('/files/{file_id}/download', summary='Скачать файл')
async def download_file(file_id: str, session: AsyncSession = Depends(get_db_session)) -> FileResponse:
    service = StoredFileService(session)
    file_item, stored_path = await service.get_file_storage_path(file_id)
    return FileResponse(
        path=stored_path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete('/files/{file_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Удалить файл')
async def delete_file_view(file_id: str, session: AsyncSession = Depends(get_db_session)) -> None:
    service = StoredFileService(session)
    await service.delete_file(file_id)
