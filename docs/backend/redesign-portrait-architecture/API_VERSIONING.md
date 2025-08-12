# API документация: Система версионирования чеклистов

## Обзор

API для управления версиями чеклистов предоставляет полный набор эндпоинтов для:
- Проверки обновлений чеклистов
- Анализа изменений между версиями
- Обновления чеклистов с миграцией данных
- Управления пользовательскими ответами при изменениях

Базовый URL: `/api/checklist-versions`

## Эндпоинты

### 1. Проверка обновлений

**POST** `/api/checklist-versions/{checklist_id}/check-updates`

Проверяет наличие обновлений для чеклиста путем сравнения с новым JSON файлом.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста
- `json_file` (form-data, file) - JSON файл новой версии чеклиста

#### Ответ
```json
{
  "success": true,
  "data": {
    "has_updates": true,
    "is_new": false,
    "current_version": "1.0.0",
    "new_version": "2.0.0",
    "file_hash_changed": true,
    "changes": [
      "Обновление версии",
      "Изменения в структуре"
    ]
  }
}
```

#### Коды ответов
- `200` - Успешная проверка
- `404` - Чеклист не найден
- `500` - Ошибка сервера

---

### 2. Анализ изменений

**POST** `/api/checklist-versions/{checklist_id}/analyze-changes`

Выполняет детальный анализ изменений между текущей и новой версией чеклиста.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста
- `json_file` (form-data, file) - JSON файл новой версии

#### Ответ
```json
{
  "success": true,
  "data": {
    "checklist_changes": {
      "title_changed": true,
      "version_changed": true
    },
    "entity_matches": {
      "sections": [
        {
          "match_type": "exact",
          "old_entity_id": "section_1",
          "new_entity_id": "section_1",
          "confidence": 1.0
        }
      ],
      "questions": [
        {
          "match_type": "similar",
          "old_entity_id": "question_1",
          "new_entity_id": "question_1_updated",
          "confidence": 0.85
        }
      ]
    },
    "summary": {
      "total_changes": 5,
      "breaking_changes": 1,
      "new_entities": 2,
      "deleted_entities": 1
    }
  }
}
```

---

### 3. Обновление чеклиста

**POST** `/api/checklist-versions/{checklist_id}/update`

Обновляет чеклист до новой версии с автоматической миграцией данных.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста
- `json_file` (form-data, file) - JSON файл новой версии
- `force_update` (form-data, boolean, default: false) - Принудительное обновление
- `migrate_responses` (form-data, boolean, default: true) - Мигрировать ответы пользователей

#### Ответ
```json
{
  "success": true,
  "data": {
    "action": "updated",
    "message": "Чеклист успешно обновлен",
    "checklist_id": 1,
    "changes": ["Обновление версии", "Новые вопросы"],
    "migration_results": {
      "migrated_responses": 15,
      "archived_responses": 3,
      "failed_migrations": 0,
      "errors": []
    }
  }
}
```

---

### 4. История версий

**GET** `/api/checklist-versions/{checklist_id}/versions`

Получает историю версий чеклиста.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста

#### Ответ
```json
{
  "success": true,
  "data": [
    {
      "version": "2.0.0",
      "file_hash": "abc123...",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "is_current": true
    },
    {
      "version": "1.0.0",
      "file_hash": "def456...",
      "created_at": "2024-01-01T09:00:00Z",
      "updated_at": "2024-01-01T09:00:00Z",
      "is_current": false
    }
  ]
}
```

---

### 5. Анализ влияния миграции

**POST** `/api/checklist-versions/{checklist_id}/migration/analyze`

Анализирует влияние обновления чеклиста на существующие ответы пользователей.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста
- `json_file` (form-data, file) - JSON файл новой версии

#### Ответ
```json
{
  "success": true,
  "data": {
    "total_responses": 50,
    "affected_responses": 12,
    "migration_plan": {
      "question_1": {
        "strategy": "preserve_exact",
        "target_question_id": 1,
        "requires_user_action": false,
        "response_count": 25
      },
      "question_2": {
        "strategy": "migrate_similar",
        "target_question_id": 2,
        "requires_user_action": false,
        "response_count": 15
      },
      "question_3": {
        "strategy": "archive_deleted",
        "target_question_id": null,
        "requires_user_action": true,
        "response_count": 10
      }
    },
    "user_actions_required": [
      {
        "question_id": 3,
        "question_text": "Старый вопрос о росте...",
        "affected_users": 8,
        "reason": "Вопрос удален из чеклиста"
      }
    ]
  }
}
```

---

### 6. Выполнение миграции

**POST** `/api/checklist-versions/{checklist_id}/migration/execute`

Выполняет миграцию ответов пользователей согласно плану миграции.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста
- `migration_plan` (body, object) - План миграции из анализа
- `dry_run` (form-data, boolean, default: false) - Тестовый режим без изменений

