# Стратегия идентификации сущностей при обновлении чеклистов

## Проблема идентификации

При обновлении JSON файла чеклиста система должна понимать, какие сущности (секции, подсекции, группы, вопросы) являются **новыми**, **измененными** или **удаленными**. В текущей модели данных отсутствуют уникальные идентификаторы для сопоставления.

## Анализ текущей структуры

### Текущие модели без уникальных ID
```python
# Нет уникальных идентификаторов для сопоставления
class ChecklistSection(BaseModel):
    title = Column(String(500), nullable=False)  # ❌ Может измениться
    number = Column(String(10))                  # ❌ Может измениться
    order_index = Column(Integer, default=0)     # ❌ Может измениться

class ChecklistSubsection(BaseModel):
    title = Column(String(500), nullable=False)  # ❌ Может измениться
    number = Column(String(20))                  # ❌ Может измениться
    order_index = Column(Integer, default=0)     # ❌ Может измениться

class ChecklistQuestionGroup(BaseModel):
    title = Column(String(500), nullable=False)  # ❌ Может измениться
    order_index = Column(Integer, default=0)     # ❌ Может измениться

class ChecklistQuestion(BaseModel):
    text = Column(Text, nullable=False)          # ❌ Может измениться
    order_index = Column(Integer, default=0)     # ❌ Может измениться
```

### Проблемы сопоставления
1. **Изменение заголовков** - если title изменится, система не поймет, что это та же сущность
2. **Изменение порядка** - если order_index изменится, сопоставление нарушится
3. **Изменение нумерации** - если number изменится, связь потеряется

## Стратегии решения

### Стратегия 1: Добавление уникальных идентификаторов в JSON (Рекомендуемая)

#### Структура JSON с ID
```json
{
  "slug": "physical-portrait",
  "title": "Физический портрет персонажа",
  "sections": [
    {
      "id": "section-appearance",
      "title": "ВНЕШНОСТЬ И ФИЗИЧЕСКИЕ ДАННЫЕ",
      "subsections": [
        {
          "id": "subsection-body-build",
          "title": "Телосложение и антропометрия",
          "groups": [
            {
              "id": "group-height-proportions",
              "title": "Рост и пропорции тела",
              "questions": [
                {
                  "id": "question-height",
                  "question": "Какой рост у персонажа?",
                  "options": ["Низкий", "Средний", "Высокий"],
                  "optionsType": "single",
                  "source": ["text", "logic"],
                  "hint": "Учитывайте эпоху и социальный слой"
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

#### Изменения в моделях данных
```python
class ChecklistSection(BaseModel):
    __tablename__ = "checklist_sections"
    
    # Новое поле для уникальной идентификации
    external_id = Column(String(100))  # "section-appearance"
    
    # Существующие поля
    checklist_id = Column(Integer, ForeignKey("checklists.id"), nullable=False)
    title = Column(String(500), nullable=False)
    number = Column(String(10))
    icon = Column(String(50))
    order_index = Column(Integer, default=0)

class ChecklistSubsection(BaseModel):
    __tablename__ = "checklist_subsections"
    
    external_id = Column(String(100))  # "subsection-body-build"
    
    section_id = Column(Integer, ForeignKey("checklist_sections.id"), nullable=False)
    title = Column(String(500), nullable=False)
    number = Column(String(20))
    order_index = Column(Integer, default=0)
    examples = Column(Text)
    why_important = Column(Text)

class ChecklistQuestionGroup(BaseModel):
    __tablename__ = "checklist_question_groups"
    
    external_id = Column(String(100))  # "group-height-proportions"
    
    subsection_id = Column(Integer, ForeignKey("checklist_subsections.id"), nullable=False)
    title = Column(String(500), nullable=False)
    order_index = Column(Integer, default=0)

class ChecklistQuestion(BaseModel):
    __tablename__ = "checklist_questions"
    
    external_id = Column(String(100))  # "question-height"
    
    question_group_id = Column(Integer, ForeignKey("checklist_question_groups.id"), nullable=False)
    text = Column(Text, nullable=False)
    hint = Column(Text)
    order_index = Column(Integer, default=0)
    options = Column(JSON)
    option_type = Column(String(20), default="none")
    source = Column(JSON)
```

#### Алгоритм сопоставления с ID
```python
def match_entities_by_id(old_entities: List, new_entities: List) -> MatchResult:
    """Сопоставляет сущности по external_id"""
    
    old_by_id = {entity.external_id: entity for entity in old_entities}
    new_by_id = {entity['id']: entity for entity in new_entities}
    
    # Находим соответствия
    matched = []
    for entity_id, new_entity in new_by_id.items():
        if entity_id in old_by_id:
            matched.append((old_by_id[entity_id], new_entity))
    
    # Находим новые сущности
    added = [entity for entity_id, entity in new_by_id.items() 
             if entity_id not in old_by_id]
    
    # Находим удаленные сущности
    deleted = [entity for entity_id, entity in old_by_id.items() 
               if entity_id not in new_by_id]
    
    return MatchResult(matched=matched, added=added, deleted=deleted)
