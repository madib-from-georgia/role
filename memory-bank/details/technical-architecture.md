# Техническая архитектура системы

## 🏗️ Общая архитектура

```mermaid
graph TB
    subgraph "Пользователь"
        U[Актер/Режиссер]
    end
    
    subgraph "Frontend Layer"
        UI[React UI]
        Router[React Router]
        State[React Query]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Server]
        Auth[JWT Auth]
        Upload[File Upload]
    end
    
    subgraph "Business Logic"
        NLP[NLP Processor]
        Parser[File Parsers]
        Analyzer[Character Analyzer]
        Export[Export Service]
    end
    
    subgraph "Data Layer"
        DB[(SQLite Database)]
        Files[File Storage]
        Cache[JSON Cache]
    end
    
    U --> UI
    UI --> Router
    UI --> State
    State --> API
    API --> Auth
    API --> Upload
    API --> NLP
    API --> Parser
    API --> Analyzer
    API --> Export
    NLP --> DB
    Parser --> Files
    Analyzer --> DB
    Export --> DB
    DB --> Cache
```

## 🔧 Технический стек

### Frontend (React)
- **React 18** - основной UI фреймворк
- **TypeScript** - типизация и безопасность
- **Vite** - сборщик и dev-сервер
- **React Router** - маршрутизация
- **React Query** - управление состоянием и кэширование
- **React Hook Form** - работа с формами
- **Custom CSS** - стилизация без внешних библиотек

### Backend (Python)
- **FastAPI** - веб-фреймворк
- **Python 3.11+** - основной язык
- **SQLAlchemy** - ORM для работы с БД
- **Pydantic** - валидация данных
- **Uvicorn** - ASGI сервер
- **Python-multipart** - загрузка файлов

### База данных
- **SQLite** - локальная база данных
- **Alembic** - миграции схемы
- **JSON** - кэширование результатов

### NLP и обработка
- **spaCy** - основная NLP библиотека
- **PyPDF2** - парсинг PDF файлов
- **ebooklib** - парсинг EPUB
- **BeautifulSoup** - парсинг FB2/XML

## 📊 Архитектура данных

### Модель данных
```mermaid
erDiagram
    User ||--o{ Project : creates
    Project ||--o{ Text : contains
    Text ||--o{ Character : has
    Character ||--o{ ChecklistResponse : fills
    
    Checklist ||--o{ ChecklistSection : contains
    ChecklistSection ||--o{ ChecklistSubsection : contains
    ChecklistSubsection ||--o{ ChecklistQuestionGroup : contains
    ChecklistQuestionGroup ||--o{ ChecklistQuestion : contains
    ChecklistQuestion ||--o{ ChecklistAnswer : has
    ChecklistQuestion ||--o{ ChecklistResponse : answered_by
    ChecklistAnswer ||--o{ ChecklistResponse : selected_in
    
    User {
        int id PK
        string email
        string username
        string password_hash
        string full_name
        boolean is_active
        datetime created_at
    }
    
    Project {
        int id PK
        int user_id FK
        string title
        text description
        datetime created_at
    }
    
    Text {
        int id PK
        int project_id FK
        string filename
        string original_format
        text content
        json metadata
        datetime processed_at
    }
    
    Character {
        int id PK
        int text_id FK
        string name
        json aliases
        float importance_score
        json speech_attribution
        string gender
        datetime created_at
    }
    
    Checklist {
        int id PK
        string external_id
        string title
        text description
        string slug
        string icon
        int order_index
        text goal
        string version
    }
    
    ChecklistResponse {
        int id PK
        int question_id FK
        int character_id FK
        int answer_id FK
        text answer_text
        enum source_type
        text comment
        boolean is_current
        int version
    }
```

### Файловая структура
```
role/
├── frontend/                    # React приложение
│   ├── src/
│   │   ├── components/          # React компоненты
│   │   │   ├── auth/           # Авторизация
│   │   │   ├── checklists/     # Система чеклистов
│   │   │   ├── projects/       # Управление проектами
│   │   │   └── common/         # Общие компоненты
│   │   ├── pages/              # Страницы приложения
│   │   ├── services/           # API клиенты
│   │   ├── contexts/           # React контексты
│   │   ├── hooks/              # Кастомные хуки
│   │   ├── types/              # TypeScript типы
│   │   └── utils/              # Утилиты
│   ├── public/                 # Статические файлы
│   └── dist/                   # Собранное приложение
│
├── backend/                     # Python сервер
│   ├── app/
│   │   ├── main.py             # Точка входа FastAPI
│   │   ├── database/           # Модели и подключение к БД
│   │   │   ├── models/         # SQLAlchemy модели
│   │   │   └── crud/           # CRUD операции
│   │   ├── routers/            # API роутеры
│   │   ├── services/           # Бизнес-логика
│   │   │   ├── nlp/           # NLP обработка
│   │   │   ├── parsers/       # Парсеры файлов
│   │   │   └── export/        # Экспорт данных
│   │   ├── middleware/         # Middleware
│   │   ├── dependencies/       # Зависимости FastAPI
│   │   └── utils/              # Утилиты
│   ├── uploads/                # Загруженные файлы
│   ├── cache/                  # Кэш результатов
│   └── database.db             # SQLite база
│
├── memory-bank/                 # Банк знаний проекта
├── docs/                        # Документация
├── scripts/                     # Скрипты развертывания
└── shared/                      # Общие типы и утилиты
```

