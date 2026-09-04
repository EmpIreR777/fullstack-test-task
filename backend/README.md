# FileGuard Backend

Серверная часть проекта **FileGuard** — REST API для управления файлами и мониторинга алертов безопасности. Backend построен на FastAPI с использованием современных практик разработки.

## Содержание

- [Функциональность](#функциональность)
- [Технический стек](#технический-стек)
- [Структура проекта](#структура-проекта)
- [Предварительные требования](#предварительные-требования)
- [Установка и настройка](#установка-и-настройка)
- [Запуск приложения](#запуск-приложения)
- [Тестирование](#тестирование)
- [Миграции базы данных](#миграции-базы-данных)
- [Docker](#docker)
- [Разработка](#разработка)

## Функциональность

- **Управление файлами**: загрузка, скачивание, обновление и удаление файлов; загрузка стримится на диск чанками (aiofiles), физическое удаление файла выполняется только после коммита транзакции БД
- **Алерты безопасности**: автоматическое создание при сканировании файлов и просмотр через API (только чтение)
- **Асинхронная архитектура**: поддержка асинхронных операций с базой данных
- **Фоновые задачи**: обработка задач через Celery
- **Валидация данных**: строгая типизация через Pydantic схемы
- **Миграции БД**: управление схемой базы данных через Alembic

## Технический стек

- **Python** 3.14
- **FastAPI** — веб-фреймворк для создания API
- **SQLAlchemy** — ORM для работы с базой данных
- **Alembic** — миграции базы данных
- **Celery** — фоновые задачи
- **uv** — менеджер зависимостей и виртуальных окружений
- **pytest** — тестирование
- **Docker** — контейнеризация
- **pre-commit** — проверка качества кода

## Структура проекта

```
backend/
├── .pre-commit-config.yaml   # Конфигурация pre-commit хуков
├── .python-version           # Версия Python
├── Dockerfile                # Docker-образ для продакшена
├── Makefile                  # Шорткаты для разработки
├── alembic.ini               # Конфигурация Alembic
├── alembic_rev.sh            # Вспомогательный скрипт для миграций
├── entrypoint.sh             # Скрипт запуска контейнера
├── pyproject.toml            # Зависимости и конфигурация проекта
├── uv.lock                   # Lock-файл зависимостей
├── migrations/               # Миграции базы данных
│   ├── env.py
│   ├── script.py.mako
│   └── versions/             # Файлы миграций
├── src/                      # Исходный код
│   ├── app.py                # Точка входа в приложение
│   ├── run_migrations.py     # Скрипт запуска миграций
│   ├── celery/               # Фоновые задачи
│   │   ├── celery.py
│   │   ├── constants.py
│   │   └── tasks.py
│   ├── core/                 # Основная конфигурация
│   │   └── config.py
│   ├── dao/                  # Data Access Objects
│   │   ├── alert_dao.py
│   │   ├── base_dao.py
│   │   └── stored_file_dao.py
│   ├── db/                   # Работа с базой данных
│   │   ├── async_session_make.py
│   │   └── models.py
│   ├── routers/              # API роутеры
│   │   └── v1/
│   │       ├── alerts_router.py
│   │       └── files_router.py
│   ├── schemas/              # Pydantic схемы
│   │   ├── alert_schema.py
│   │   └── file_schema.py
│   ├── services/             # Бизнес-логика
│   │   ├── alert_service.py
│   │   └── stored_file_service.py
│   └── storage/              # Хранилище файлов
│       └── files/
    └── tests/                    # Тесты
    ├── conftest.py
    ├── test_alerts.py
    ├── test_files.py
    ├── test_files_extra.py
    └── test_scan_task.py
```

## Предварительные требования

- **Python** 3.14 (см. `.python-version`)
- **uv** — менеджер зависимостей ([установка](https://docs.astral.sh/uv/))
- **Docker** (опционально, для контейнеризированной разработки)
- **PostgreSQL** (используется как для локальной разработки, так и в Docker; SQLite не поддерживается)

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repo-url>
cd backend
```

### 2. Установка зависимостей

```bash
# Установка всех зависимостей включая dev-зависимости
uv sync --all-groups
```

### 3. Установка pre-commit хуков

```bash
uv run pre-commit install
```

### 4. Настройка переменных окружения

Создайте файл `backend/.env` на основе шаблона `.env.example` из корня репозитория:

```bash
cp ../.env.example .env
```

Для локального запуска (без Docker) укажите `localhost` в хостах; при запуске через Docker Compose используются имена сервисов `backend-db` и `backend-redis`:

```dotenv
# База данных (PostgreSQL)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fileguard

# Redis (брокер Celery)
REDIS_HOST=localhost
REDIS_PORT=6379
```

> `LOG_LEVEL`, `API_PREFIX`, `API_VERSION` имеют значения по умолчанию в `src/core/config.py` и могут не задаваться.

## Запуск приложения

### Локальный запуск (development)

```bash
# Запуск сервера разработки с автоперезагрузкой
uv run uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
```

API будет доступен по адресу: http://localhost:8000

Документация API (Swagger): http://localhost:8000/docs

### Запуск с Docker

```bash
# Сборка образа
docker build -t fileguard-backend .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env fileguard-backend
```

### Использование Makefile

```bash
make run           # Запуск Uvicorn dev-сервера (127.0.0.1:8000, --reload)
make sync-all      # Установка всех зависимостей через uv
make alembic-rev m="описание"  # Создание новой миграции Alembic
make alembic-up    # Применение миграций
make alembic-down  # Откат последней миграции
make lint          # Запуск pre-commit на всех файлах
make ruff          # Автоисправление и форматирование через Ruff
make mypy          # Статическая типизация через mypy
```

## Тестирование

### Запуск всех тестов

```bash
# Через uv
uv run pytest
```

### Запуск с покрытием

```bash
uv run pytest --cov=src --cov-report=html
```

### Запуск конкретного теста

```bash
uv run pytest tests/test_alerts.py -v
```

## Миграции базы данных

### Создание новой миграции

```bash
# Автогенерация миграции на основе изменений в моделях
uv run alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
# Применить все миграции до последней версии
uv run alembic upgrade head

# Откатить последнюю миграцию
uv run alembic downgrade -1
```

### Просмотр истории миграций

```bash
uv run alembic history
```

## Docker

### Сборка образа

```bash
docker build -t fileguard-backend .
```

### Запуск с docker-compose

Полный стек (backend + worker + БД + redis + frontend) запускается из корня проекта:

```bash
# Из корня репозитория
make up              # docker compose -f docker-compose.dev.yml up -d --build
```

### Остановка контейнеров

```bash
# Из корня репозитория
make down            # docker compose -f docker-compose.dev.yml down
```

## Разработка

### Линтинг и форматирование

```bash
# Запуск всех pre-commit хуков
uv run pre-commit run --all-files

# Или через Makefile
make lint
```

### Добавление новых зависимостей

```bash
# Основная зависимость
uv add <package-name>

# Dev-зависимость
uv add --dev <package-name>
```

### Альтернатива для фоновых задач: TaskIQ

В качестве замены Celery для фоновых задач можно рассмотреть библиотеку **[TaskIQ](https://github.com/taskiq-python/taskiq)**. Это лёгкая и полностью **асинхронная** библиотека, которая хорошо сочетается с асинхронным стеком проекта (FastAPI + `AsyncSession`/`AsyncEngine`).

Преимущества в контексте этого проекта:
- **Нативный async**: задачи пишутся как `async def`, что позволяет напрямую переиспользовать существующий `AsyncSession` и `DAO`-слой (`StoredFileDAO`, `AlertDAO`) без синхронных обёрток (`SyncSession`).
- **Легковесность**: минимум зависимостей и простая настройка по сравнению с Celery + отдельным брокером.

> Примечание: на данный момент проект использует Celery (см. `src/celery/`). Переход на TaskIQ потребовал бы переписывания `src/celery/tasks.py` на async-задачи и обновления воркера в `docker-compose`. Решение принимается при необходимости унифицировать весь код под асинхронный стиль.

### Структура API

API организован по версиям (v1):

- `GET /api/v1/files` — пагинированный список файлов (параметры: `page`, `query`)
- `POST /api/v1/files` — загрузка файла (multipart/form-data: `title`, `file`)
- `GET /api/v1/files/{file_id}` — получение файла по ID
- `PATCH /api/v1/files/{file_id}` — обновление названия файла
- `GET /api/v1/files/{file_id}/download` — скачивание файла
- `DELETE /api/v1/files/{file_id}` — удаление файла
- `GET /api/v1/alerts` — пагинированный список алертов (параметры: `page`, `query`)

> Примечание: алерты создаются автоматически фоновыми Celery-задачами при сканировании файлов. Через публичный API доступно только чтение списка алертов.

## Вклад в проект

1. Сделайте fork репозитория
2. Создайте ветку для новой функциональности: `git checkout -b feature/your-feature`
3. Внесите изменения и убедитесь, что:
   - Все тесты проходят: `uv run pytest`
   - Код проходит линтинг: `make lint`
   - Добавлены тесты для новой функциональности
4. Создайте Pull Request с описанием изменений

## Лицензия

[Указать лицензию]
