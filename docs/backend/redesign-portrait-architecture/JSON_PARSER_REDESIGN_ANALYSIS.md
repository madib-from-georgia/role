# Анализ изменений парсера JSON для новой структуры

## Сравнение структур JSON

### Старая структура (текущая)
```json
{
  "title": "Физический портрет персонажа",
  "goal": {
    "title": "Цель",
    "description": "Описание цели"
  },
  "sections": [
    {
      "title": "ВНЕШНОСТЬ И ФИЗИЧЕСКИЕ ДАННЫЕ",
      "subsections": [
        {
          "title": "Телосложение и антропометрия",
          "groups": [
            {
              "title": "Рост и пропорции тела",
              "questions": [
                {
                  "question": "Какой рост у персонажа?",
                  "options": ["Низкий", "Средний", "Высокий"],
                  "optionsType": "single",
                  "source": ["text", "logic"],
                  "hint": "Учитывайте эпоху и социальный слой"
                }
              ]
            }
          ],
          "examples": [...],
          "whyImportant": "..."
        }
      ]
    }
  ]
}
```

### Новая структура (требуемая)
```typescript
interface Portrait {
  id: string;          // "physical-portrait"
  title: string;       // "Физический портрет"
  sections: Section[];
}

interface Section {
  id: string;          // "appearance"
  title: string;       // "Внешность и физические данные"
  subsections: Subsection[];
}

interface Subsection {
  id: string;          // "physique"
  title: string;       // "Телосложение и антропометрия"
  questionGroups: QuestionGroup[];
}

interface QuestionGroup {
  id: string;          // "height-proportions"
  title: string;       // "Рост и пропорции тела"
  questions: Question[];
}

interface Question {
  id: string;          // "height"
  title: string;       // "Какой у меня рост?"
  answers: Answer[];
  answerType: string;  // "single", "multiple"
  source: string;      // "text"
}

interface Answer {
  id: string;          // "short", "average", "tall", "custom"
  value: AnswerValue;
  exportedValue: AnswerValue;
  hint: string;
}

interface AnswerValue {
  male: string;        // "низкий"
  female: string;      // "низкий"
}
```

## Ключевые изменения

### 1. **Добавление ID на всех уровнях** ✅
- **Portrait.id** - уникальный идентификатор портрета
- **Section.id** - идентификатор секции
- **Subsection.id** - идентификатор подсекции  
- **QuestionGroup.id** - идентификатор группы вопросов
- **Question.id** - идентификатор вопроса
- **Answer.id** - идентификатор ответа

### 2. **Изменение структуры ответов** ⚠️ КРИТИЧНО
**Старая структура:**
```json
{
  "question": "Какой рост у персонажа?",
  "options": ["Низкий", "Средний", "Высокий"],
  "optionsType": "single",
  "hint": "Учитывайте эпоху и социальный слой"
}
```

**Новая структура:**
```json
{
  "id": "height",
  "title": "Какой у меня рост?",
  "answers": [
    {
      "id": "short",
      "value": {"male": "низкий", "female": "низкий"},
      "exportedValue": {"male": "Я невысокого роста", "female": "Я невысокого роста"},
      "hint": "Невысокий человек может компенсировать или комплексовать"
    }
  ],
  "answerType": "single",
  "source": "text"
}
```

### 3. **Удаленные поля**
- `goal` - цель чеклиста (больше не используется)
- `examples` - примеры из литературы (удалены из подсекций)
- `whyImportant` - объяснение важности (удалено из подсекций)

### 4. **Переименования полей**
- `question` → `title` (в Question)
- `options` → `answers` (массив объектов вместо строк)
- `groups` → `questionGroups` (в Subsection)

## Влияние на модели базы данных

### Текущие модели требуют изменений:

#### ChecklistQuestion
```python
# СТАРАЯ МОДЕЛЬ
class ChecklistQuestion(BaseModel):
    text = Column(Text, nullable=False)          # question
    hint = Column(Text)                          # hint (общий для вопроса)
    options = Column(JSON)                       # ["Низкий", "Средний", "Высокий"]
    option_type = Column(String(20))             # "single"
    source = Column(JSON)                        # ["text", "logic"]

# НОВАЯ МОДЕЛЬ (требуется)
class ChecklistQuestion(BaseModel):
    external_id = Column(String(100))            # id из JSON
    title = Column(Text, nullable=False)         # title
    answer_type = Column(String(20))             # answerType
    source = Column(String(50))                  # source (строка, не массив)
    # hint удаляется - теперь у каждого ответа свой hint
    # options удаляется - заменяется на отдельную таблицу ответов
```

