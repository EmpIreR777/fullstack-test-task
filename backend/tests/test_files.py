import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.enums import ProcessingStatus
from src.db.models import StoredFile


@pytest.mark.asyncio
class TestFilesIntegration:
    """Интеграционные тесты для endpoint'ов файлов."""

    async def test_list_files_empty(self, client: AsyncClient) -> None:
        """Тест получения списка файлов (проверка структуры пагинированного ответа)."""
        response = await client.get('/api/v1/files')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert isinstance(data['items'], list)
        assert 'page' in data
        assert 'page_size' in data
        assert 'total' in data
        assert 'total_pages' in data

    async def test_list_files_with_data(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест получения списка файлов с данными."""
        # Подготовка: добавление тестового файла
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='Test Document',
            original_name='document.pdf',
            stored_name='stored_document_123.pdf',
            mime_type='application/pdf',
            size=1024,
            processing_status=ProcessingStatus.UPLOADED,
            scan_status=None,
            metadata_json=None,
            requires_attention=False,
        )
        db_session.add(test_file)
        await db_session.commit()

        # Выполнение
        response = await client.get('/api/v1/files')

        # Проверка
        assert response.status_code == 200
        data = response.json()
        items = data['items']
        assert len(items) >= 1
        # Ищем наш файл среди всех (могут быть данные из других тестов/данных)
        our_file = next(item for item in items if item['id'] == file_id)
        assert our_file['id'] == file_id
        assert our_file['title'] == 'Test Document'
        assert our_file['original_name'] == 'document.pdf'
        assert our_file['mime_type'] == 'application/pdf'
        assert our_file['size'] == 1024

    async def test_list_files_multiple_records(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест получения списка нескольких файлов."""
        # Подготовка: добавление нескольких файлов
        files_data = [
            {
                'id': str(uuid.uuid4()),
                'title': 'File 1',
                'original_name': 'file1.txt',
                'stored_name': 'stored_file1.txt',
            },
            {
                'id': str(uuid.uuid4()),
                'title': 'File 2',
                'original_name': 'file2.txt',
                'stored_name': 'stored_file2.txt',
            },
        ]

        for file_data in files_data:
            test_file = StoredFile(
                id=file_data['id'],
                title=file_data['title'],
                original_name=file_data['original_name'],
                stored_name=file_data['stored_name'],
                mime_type='text/plain',
                size=512,
                processing_status=ProcessingStatus.UPLOADED,
            )
            db_session.add(test_file)
        await db_session.commit()

        # Выполнение
        response = await client.get('/api/v1/files')

        # Проверка
        assert response.status_code == 200
        data = response.json()
        items = data['items']
        assert len(items) >= 2
        our_ids = {f['id'] for f in files_data}
        found_ids = {item['id'] for item in items if item['id'] in our_ids}
        assert found_ids == our_ids

        titles_in_response = [item['title'] for item in items if item['id'] in our_ids]
        assert 'File 1' in titles_in_response
        assert 'File 2' in titles_in_response

    async def test_get_file_by_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест получения файла по ID."""
        # Подготовка
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='Specific File',
            original_name='specific.pdf',
            stored_name='stored_specific.pdf',
            mime_type='application/pdf',
            size=2048,
            processing_status=ProcessingStatus.UPLOADED,
            scan_status='completed',
            requires_attention=True,
        )
        db_session.add(test_file)
        await db_session.commit()

        # Выполнение
        response = await client.get(f'/api/v1/files/{file_id}')

        # Проверка
        assert response.status_code == 200
        data = response.json()
        assert data['id'] == file_id
        assert data['title'] == 'Specific File'
        assert data['scan_status'] == 'completed'
        assert data['requires_attention'] is True

    async def test_get_file_not_found(self, client: AsyncClient) -> None:
        """Тест получения несуществующего файла."""
        # Выполнение
        non_existent_id = str(uuid.uuid4())
        response = await client.get(f'/api/v1/files/{non_existent_id}')

        # Проверка
        assert response.status_code == 404

    async def test_list_files_response_structure(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест структуры ответа при получении списка файлов."""
        # Подготовка
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='Structured File',
            original_name='structured.zip',
            stored_name='stored_structured.zip',
            mime_type='application/zip',
            size=5120,
            processing_status=ProcessingStatus.UPLOADED,
            scan_details='All checks passed',
            metadata_json={'version': '1.0', 'author': 'test'},
        )
        db_session.add(test_file)
        await db_session.commit()

        # Выполнение
        response = await client.get('/api/v1/files')

        # Проверка структуры
        assert response.status_code == 200
        data = response.json()

        # Проверяем поля пагинации
        pagination_fields = ['items', 'page', 'page_size', 'total', 'total_pages']
        for field in pagination_fields:
            assert field in data, f'Поле {field} отсутствует в ответе'

        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

        file_item = data['items'][0]
        required_fields = [
            'id',
            'title',
            'original_name',
            'mime_type',
            'size',
            'processing_status',
            'scan_status',
            'scan_details',
            'metadata_json',
            'requires_attention',
            'created_at',
            'updated_at',
        ]

        for field in required_fields:
            assert field in file_item, f'Поле {field} отсутствует в ответе'
