# API Endpoints

## 🌐 Общая информация

**Base URL**: `http://localhost:8000`  
**API Prefix**: `/api`  
**Документация**: `http://localhost:8000/docs` (Swagger UI)  
**Формат данных**: JSON  
**Авторизация**: JWT Bearer Token

## 🔐 Авторизация

Все эндпоинты, кроме авторизации, требуют JWT токен в заголовке:
```
Authorization: Bearer <access_token>
```

### Типы токенов
- **Access Token** - срок действия 15 минут
- **Refresh Token** - срок действия 7 дней

## 📋 Группы эндпоинтов

### 🔑 Авторизация (`/api/auth`)

#### POST `/api/auth/register`
Регистрация нового пользователя.

**Запрос**:
```json
{
    "email": "actor@example.com",
    "username": "actor123",
    "password": "securePassword123",
    "full_name": "Иван Петров"
}
```

**Ответ** (201):
```json
{
    "id": 1,
    "email": "actor@example.com",
    "username": "actor123",
    "full_name": "Иван Петров",
    "is_active": true,
    "created_at": "2025-08-15T12:00:00Z"
}
```

**Ошибки**:
- `400` - Валидация данных
- `409` - Email или username уже существует

#### POST `/api/auth/login`
Вход в систему.

**Запрос**:
```json
{
    "email": "actor@example.com",
    "password": "securePassword123"
}
```

**Ответ** (200):
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
        "id": 1,
        "email": "actor@example.com",
        "username": "actor123",
        "full_name": "Иван Петров"
    }
}
```

**Ошибки**:
- `401` - Неверные учетные данные
- `403` - Аккаунт заблокирован

#### POST `/api/auth/refresh`
Обновление access токена.

**Запрос**:
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Ответ** (200):
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900
}
```

#### POST `/api/auth/logout`
Выход из системы (отзыв токенов).

**Заголовки**: `Authorization: Bearer <access_token>`

**Ответ** (200):
```json
{
    "message": "Successfully logged out"
}
```

#### GET `/api/auth/me`
Получение информации о текущем пользователе.

**Заголовки**: `Authorization: Bearer <access_token>`

**Ответ** (200):
```json
{
    "id": 1,
    "email": "actor@example.com",
    "username": "actor123",
    "full_name": "Иван Петров",
    "is_active": true,
    "created_at": "2025-08-15T12:00:00Z"
}
```

#### PUT `/api/auth/me`
Обновление профиля пользователя.

**Заголовки**: `Authorization: Bearer <access_token>`

**Запрос**:
```json
{
    "full_name": "Иван Александрович Петров",
    "email": "new_email@example.com"
}
```

**Ответ** (200):
```json
{
    "id": 1,
    "email": "new_email@example.com",
    "username": "actor123",
    "full_name": "Иван Александрович Петров",
    "is_active": true,
    "updated_at": "2025-08-15T12:30:00Z"
}
```

### 📚 Проекты (`/api/projects`)

#### GET `/api/projects`
Получение списка проектов пользователя.

**Параметры запроса**:
- `page` (int, optional) - номер страницы (по умолчанию 1)
- `limit` (int, optional) - количество на странице (по умолчанию 20)
- `search` (string, optional) - поиск по названию

**Ответ** (200):
```json
{
    "items": [
        {
            "id": 1,
            "title": "Анализ Гамлета",
            "description": "Детальный анализ персонажей трагедии Шекспира",
            "created_at": "2025-08-15T10:00:00Z",
            "updated_at": "2025-08-15T12:00:00Z",
            "text_count": 1,
            "character_count": 5
        }
    ],
    "total": 1,
    "page": 1,
    "limit": 20,
    "pages": 1
}
```

#### POST `/api/projects`
Создание нового проекта.

**Запрос**:
```json
{
    "title": "Анализ Чайки",
    "description": "Анализ персонажей пьесы А.П. Чехова"
}
```

