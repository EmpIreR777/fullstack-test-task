from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_id: str
    level: str
    message: str
    created_at: datetime


class PaginatedAlertResponse(BaseModel):
    items: list[AlertItem]
    page: int
    page_size: int
    total: int
    total_pages: int
