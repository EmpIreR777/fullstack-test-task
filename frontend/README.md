# FileGuard Frontend

Клиентская часть проекта **FileGuard** — React/Next.js приложение для управления файлами и мониторинга алертов безопасности. Интерфейс обеспечивает удобную работу с REST API backend.

## Содержание

- [Функциональность](#функциональность)
- [Технический стек](#технический-стек)
- [Структура проекта](#структура-проекта)
- [Предварительные требования](#предварительные-требования)
- [Установка и настройка](#установка-и-настройка)
- [Запуск приложения](#запуск-приложения)
- [Сборка для продакшена](#сборка-для-продакшена)
- [Docker](#docker)
- [Разработка](#разработка)

## Функциональность

- **Управление файлами**: загрузка, просмотр, обновление и удаление файлов
- **Алерты безопасности**: просмотр списка алертов с поиском по сообщению
- **Поиск**: поиск по файлам (по названию) и по алертам (по сообщению) через отдельные строки поиска
- **Загрузка файлов**: модальное окно для загрузки файлов с валидацией
- **Адаптивный интерфейс**: поддержка различных размеров экрана
- **Серверное состояние**: управление данными через React Query (кэширование, пагинация, refetch)
- **Обработка ошибок**: централизованная обработка ошибок API

## Технический стек

- **Next.js** 14+ (App Router)
- **TypeScript** — строгая типизация
- **Tailwind CSS** — стилизация компонентов
- **React Query (TanStack Query)** — управление серверным состоянием
- **Axios** — HTTP-клиент для API запросов
- **React** — функциональные компоненты с хуками
- **Docker** — контейнеризация

## Структура проекта

```
frontend/
├── .dockerignore              # Исключения для Docker
├── .gitignore                 # Исключения для Git
├── app.json                   # Конфигурация приложения
├── Dockerfile                 # Docker-образ (npm/yarn/pnpm)
├── Dockerfile.bun             # Docker-образ для Bun
├── next.config.ts             # Конфигурация Next.js
├── package-lock.json          # Lock-файл зависимостей
├── package.json               # Зависимости и скрипты
├── postcss.config.mjs         # Конфигурация PostCSS
├── tsconfig.json              # Конфигурация TypeScript
├── public/                    # Статические файлы
│   ├── favicon.ico
│   └── vercel.svg
└── src/                       # Исходный код
    ├── app/                   # App Router (Next.js 13+)
    │   ├── globals.css        # Глобальные стили
    │   ├── layout.tsx         # Корневой layout
    │   └── page.tsx           # Главная страница
    ├── components/            # React компоненты
    │   ├── features/          # Фичевые компоненты
    │   │   ├── alerts/        # Компоненты для алертов
    │   │   │   ├── AlertSearchBar.tsx
    │   │   │   └── AlertTable.tsx
    │   │   └── files/         # Компоненты для файлов
    │   │       ├── FilePagination.tsx
    │   │       ├── FileSearchBar.tsx
    │   │       ├── FileTable.tsx
    │   │       ├── FileTableRow.tsx
    │   │       ├── FileToolbar.tsx
    │   │       └── FileUploadModal.tsx
    │   ├── layout/            # Компоненты layout
    │   │   └── Header.tsx
    │   └── ui/                # Переиспользуемые UI компоненты
    │       ├── Badge.tsx
    │       ├── Button.tsx
    │       ├── Modal.tsx
    │       └── Spinner.tsx
    ├── hooks/                 # Кастомные React хуки
    │   ├── useAlerts.ts
    │   ├── useDeleteFile.ts
    │   ├── useFiles.ts
    │   ├── useUpdateFile.ts
    │   └── useUploadFile.ts
    ├── lib/                   # Вспомогательные утилиты
    │   ├── api-client.ts      # Axios конфигурация
    │   └── utils.ts           # Утилитарные функции
    ├── providers/             # React провайдеры
    │   └── QueryProvider.tsx  # Провайдер React Query
    ├── services/              # API сервисы
    │   ├── alert.service.ts
    │   └── file.service.ts
    └── types/                 # TypeScript типы
        ├── alert.ts
        └── file.ts
```

## Предварительные требования

- **Node.js** 18+ (рекомендуется 20+)
- **npm**, **yarn**, **pnpm** или **bun** (пакетные менеджеры)
- **Docker** (опционально, для контейнеризированной разработки)

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repo-url>
cd frontend
```

### 2. Установка зависимостей

```bash
# npm
npm install

# или yarn
yarn install

# или pnpm
pnpm install

# или bun
bun install
```

### 3. Настройка переменных окружения

Создайте файл `.env.local` в корне проекта:

```bash
cp .env.example .env.local  # если есть .env.example
```

Настройте переменные:

```dotenv
# URL backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Другие переменные
NEXT_PUBLIC_APP_NAME=FileGuard
```

## Запуск приложения

### Локальный запуск (development)

```bash
# npm
npm run dev

# или yarn
yarn dev

# или pnpm
pnpm dev

# или bun
bun run dev
```

Приложение будет доступно по адресу: http://localhost:3000

Страница автоматически обновляется при изменении файлов (Hot Reload).

### Отладка

Для отладки в браузере:

```bash
npm run dev
# Затем откройте в браузере: http://localhost:3000
```

## Сборка для продакшена

### Локальная сборка

```bash
# Создание оптимизированной сборки
npm run build

# Запуск продакшен-сервера
npm run start
```

### Сборка с Docker

#### Для npm/yarn/pnpm

```bash
# Сборка образа
docker build -t fileguard-frontend .

# Запуск контейнера
docker run -p 3000:3000 fileguard-frontend
```

#### Для Bun

```bash
# Сборка образа
docker build -f Dockerfile.bun -t fileguard-frontend .

# Запуск контейнера
docker run -p 3000:3000 fileguard-frontend
```

## Docker

### Использование готового Dockerfile

Проект содержит два Dockerfile:

- `Dockerfile` — для npm, yarn, pnpm
- `Dockerfile.bun` — для Bun runtime

### Конфигурация Next.js для Docker

Для работы standalone режима добавьте в `next.config.ts`:

```typescript
const nextConfig = {
  output: 'standalone',
};

export default nextConfig;
```

### Docker Compose

Используйте docker-compose из корня проекта:

```bash
# Запуск всех сервисов (backend + frontend + БД + Redis)
docker-compose -f docker-compose.dev.yml up
```

## Разработка

### Доступные скрипты

```bash
npm run dev          # Запуск сервера разработки
npm run build        # Сборка для продакшена
```

> Примечание: в `package.json` определены только скрипты `dev` и `build`. Скрипты `start` и `lint` не настроены.

### Структура компонентов

#### Feature Components (фичевые компоненты)

Содержат бизнес-логику и расположены в `src/components/features/`:

- **alerts/** — работа с алертами безопасности
  - `AlertSearchBar.tsx` — поисковая строка для алертов
  - `AlertTable.tsx` — таблица отображения алертов

- **files/** — работа с файлами
  - `FileSearchBar.tsx` — поисковая строка для файлов
  - `FileTable.tsx` — таблица файлов
  - `FileTableRow.tsx` — строка таблицы файлов
  - `FileUploadModal.tsx` — модальное окно загрузки

#### UI Components (переиспользуемые компоненты)

Базовые компоненты интерфейса в `src/components/ui/`:

- `Badge.tsx` — бейджи
- `Button.tsx` — кнопки
- `Modal.tsx` — модальные окна
- `Spinner.tsx` — индикаторы загрузки

### Кастомные хуки

Логика работы с API вынесена в кастомные хуки:

- `useFiles.ts` — получение пагинированного списка файлов (параметры: `page`, `query`)
- `useAlerts.ts` — получение пагинированного списка алертов
- `useUploadFile.ts` — загрузка файлов
- `useDeleteFile.ts` — удаление файлов
- `useUpdateFile.ts` — обновление названия файлов

### API сервисы

HTTP-клиент настроен в `src/lib/api-client.ts` на базе Axios:

- `src/services/file.service.ts` — методы для работы с файлами
- `src/services/alert.service.ts` — методы для работы с алертами

### TypeScript типы

Типы данных определены в `src/types/`:

- `file.ts` — типы для файлов
- `alert.ts` — типы для алертов

### Добавление новых зависимостей

```bash
# npm
npm install <package-name>

# yarn
yarn add <package-name>

# pnpm
pnpm add <package-name>

# bun
bun add <package-name>
```

## API Endpoints

Приложение взаимодействует с backend по следующим эндпоинтам:

### Файлы

- `GET /api/v1/files` — пагинированный список файлов (параметры: `page`, `query`)
- `POST /api/v1/files` — загрузка файла (multipart/form-data: `title`, `file`)
- `GET /api/v1/files/{file_id}` — получение файла по ID
- `PATCH /api/v1/files/{file_id}` — обновление названия файла
- `GET /api/v1/files/{file_id}/download` — скачивание файла
- `DELETE /api/v1/files/{file_id}` — удаление файла

### Алерты

- `GET /api/v1/alerts` — пагинированный список алертов (параметры: `page`, `query`)

## Вклад в проект

1. Сделайте fork репозитория
2. Создайте ветку для новой функциональности: `git checkout -b feature/your-feature`
3. Внесите изменения и убедитесь, что:
   - Приложение собирается без ошибок: `npm run build`
   - Добавлены типы для новых данных
4. Создайте Pull Request с описанием изменений

## Деплой

### Vercel (рекомендуется)

Проект оптимизирован для деплоя на Vercel:

1. Подключите репозиторий к Vercel
2. Настройте переменные окружения
3. Деплой произойдет автоматически при пуше в main

### Другие платформы

Приложение можно деплоить на любую платформу поддерживающую Next.js:
- Netlify
- AWS Amplify
- Digital Ocean App Platform
- Собственный сервер с Docker

## Лицензия

[Указать лицензию]