**Ответ** (201):
```json
{
    "id": 2,
    "title": "Анализ Чайки",
    "description": "Анализ персонажей пьесы А.П. Чехова",
    "created_at": "2025-08-15T13:00:00Z",
    "updated_at": "2025-08-15T13:00:00Z"
}
```

#### GET `/api/projects/{project_id}`
Получение детальной информации о проекте.

**Ответ** (200):
```json
{
    "id": 1,
    "title": "Анализ Гамлета",
    "description": "Детальный анализ персонажей трагедии Шекспира",
    "created_at": "2025-08-15T10:00:00Z",
    "updated_at": "2025-08-15T12:00:00Z",
    "texts": [
        {
            "id": 1,
            "filename": "hamlet.pdf",
            "original_format": "pdf",
            "processed_at": "2025-08-15T10:30:00Z",
            "character_count": 5
        }
    ]
}
```

#### PUT `/api/projects/{project_id}`
Обновление проекта.

**Запрос**:
```json
{
    "title": "Анализ Гамлета (обновленный)",
    "description": "Расширенный анализ с психологическими модулями"
}
```

#### DELETE `/api/projects/{project_id}`
Удаление проекта.

**Ответ** (204): Нет содержимого

### 📄 Тексты (`/api/texts`)

#### POST `/api/projects/{project_id}/texts/upload`
Загрузка файла произведения.

**Content-Type**: `multipart/form-data`

**Параметры**:
- `file` (file) - файл произведения (TXT, PDF, FB2, EPUB)
- `auto_process` (bool, optional) - автоматически обработать после загрузки

**Ответ** (201):
```json
{
    "id": 1,
    "filename": "hamlet.pdf",
    "original_format": "pdf",
    "metadata": {
        "file_size": 1024000,
        "page_count": 150,
        "word_count": 50000
    },
    "created_at": "2025-08-15T10:00:00Z",
    "processed_at": null
}
```

**Ошибки**:
- `400` - Неподдерживаемый формат файла
- `413` - Файл слишком большой (>100MB)

#### GET `/api/projects/{project_id}/texts`
Получение списка текстов проекта.

**Ответ** (200):
```json
{
    "items": [
        {
            "id": 1,
            "filename": "hamlet.pdf",
            "original_format": "pdf",
            "processed_at": "2025-08-15T10:30:00Z",
            "character_count": 5,
            "metadata": {
                "word_count": 50000,
                "page_count": 150
            }
        }
    ]
}
```

#### GET `/api/texts/{text_id}`
Получение информации о тексте.

**Ответ** (200):
```json
{
    "id": 1,
    "filename": "hamlet.pdf",
    "original_format": "pdf",
    "content": "HAMLET\n\nACT I\nSCENE I...",
    "metadata": {
        "file_size": 1024000,
        "page_count": 150,
        "word_count": 50000,
        "character_count": 300000,
        "language": "en"
    },
    "processed_at": "2025-08-15T10:30:00Z",
    "characters": [
        {
            "id": 1,
            "name": "Hamlet",
            "importance_score": 1.0,
            "gender": "male"
        }
    ]
}
```

#### POST `/api/texts/{text_id}/process`
Запуск обработки текста (извлечение персонажей).

**Ответ** (202):
```json
{
    "message": "Text processing started",
    "task_id": "abc123",
    "estimated_time": 60
}
```

#### DELETE `/api/texts/{text_id}`
Удаление текста.

**Ответ** (204): Нет содержимого

### 👥 Персонажи (`/api/characters`)

#### GET `/api/texts/{text_id}/characters`
Получение списка персонажей текста.

**Параметры запроса**:
- `min_importance` (float, optional) - минимальная важность (0.0-1.0)
- `gender` (string, optional) - фильтр по полу (male, female, unknown)

