# 🔄 Руководство по миграции компонентов

## 📋 Обзор миграции

### 🎯 Стратегия замены:
**Полная замена** существующих компонентов на новую архитектуру с сохранением всех API интерфейсов

### 🗂️ Текущие компоненты для замены:

#### Стартовая страница:
- CharacterChecklists.tsx

#### Страница отдельного чеклиста:
- ChecklistView.tsx
- ChecklistSection.tsx  
- ChecklistSubsection.tsx
- ChecklistQuestionGroup.tsx
- ChecklistQuestion.tsx

### 🆕 Новые компоненты:

#### Стартовая страница:
- ChecklistsOverview.tsx
- RecommendedNextStep.tsx
- ChecklistGroup.tsx
- ChecklistCard.tsx (новый, отличается от карточки в ChecklistView)
- OverallProgress.tsx

#### Страница отдельного чеклиста:
- QuestionFlow.tsx
- QuestionCard.tsx
- ProgressBar.tsx
- NavigationSidebar.tsx
- QuestionNavigation.tsx
- ChecklistSwitcher.tsx

---

## 🔄 Таблица соответствия компонентов

| Старый компонент | Новый компонент | Статус миграции | Примечания |
|------------------|-----------------|-----------------|------------|
| **СТАРТОВАЯ СТРАНИЦА** |
| CharacterChecklists | ChecklistsOverview | 🔄 Заменяется | Полная переработка логики |
| - | RecommendedNextStep | ✅ Новый | Умная логика рекомендаций |
| - | ChecklistGroup | ✅ Новый | Группировка с блокировкой |
| - | OverallProgress | ✅ Новый | Общий прогресс по всем чеклистам |
| **СТРАНИЦА ЧЕКЛИСТА** |
| ChecklistView | QuestionFlow | 🔄 Заменяется | Упрощенная логика |
| ChecklistSection | - | ❌ Удаляется | Логика переносится в NavigationSidebar |
| ChecklistSubsection | - | ❌ Удаляется | Логика переносится в NavigationSidebar |
| ChecklistQuestionGroup | - | ❌ Удаляется | Логика переносится в QuestionFlow |
| ChecklistQuestion | QuestionCard | 🔄 Заменяется | Полная переработка |
| - | ProgressBar | ✅ Новый | Отдельный компонент прогресса |
| - | NavigationSidebar | ✅ Новый | Боковая навигация + переключение чеклистов |
| - | QuestionNavigation | ✅ Новый | Навигация между вопросами |
| - | ChecklistSwitcher | ✅ Новый | Переключение между чеклистами |

---

## 📊 Анализ текущих API

### CharacterChecklists Props (текущие):
```typescript
// Из useParams
interface CharacterChecklistsParams {
  characterId: string;
}
```

### ChecklistsOverview Props (новые):
```typescript
interface ChecklistsOverviewProps {
  characterId: number; // из useParams, но типизированный
}
```

### ChecklistView Props (текущие):
```typescript
interface ChecklistViewProps {
  checklistSlug: string;
  characterId: number;
}
```
**↓ Мигрирует в QuestionFlow без изменений**

### ChecklistQuestion Props (текущие):
```typescript
interface ChecklistQuestionProps {
  question: ChecklistQuestionData;
  onAnswerUpdate: (questionId: number, data: UpdateData) => void;
  onAnswerDelete: (responseId: number) => void;
  isExpanded?: boolean;
}
```

### QuestionCard Props (новые):
```typescript
interface QuestionCardProps {
  question: ChecklistQuestionData;
  onAnswerUpdate: (questionId: number, data: UpdateData) => void;
  onAnswerDelete: (responseId: number) => void;
  // isExpanded убираем - всегда развернуто
}
```

---

## 🏗️ Архитектурные изменения

### 🔀 Изменение иерархии:

#### Старая структура:
```
ChecklistView
├── ChecklistSection
│   └── ChecklistSubsection
│       └── ChecklistQuestionGroup
│           └── ChecklistQuestion
```

#### Новая структура:
```
QuestionFlow
├── QuestionCard (один активный)
├── ProgressBar
├── NavigationSidebar (опционально)
└── QuestionNavigation
```

### 🎯 Ключевые изменения:

1. **Линейный поток** вместо древовидной структуры
2. **Один вопрос** на экране вместо множества
3. **Боковая навигация** вместо аккордеонов
4. **Прогресс-бар** как отдельный компонент

---