```

### Стратегия 2: Автоматическая генерация ID из содержимого

#### Генерация стабильных ID
```python
def generate_stable_id(content: str, entity_type: str, parent_path: str = "") -> str:
    """Генерирует стабильный ID из содержимого"""
    import hashlib
    
    # Нормализуем содержимое
    normalized = content.lower().strip()
    normalized = re.sub(r'[^\w\s-]', '', normalized)  # Убираем спецсимволы
    normalized = re.sub(r'\s+', '-', normalized)      # Пробелы в дефисы
    
    # Создаем короткий хеш для уникальности
    content_hash = hashlib.md5(f"{parent_path}:{normalized}".encode()).hexdigest()[:8]
    
    # Комбинируем читаемую часть с хешем
    readable_part = normalized[:30]  # Первые 30 символов
    return f"{entity_type}-{readable_part}-{content_hash}"

# Примеры генерации:
# "ВНЕШНОСТЬ И ФИЗИЧЕСКИЕ ДАННЫЕ" → "section-vneshnost-i-fizicheskie-dannye-a1b2c3d4"
# "Какой рост у персонажа?" → "question-kakoy-rost-u-personazha-e5f6g7h8"
```

#### Алгоритм сопоставления по содержимому
```python
def match_entities_by_content(old_entities: List, new_entities: List) -> MatchResult:
    """Сопоставляет сущности по сгенерированным ID"""
    
    # Генерируем ID для старых сущностей
    old_with_ids = []
    for entity in old_entities:
        generated_id = generate_stable_id(entity.title, "section", entity.checklist.slug)
        old_with_ids.append((generated_id, entity))
    
    # Генерируем ID для новых сущностей
    new_with_ids = []
    for entity_data in new_entities:
        generated_id = generate_stable_id(entity_data['title'], "section", checklist_slug)
        new_with_ids.append((generated_id, entity_data))
    
    # Сопоставляем по ID
    old_by_id = {id_: entity for id_, entity in old_with_ids}
    new_by_id = {id_: entity for id_, entity in new_with_ids}
    
    return match_by_ids(old_by_id, new_by_id)
```

### Стратегия 3: Гибридный подход (Компромиссное решение)

#### Приоритетное сопоставление
```python
def match_entities_hybrid(old_entities: List, new_entities: List) -> MatchResult:
    """Гибридное сопоставление с несколькими стратегиями"""
    
    # 1. Сначала пытаемся сопоставить по external_id (если есть)
    matched_by_id = []
    remaining_old = []
    remaining_new = []
    
    for old_entity in old_entities:
        if old_entity.external_id:
            # Ищем в новых по ID
            found = next((new for new in new_entities if new.get('id') == old_entity.external_id), None)
            if found:
                matched_by_id.append((old_entity, found))
                continue
        remaining_old.append(old_entity)
    
    # Убираем уже сопоставленные новые сущности
    matched_new_ids = {new['id'] for _, new in matched_by_id if 'id' in new}
    remaining_new = [new for new in new_entities if new.get('id') not in matched_new_ids]
    
    # 2. Для оставшихся пытаемся сопоставить по содержимому
    matched_by_content = match_by_content_similarity(remaining_old, remaining_new)
    
    # 3. Для оставшихся пытаемся сопоставить по позиции
    matched_by_position = match_by_position(
        remaining_old - matched_by_content.old,
        remaining_new - matched_by_content.new
    )
    
    # Объединяем результаты
    return combine_match_results([matched_by_id, matched_by_content, matched_by_position])
```

## Рекомендуемое решение

### Поэтапное внедрение

#### Этап 1: Добавление поддержки external_id в модели
```sql
-- Миграция: добавление external_id
ALTER TABLE checklist_sections ADD COLUMN external_id VARCHAR(100);
ALTER TABLE checklist_subsections ADD COLUMN external_id VARCHAR(100);
ALTER TABLE checklist_question_groups ADD COLUMN external_id VARCHAR(100);
ALTER TABLE checklist_questions ADD COLUMN external_id VARCHAR(100);

-- Индексы для быстрого поиска
CREATE INDEX idx_sections_external_id ON checklist_sections(external_id);
CREATE INDEX idx_subsections_external_id ON checklist_subsections(external_id);
CREATE INDEX idx_groups_external_id ON checklist_question_groups(external_id);
CREATE INDEX idx_questions_external_id ON checklist_questions(external_id);

-- Составные индексы для уникальности в рамках чеклиста
CREATE UNIQUE INDEX idx_sections_checklist_external_id ON checklist_sections(checklist_id, external_id) WHERE external_id IS NOT NULL;
```

#### Этап 2: Обновление парсера JSON
```python
class ChecklistJsonParser:
    def _parse_section(self, section_data: Dict[str, Any], order_index: int) -> ChecklistSection:
        section = ChecklistSection()
        section.title = section_data.get('title', '')
        section.external_id = section_data.get('id')  # Новое поле
        section.order_index = order_index
        # ... остальная логика
        return section
