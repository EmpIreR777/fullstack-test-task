import logging

from sqlalchemy import String, cast, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.dao import AlertDAO
from src.db.models import Alert

logger = logging.getLogger(__name__)


class AlertService:
    """Сервис для работы с алертами."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_alerts(
        self,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
        query: str | None = None,
    ) -> tuple[list[Alert], int]:
        query = query.strip() if query else None

        logger.info(f'Получение списка алертов. page={page}, page_size={page_size}, query={query!r}')

        search_filter = None
        if query:
            search_filter = or_(
                cast(Alert.id, String).ilike(f'%{query}%'),
                cast(Alert.file_id, String).ilike(f'%{query}%'),
            )

        alerts, total = await AlertDAO.paginate(
            self.session,
            page=page,
            page_size=page_size,
            filters=search_filter,
            order_by=Alert.created_at.desc(),
        )

        logger.info(f'Найдено {len(alerts)} алертов, всего: {total}')
        return alerts, total