**Ответ** (200):
```json
{
    "items": [
        {
            "id": 1,
            "name": "Hamlet",
            "aliases": ["Гамлет", "принц Гамлет", "принц датский"],
            "importance_score": 1.0,
            "gender": "male",
            "speech_attribution": {
                "total_lines": 342,
                "total_words": 15420,
                "first_appearance": "Act 1, Scene 2"
            },
            "analysis_progress": {
                "completed_modules": 3,
                "total_modules": 20,
                "percentage": 15.0
            }
        }
    ]
}
```

#### GET `/api/characters/{character_id}`
Получение детальной информации о персонаже.

**Ответ** (200):
```json
{
    "id": 1,
    "name": "Hamlet",
    "aliases": ["Гамлет", "принц Гамлет"],
    "importance_score": 1.0,
    "gender": "male",
    "speech_attribution": {
        "total_lines": 342,
        "total_words": 15420,
        "first_appearance": "Act 1, Scene 2",
        "last_appearance": "Act 5, Scene 2",
        "speech_patterns": {
            "formal": 0.7,
            "emotional": 0.8,
            "philosophical": 0.9
        }
    },
    "text": {
        "id": 1,
        "filename": "hamlet.pdf",
        "title": "Hamlet"
    }
}
```

#### PUT `/api/characters/{character_id}`
Обновление информации о персонаже.

**Запрос**:
```json
{
    "name": "Prince Hamlet",
    "aliases": ["Гамлет", "принц Гамлет", "принц датский", "сын короля"],
    "gender": "male"
}
```

### 📋 Чеклисты (`/api/checklists`)

#### GET `/api/checklists`
Получение списка всех доступных чеклистов.

**Ответ** (200):
```json
{
    "items": [
        {
            "id": 1,
            "external_id": "physical-portrait",
            "title": "Физический портрет персонажа",
            "description": "Детальное описание внешности и физических проявлений",
            "slug": "physical-portrait",
            "icon": "🎭",
            "order_index": 1,
            "goal": "Создание детального описания внешности и физических проявлений персонажа",
            "version": "1.0.0",
            "is_active": true
        }
    ]
}
```

#### GET `/api/characters/{character_id}/checklists`
Получение всех чеклистов персонажа с прогрессом.

**Ответ** (200):
```json
{
    "character": {
        "id": 1,
        "name": "Hamlet"
    },
    "checklists": [
        {
            "id": 1,
            "title": "Физический портрет персонажа",
            "slug": "physical-portrait",
            "icon": "🎭",
            "progress": {
                "answered_questions": 15,
                "total_questions": 45,
                "percentage": 33.3,
                "is_completed": false
            }
        }
    ]
}
```

#### GET `/api/characters/{character_id}/checklists/{checklist_slug}`
Получение структуры чеклиста с ответами персонажа.

**Ответ** (200):
```json
{
    "checklist": {
        "id": 1,
        "title": "Физический портрет персонажа",
        "description": "Детальное описание внешности",
        "goal": "Создание детального описания внешности персонажа"
    },
    "sections": [
        {
            "id": 1,
            "title": "ВНЕШНОСТЬ И ФИЗИЧЕСКИЕ ДАННЫЕ",
            "number": "1",
            "icon": "📏",
            "subsections": [
                {
                    "id": 1,
                    "title": "Телосложение и антропометрия",
                    "number": "1.1",
                    "examples": "Примеры из литературы...",
                    "why_important": "Почему это важно...",
                    "question_groups": [
                        {
                            "id": 1,
                            "title": "Рост и пропорции тела",
                            "questions": [
                                {
                                    "id": 1,
                                    "text": "Какой рост у персонажа?",
                                    "answer_type": "single",
                                    "answers": [
                                        {
                                            "id": 1,
                                            "external_id": "short",
                                            "value_male": "низкий",
                                            "value_female": "низкая",
                                            "hint": "Рост влияет на самооценку"
                                        }
                                    ],
                                    "response": {
                                        "id": 1,
                                        "answer_id": 2,
                                        "answer_text": null,
                                        "source_type": "FOUND_IN_TEXT",
                                        "comment": "Цитата из текста: '...'"
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}
```

