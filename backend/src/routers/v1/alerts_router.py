from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.db.session_make import get_db_session
from src.schemas import AlertItem, PaginatedAlertResponse
from src.services.alert_service import AlertService

router = APIRouter(tags=['Alerts'])


@router.get('/alerts', response_model=PaginatedAlertResponse, summary='Пагинированный список алертов безопасности')
async def list_alerts_view(
    page: int = 1,
    query: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> PaginatedAlertResponse:
    effective_page_size = settings.DEFAULT_PAGE_SIZE
    service = AlertService(session)

    items, total = await service.list_alerts(
        page=page,
        page_size=effective_page_size,
        query=query,
    )

    total_pages = (total + effective_page_size - 1) // effective_page_size

    return PaginatedAlertResponse(
        items=[AlertItem.model_validate(alert) for alert in items],
        page=page,
        page_size=effective_page_size,
        total=total,
        total_pages=total_pages,
    )
