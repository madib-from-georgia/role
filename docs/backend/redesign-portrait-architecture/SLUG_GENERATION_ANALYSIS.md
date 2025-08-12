# Анализ генерации SLUG в системе чеклистов

## Текущий механизм генерации SLUG

### Код генерации
В файле [`backend/app/services/checklist_json_parser.py:255-261`](../backend/app/services/checklist_json_parser.py:255-261):

```python
def _generate_slug(self, filename: str) -> str:
    """Генерирует slug из имени файла"""
    # Убираем префиксы и суффиксы
    slug = filename.replace('ACTOR_', '').replace('_CHECKLIST', '')
    # Заменяем подчеркивания на дефисы
    slug = slug.replace('_', '-').lower()
    return slug
```

### Вызов генерации
В методе [`parse_file()`](../backend/app/services/checklist_json_parser.py:138):

```python
structure.slug = self._generate_slug(Path(file_path).stem)
```

## Примеры генерации SLUG

### Для файла `ACTOR_PHYSICAL_CHECKLIST.json`
- **Входной файл**: `docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.json`
- **Path(file_path).stem**: `ACTOR_PHYSICAL_CHECKLIST`
- **После удаления префиксов**: `PHYSICAL` (убираем `ACTOR_` и `_CHECKLIST`)
- **Финальный slug**: `physical`

### Другие возможные примеры
- `ACTOR_PSYCHOLOGICAL_CHECKLIST.json` → `psychological`
- `ACTOR_SOCIAL_CHECKLIST.json` → `social`
- `ACTOR_BACKSTORY_CHECKLIST.json` → `backstory`

## Критический анализ стабильности SLUG

### ✅ Стабильные факторы
1. **Основа на имени файла** - slug генерируется из имени файла, а не из содержимого JSON
2. **Детерминированный алгоритм** - одинаковое имя файла всегда даст одинаковый slug
3. **Простая логика** - убираем стандартные префиксы/суффиксы

### ⚠️ Потенциальные риски
1. **Переименование файлов** - если файл будет переименован, slug изменится
2. **Изменение структуры папок** - slug не зависит от пути, только от имени файла
3. **Изменение соглашений именования** - если изменится формат имен файлов

## Влияние на систему версионирования

### Сценарий 1: Обновление содержимого JSON (✅ Безопасно)
```
Файл: ACTOR_PHYSICAL_CHECKLIST.json
Содержимое: изменено (новые вопросы, секции)
Slug: physical (остается тем же)
Результат: ✅ Система версионирования сработает корректно
```

### Сценарий 2: Переименование файла (⚠️ Проблема)
```
Старый файл: ACTOR_PHYSICAL_CHECKLIST.json → slug: physical
Новый файл: ACTOR_PHYSICAL_PORTRAIT_CHECKLIST.json → slug: physical-portrait
Результат: ❌ Система создаст новый чеклист вместо обновления
```

### Сценарий 3: Изменение соглашений (⚠️ Проблема)
```
Старый формат: ACTOR_PHYSICAL_CHECKLIST.json → slug: physical
Новый формат: CHARACTER_PHYSICAL_CHECKLIST.json → slug: character-physical
Результат: ❌ Система создаст новый чеклист
```

## Рекомендации по улучшению

### Вариант 1: Явное указание SLUG в JSON (Рекомендуемый)
Добавить поле `slug` в JSON файл:

```json
{
  "slug": "physical-portrait",
  "title": "Физический портрет персонажа",
  "goal": {...},
  "sections": [...]
}
```

**Преимущества:**
- Полный контроль над slug
- Независимость от имени файла
- Возможность миграции при переименовании

**Изменения в коде:**
```python
def _generate_slug(self, filename: str, json_data: Dict[str, Any]) -> str:
    """Генерирует slug из JSON или имени файла"""
    # Приоритет: явно указанный slug в JSON
    if 'slug' in json_data:
        return json_data['slug'].lower().strip()
    
    # Fallback: генерация из имени файла (текущая логика)
    slug = filename.replace('ACTOR_', '').replace('_CHECKLIST', '')
    slug = slug.replace('_', '-').lower()
    return slug
```

