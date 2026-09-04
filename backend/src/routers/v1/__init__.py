from fastapi import APIRouter
from src.core.config import settings

from .alerts_router import router as alerts_router
from .files_router import router as files_router

router = APIRouter(prefix=settings.API_PREFIX)
router.include_router(files_router)
router.include_router(alerts_router)

__all__ = ['router']