#### Тело запроса
```json
{
  "question_1": {
    "strategy": "preserve_exact",
    "target_question_id": 1
  },
  "question_2": {
    "strategy": "migrate_similar", 
    "target_question_id": 2
  }
}
```

#### Ответ
```json
{
  "success": true,
  "data": {
    "migrated_responses": 40,
    "archived_responses": 10,
    "failed_migrations": 0,
    "errors": []
  }
}
```

---

### 7. Отчет о миграции

**GET** `/api/checklist-versions/{checklist_id}/migration/report`

Получает отчет о последней миграции чеклиста.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста

#### Ответ
```json
{
  "success": true,
  "data": {
    "checklist_id": 1,
    "checklist_title": "Физический портрет",
    "current_version": "2.0.0",
    "file_hash": "abc123...",
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

---

### 8. Задачи миграции пользователя

**GET** `/api/checklist-versions/user/{character_id}/migration-tasks`

Получает список задач миграции для конкретного пользователя.

#### Параметры
- `character_id` (path, integer) - ID персонажа
- `checklist_id` (query, integer, optional) - ID конкретного чеклиста

#### Ответ
```json
{
  "success": true,
  "data": [
    {
      "response_id": 123,
      "question_text": "Какой рост у персонажа?",
      "old_answer": "Высокий",
      "action_required": "review_and_update",
      "reason": "Вопрос был изменен или удален"
    }
  ]
}
```

---

### 9. Восстановление ответа

**POST** `/api/checklist-versions/user/response/{response_id}/restore`

Восстанавливает архивированный ответ пользователя.

#### Параметры
- `response_id` (path, integer) - ID ответа
- `new_answer_id` (form-data, integer, optional) - ID нового ответа

#### Ответ
```json
{
  "success": true,
  "message": "Ответ успешно восстановлен"
}
```

---

### 10. Проверка совместимости

**GET** `/api/checklist-versions/{checklist_id}/compatibility/{target_checklist_id}`

Проверяет совместимость между двумя версиями чеклиста.

#### Параметры
- `checklist_id` (path, integer) - ID исходного чеклиста
- `target_checklist_id` (path, integer) - ID целевого чеклиста

#### Ответ
```json
{
  "success": true,
  "data": {
    "compatible": true,
    "source_version": "1.0.0",
    "target_version": "2.0.0",
    "source_hash": "abc123...",
    "target_hash": "def456...",
    "same_structure": true
  }
}
```

---

### 11. Откат версии

**POST** `/api/checklist-versions/{checklist_id}/rollback/{target_version}`

Откатывает чеклист к предыдущей версии.

#### Параметры
- `checklist_id` (path, integer) - ID чеклиста
- `target_version` (path, string) - Целевая версия для отката

#### Ответ
```json
{
  "success": false,
  "message": "Функция отката пока не реализована"
}
```

## Коды ошибок

### Общие коды
- `200` - Успешный запрос
- `400` - Неверные параметры запроса
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера

### Специфичные ошибки
- `CHECKLIST_NOT_FOUND` - Чеклист не найден
- `INVALID_JSON_FORMAT` - Неверный формат JSON файла
- `VERSION_CONFLICT` - Конфликт версий
- `MIGRATION_FAILED` - Ошибка миграции данных
- `INCOMPATIBLE_STRUCTURE` - Несовместимая структура чеклиста

## Примеры использования

### Обновление чеклиста с проверкой

```bash
# 1. Проверить обновления
curl -X POST \
  http://localhost:8000/api/checklist-versions/1/check-updates \
  -F "json_file=@new_checklist.json"

# 2. Проанализировать изменения
curl -X POST \
  http://localhost:8000/api/checklist-versions/1/analyze-changes \
  -F "json_file=@new_checklist.json"

# 3. Проанализировать влияние на ответы
curl -X POST \
  http://localhost:8000/api/checklist-versions/1/migration/analyze \
  -F "json_file=@new_checklist.json"

# 4. Выполнить обновление
curl -X POST \
  http://localhost:8000/api/checklist-versions/1/update \
  -F "json_file=@new_checklist.json" \
  -F "migrate_responses=true"
```

### Работа с задачами пользователя

```bash
# Получить задачи пользователя
curl -X GET \
  http://localhost:8000/api/checklist-versions/user/123/migration-tasks?checklist_id=1

# Восстановить ответ
curl -X POST \
  http://localhost:8000/api/checklist-versions/user/response/456/restore \
  -F "new_answer_id=789"
```

## Безопасность

- Все эндпоинты требуют аутентификации
- Загрузка файлов ограничена размером и типом
- Валидация JSON структуры перед обработкой
- Логирование всех операций версионирования

## Ограничения

- Максимальный размер JSON файла: 10MB
- Поддерживаемые форматы: только JSON
- Одновременное обновление только одного чеклиста
- История версий хранится в базе данных (не файловая система)