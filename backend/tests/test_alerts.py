import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.enums import ProcessingStatus
from src.db.models import Alert, StoredFile


@pytest.mark.asyncio
class TestAlertsIntegration:
    """Интеграционные тесты для endpoint'ов алертов."""

    async def test_list_alerts_empty(self, client: AsyncClient) -> None:
        """Тест получения списка алертов (проверка структуры пагинированного ответа)."""
        response = await client.get('/api/v1/alerts')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert isinstance(data['items'], list)
        assert 'page' in data
        assert 'page_size' in data
        assert 'total' in data
        assert 'total_pages' in data

    async def test_list_alerts_with_data(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест получения списка алертов с данными."""
        # Подготовка: создание файла и алерта
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='Suspicious File',
            original_name='suspicious.exe',
            stored_name='stored_suspicious.exe',
            mime_type='application/x-msdownload',
            size=512,
            processing_status=ProcessingStatus.UPLOADED,
            requires_attention=True,
        )
        db_session.add(test_file)
        await db_session.flush()

        alert = Alert(
            file_id=file_id,
            level='high',
            message='Potential malware detected',
        )
        db_session.add(alert)
        await db_session.commit()

        # Выполнение
        response = await client.get('/api/v1/alerts')

        # Проверка
        assert response.status_code == 200
        data = response.json()
        items = data['items']
        assert len(items) >= 1
        # Ищем наш алерт среди всех (могут быть данные из других тестов/данных)
        our_alert = next(item for item in items if item['file_id'] == file_id)
        assert our_alert['file_id'] == file_id
        assert our_alert['level'] == 'high'
        assert our_alert['message'] == 'Potential malware detected'

    async def test_list_alerts_multiple_records(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест получения списка нескольких алертов."""
        # Подготовка: создание нескольких файлов и алертов
        file_ids = [str(uuid.uuid4()) for _ in range(2)]

        for file_id in file_ids:
            test_file = StoredFile(
                id=file_id,
                title=f'File {file_id}',
                original_name=f'file_{file_id}.bin',
                stored_name=f'stored_{file_id}.bin',
                mime_type='application/octet-stream',
                size=1024,
                processing_status=ProcessingStatus.UPLOADED,
            )
            db_session.add(test_file)
        await db_session.flush()

        alerts_data = [
            {
                'file_id': file_ids[0],
                'level': 'critical',
                'message': 'Critical threat detected',
            },
            {
                'file_id': file_ids[1],
                'level': 'low',
                'message': 'Suspicious script found',
            },
        ]

        for alert_data in alerts_data:
            alert = Alert(
                file_id=alert_data['file_id'],
                level=alert_data['level'],
                message=alert_data['message'],
            )
            db_session.add(alert)
        await db_session.commit()

        # Выполнение
        response = await client.get('/api/v1/alerts')

        # Проверка
        assert response.status_code == 200
        data = response.json()
        items = data['items']
        assert len(items) >= 2
        # Проверяем что наши алерты присутствуют в ответе
        our_file_ids = set(file_ids)
        found_file_ids = {item['file_id'] for item in items if item['file_id'] in our_file_ids}
        assert found_file_ids == our_file_ids

        levels_in_response = [item['level'] for item in items if item['file_id'] in our_file_ids]
        assert 'critical' in levels_in_response
        assert 'low' in levels_in_response

    async def test_list_alerts_response_structure(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест структуры ответа при получении списка алертов."""
        # Подготовка
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='Test File',
            original_name='test.pdf',
            stored_name='stored_test.pdf',
            mime_type='application/pdf',
            size=256,
            processing_status=ProcessingStatus.UPLOADED,
        )
        db_session.add(test_file)
        await db_session.flush()

        alert = Alert(
            file_id=file_id,
            level='medium',
            message='Minor issue detected',
        )
        db_session.add(alert)
        await db_session.commit()

        # Выполнение
        response = await client.get('/api/v1/alerts')

        # Проверка структуры пагинированного ответа
        assert response.status_code == 200
        data = response.json()

        # Проверяем поля пагинации
        pagination_fields = ['items', 'page', 'page_size', 'total', 'total_pages']
        for field in pagination_fields:
            assert field in data, f'Поле {field} отсутствует в ответе'

        assert isinstance(data['items'], list)
        assert len(data['items']) > 0

        # Проверяем структуру элемента алерта
        alert_item = data['items'][0]
        required_fields = ['id', 'file_id', 'level', 'message', 'created_at']

        for field in required_fields:
            assert field in alert_item, f'Поле {field} отсутствует в ответе'

    async def test_list_alerts_levels_variety(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест получения алертов с разными уровнями серьезности."""
        # Подготовка: создаём файл и 3 алерта (помещается на 1 страницу при page_size=3)
        file_id = str(uuid.uuid4())
        test_file = StoredFile(
            id=file_id,
            title='Multi-alert File',
            original_name='multi.zip',
            stored_name='stored_multi.zip',
            mime_type='application/zip',
            size=2048,
            processing_status=ProcessingStatus.UPLOADED,
        )
        db_session.add(test_file)
        await db_session.flush()

        levels = ['low', 'medium', 'high']
        for _, level in enumerate(levels):
            alert = Alert(
                file_id=file_id,
                level=level,
                message=f'{level.capitalize()} severity alert',
            )
            db_session.add(alert)
        await db_session.commit()

        # Выполнение
        response = await client.get('/api/v1/alerts')

        # Проверка
        assert response.status_code == 200
        data = response.json()
        items = data['items']
        # Ищем алерты с нашим file_id
        our_alerts = [item for item in items if item['file_id'] == file_id]
        assert len(our_alerts) == 3
        response_levels = sorted([item['level'] for item in our_alerts])
        assert response_levels == sorted(levels)

    async def test_search_alerts_by_file_id(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ) -> None:
        """Тест поиска алертов по file_id через query-параметр."""
        # Подготовка: создаём два файла с алертами
        target_file_id = str(uuid.uuid4())
        other_file_id = str(uuid.uuid4())

        for file_id in (target_file_id, other_file_id):
            test_file = StoredFile(
                id=file_id,
                title=f'File {file_id}',
                original_name=f'file_{file_id}.bin',
                stored_name=f'stored_{file_id}.bin',
                mime_type='application/octet-stream',
                size=1024,
                processing_status=ProcessingStatus.UPLOADED,
            )
            db_session.add(test_file)
        await db_session.flush()

        db_session.add(Alert(file_id=target_file_id, level='high', message='Target alert'))
        db_session.add(Alert(file_id=other_file_id, level='low', message='Other alert'))
        await db_session.commit()

        # Выполнение: ищем только по target_file_id
        response = await client.get('/api/v1/alerts', params={'query': target_file_id})

        # Проверка
        assert response.status_code == 200
        data = response.json()
        items = data['items']
        assert len(items) >= 1
        assert all(item['file_id'] == target_file_id for item in items)
        assert any(item['message'] == 'Target alert' for item in items)
