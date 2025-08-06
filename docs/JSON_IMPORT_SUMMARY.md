# Переход на JSON импорт чеклистов

## Что было сделано

### 1. Создан новый JSON парсер
- **Файл**: `backend/app/services/checklist_json_parser.py`
- **Функциональность**: Парсит JSON файлы с четкой структурой
- **Поддерживаемые поля**:
  - `title`: заголовок чеклиста
  - `goal`: цель чеклиста (объект с title и description)
  - `sections`: массив секций с подсекциями, группами вопросов и вопросами
  - Каждый вопрос содержит: `question`, `options`, `optionsType`, `source`, `hint`

### 2. Обновлены модели базы данных
- **Файл**: `backend/app/database/models/checklist.py`
- **Добавлено поле**: `source` в модель `ChecklistQuestion` (JSON поле)
- **Удалено поле**: `how_to_use` (не используется в JSON структуре)

### 3. Обновлены Pydantic схемы
- **Файл**: `backend/app/schemas/checklist.py`
- **Добавлено поле**: `source` в схемы вопросов
- **Удалено поле**: `how_to_use`

### 4. Обновлен сервис чеклистов
- **Файл**: `backend/app/services/checklist_service.py`
- **Изменен парсер**: с `ChecklistMarkdownParser` на `ChecklistJsonParser`
- **Обновлен импорт**: сохранение поля `source` в базу данных

### 5. Обновлен скрипт импорта
- **Файл**: `backend/scripts/import_checklists.py`
- **Изменены пути**: с `.md` на `.json` файлы
- **Обновлена документация**: добавлено описание JSON структуры

## Структура JSON файла

```json
{
  "title": "Заголовок чеклиста",
  "goal": {
    "title": "Цель",
    "description": "Описание цели"
  },
  "sections": [
    {
      "title": "Заголовок секции",
      "subsections": [
        {
          "title": "Заголовок подсекции",
          "groups": [
            {
              "title": "Заголовок группы",
              "questions": [
                {
                  "question": "Текст вопроса",
                  "options": ["вариант1", "вариант2"],
                  "optionsType": "single",
                  "source": ["text", "logic"],
                  "hint": "Подсказка"
                }
              ]
            }
          ],
          "examples": [
            {
              "text": "Пример из литературы",
              "value": "Объяснение примера"
            }
          ],
          "whyImportant": "Объяснение важности"
        }
      ]
    }
  ]
}
```

## Поддерживаемые типы

### Источники ответов (source)
- `text`: найдено в тексте
- `logic`: логически выведено
- `imagination`: придумано

### Типы вариантов (optionsType)
- `single`: один ответ
- `multiple`: несколько ответов
- `none`: без вариантов

## Результат

✅ **Успешно импортирован чеклист**: "Расширенный чеклист физического портрета персонажа для актера"
- **341 вопрос** в базе данных
- **7 секций**, **22 подсекции**, **84 группы вопросов**
- **Slug**: `physical`
- **Поле source** корректно сохраняется для каждого вопроса

## Использование

### Валидация файлов
```bash
python scripts/import_checklists.py --validate-only
```

### Импорт в базу данных
```bash
python scripts/import_checklists.py
```

### Проверка импортированных данных
```bash
python scripts/check_imported_data.py
``` 
