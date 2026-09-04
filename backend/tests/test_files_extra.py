import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.enums import ProcessingStatus
from src.db.models import StoredFile


@pytest.mark.asyncio
class TestFilesExtraIntegration:
    """Дополнительные тесты: поиск, обновление, удаление, скачивание."""

    async def test_search_files_by_title(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест поиска файлов по названию (ILIKE, частичное совпадение)."""
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='UniqueSearchableTitle',
            original_name='search_doc.pdf',
            stored_name='stored_search.pdf',
            mime_type='application/pdf',
            size=1024,
            processing_status=ProcessingStatus.UPLOADED,
        )
        db_session.add(test_file)
        await db_session.commit()

        # Ищем по части названия (без учета регистра)
        response = await client.get('/api/v1/files', params={'query': 'searchable'})
        assert response.status_code == 200
        data = response.json()
        items = data['items']
        assert len(items) >= 1
        assert any(item['id'] == file_id for item in items)

    async def test_search_files_no_match(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест поиска по несуществующему запросу — пустой результат."""
        test_file = StoredFile(
            id=str(uuid.uuid4()),
            title='ExistingFile',
            original_name='existing.pdf',
            stored_name='stored_existing.pdf',
            mime_type='application/pdf',
            size=1024,
            processing_status=ProcessingStatus.UPLOADED,
        )
        db_session.add(test_file)
        await db_session.commit()

        response = await client.get('/api/v1/files', params={'query': 'zzz_nonexistent_zzz'})
        assert response.status_code == 200
        data = response.json()
        assert data['items'] == []
        assert data['total'] == 0

    async def test_update_file_title(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест обновления названия файла."""
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='Old Title',
            original_name='update.pdf',
            stored_name='stored_update.pdf',
            mime_type='application/pdf',
            size=1024,
            processing_status=ProcessingStatus.UPLOADED,
        )
        db_session.add(test_file)
        await db_session.commit()

        response = await client.patch(
            f'/api/v1/files/{file_id}',
            json={'title': 'New Title'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['title'] == 'New Title'

    async def test_update_file_not_found(self, client: AsyncClient) -> None:
        """Тест обновления несуществующего файла — 404."""
        non_existent_id = str(uuid.uuid4())
        response = await client.patch(
            f'/api/v1/files/{non_existent_id}',
            json={'title': 'New Title'},
        )
        assert response.status_code == 404

    async def test_delete_file(
        self,
        client: AsyncClient,
    ) -> None:
        """Тест удаления файла."""
        # Сначала создаем файл через API
        file_content = b'To delete content'
        files = {'file': ('delete.pdf', io.BytesIO(file_content), 'application/pdf')}
        create_resp = await client.post('/api/v1/files', data={'title': 'To Delete'}, files=files)
        assert create_resp.status_code == 201
        file_id = create_resp.json()['id']

        # Проверяем что файл виден
        get_before = await client.get(f'/api/v1/files/{file_id}')
        assert get_before.status_code == 200

        # Удаляем
        response = await client.delete(f'/api/v1/files/{file_id}')
        assert response.status_code == 204

        # Проверяем что файл удален
        get_response = await client.get(f'/api/v1/files/{file_id}')
        assert get_response.status_code == 404

    async def test_delete_file_not_found(self, client: AsyncClient) -> None:
        """Тест удаления несуществующего файла — 404."""
        non_existent_id = str(uuid.uuid4())
        response = await client.delete(f'/api/v1/files/{non_existent_id}')
        assert response.status_code == 404

    async def test_download_file_not_found(self, client: AsyncClient) -> None:
        """Тест скачивания несуществующего файла — 404."""
        non_existent_id = str(uuid.uuid4())
        response = await client.get(f'/api/v1/files/{non_existent_id}/download')
        assert response.status_code == 404

    async def test_download_file_success(
        self,
        client: AsyncClient,
    ) -> None:
        """Тест успешного скачивания ранее загруженного файла."""
        file_content = b'Downloadable content'
        files = {'file': ('downloadable.txt', io.BytesIO(file_content), 'text/plain')}
        create_resp = await client.post('/api/v1/files', data={'title': 'Downloadable'}, files=files)
        assert create_resp.status_code == 201
        file_id = create_resp.json()['id']

        response = await client.get(f'/api/v1/files/{file_id}/download')
        assert response.status_code == 200
        assert response.content == file_content
        assert response.headers['content-type'].startswith('text/plain')

    async def test_upload_file(
        self,
        client: AsyncClient,
    ) -> None:
        """Тест загрузки файла через multipart/form-data."""
        file_content = b'Hello, World!'
        files = {'file': ('test_upload.txt', io.BytesIO(file_content), 'text/plain')}
        data = {'title': 'Uploaded File'}

        response = await client.post('/api/v1/files', data=data, files=files)
        assert response.status_code == 201
        result = response.json()
        assert result['title'] == 'Uploaded File'
        assert result['original_name'] == 'test_upload.txt'
        assert result['size'] == len(file_content)
        assert result['processing_status'] == ProcessingStatus.UPLOADED

        # Проверяем что файл появился через client
        get_response = await client.get(f'/api/v1/files/{result["id"]}')
        assert get_response.status_code == 200