#### POST `/api/characters/{character_id}/checklists/{checklist_slug}`
Сохранение ответов на чеклист.

**Запрос**:
```json
{
    "responses": [
        {
            "question_id": 1,
            "answer_id": 2,
            "source_type": "FOUND_IN_TEXT",
            "comment": "Цитата: 'высокий принц'"
        },
        {
            "question_id": 2,
            "answer_text": "Свободный ответ",
            "source_type": "LOGICALLY_DERIVED",
            "comment": "Выведено из поведения"
        }
    ]
}
```

**Ответ** (200):
```json
{
    "message": "Responses saved successfully",
    "saved_count": 2,
    "updated_count": 0
}
```

#### PUT `/api/characters/{character_id}/checklists/{checklist_slug}`
Обновление ответов на чеклист.

**Запрос**: Аналогичен POST

**Ответ** (200):
```json
{
    "message": "Responses updated successfully",
    "saved_count": 1,
    "updated_count": 1
}
```

### 📄 Экспорт (`/api/export`)

#### GET `/api/characters/{character_id}/export/pdf`
Экспорт анализа персонажа в PDF.

**Параметры запроса**:
- `format` (string, optional) - формат отчета (detailed, compact, summary)
- `modules` (string, optional) - список модулей через запятую

**Ответ** (200):
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="hamlet_analysis.pdf"

[PDF content]
```

#### GET `/api/characters/{character_id}/export/docx`
Экспорт анализа персонажа в DOCX.

**Параметры запроса**: Аналогичны PDF

**Ответ** (200):
```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="hamlet_analysis.docx"

[DOCX content]
```

#### GET `/api/characters/{character_id}/export/json`
Экспорт анализа персонажа в JSON.

**Ответ** (200):
```json
{
    "character": {
        "name": "Hamlet",
        "text": "Hamlet by William Shakespeare"
    },
    "analysis": {
        "physical_portrait": {
            "completed": true,
            "responses": [...]
        },
        "emotional_profile": {
            "completed": false,
            "responses": [...]
        }
    },
    "export_metadata": {
        "exported_at": "2025-08-15T15:00:00Z",
        "format": "json",
        "version": "1.0.0"
    }
}
```

## 🔍 Служебные эндпоинты

### GET `/`
Корневая страница API.

**Ответ** (200):
```json
{
    "message": "Character Analysis API",
    "version": "1.0.0",
    "docs_url": "/docs"
}
```

### GET `/health`
Проверка состояния сервиса.

**Ответ** (200):
```json
{
    "status": "healthy",
    "timestamp": "2025-08-15T15:00:00Z",
    "database": "connected",
    "version": "1.0.0"
}
```

## ⚠️ Обработка ошибок

### Стандартные HTTP коды
- `200` - Успешный запрос
- `201` - Ресурс создан
- `204` - Успешно, нет содержимого
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `409` - Конфликт (дублирование)
- `413` - Слишком большой запрос
- `422` - Ошибка валидации данных
- `429` - Превышен лимит запросов
- `500` - Внутренняя ошибка сервера

### Формат ошибок
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Validation failed",
        "details": [
            {
                "field": "email",
                "message": "Invalid email format"
            }
        ]
    },
    "timestamp": "2025-08-15T15:00:00Z",
    "path": "/api/auth/register"
}
```

## 🔒 Безопасность

### Rate Limiting
- **100 запросов в минуту** на IP адрес
- **1000 запросов в час** на пользователя
- **10 попыток входа в час** на email

### Валидация данных
- **Pydantic схемы** для всех входных данных
- **Санитизация** пользовательского ввода
- **Проверка типов файлов** по MIME-type
- **Ограничение размера** запросов и файлов

### CORS
```python
# Настройки CORS для production
CORS_ORIGINS = [
    "https://your-domain.com",
    "http://localhost:5173"  # для разработки
]
```

---

*API спроектирован для удобства использования, безопасности и производительности*