#### Новая модель ChecklistAnswer (требуется создать)
```python
class ChecklistAnswer(BaseModel):
    """Вариант ответа на вопрос"""
    __tablename__ = "checklist_answers"
    
    question_id = Column(Integer, ForeignKey("checklist_questions.id"), nullable=False)
    external_id = Column(String(100))            # id из JSON
    
    # Значения для отображения в UI
    value_male = Column(String(500))             # value.male
    value_female = Column(String(500))           # value.female
    
    # Значения для экспорта
    exported_value_male = Column(Text)           # exportedValue.male
    exported_value_female = Column(Text)         # exportedValue.female
    
    hint = Column(Text)                          # hint для этого ответа
    order_index = Column(Integer, default=0)
    
    # Relationships
    question = relationship("ChecklistQuestion", back_populates="answers")
```

## Изменения в парсере

### Новый ChecklistJsonParser

```python
class ChecklistJsonParser:
    """Парсер для новой структуры JSON"""
    
    def parse_file(self, file_path: str) -> ChecklistStructure:
        """Парсит JSON файл новой структуры"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        structure = ChecklistStructure()
        
        # Основные поля портрета
        structure.id = data.get('id', '')                    # НОВОЕ
        structure.title = data.get('title', '')
        structure.slug = self._generate_slug_from_id(structure.id)  # Из ID, не из файла
        
        # Парсим секции
        sections_data = data.get('sections', [])
        for section_data in sections_data:
            section = self._parse_section(section_data)
            structure.sections.append(section)
        
        return structure
    
    def _parse_section(self, section_data: Dict[str, Any]) -> ChecklistSection:
        """Парсит секцию новой структуры"""
        section = ChecklistSection()
        section.external_id = section_data.get('id', '')     # НОВОЕ
        section.title = section_data.get('title', '')
        
        # Парсим подсекции
        subsections_data = section_data.get('subsections', [])
        for subsection_data in subsections_data:
            subsection = self._parse_subsection(subsection_data)
            section.subsections.append(subsection)
        
        return section
    
    def _parse_subsection(self, subsection_data: Dict[str, Any]) -> ChecklistSubsection:
        """Парсит подсекцию новой структуры"""
        subsection = ChecklistSubsection()
        subsection.external_id = subsection_data.get('id', '')  # НОВОЕ
        subsection.title = subsection_data.get('title', '')
        
        # examples и whyImportant больше НЕ ПАРСИМ
        
        # Парсим группы вопросов (переименовано)
        groups_data = subsection_data.get('questionGroups', [])  # ИЗМЕНЕНО
        for group_data in groups_data:
            group = self._parse_question_group(group_data)
            subsection.question_groups.append(group)
        
        return subsection
    
    def _parse_question_group(self, group_data: Dict[str, Any]) -> ChecklistQuestionGroup:
        """Парсит группу вопросов"""
        group = ChecklistQuestionGroup()
        group.external_id = group_data.get('id', '')        # НОВОЕ
        group.title = group_data.get('title', '')
        
        # Парсим вопросы
        questions_data = group_data.get('questions', [])
        for question_data in questions_data:
            question = self._parse_question(question_data)
            group.questions.append(question)
        
        return group
    
    def _parse_question(self, question_data: Dict[str, Any]) -> ChecklistQuestion:
        """Парсит вопрос новой структуры"""
        question = ChecklistQuestion()
        question.external_id = question_data.get('id', '')      # НОВОЕ
        question.title = question_data.get('title', '')         # ИЗМЕНЕНО: было question
        question.answer_type = question_data.get('answerType', 'single')  # ИЗМЕНЕНО
        question.source = question_data.get('source', 'text')   # ИЗМЕНЕНО: строка, не массив
        
        # Парсим ответы (новая структура)
        answers_data = question_data.get('answers', [])
        for answer_data in answers_data:
            answer = self._parse_answer(answer_data)
            question.answers.append(answer)
        
        return question
    
    def _parse_answer(self, answer_data: Dict[str, Any]) -> ChecklistAnswer:
        """Парсит ответ (новая сущность)"""
        answer = ChecklistAnswer()
        answer.external_id = answer_data.get('id', '')
        
        # Значения для UI
        value = answer_data.get('value', {})
        answer.value_male = value.get('male', '')
        answer.value_female = value.get('female', '')
        
        # Значения для экспорта
        exported_value = answer_data.get('exportedValue', {})
        answer.exported_value_male = exported_value.get('male', '')
        answer.exported_value_female = exported_value.get('female', '')
        
        answer.hint = answer_data.get('hint', '')
        
        return answer
    
    def _generate_slug_from_id(self, portrait_id: str) -> str:
        """Генерирует slug из ID портрета"""
        # portrait_id уже в нужном формате: "physical-portrait"
        return portrait_id.lower().strip()
```

