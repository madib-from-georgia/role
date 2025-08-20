# UI Components и дизайн-система

## 🎨 Дизайн-философия

### Принципы дизайна
- **Театральная эстетика** - элегантный, профессиональный дизайн
- **Минимализм** - фокус на содержании, не на декорации
- **Интуитивность** - актеры должны понимать интерфейс без обучения
- **Адаптивность** - работа на разных размерах экранов

### Цветовая палитра
```css
:root {
  /* Основные цвета */
  --primary-blue: #1e3a8a;      /* Темно-синий */
  --primary-gold: #f59e0b;      /* Золотой */
  --primary-white: #ffffff;     /* Белый */
  
  /* Акцентные цвета */
  --accent-red: #dc2626;        /* Красный для важных элементов */
  --accent-green: #059669;      /* Зеленый для успеха */
  
  /* Нейтральные цвета */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
}
```

### Типографика
```css
/* Шрифты */
--font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Размеры */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* Веса */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

## 🧩 Атомарные компоненты

### Button
Основной компонент кнопки с различными вариантами.

```tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  children: ReactNode;
  onClick?: () => void;
}

// Использование
<Button variant="primary" size="md" icon={<PlusIcon />}>
  Создать проект
</Button>
```

**Варианты**:
- `primary` - основная кнопка (синий фон)
- `secondary` - вторичная кнопка (золотой фон)
- `outline` - кнопка с границей
- `ghost` - прозрачная кнопка
- `danger` - кнопка удаления (красный)

### Input
Поле ввода с валидацией и различными типами.

```tsx
interface InputProps {
  type: 'text' | 'email' | 'password' | 'search' | 'textarea';
  label?: string;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  icon?: ReactNode;
  value: string;
  onChange: (value: string) => void;
}

// Использование
<Input
  type="email"
  label="Email"
  placeholder="actor@example.com"
  error={errors.email}
  required
  value={email}
  onChange={setEmail}
/>
```

### Badge
Компонент для отображения статусов и меток.

```tsx
interface BadgeProps {
  variant: 'default' | 'success' | 'warning' | 'error' | 'info';
  size: 'sm' | 'md';
  children: ReactNode;
}

// Использование
<Badge variant="success">Завершен</Badge>
<Badge variant="warning">В процессе</Badge>
```

### Icon
Унифицированный компонент для иконок.

```tsx
interface IconProps {
  name: string;
  size: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
}

// Использование
<Icon name="user" size="md" />
<Icon name="check" size="sm" color="green" />
```

## 📱 Молекулярные компоненты

### Card
Контейнер для группировки связанного контента.

```tsx
interface CardProps {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
}

// Использование
<Card 
  title="Анализ Гамлета" 
  subtitle="5 персонажей"
  actions={<Button variant="outline">Открыть</Button>}
>
  <p>Детальный Роль трагедии Шекспира</p>
</Card>
```

### Modal
Модальное окно для диалогов и форм.

```tsx
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  size: 'sm' | 'md' | 'lg' | 'xl';
  children: ReactNode;
}

// Использование
<Modal 
  isOpen={isModalOpen} 
  onClose={() => setIsModalOpen(false)}
  title="Создать новый проект"
  size="md"
>
  <ProjectForm onSubmit={handleSubmit} />
</Modal>
```

### Dropdown
Выпадающее меню для выбора опций.

```tsx
interface DropdownProps {
  trigger: ReactNode;
  items: DropdownItem[];
  placement: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end';
}

interface DropdownItem {
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  danger?: boolean;
}

// Использование
<Dropdown
  trigger={<Button variant="ghost">Действия</Button>}
  items={[
    { label: 'Редактировать', icon: <EditIcon />, onClick: handleEdit },
    { label: 'Удалить', icon: <DeleteIcon />, onClick: handleDelete, danger: true }
  ]}
/>
```

### ProgressBar
Индикатор прогресса выполнения.

```tsx
interface ProgressBarProps {
  value: number; // 0-100
  max?: number;
  label?: string;
  showPercentage?: boolean;
  variant: 'default' | 'success' | 'warning' | 'error';
}