### Вариант 2: Улучшенная генерация из файла
```python
def _generate_slug(self, file_path: str) -> str:
    """Улучшенная генерация slug"""
    path = Path(file_path)
    
    # Используем путь к файлу для уникальности
    # docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.json
    # → physical-portrait
    
    parent_dir = path.parent.name
    if parent_dir.startswith(('01-', '02-', '03-')):
        # Убираем числовой префиксы из папки
        return parent_dir[3:]  # "01-physical-portrait" → "physical-portrait"
    
    # Fallback к текущей логике
    filename = path.stem
    slug = filename.replace('ACTOR_', '').replace('_CHECKLIST', '')
    return slug.replace('_', '-').lower()
```

### Вариант 3: Комбинированный подход
```python
def _generate_slug(self, file_path: str, json_data: Dict[str, Any]) -> str:
    """Комбинированная генерация slug"""
    # 1. Приоритет: явный slug в JSON
    if 'slug' in json_data:
        return json_data['slug'].lower().strip()
    
    # 2. Генерация из структуры папок
    path = Path(file_path)
    parent_dir = path.parent.name
    if parent_dir.startswith(('01-', '02-', '03-')):
        return parent_dir[3:]
    
    # 3. Fallback: из имени файла
    filename = path.stem
    slug = filename.replace('ACTOR_', '').replace('_CHECKLIST', '')
    return slug.replace('_', '-').lower()
```

## Влияние на архитектуру версионирования

### Текущая ситуация: Стабильность SLUG
Для файла `docs/modules/01-physical-portrait/ACTOR_PHYSICAL_CHECKLIST.json`:
- **Slug**: `physical` (стабильный при изменении содержимого)
- **Система версионирования**: ✅ Будет работать корректно

### Рекомендуемые изменения в архитектуре

#### 1. Добавить поле `original_file_path` в таблицу `checklists`
```sql
ALTER TABLE checklists ADD COLUMN original_file_path VARCHAR(500);
```

Это поможет отслеживать перемещения файлов.

#### 2. Добавить проверку миграции SLUG
```python
def find_checklist_by_file_or_slug(self, db: Session, file_path: str, slug: str) -> Optional[Checklist]:
    """Ищет чеклист по файлу или slug для обработки переименований"""
    
    # Сначала ищем по slug (основной способ)
    checklist = checklist_crud.get_by_slug(db, slug)
    if checklist:
        return checklist
    
    # Если не найден, ищем по пути к файлу (для обработки переименований)
    checklist = checklist_crud.get_by_file_path(db, file_path)
    if checklist:
        logger.warning(f"Найден чеклист по пути файла, но slug изменился: {checklist.slug} → {slug}")
        # Можно предложить пользователю выбор: обновить slug или создать новый чеклист
        return checklist
    
    return None
```

#### 3. Обновить ChecklistVersionService
```python
def import_or_update_checklist(self, db: Session, file_path: str, strategy: UpdateStrategy) -> ImportResult:
    """Импорт с учетом возможных изменений slug"""
    
    # Парсим структуру
    structure = self.parser.parse_file(file_path)
    
    # Ищем существующий чеклист (по slug или файлу)
    existing = self.find_checklist_by_file_or_slug(db, file_path, structure.slug)
    
    if existing and existing.slug != structure.slug:
        # Обнаружено изменение slug
        return self.handle_slug_migration(db, existing, structure, file_path, strategy)
    
    # Обычная логика обновления
    # ...
```

## Заключение

### Текущая стабильность SLUG: ✅ Хорошая
- Для обычных обновлений содержимого JSON система будет работать корректно
- Slug генерируется детерминированно из имени файла
- Риски связаны только с переименованием файлов

### Рекомендации для повышения надежности:
1. **Краткосрочно**: Текущая система достаточна для начала работы
2. **Среднесрочно**: Добавить поле `slug` в JSON файлы для явного контроля
3. **Долгосрочно**: Реализовать механизм обработки миграции SLUG при переименованиях

### Влияние на план реализации:
- ✅ Можно начинать реализацию системы версионирования с текущим механизмом SLUG
- ⚠️ Добавить в план задачу по улучшению генерации SLUG (низкий приоритет)
- 📝 Документировать соглашения по именованию файлов для команды