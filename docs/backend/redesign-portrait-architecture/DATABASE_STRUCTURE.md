# Структура базы данных

Документация по структуре базы данных системы анализа литературных персонажей с использованием чеклистов.

## Обзор

База данных содержит **11 основных таблиц**, организованных в несколько логических групп для поддержки системы анализа персонажей литературных произведений.

## 1. Пользователи и аутентификация

### `users` - основная таблица пользователей
**Файл модели**: [`backend/app/database/models/user.py`](../../../backend/app/database/models/user.py)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `email` | String(255) | Уникальный email (индексированный) |
| `username` | String(100) | Уникальное имя пользователя (индексированный) |
| `password_hash` | String(255) | Хеш пароля |
| `full_name` | String(255) | Полное имя |
| `is_active` | Boolean | Статус активности |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

### `user_tokens` - JWT токены пользователей
**Файл модели**: [`backend/app/database/models/token.py`](../../../backend/app/database/models/token.py)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `user_id` | Integer (FK) | Ссылка на users.id |
| `token_hash` | String(255) | Хеш токена (индексированный) |
| `token_type` | String(20) | Тип токена (access/refresh) |
| `expires_at` | DateTime | Время истечения |
| `is_revoked` | Boolean | Статус отзыва |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

## 2. Проекты и тексты

### `projects` - проекты пользователей
**Файл модели**: [`backend/app/database/models/project.py`](../../../backend/app/database/models/project.py)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `user_id` | Integer (FK) | Ссылка на users.id |
| `title` | String(255) | Название проекта |
| `description` | Text | Описание |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

### `texts` - загруженные литературные произведения
**Файл модели**: [`backend/app/database/models/text.py`](../../../backend/app/database/models/text.py)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `project_id` | Integer (FK) | Ссылка на projects.id |
| `filename` | String(255) | Имя файла |
| `original_format` | String(10) | Формат файла (txt, pdf, fb2, epub) |
| `content` | Text | Извлеченный текст |
| `file_metadata` | JSON | Метаданные файла |
| `processed_at` | DateTime | Время NLP обработки |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

### `characters` - персонажи из произведений
**Файл модели**: [`backend/app/database/models/character.py`](../../../backend/app/database/models/character.py)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `text_id` | Integer (FK) | Ссылка на texts.id |
| `name` | String(255) | Имя персонажа |
| `aliases` | JSON | Альтернативные имена и прозвища |
| `importance_score` | Float | Оценка важности персонажа (0-1) |
| `speech_attribution` | JSON | Атрибуция речи от NLP |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

## 3. Система чеклистов (иерархическая структура)

**Файл модели**: [`backend/app/database/models/checklist.py`](../../../backend/app/database/models/checklist.py)

### `checklists` - основные чеклисты
Основные категории чеклистов (физический портрет, эмоциональный профиль и т.д.)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `title` | String(500) | Название чеклиста |
| `description` | Text | Описание |
| `slug` | String(100) | Уникальный идентификатор (индексированный) |
| `icon` | String(50) | Иконка |
| `order_index` | Integer | Порядок отображения |
| `is_active` | Boolean | Статус активности |
| `goal` | Text | Цель чеклиста |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

### `checklist_sections` - секции чеклистов (темы)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `checklist_id` | Integer (FK) | Ссылка на checklists.id |
| `title` | String(500) | Название секции |
| `number` | String(10) | Номер секции |
| `icon` | String(50) | Иконка |
| `order_index` | Integer | Порядок |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

### `checklist_subsections` - подсекции (разделы тем)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `section_id` | Integer (FK) | Ссылка на checklist_sections.id |
| `title` | String(500) | Название подсекции |
| `number` | String(20) | Номер подсекции |
| `order_index` | Integer | Порядок |
| `examples` | Text | Примеры из литературы |
| `why_important` | Text | Объяснение важности |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

### `checklist_question_groups` - группы вопросов

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `subsection_id` | Integer (FK) | Ссылка на checklist_subsections.id |
| `title` | String(500) | Название группы |
| `order_index` | Integer | Порядок |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

