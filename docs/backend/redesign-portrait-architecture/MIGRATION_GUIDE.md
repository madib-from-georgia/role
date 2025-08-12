# Руководство по миграции: Переход на новую архитектуру чеклистов

## 📋 Обзор

Данное руководство описывает процесс миграции с старой архитектуры чеклистов на новую систему с поддержкой версионирования и гендерно-специфичных ответов.

## 🎯 Что изменилось

### Старая архитектура
```
Checklist
├── ChecklistSection
│   └── ChecklistSubsection
│       └── ChecklistQuestion
│           ├── options (JSON)
│           ├── option_type
│           └── hint
```

### Новая архитектура
```
Checklist
├── ChecklistSection
│   └── ChecklistSubsection
│       └── ChecklistQuestionGroup (НОВОЕ)
│           └── ChecklistQuestion
│               └── ChecklistAnswer (НОВОЕ)
│                   ├── value_male
│                   ├── value_female
│                   ├── exported_value_male
│                   └── exported_value_female
```

### Ключевые изменения

1. **Новый уровень иерархии**: `ChecklistQuestionGroup` для группировки связанных вопросов
2. **Отдельная модель ответов**: `ChecklistAnswer` вместо JSON поля `options`
3. **Гендерно-специфичные ответы**: отдельные значения для мужских и женских персонажей
4. **Версионирование**: поддержка `external_id`, `file_hash`, `version` для всех сущностей
5. **Новая структура ответов пользователей**: ссылка на `ChecklistAnswer` вместо текста

## 🔄 Процесс миграции

### Этап 1: Подготовка

#### 1.1 Резервное копирование
```bash
# Создать резервную копию базы данных
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db
```

#### 1.2 Проверка текущего состояния
```bash
# Проверить текущую версию схемы
alembic current

# Проверить количество существующих данных
sqlite3 database.db "SELECT COUNT(*) FROM checklists;"
sqlite3 database.db "SELECT COUNT(*) FROM checklist_responses;"
```

### Этап 2: Применение миграции

#### 2.1 Обновление кода
```bash
# Получить последние изменения
git pull origin main

# Установить зависимости
pip install -r requirements.txt
```

#### 2.2 Применение миграции базы данных
```bash
# Применить миграцию
alembic upgrade head

# Проверить успешность миграции
alembic current
```

#### 2.3 Проверка структуры
```bash
# Проверить новые таблицы
sqlite3 database.db ".tables"

# Проверить структуру новых таблиц
sqlite3 database.db ".schema checklist_answers"
sqlite3 database.db ".schema checklist_question_groups"
```

### Этап 3: Миграция данных

#### 3.1 Импорт новых чеклистов
```python
# Запустить тест импорта
python test_import.py
```

#### 3.2 Проверка импорта
```bash
# Проверить импортированные данные
sqlite3 database.db "SELECT id, title, version, file_hash FROM checklists;"
sqlite3 database.db "SELECT COUNT(*) FROM checklist_answers;"
```

### Этап 4: Тестирование

#### 4.1 Тестирование API
```bash
# Запустить сервер
python -m uvicorn app.main:app --reload

# Тестировать основные эндпоинты
curl http://localhost:8000/api/checklists/
curl http://localhost:8000/api/checklists/1/
```

#### 4.2 Тестирование версионирования
```python
# Запустить тесты версионирования
python test_versioning.py
```

## 📊 Сопоставление данных

### Модели

| Старая модель | Новая модель | Изменения |
|---------------|--------------|-----------|
| `ChecklistQuestion.options` | `ChecklistAnswer` | JSON → отдельная таблица |
| `ChecklistQuestion.option_type` | `ChecklistQuestion.answer_type` | Переименовано |
| `ChecklistQuestion.hint` | `ChecklistAnswer.hint` | Перенесено в ответы |
| `ChecklistResponse.answer` | `ChecklistResponse.answer_id` | Текст → ссылка на ответ |

### Поля

| Старое поле | Новое поле | Тип изменения |
|-------------|------------|---------------|
| `options` (JSON) | `ChecklistAnswer.value_male/female` | Разделение по полам |
| `hint` | `ChecklistAnswer.hint` | Перемещение |
| - | `external_id` | Новое поле |
| - | `file_hash` | Новое поле |
| - | `version` | Новое поле |

## 🔧 Обновление кода

### Backend изменения

#### 1. Обновление импортов
```python
# Старый импорт
from app.database.models.checklist import ChecklistQuestion

# Новый импорт
from app.database.models.checklist import ChecklistQuestion, ChecklistAnswer, ChecklistQuestionGroup
```