// Использование
<ProgressBar 
  value={75} 
  label="Прогресс анализа"
  showPercentage
  variant="success"
/>
```

## 🏗️ Организменные компоненты

### Header
Главная навигация приложения.

```tsx
interface HeaderProps {
  user?: User;
  onLogout: () => void;
}

// Структура
<Header>
  <Logo />
  <Navigation>
    <NavItem href="/projects">Проекты</NavItem>
    <NavItem href="/library">Библиотека</NavItem>
  </Navigation>
  <UserMenu user={user} onLogout={onLogout} />
</Header>
```

### Sidebar
Боковая панель для навигации по разделам.

```tsx
interface SidebarProps {
  items: SidebarItem[];
  activeItem?: string;
  collapsed?: boolean;
  onToggle?: () => void;
}

interface SidebarItem {
  id: string;
  label: string;
  icon: ReactNode;
  href?: string;
  badge?: string;
  children?: SidebarItem[];
}

// Использование
<Sidebar
  items={[
    { id: 'texts', label: 'Тексты', icon: <BookIcon />, badge: '3' },
    { id: 'characters', label: 'Персонажи', icon: <UserIcon />, badge: '12' }
  ]}
  activeItem="characters"
/>
```

### DataTable
Таблица для отображения структурированных данных.

```tsx
interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  pagination?: PaginationProps;
  sorting?: SortingProps;
  selection?: SelectionProps<T>;
}

interface Column<T> {
  key: keyof T;
  title: string;
  render?: (value: any, record: T) => ReactNode;
  sortable?: boolean;
  width?: string;
}

// Использование
<DataTable
  data={projects}
  columns={[
    { key: 'title', title: 'Название', sortable: true },
    { key: 'created_at', title: 'Создан', render: formatDate },
    { key: 'actions', title: 'Действия', render: renderActions }
  ]}
  pagination={{ page: 1, limit: 20, total: 100 }}
/>
```

## 🎭 Специализированные компоненты

### CharacterCard
Карточка персонажа с основной информацией.

```tsx
interface CharacterCardProps {
  character: Character;
  onAnalyze: (id: string) => void;
  onExport: (id: string) => void;
}

// Структура
<CharacterCard character={hamlet}>
  <CharacterAvatar name={character.name} />
  <CharacterInfo>
    <CharacterName>{character.name}</CharacterName>
    <CharacterStats>
      <Stat label="Важность" value={character.importance_score} />
      <Stat label="Реплик" value={character.speech_count} />
    </CharacterStats>
  </CharacterInfo>
  <CharacterProgress value={character.analysis_progress} />
  <CharacterActions>
    <Button onClick={() => onAnalyze(character.id)}>Анализировать</Button>
    <Button variant="outline" onClick={() => onExport(character.id)}>Экспорт</Button>
  </CharacterActions>
</CharacterCard>
```

### ChecklistForm
Форма для заполнения чеклиста персонажа.

```tsx
interface ChecklistFormProps {
  checklist: Checklist;
  character: Character;
  responses: ChecklistResponse[];
  onSave: (responses: ChecklistResponse[]) => void;
  onNext: () => void;
}

