import logging
from typing import Any, TypeVar

from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement, ColumnExpressionArgument
from src.core.config import settings
from src.db.models import Base

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=Base)


class BaseDAO[T]:
    """Базовый DAO с CRUD-операциями для SQLAlchemy моделей."""

    model: type[T]

    @classmethod
    async def paginate(
        cls,
        session: AsyncSession,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
        filters: dict[str, Any] | ColumnElement[bool] | None = None,
        order_by: ColumnExpressionArgument[Any] | None = None,
    ) -> tuple[list[T], int]:
        """Возвращает пагинированный список записей и общее количество."""
        if page < 1:
            raise ValueError('Номер страницы должен быть положительным.')
        if page_size < 1:
            raise ValueError('Размер страницы должен быть положительным.')

        try:
            total_stmt = select(func.count()).select_from(cls.model)
            items_stmt = select(cls.model)

            if isinstance(filters, dict):
                total_stmt = total_stmt.filter_by(**filters)
                items_stmt = items_stmt.filter_by(**filters)
            elif filters is not None:
                total_stmt = total_stmt.where(filters)
                items_stmt = items_stmt.where(filters)

            total_res = await session.execute(total_stmt)
            total = int(total_res.scalar_one() or 0)

            if order_by is not None:
                items_stmt = items_stmt.order_by(order_by)

            items_stmt = items_stmt.offset((page - 1) * page_size).limit(page_size)
            items_res = await session.execute(items_stmt)
            items = list(items_res.scalars().all())

            return items, total
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при пагинации записей {cls.model.__name__}: {e}')
            raise

    @classmethod
    async def find_one_or_none(
        cls,
        session: AsyncSession,
        filters: dict[str, Any] | None = None,
    ) -> T | None:
        """Находит запись по фильтрам."""
        filter_dict = filters or {}
        logger.info(f'Поиск {cls.model.__name__} с фильтрами: {filter_dict}')
        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()
            logger.info(f'Запись {"найдена" if record else "не найдена"} с фильтрами: {filter_dict}')
            return record
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при поиске записи с фильтрами {filter_dict}: {e}')
            raise

    @classmethod
    async def add(cls, session: AsyncSession, values: dict[str, Any]) -> T:
        """Добавляет запись в БД."""
        logger.info(f'Добавление {cls.model.__name__} с данными: {values}')
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.flush()
            logger.info(f'{cls.model.__name__} успешно добавлена.')
            return new_instance
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при добавлении записи: {e}')
            raise

    @classmethod
    async def delete(cls, session: AsyncSession, filters: dict[str, Any]) -> int:
        """Удаляет записи по фильтрам и возвращает количество удалённых."""
        if not filters:
            raise ValueError('Для удаления требуется хотя бы один фильтр.')

        logger.info(f'Удаление {cls.model.__name__} с фильтрами: {filters}')
        query = sqlalchemy_delete(cls.model).filter_by(**filters)
        try:
            result = await session.execute(query)
            await session.flush()
            rowcount = getattr(result, 'rowcount', 0) or 0
            logger.info(f'Удалено {rowcount} записей.')
            return rowcount
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при удалении записей: {e}')
            raise