## Миграция данных

### Проблемы совместимости

1. **Структура ответов кардинально изменилась**
   - Старые `options: ["A", "B", "C"]` → Новые `answers: [{id, value: {male, female}, ...}]`
   - Невозможна автоматическая миграция без потери данных

2. **Пользовательские ответы**
   - В `ChecklistResponse.answer` хранится текст ответа
   - При новой структуре нужно сопоставлять с `Answer.id`

3. **Удаленные поля**
   - `examples` и `whyImportant` из подсекций будут потеряны

### Стратегия миграции: Полная перезапись

```python
def migrate_to_new_structure():
    """Миграция на новую структуру JSON"""
    
    # 1. Создаем резервную копию старых данных
    backup_old_data()
    
    # 2. Создаем новые таблицы
    create_checklist_answers_table()
    
    # 3. Удаляем старые чеклисты (они несовместимы)
    clear_old_checklists()
    
    # 4. Импортируем новые чеклисты
    import_new_structure_checklists()
    
    # 5. Уведомляем пользователей о необходимости заново заполнить ответы
    notify_users_about_reset()
```

**Обоснование выбора:**
- Старая и новая структуры слишком разные для автоматической миграции
- Структура ответов кардинально изменилась: `options: ["A", "B"]` → `answers: [{id, value: {male, female}}]`
- Лучше начать "с чистого листа" с новой структурой
- Попытка сохранения данных приведет к сложности и потенциальным ошибкам

## Обновленный план реализации

### Фаза 1: Подготовка к новой структуре
1. **Создать новую модель ChecklistAnswer**
2. **Переписать ChecklistJsonParser для новой структуры**
3. **Обновить модели данных с учетом изменений**
4. **Создать миграцию базы данных**

### Фаза 2: Система версионирования (мягкое обновление)
5. **Реализовать ChecklistVersionService**
6. **Создать EntityMatcher с поддержкой external_id**
7. **Разработать ResponseMigrationService**

### Фаза 3: Интеграция и тестирование
8. **Обновить API эндпоинты**
9. **Модифицировать скрипт импорта**
10. **Написать тесты**
11. **Протестировать миграцию**

## Рекомендации

### 1. **Приоритет: Новая структура JSON**
- Сначала полностью переписать парсер под новую структуру
- Затем добавлять систему версионирования

### 2. **Стратегия миграции: Полная перезапись**
- Старая и новая структуры слишком разные для автоматической миграции
- Лучше начать "с чистого листа" с новой структурой

### 3. **ID как основа версионирования**
- Новые ID в JSON идеально подходят для системы версионирования
- external_id будет заполняться автоматически из JSON

### 4. **Поэтапное внедрение**
- Сначала новый парсер + новые модели
- Потом система версионирования (мягкое обновление)
- В конце миграция существующих данных

## Заключение

Новая структура JSON кардинально меняет подход к хранению и обработке данных. Это требует:

1. **Полной переработки парсера JSON**
2. **Создания новой модели ChecklistAnswer**
3. **Обновления всех связанных компонентов**
4. **Стратегии миграции пользовательских данных**

Рекомендуется сначала реализовать поддержку новой структуры, а затем добавить систему версионирования поверх неё.