#### 2. Обновление запросов
```python
# Старый способ получения ответов
question = db.query(ChecklistQuestion).filter_by(id=1).first()
options = json.loads(question.options)

# Новый способ
question = db.query(ChecklistQuestion).options(
    selectinload(ChecklistQuestion.answers)
).filter_by(id=1).first()
answers = question.answers
```

#### 3. Обновление создания ответов
```python
# Старый способ
response = ChecklistResponse(
    question_id=1,
    character_id=1,
    answer="Высокий"
)

# Новый способ
response = ChecklistResponse(
    question_id=1,
    character_id=1,
    answer_id=5  # ID из ChecklistAnswer
)
```

### Frontend изменения

#### 1. Обновление API вызовов
```javascript
// Старый способ
const question = await api.get(`/questions/${id}`);
const options = JSON.parse(question.options);

// Новый способ
const question = await api.get(`/questions/${id}`);
const answers = question.answers; // Уже массив объектов
```

#### 2. Обновление отображения ответов
```javascript
// Старый способ
options.forEach(option => {
    console.log(option); // Строка
});

// Новый способ
answers.forEach(answer => {
    const value = character.gender === 'male' 
        ? answer.value_male 
        : answer.value_female;
    console.log(value);
});
```

#### 3. Обновление отправки ответов
```javascript
// Старый способ
const response = {
    question_id: 1,
    answer: "Высокий"
};

// Новый способ
const response = {
    question_id: 1,
    answer_id: selectedAnswer.id
};
```

## ⚠️ Важные моменты

### Обратная совместимость
- Старые API эндпоинты временно поддерживаются
- Постепенный переход на новые эндпоинты
- Автоматическая миграция существующих ответов

### Производительность
- Новая структура может потребовать больше JOIN операций
- Рекомендуется использовать `selectinload` для загрузки связанных данных
- Индексы созданы для оптимизации запросов

### Данные пользователей
- Существующие ответы автоматически мигрируются
- При конфликтах создаются задачи для ручной проверки
- История изменений сохраняется

## 🐛 Устранение проблем

### Частые ошибки

#### 1. Ошибка "No such column: checklist_responses.answer_id"
```bash
# Решение: применить миграцию
alembic upgrade head
```

#### 2. Ошибка "ChecklistAnswer object has no attribute 'value'"
```python
# Проблема: использование старого API
answer.value  # Неправильно

# Решение: использовать гендерно-специфичные поля
answer.value_male if gender == 'male' else answer.value_female
```

#### 3. Ошибка "Foreign key constraint failed"
```python
# Проблема: ссылка на несуществующий answer_id
response.answer_id = 999  # Неправильно

# Решение: проверить существование ответа
answer = db.query(ChecklistAnswer).filter_by(id=answer_id).first()
if answer:
    response.answer_id = answer.id
```

### Логи и отладка

#### Включение подробного логирования
```python
# В settings.py
DEBUG = True
DATABASE_ECHO = True  # Логирование SQL запросов
```

#### Проверка миграции
```bash
# Проверить статус миграции
alembic current -v

# Проверить историю миграций
alembic history

# Откатить миграцию (если нужно)
alembic downgrade -1
```

## 📈 Мониторинг

### Метрики для отслеживания
- Количество успешных миграций ответов
- Количество конфликтов при миграции
- Производительность новых API эндпоинтов
- Использование новых функций версионирования

### Рекомендуемые проверки
```bash
# Ежедневные проверки
sqlite3 database.db "SELECT COUNT(*) FROM checklist_responses WHERE is_current = 0;"
sqlite3 database.db "SELECT COUNT(*) FROM checklist_answers;"

# Еженедельные проверки
python test_versioning.py
curl -f http://localhost:8000/health
```

## 🎯 Следующие шаги

1. **Обновление фронтенда** - адаптация компонентов под новую структуру
2. **Тестирование интеграции** - полное тестирование системы
3. **Обучение пользователей** - документация для конечных пользователей
4. **Мониторинг производительности** - оптимизация запросов

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи приложения
2. Убедитесь в корректности миграции БД
3. Проверьте совместимость версий API
4. Обратитесь к команде разработки с подробным описанием ошибки

Миграция завершена успешно, когда:
- ✅ Все тесты проходят
- ✅ API возвращает корректные данные
- ✅ Пользовательские ответы сохранены
- ✅ Система версионирования работает