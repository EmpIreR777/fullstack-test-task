from src.dao.base_dao import BaseDAO
from src.db.models import StoredFile


class StoredFileDAO(BaseDAO[StoredFile]):
    model = StoredFile