// Структура
<ChecklistForm>
  <ChecklistHeader>
    <ChecklistTitle>{checklist.title}</ChecklistTitle>
    <ChecklistProgress value={completionPercentage} />
  </ChecklistHeader>
  
  <ChecklistSections>
    {checklist.sections.map(section => (
      <ChecklistSection key={section.id}>
        <SectionHeader>{section.title}</SectionHeader>
        <QuestionGroups>
          {section.questionGroups.map(group => (
            <QuestionGroup key={group.id}>
              <GroupTitle>{group.title}</GroupTitle>
              <Questions>
                {group.questions.map(question => (
                  <QuestionCard key={question.id}>
                    <QuestionText>{question.text}</QuestionText>
                    <AnswerOptions>
                      {question.answers.map(answer => (
                        <AnswerOption key={answer.id}>
                          <Radio 
                            name={`question_${question.id}`}
                            value={answer.id}
                            checked={isSelected(answer.id)}
                            onChange={handleAnswerChange}
                          />
                          <AnswerLabel>{answer.value}</AnswerLabel>
                        </AnswerOption>
                      ))}
                    </AnswerOptions>
                    <SourceTypeSelector>
                      <Select 
                        value={response.source_type}
                        onChange={handleSourceTypeChange}
                        options={sourceTypeOptions}
                      />
                    </SourceTypeSelector>
                    <CommentField>
                      <Textarea 
                        placeholder="Комментарий, цитата из текста..."
                        value={response.comment}
                        onChange={handleCommentChange}
                      />
                    </CommentField>
                  </QuestionCard>
                ))}
              </Questions>
            </QuestionGroup>
          ))}
        </QuestionGroups>
      </ChecklistSection>
    ))}
  </ChecklistSections>
  
  <ChecklistActions>
    <Button variant="outline" onClick={onSave}>Сохранить</Button>
    <Button variant="primary" onClick={onNext}>Следующий модуль</Button>
  </ChecklistActions>
</ChecklistForm>
```

### FileUpload
Компонент для загрузки файлов произведений.

```tsx
interface FileUploadProps {
  accept: string[];
  maxSize: number;
  multiple?: boolean;
  onUpload: (files: File[]) => void;
  onError: (error: string) => void;
}

// Структура
<FileUpload>
  <DropZone>
    <DropZoneIcon />
    <DropZoneText>
      Перетащите файл сюда или <UploadButton>выберите файл</UploadButton>
    </DropZoneText>
    <SupportedFormats>
      Поддерживаемые форматы: TXT, PDF, FB2, EPUB
    </SupportedFormats>
  </DropZone>
  
  <UploadProgress files={uploadingFiles} />
  
  <UploadedFiles files={uploadedFiles} onRemove={handleRemove} />
</FileUpload>
```

### AnalysisResults
Компонент для отображения результатов анализа.

```tsx
interface AnalysisResultsProps {
  character: Character;
  module: AnalysisModule;
  responses: ChecklistResponse[];
  onEdit: () => void;
  onExport: () => void;
}

// Структура
<AnalysisResults>
  <ResultsHeader>
    <ModuleTitle>{module.title}</ModuleTitle>
    <ModuleActions>
      <Button variant="outline" onClick={onEdit}>Редактировать</Button>
      <Button variant="secondary" onClick={onExport}>Экспорт</Button>
    </ModuleActions>
  </ResultsHeader>
  
  <ResultsSections>
    {module.sections.map(section => (
      <ResultsSection key={section.id}>
        <SectionTitle>{section.title}</SectionTitle>
        <SectionContent>
          {section.subsections.map(subsection => (
            <Subsection key={subsection.id}>
              <SubsectionTitle>{subsection.title}</SubsectionTitle>
              <ResponsesList>
                {getResponsesForSubsection(subsection.id).map(response => (
                  <ResponseItem key={response.id}>
                    <QuestionText>{response.question.text}</QuestionText>
                    <AnswerText>{response.answer_text}</AnswerText>
                    <SourceBadge type={response.source_type} />
                    {response.comment && (
                      <CommentText>{response.comment}</CommentText>
                    )}
                  </ResponseItem>
                ))}
              </ResponsesList>
            </Subsection>
          ))}
        </SectionContent>
      </ResultsSection>
    ))}
  </ResultsSections>
  
  <ActorRecommendations>
    <RecommendationsTitle>Рекомендации актеру</RecommendationsTitle>
    <RecommendationsList>
      {generateRecommendations(responses).map(rec => (
        <RecommendationItem key={rec.id}>
          <RecommendationText>{rec.text}</RecommendationText>
          <RecommendationCategory>{rec.category}</RecommendationCategory>
        </RecommendationItem>
      ))}
    </RecommendationsList>
  </ActorRecommendations>