### `checklist_questions` - отдельные вопросы

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `question_group_id` | Integer (FK) | Ссылка на checklist_question_groups.id |
| `text` | Text | Текст вопроса |
| `hint` | Text | Подсказка |
| `order_index` | Integer | Порядок |
| `options` | JSON | Варианты ответов |
| `option_type` | String(20) | Тип вариантов (single/multiple/none) |
| `source` | JSON | Источники ответа (text/logic/imagination) |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

## 4. Ответы и история

### `checklist_responses` - ответы пользователей на вопросы

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `question_id` | Integer (FK) | Ссылка на checklist_questions.id |
| `character_id` | Integer (FK) | Ссылка на characters.id |
| `answer` | Text | Текст ответа |
| `source_type` | Enum | Тип источника (см. SourceType) |
| `comment` | Text | Комментарий/обоснование |
| `is_current` | Boolean | Является ли текущей версией |
| `version` | Integer | Номер версии |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

#### SourceType (Enum)
- `FOUND_IN_TEXT` - найдено в тексте
- `LOGICALLY_DERIVED` - логически выведено
- `IMAGINED` - придумано

### `checklist_response_history` - история изменений ответов

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | Integer (PK) | Первичный ключ |
| `response_id` | Integer (FK) | Ссылка на checklist_responses.id |
| `previous_answer` | Text | Предыдущий ответ |
| `previous_source_type` | Enum | Предыдущий тип источника |
| `previous_comment` | Text | Предыдущий комментарий |
| `previous_version` | Integer | Предыдущая версия |
| `change_reason` | String(200) | Причина изменения |
| `created_at` | DateTime | Время создания |
| `updated_at` | DateTime | Время последнего обновления |

## Особенности архитектуры

### 1. Иерархическая структура чеклистов
4-уровневая вложенность обеспечивает гибкую организацию вопросов:
```
Checklist → Section → Subsection → QuestionGroup → Question
```

### 2. Версионирование ответов
Система отслеживания изменений с полной историей:
- Каждый ответ имеет номер версии
- История изменений сохраняется в отдельной таблице
- Возможность отката к предыдущим версиям

### 3. Поддержка множественных форматов
Система поддерживает загрузку файлов в форматах:
- TXT
- PDF
- FB2
- EPUB

### 4. NLP интеграция
Специальные поля для результатов обработки естественного языка:
- `speech_attribution` - атрибуция речи персонажей
- `processed_at` - отметка времени обработки
- `importance_score` - автоматическая оценка важности персонажа

### 5. JSON поля
Гибкое хранение структурированных данных:
- Метаданные файлов
- Варианты ответов на вопросы
- Альтернативные имена персонажей
- Настройки источников ответов

### 6. Каскадное удаление
Настроено для поддержания целостности данных:
- Удаление пользователя → удаление всех его проектов
- Удаление проекта → удаление всех текстов
- Удаление текста → удаление всех персонажей
- Удаление персонажа → удаление всех ответов

## Миграции

Структура создана с помощью Alembic миграций:

1. **50b61de1fbfd** - Начальная миграция с полной структурой чеклистов
2. **7b07d6908d09** - Добавление поля `source` в таблицу `checklist_questions`

## Текущий статус

**Важно**: В текущей версии чеклисты временно отключены в коде (закомментированы в [`backend/app/database/models/all_models.py`](../../../backend/app/database/models/all_models.py)), но структура БД полностью готова для их использования.

Активные модели:
- ✅ User, UserToken
- ✅ Project, Text, Character
- ⏸️ Checklist (структура готова, но отключена)

## Связи между таблицами

```mermaid
erDiagram
    users ||--o{ projects : "has many"
    users ||--o{ user_tokens : "has many"
    projects ||--o{ texts : "has many"
    texts ||--o{ characters : "has many"
    
    checklists ||--o{ checklist_sections : "has many"
    checklist_sections ||--o{ checklist_subsections : "has many"
    checklist_subsections ||--o{ checklist_question_groups : "has many"
    checklist_question_groups ||--o{ checklist_questions : "has many"
    
    checklist_questions ||--o{ checklist_responses : "has many"
    characters ||--o{ checklist_responses : "has many"
    checklist_responses ||--o{ checklist_response_history : "has many"