## 🔄 Потоки данных

### 1. Загрузка и обработка файла
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant API as Backend API
    participant Parser as File Parser
    participant NLP as NLP Processor
    participant DB as Database
    
    U->>UI: Загружает файл
    UI->>API: POST /api/projects/{id}/texts/upload
    API->>Parser: Парсинг файла
    Parser->>API: Извлеченный текст
    API->>DB: Сохранение текста
    API->>NLP: Запуск обработки
    NLP->>NLP: Извлечение персонажей
    NLP->>NLP: Атрибуция речи
    NLP->>DB: Сохранение персонажей
    API->>UI: Результат обработки
    UI->>U: Отображение персонажей
```

### 2. Анализ персонажа
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Frontend
    participant API as Backend API
    participant Analyzer as Character Analyzer
    participant AI as AI Service
    participant DB as Database
    
    U->>UI: Выбирает модуль анализа
    UI->>API: GET /api/characters/{id}/checklists/{type}
    API->>DB: Загрузка чеклиста
    DB->>API: Структура чеклиста
    API->>UI: Вопросы чеклиста
    UI->>U: Отображение формы
    U->>UI: Заполняет ответы
    UI->>API: POST /api/characters/{id}/checklists/{type}
    API->>DB: Сохранение ответов
    API->>Analyzer: Анализ ответов
    Analyzer->>AI: Запрос к AI (опционально)
    AI->>Analyzer: Рекомендации
    Analyzer->>DB: Сохранение результатов
    API->>UI: Результаты анализа
    UI->>U: Отображение результатов
```

## 🔐 Безопасность

### Аутентификация и авторизация
- **JWT токены** - Access (15 мин) + Refresh (7 дней)
- **bcrypt** - хеширование паролей с солью
- **Middleware** - проверка токенов на каждый запрос
- **CORS** - настроенный для production домена

### Защита данных
- **Row Level Security** - пользователи видят только свои данные
- **Валидация входных данных** - Pydantic схемы
- **Ограничение размера файлов** - максимум 100 МБ
- **Проверка типов файлов** - MIME-type validation

### Сетевая безопасность
- **HTTPS** - принудительное шифрование
- **Rate Limiting** - 100 запросов в минуту
- **Secure Headers** - CSP, HSTS, X-Frame-Options

## ⚡ Производительность

### Frontend оптимизации
- **Code Splitting** - разделение кода по роутам
- **Lazy Loading** - ленивая загрузка компонентов
- **React Query** - кэширование API запросов
- **Виртуализация** - для больших списков

### Backend оптимизации
- **Асинхронность** - FastAPI с async/await
- **Пулы соединений** - SQLAlchemy connection pooling
- **Кэширование** - JSON кэш для результатов NLP
- **Пагинация** - для больших наборов данных

### База данных
- **Индексы** - на часто запрашиваемые поля
- **Нормализация** - оптимальная структура таблиц
- **Batch операции** - для массовых вставок
- **Vacuum** - регулярная оптимизация SQLite

## 🔧 Развертывание

### Локальная разработка
```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Production развертывание
```bash
# Сборка frontend
cd frontend && npm run build

# Запуск через PM2
pm2 start ecosystem.config.js

# Nginx конфигурация
# Frontend: статические файлы
# Backend: reverse proxy на :8000
```

### Docker (планируется)
```dockerfile
# Multi-stage build
FROM node:18 AS frontend-build
FROM python:3.11 AS backend-build
FROM nginx:alpine AS production
```

## 📊 Мониторинг

### Логирование
- **Структурированные логи** - JSON формат
- **Уровни логирования** - DEBUG, INFO, WARNING, ERROR
- **Ротация логов** - по размеру и времени
- **Централизованное логирование** - все компоненты в одном месте

### Метрики
- **Время ответа API** - средние и перцентили
- **Использование памяти** - backend процессы
- **Размер базы данных** - рост во времени
- **Ошибки** - частота и типы

### Мониторинг здоровья
- **Health checks** - `/health` эндпоинт
- **Database connectivity** - проверка подключения к БД
- **File system** - доступность директорий
- **Memory usage** - использование памяти

## 🔄 Интеграции

### Внешние сервисы
- **AI сервисы** - Yandex GPT, OpenAI (опционально)
- **Email** - уведомления (планируется)
- **Cloud Storage** - резервное копирование (планируется)

### API интеграции
- **RESTful API** - основной интерфейс
- **WebSocket** - real-time обновления (планируется)
- **Webhooks** - интеграция с внешними системами (планируется)

## 🚀 Масштабирование

### Горизонтальное масштабирование
- **Микросервисная архитектура** - разделение на сервисы
- **Load Balancer** - распределение нагрузки
- **Database sharding** - разделение данных

### Вертикальное масштабирование
- **CPU оптимизация** - многопоточность для NLP
- **Memory optimization** - эффективное использование памяти
- **SSD storage** - быстрый доступ к данным

---

*Архитектура спроектирована для надежности, производительности и масштабируемости*