</AnalysisResults>
```

## 📱 Адаптивность

### Breakpoints
```css
/* Мобильные устройства */
@media (max-width: 640px) { /* sm */ }

/* Планшеты */
@media (min-width: 641px) and (max-width: 1024px) { /* md */ }

/* Десктоп */
@media (min-width: 1025px) { /* lg */ }

/* Большие экраны */
@media (min-width: 1280px) { /* xl */ }
```

### Мобильная адаптация
- **Навигация** - гамбургер меню
- **Карточки** - вертикальная компоновка
- **Формы** - полная ширина полей
- **Таблицы** - горизонтальная прокрутка
- **Модальные окна** - полноэкранные на мобильных

### Сенсорные интерфейсы
- **Минимальный размер** кнопок 44px
- **Swipe-жесты** для навигации
- **Pull-to-refresh** для обновления данных
- **Haptic feedback** для важных действий

## ♿ Доступность (A11y)

### Семантическая разметка
```tsx
// Правильная структура заголовков
<h1>Роль</h1>
  <h2>Проекты</h2>
    <h3>Анализ Гамлета</h3>
      <h4>Персонажи</h4>

// ARIA атрибуты
<button 
  aria-label="Удалить проект"
  aria-describedby="delete-help-text"
  onClick={handleDelete}
>
  <DeleteIcon />
</button>

// Роли и состояния
<div role="tabpanel" aria-labelledby="tab-1" aria-hidden="false">
  Содержимое вкладки
</div>
```

### Клавиатурная навигация
- **Tab** - переход между элементами
- **Enter/Space** - активация кнопок
- **Escape** - закрытие модальных окон
- **Arrow keys** - навигация в списках

### Контрастность
- **Минимальный контраст** 4.5:1 для обычного текста
- **Минимальный контраст** 3:1 для крупного текста
- **Фокус-индикаторы** с высоким контрастом

### Поддержка скринридеров
```tsx
// Живые области для динамического контента
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>

// Описания для сложных элементов
<div 
  role="progressbar" 
  aria-valuenow={progress} 
  aria-valuemin={0} 
  aria-valuemax={100}
  aria-label="Прогресс анализа персонажа"
>
  <div style={{ width: `${progress}%` }} />
</div>
```

## 🎨 Анимации и переходы

### Принципы анимации
- **Быстрые переходы** (200-300ms) для интерактивных элементов
- **Средние переходы** (300-500ms) для смены состояний
- **Медленные переходы** (500ms+) для сложных трансформаций

### Easing функции
```css
/* Стандартные переходы */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);

/* Пружинные эффекты */
--ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
```

### Микроанимации
```tsx
// Hover эффекты
.button {
  transition: all 200ms var(--ease-out);
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

// Загрузочные состояния
.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

// Появление элементов
.fade-in {
  animation: fadeIn 300ms var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

## 🔧 Состояния компонентов

### Загрузка (Loading)
```tsx
// Скелетоны для контента
<SkeletonCard />
<SkeletonText lines={3} />
<SkeletonAvatar />

// Спиннеры для действий
<Button loading>Сохранение...</Button>
<LoadingSpinner size="lg" />
```

### Ошибки (Error)
```tsx
// Состояния ошибок
<ErrorBoundary fallback={<ErrorPage />}>
  <App />
</ErrorBoundary>

<ErrorMessage 
  title="Ошибка загрузки"
  message="Не удалось загрузить данные"
  action={<Button onClick={retry}>Повторить</Button>}
/>
```

### Пустые состояния (Empty)
```tsx
// Пустые списки
<EmptyState
  icon={<ProjectIcon />}
  title="Нет проектов"
  description="Создайте свой первый проект для анализа персонажей"
  action={<Button onClick={createProject}>Создать проект</Button>}
/>
```

---

*Дизайн-система создана для обеспечения консистентности, доступности и отличного пользовательского опыта*