## 🔧 План миграции состояния

### 🗄️ Текущее состояние в ChecklistView:
- localData: ChecklistData
- showHowToUse: boolean

### 🗄️ Новое состояние в QuestionFlow:
- currentQuestionIndex: number
- questions: FlatQuestionData[]  
- sidebarOpen: boolean
- searchQuery: string
- bookmarks: number[]

### 🔄 Трансформация данных на фронтенде:

#### ✅ Данные с бекенда остаются без изменений (иерархические):
```
ChecklistData {
  sections: [
    {
      subsections: [
        {
          groups: [
            {
              questions: [...]
            }
          ]
        }
      ]
    }
  ]
}
```

#### 🎯 Создаем утилиту для навигации (только для UI):
```
NavigableQuestion[] [
  {
    ...originalQuestion,
    navigation: {
      sectionTitle: string,
      subsectionTitle: string,
      groupTitle: string,
      path: [sectionIndex, subsectionIndex, groupIndex, questionIndex],
      breadcrumbs: string,
      totalIndex: number // для прогресс-бара
    }
  }
]
```

**Ключевое преимущество**: Никаких изменений в бекенде, вся трансформация на фронтенде!

---

## 📝 Пошаговый план миграции

### Шаг 1: Подготовка утилит
- Создать функцию трансформации данных
- Создать логику группировки чеклистов
- Создать алгоритм определения рекомендуемого шага
- Создать хуки для управления состоянием
- Подготовить типы TypeScript

### Шаг 2: Стартовая страница чеклистов
- ChecklistsOverview (замена CharacterChecklists)
- RecommendedNextStep (умная логика рекомендаций)
- ChecklistGroup (группировка с блокировкой)
- OverallProgress (общий прогресс)

### Шаг 3: Базовые компоненты QuestionFlow
- QuestionFlow (базовая структура)
- QuestionCard (без логики форм)
- ProgressBar
- ChecklistSwitcher (переключение чеклистов)

### Шаг 4: Миграция логики вопросов
- Перенести логику из ChecklistQuestion
- Адаптировать под новый формат данных
- Сохранить совместимость API

### Шаг 5: Создание навигации
- NavigationSidebar (с переключением чеклистов)
- QuestionNavigation
- Логика переходов

### Шаг 6: Интеграция и тестирование
- Подключить к существующим роутам
- Протестировать все сценарии переходов
- Протестировать логику блокировки чеклистов
- Оптимизировать производительность

---

## ⚠️ Критические моменты

### 🔒 Сохранение совместимости:
- API endpoints остаются без изменений
- Формат данных ответов не меняется
- Все колбэки работают как прежде

### 🎯 Особое внимание:
- Корректная трансформация иерархических данных
- Сохранение всех текущих ответов
- Обработка состояний загрузки/ошибок
- Логика группировки и блокировки чеклистов
- Алгоритм определения рекомендуемого следующего шага
- Переключение между чеклистами без потери контекста

### 🧪 Обязательное тестирование:
- Сохранение и загрузка ответов
- Навигация между вопросами
- Переходы между чеклистами
- Логика блокировки чеклистов на основе прогресса
- Корректность рекомендаций следующего шага
- Работа на мобильных устройствах
- Производительность с 300+ вопросами
- Производительность загрузки прогресса по 20 чеклистам

---

## 📚 Дополнительные материалы

### 🔗 Связанные файлы:
- `docs/frontent/redesigned_checklist_ui.md` - Визуальный дизайн
- `docs/frontent/component_specifications.md` - Технические спецификации
- `docs/frontent/redesign/implementation_roadmap.md` - Детальный план

### 🛠️ Утилиты для миграции:
- Создать скрипт валидации старых/новых данных
- Подготовить миграцию CSS классов
- Настроить переключение между версиями

### 📋 Чек-лист готовности:
- [ ] Все новые компоненты стартовой страницы созданы
- [ ] Все новые компоненты страницы чеклиста созданы
- [ ] Логика группировки чеклистов работает
- [ ] Алгоритм рекомендаций следующего шага работает
- [ ] Логика блокировки/разблокировки чеклистов работает
- [ ] Логика трансформации данных работает
- [ ] API интеграция протестирована
- [ ] Переключение между чеклистами работает
- [ ] Мобильная версия работает корректно
- [ ] Производительность загрузки 20 чеклистов оптимизирована
- [ ] Производительность QuestionFlow оптимизирована
- [ ] Документация обновлена