```

#### Этап 3: Реализация алгоритма сопоставления
```python
class EntityMatcher:
    """Сервис для сопоставления сущностей при обновлении"""
    
    def match_sections(self, old_sections: List[ChecklistSection], new_sections: List[Dict]) -> SectionMatchResult:
        """Сопоставляет секции"""
        if self._has_external_ids(new_sections):
            return self._match_by_external_id(old_sections, new_sections)
        else:
            return self._match_by_content_similarity(old_sections, new_sections)
    
    def _has_external_ids(self, entities: List[Dict]) -> bool:
        """Проверяет, есть ли external_id в новых сущностях"""
        return any('id' in entity for entity in entities)
    
    def _match_by_external_id(self, old_entities, new_entities) -> MatchResult:
        """Сопоставление по external_id"""
        # Реализация сопоставления по ID
        pass
    
    def _match_by_content_similarity(self, old_entities, new_entities) -> MatchResult:
        """Сопоставление по схожести содержимого"""
        # Реализация сопоставления по содержимому
        pass
```

### Миграция пользовательских ответов

#### Стратегия миграции ответов
```python
class ResponseMigrationService:
    """Сервис для миграции пользовательских ответов"""
    
    def migrate_responses(self, match_result: MatchResult, character_id: int) -> MigrationReport:
        """Мигрирует ответы пользователей при обновлении структуры"""
        
        migrated_count = 0
        orphaned_responses = []
        
        # 1. Мигрируем ответы на сопоставленные вопросы
        for old_question, new_question in match_result.matched_questions:
            responses = self._get_user_responses(old_question.id, character_id)
            for response in responses:
                # Переносим ответ на новый вопрос
                response.question_id = new_question.id
                response.migration_status = MigrationStatus.MIGRATED
                migrated_count += 1
        
        # 2. Помечаем ответы на удаленные вопросы как "осиротевшие"
        for deleted_question in match_result.deleted_questions:
            responses = self._get_user_responses(deleted_question.id, character_id)
            for response in responses:
                response.migration_status = MigrationStatus.ORPHANED
                orphaned_responses.append(response)
        
        return MigrationReport(
            migrated_count=migrated_count,
            orphaned_count=len(orphaned_responses),
            orphaned_responses=orphaned_responses
        )
```

## Влияние на архитектуру

### Обновленный план реализации

```python
# Обновленный ChecklistVersionService
class ChecklistVersionService:
    def __init__(self):
        self.parser = ChecklistJsonParser()
        self.matcher = EntityMatcher()
        self.migration_service = ResponseMigrationService()
    
    def import_or_update_checklist(self, db: Session, file_path: str, strategy: UpdateStrategy) -> ImportResult:
        """Импорт с поддержкой сопоставления сущностей"""
        
        # 1. Парсим новую структуру
        new_structure = self.parser.parse_file(file_path)
        
        # 2. Ищем существующий чеклист
        existing = checklist_crud.get_by_slug(db, new_structure.slug)
        if not existing:
            return self.create_new_checklist(db, new_structure, file_path)
        
        # 3. Сопоставляем сущности
        match_result = self.matcher.match_all_entities(existing, new_structure)
        
        # 4. Применяем изменения согласно стратегии
        if strategy == UpdateStrategy.SOFT_UPDATE:
            return self.soft_update_with_matching(db, existing, new_structure, match_result, file_path)
        elif strategy == UpdateStrategy.SMART_MERGE:
            return self.smart_merge_with_matching(db, existing, new_structure, match_result, file_path)
        
        # 5. Мигрируем пользовательские ответы
        migration_report = self.migration_service.migrate_all_responses(match_result, db)
        
        return ImportResult(
            status="UPDATED",
            checklist=updated_checklist,
            migration_report=migration_report,
            match_result=match_result
        )
```

## Заключение

### Рекомендуемый подход:
1. **Добавить поле `external_id`** во все модели сущностей
2. **Поддержать ID в JSON** файлах (опционально)
3. **Реализовать гибридное сопоставление** (по ID → по содержимому → по позиции)
4. **Создать сервис миграции ответов** для сохранения пользовательских данных

### Преимущества:
- ✅ **Точное сопоставление** при наличии ID в JSON
- ✅ **Обратная совместимость** с существующими JSON без ID
- ✅ **Сохранение пользовательских данных** при структурных изменениях
- ✅ **Гибкость** в выборе стратегии сопоставления

### Риски:
- ⚠️ **Сложность реализации** алгоритмов сопоставления
- ⚠️ **Необходимость обновления JSON** файлов для максимальной точности
- ⚠️ **Возможные ошибки** при автоматическом сопоставлении по содержимому

Данный подход обеспечивает надежную основу для системы версионирования с сохранением пользовательских данных.