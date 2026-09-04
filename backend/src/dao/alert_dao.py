from src.dao.base_dao import BaseDAO
from src.db.models import Alert


class AlertDAO(BaseDAO[Alert]):
    model = Alert
