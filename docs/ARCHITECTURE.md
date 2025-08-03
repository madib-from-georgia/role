# Архитектура веб-приложения для анализа персонажей

## Обзор системы

Веб-приложение для актеров, которое анализирует художественные произведения и создает детальные характеристики персонажей.

## Упрощенный технический стек

### Frontend

- **React 18** с TypeScript
- **Vite** для сборки и dev-сервера
- **Tailwind CSS** для стилизации
- **React Query** для управления состоянием
- **React Hook Form** для работы с формами

### Backend

- **Python** с FastAPI
- **SQLite** для локального хранения данных
- **SQLAlchemy** для работы с базой данных
- **Python-multipart** для загрузки файлов

### ML сервисы

- **Библиотеки парсинга**: pdf-parse, epub-parser, fb2-parser

### Локальное хранение

- **SQLite база данных** - один файл `database.db`
- **Файловая система** - для хранения загруженных файлов
- **JSON файлы** - для конфигурации и кэша

## Архитектура локального приложения

### Структура проекта

```
role/
├── frontend/                 # React приложение
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # Python FastAPI сервер
│   ├── app/
│   ├── database.db          # SQLite база
│   ├── uploads/             # Загруженные файлы
│   ├── cache/               # Кэш результатов
│   └── requirements.txt
├── shared/                   # Общие типы
│   └── types.ts
├── scripts/                  # Скрипты запуска
│   ├── start.js
│   └── install.js
├── package.json             # Root package.json
└── README.md
```

## Локальная архитектура системы

### Компоненты системы

1. **Локальный веб-сервер** (FastAPI на порту 8000)
2. **Веб-интерфейс** (React на порту 3000)
3. **SQLite база данных** (файл database.db)
4. **Файловое хранилище** (папка uploads/)
5. **Кэш в памяти** (Python dict)

### Поток данных

```
Пользователь → React UI → FastAPI → SQLite + AI API → Результат
```

### API Endpoints (упрощенные)

#### Проекты

```
GET /api/projects           # Список проектов
POST /api/projects          # Создать проект
GET /api/projects/:id       # Получить проект
PUT /api/projects/:id       # Обновить проект
DELETE /api/projects/:id    # Удалить проект
```

#### Тексты

```
POST /api/projects/:id/texts/upload  # Загрузить файл
GET /api/projects/:id/texts          # Список текстов проекта
GET /api/texts/:id                   # Получить текст
DELETE /api/texts/:id                # Удалить текст
POST /api/texts/:id/process          # Обработать текст
```

#### Персонажи

```
GET /api/texts/:id/characters        # Персонажи в тексте
GET /api/characters/:id              # Данные персонажа
POST /api/characters/:id/analyze     # Анализировать персонажа
GET /api/characters/:id/analyses     # Результаты анализа
```

## Упрощенная структура backend

```
backend/app/
├── main.py                  # Главный файл приложения FastAPI
├── database/
│   ├── connection.py        # Подключение к SQLite
│   ├── migrations.py        # Создание таблиц
│   └── models/
│       ├── project.py
│       ├── text.py
│       ├── character.py
│       └── analysis.py
├── routers/
│   ├── projects.py
│   ├── texts.py
│   ├── characters.py
│   └── analysis.py
├── services/
│   ├── file_parser.py
│   ├── character_extractor.py
│   └── analysis.py
├── parsers/
│   ├── txt_parser.py
│   ├── pdf_parser.py
│   ├── fb2_parser.py
│   └── epub_parser.py
├── utils/
│   ├── text_processing.py
│   ├── cache.py
│   └── file_utils.py
└── config/
```

## Упрощенная установка и использование

### Для пользователя

1. **Скачать архив** с приложением
2. **Распаковать** в любую папку
3. **Запустить** `python scripts/install.py` (один раз)
4. **Настроить** API ключи в файле `.env`
5. **Запустить** `python scripts/start.py`
6. **Открыть** http://localhost:3000 в браузере

### Требования к системе

- **Python** 3.11+
- **pip** (менеджер пакетов Python)
- **Node.js** 18+ (для frontend)
- **Интернет** для AI API
- **5 ГБ** свободного места
