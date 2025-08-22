# Скрипты для управления проектом

## 🚀 Запуск сервисов

### Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend (React)
```bash
cd frontend
npm run dev
```

## 🔐 Управление авторизацией

### Основной скрипт: `toggle-auth.sh`

Удобный скрипт для полного управления авторизацией в проекте.

#### Команды:
```bash
./scripts/toggle-auth.sh status     # Показать текущее состояние
./scripts/toggle-auth.sh enable     # Включить авторизацию
./scripts/toggle-auth.sh disable    # Отключить авторизацию
./scripts/toggle-auth.sh restart    # Перезапустить сервисы
./scripts/toggle-auth.sh help       # Показать справку
```

#### Примеры использования:
```bash
# Проверить состояние
./scripts/toggle-auth.sh status

# Отключить авторизацию для разработки
./scripts/toggle-auth.sh disable

# Включить авторизацию для production
./scripts/toggle-auth.sh enable

# Перезапустить сервисы после изменения
./scripts/toggle-auth.sh restart
```

### 📋 Состояния авторизации

#### 🔴 Авторизация включена
- **Backend**: `auth_enabled: bool = True`
- **Frontend**: `authEnabled: true`
- **Поведение**: Все API запросы требуют JWT токены
- **Использование**: Production, тестирование безопасности

#### 🟢 Авторизация отключена
- **Backend**: `auth_enabled: bool = False`
- **Frontend**: `authEnabled: false`
- **Поведение**: Все API запросы работают без токенов
- **Использование**: Разработка, демонстрация, тестирование

### ⚠️ Важные замечания

1. **После изменения конфигурации обязательно перезапустите сервисы**
2. **В production всегда включайте авторизацию**
3. **Mock пользователь создается автоматически при отключенной авторизации**
4. **Все изменения делаются в конфигурационных файлах**

### 🔧 Технические детали

### Файлы конфигурации:
- **Backend**: `backend/app/config/settings.py`
- **Frontend**: `frontend/src/config.ts`

### Mock пользователь (при отключенной авторизации):
- **ID**: 1
- **Username**: `dev_user`
- **Email**: `dev@example.com`
- **Password**: `dev_password_123`

### 🆘 Решение проблем

### Ошибка 401 Unauthorized
```bash
# Отключить авторизацию
./scripts/toggle-auth.sh disable

# Перезапустить сервисы
./scripts/toggle-auth.sh restart
```

### Проверка состояния
```bash
./scripts/toggle-auth.sh status
```

### Сброс к состоянию по умолчанию
```bash
./scripts/toggle-auth.sh disable
./scripts/toggle-auth.sh restart
```

---

*Скрипты автоматически определяют ОС и используют соответствующие команды sed*

## 📁 Разделение чеклистов на дерево файлов

### Скрипт `checklist-split-json-to-files`

Удобный скрипт для разделения большого JSON файла с иерархической структурой чеклиста на множество маленьких файлов, сохраняя отношения в виде дерева на файловой системе.

#### Структура данных

Скрипт работает с иерархической структурой:
```
Portrait -> Section -> Subsection -> QuestionGroup -> Question -> Answer
```

#### Быстрый старт

##### 1. Разделение JSON файла
```bash
# Разделяем JSON файл на дерево файлов
npm run checklist-split-json-to-files input.json output_folder
```

##### 2. Восстановление JSON файла
```bash
# Восстанавливаем исходный JSON из дерева файлов
npm run checklist-join-files-to-json output_folder restored_file.json
```

##### 3. Проверка результата
```bash
# Сравниваем исходный и восстановленный файлы
diff input.json restored_file.json
```

#### Использование

##### Основная команда
```bash
npm run checklist-split-json-to-files input.json output_directory
```

##### Восстановление JSON
```bash
npm run checklist-join-files-to-json output_directory restored_file.json
```

##### Примеры для разных случаев

###### Для больших чек-листов
```bash
npm run checklist-split-json-to-files huge_checklist.json checklist_modules
npm run checklist-join-files-to-json checklist_modules restored_checklist.json
```

#### Структура выходных файлов

После разделения создается следующая структура:

```
output_directory/
├── index.json                          # Индексный файл с метаданными
├── rebuild_json.py                     # Скрипт восстановления
└── portrait_id/                        # Папка портрета
    ├── portrait.json                   # Основные данные портрета
    └── section_id/                     # Папка секции
        ├── section.json                # Основные данные секции
        └── subsection_id/              # Папка подсекции
            ├── subsection.json         # Основные данные подсекции
            └── question_group_id/      # Папка группы вопросов
                ├── group.json          # Основные данные группы
                └── question_id/        # Папка вопроса
                    ├── question.json   # Основные данные вопроса
                    ├── answer1_id.json # Файл ответа 1
                    ├── answer2_id.json # Файл ответа 2
                    └── ...             # Другие ответы
```

#### Формат файлов

##### Файлы с данными
Каждый файл содержит:
- `id` - идентификатор элемента
- `title` - название элемента (только если есть в исходных данных)
- `type` - тип элемента (portrait, section, subsection, question_group, question, answer)
- `children` - массив ссылок на дочерние файлы (если есть)
- Специфичные поля для каждого типа

##### Индексный файл
```json
{
  "root": "portrait_id/portrait.json",
  "created_at": "timestamp",
  "source_file": "input.json",
  "structure": "portrait -> section -> subsection -> question_group -> question -> answer"
}
```
