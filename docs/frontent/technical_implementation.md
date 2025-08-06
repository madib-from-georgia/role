# 🔧 Техническая реализация компонентов чеклиста

## 📦 **СТРУКТУРА ПРОЕКТА**

### **Новая организация файлов:**
```
frontend/src/
├── components/checklist/
│   ├── index.ts                    # Экспорт всех компонентов
│   ├── ChecklistView.tsx           # Главный контейнер
│   ├── ChecklistProgress.tsx       # Прогресс и статистика
│   ├── ChecklistNavigation.tsx     # Навигация
│   ├── QuestionBlock.tsx           # Универсальный блок вопроса
│   ├── QuestionTypes/
│   │   ├── SingleChoice.tsx
│   │   ├── MultipleChoice.tsx
│   │   ├── TextInput.tsx
│   │   └── CustomAnswer.tsx
│   ├── SmartFeatures/                    # ⚠️ РЕАЛИЗУЕТСЯ В ПОСЛЕДНЮЮ ОЧЕРЕДЬ
│   │   ├── AutoComplete.tsx
│   │   ├── ContradictionDetector.tsx
│   │   ├── ContextualHelp.tsx
│   │   └── ExamplesPanel.tsx
│   ├── Mobile/
│   │   ├── MobileQuestionBlock.tsx
│   │   ├── MobileNavigation.tsx
│   │   └── TouchGestures.tsx
│   └── utils/
│       ├── questionTypes.ts
│       ├── validation.ts
│       └── smartLogic.ts
├── hooks/
│   ├── useChecklist.ts
│   ├── useQuestionBlock.ts
│   └── useTouchGestures.ts
├── types/
│   ├── checklist.ts
│   ├── question.ts
│   └── response.ts
└── services/
    ├── checklistApi.ts
    └── smartFeaturesApi.ts
```

## 🎯 **ОСНОВНЫЕ КОМПОНЕНТЫ**

### **1. ChecklistView - Главный контейнер**

```typescript
// components/checklist/ChecklistView.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { ChecklistProgress } from './ChecklistProgress';
import { ChecklistNavigation } from './ChecklistNavigation';
import { QuestionBlock } from './QuestionBlock';
import { ChecklistData } from '../../types/checklist';

interface ChecklistViewProps {
  checklistSlug: string;
  characterId: number;
  isMobile?: boolean;
}

export const ChecklistView: React.FC<ChecklistViewProps> = ({
  checklistSlug,
  characterId,
  isMobile = false
}) => {
  const queryClient = useQueryClient();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showSmartFeatures, setShowSmartFeatures] = useState(true);
  
  const {
    data: checklist,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['checklist', checklistSlug, characterId],
    queryFn: () => checklistApi.getChecklist(checklistSlug, characterId),
    staleTime: 5 * 60 * 1000,
  });

  const updateAnswerMutation = useMutation({
    mutationFn: (data: { questionId: number; response: any }) =>
      checklistApi.updateAnswer(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['checklist', checklistSlug, characterId]);
    }
  });

  const handleAnswerChange = (questionId: number, response: any) => {
    updateAnswerMutation.mutate({ questionId, response });
  };

  if (isLoading) return <LoadingState />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;
  if (!checklist) return <EmptyState />;

  return (
    <div className="checklist-view">
      <ChecklistProgress 
        progress={checklist.completion_stats}
        currentQuestion={currentQuestionIndex + 1}
        totalQuestions={checklist.questions.length}
      />
      
      <div className="checklist-content">
        <ChecklistNavigation
          questions={checklist.questions}
          currentIndex={currentQuestionIndex}
          onNavigate={setCurrentQuestionIndex}
          isMobile={isMobile}
        />
        
        <QuestionBlock
          question={checklist.questions[currentQuestionIndex]}
          response={checklist.responses[currentQuestionIndex]}
          onAnswerChange={(response) => 
            handleAnswerChange(checklist.questions[currentQuestionIndex].id, response)
          }
          isMobile={isMobile}
          showSmartFeatures={showSmartFeatures}
        />
      </div>
    </div>
  );
};
```

### **2. QuestionBlock - Универсальный блок вопроса**

```typescript
// components/checklist/QuestionBlock.tsx
import React, { useState, useMemo } from 'react';
import { SingleChoice } from './QuestionTypes/SingleChoice';
import { MultipleChoice } from './QuestionTypes/MultipleChoice';
import { TextInput } from './QuestionTypes/TextInput';
import { CustomAnswer } from './QuestionTypes/CustomAnswer';
import { AutoComplete } from './SmartFeatures/AutoComplete';
import { ContradictionDetector } from './SmartFeatures/ContradictionDetector';
import { ContextualHelp } from './SmartFeatures/ContextualHelp';
import { QuestionBlock as QuestionBlockType, QuestionResponse } from '../../types/question';

interface QuestionBlockProps {
  question: QuestionBlockType;
  response?: QuestionResponse;
  onAnswerChange: (response: QuestionResponse) => void;
  isMobile?: boolean;
  showSmartFeatures?: boolean;
}

export const QuestionBlock: React.FC<QuestionBlockProps> = ({
  question,
  response,
  onAnswerChange,
  isMobile = false,
  showSmartFeatures = true
}) => {
  const [showHelp, setShowHelp] = useState(false);
  const [showExamples, setShowExamples] = useState(false);
  
  const renderQuestionType = () => {
    const commonProps = {
      question,
      response,
      onAnswerChange,
      isMobile
    };

    switch (question.type) {
      case 'single':
        return <SingleChoice {...commonProps} />;
      case 'multiple':
        return <MultipleChoice {...commonProps} />;
      case 'text':
        return <TextInput {...commonProps} />;
      case 'custom':
        return <CustomAnswer {...commonProps} />;
      default:
        return <TextInput {...commonProps} />;
    }
  };

  const hasContradictions = useMemo(() => {
    if (!showSmartFeatures) return false;
    // Логика проверки противоречий
    return false;
  }, [question, response, showSmartFeatures]);

  return (
    <div className={`question-block ${isMobile ? 'mobile' : 'desktop'}`}>
      <div className="question-header">
        <h2 className="question-title">{question.text}</h2>
        {question.hint && (
          <button 
            className="help-button"
            onClick={() => setShowHelp(!showHelp)}
            aria-label="Показать подсказку"
          >
            💡
          </button>
        )}
      </div>

      <div className="question-content">
        {renderQuestionType()}
        
        {showSmartFeatures && (
          <>
            <AutoComplete 
              question={question}
              onSuggestion={onAnswerChange}
            />
            
            {hasContradictions && (
              <ContradictionDetector 
                question={question}
                response={response}
              />
            )}
          </>
        )}
      </div>

      {showHelp && (
        <ContextualHelp 
          question={question}
          onClose={() => setShowHelp(false)}
        />
      )}
    </div>
  );
};
```

## 🎨 **CSS СТИЛИ**

### **Основные стили для QuestionBlock**
```css
/* components/checklist/QuestionBlock.css */
.question-block {
  background: var(--surface);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 300ms ease;
}

.question-block:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.question-title {
  font-size: clamp(18px, 4vw, 24px);
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  margin: 0;
}

.help-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 200ms ease;
}

.help-button:hover {
  background-color: var(--surface);
}

/* Мобильная версия */
.question-block.mobile {
  padding: 16px;
  margin-bottom: 16px;
}

.question-block.mobile .question-title {
  font-size: 18px;
}

/* Анимации */
.question-block {
  animation: slideIn 300ms ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### **Стили для вариантов ответов**
```css
/* components/checklist/QuestionTypes/options.css */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border: 2px solid var(--surface);
  border-radius: 8px;
  cursor: pointer;
  transition: all 200ms ease;
  background: white;
}

.option-item:hover {
  border-color: var(--accent);
  background: var(--surface);
}

.option-item input[type="radio"],
.option-item input[type="checkbox"] {
  margin-right: 12px;
  transform: scale(1.2);
}

.option-text {
  font-size: 16px;
  color: var(--text-primary);
  flex: 1;
}

.custom-option {
  border-color: var(--warning);
  background: rgba(243, 156, 18, 0.05);
}

.custom-option:hover {
  border-color: var(--warning);
  background: rgba(243, 156, 18, 0.1);
}

/* Мобильная версия */
.mobile .option-item {
  padding: 16px;
  min-height: 44px;
}

.mobile .option-text {
  font-size: 16px;
}
```

## 🔧 **ХУКИ И УТИЛИТЫ**

### **useChecklist - Хук для работы с чеклистом**
```typescript
// hooks/useChecklist.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { checklistApi } from '../services/checklistApi';

export const useChecklist = (checklistSlug: string, characterId: number) => {
  const queryClient = useQueryClient();

  const {
    data: checklist,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['checklist', checklistSlug, characterId],
    queryFn: () => checklistApi.getChecklist(checklistSlug, characterId),
    staleTime: 5 * 60 * 1000, // 5 минут
    cacheTime: 10 * 60 * 1000, // 10 минут
  });

  const updateAnswerMutation = useMutation({
    mutationFn: (data: { questionId: number; response: any }) =>
      checklistApi.updateAnswer(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['checklist', checklistSlug, characterId]);
    },
    onError: (error) => {
      console.error('Ошибка обновления ответа:', error);
    }
  });

  const updateProgress = (questionId: number, response: any) => {
    updateAnswerMutation.mutate({ questionId, response });
  };

  return {
    checklist,
    isLoading,
    error,
    refetch,
    updateProgress,
    isUpdating: updateAnswerMutation.isLoading
  };
};
```

### **useTouchGestures - Хук для мобильных жестов**
```typescript
// hooks/useTouchGestures.ts
import { useState, useEffect, useRef } from 'react';

interface TouchGesturesOptions {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onLongPress?: () => void;
  threshold?: number;
  longPressDelay?: number;
}

export const useTouchGestures = (options: TouchGesturesOptions) => {
  const {
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown,
    onLongPress,
    threshold = 50,
    longPressDelay = 500
  } = options;

  const elementRef = useRef<HTMLElement>(null);
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const [longPressTimer, setLongPressTimer] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const handleTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0];
      setTouchStart({ x: touch.clientX, y: touch.clientY });

      // Запуск таймера для long press
      if (onLongPress) {
        const timer = setTimeout(() => {
          onLongPress();
        }, longPressDelay);
        setLongPressTimer(timer);
      }
    };

    const handleTouchMove = (e: TouchEvent) => {
      // Отмена long press при движении
      if (longPressTimer) {
        clearTimeout(longPressTimer);
        setLongPressTimer(null);
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (!touchStart) return;

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - touchStart.x;
      const deltaY = touch.clientY - touchStart.y;

      // Отмена long press
      if (longPressTimer) {
        clearTimeout(longPressTimer);
        setLongPressTimer(null);
      }

      // Определение направления свайпа
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        if (Math.abs(deltaX) > threshold) {
          if (deltaX > 0 && onSwipeRight) {
            onSwipeRight();
          } else if (deltaX < 0 && onSwipeLeft) {
            onSwipeLeft();
          }
        }
      } else {
        if (Math.abs(deltaY) > threshold) {
          if (deltaY > 0 && onSwipeDown) {
            onSwipeDown();
          } else if (deltaY < 0 && onSwipeUp) {
            onSwipeUp();
          }
        }
      }

      setTouchStart(null);
    };

    element.addEventListener('touchstart', handleTouchStart);
    element.addEventListener('touchmove', handleTouchMove);
    element.addEventListener('touchend', handleTouchEnd);

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
      if (longPressTimer) {
        clearTimeout(longPressTimer);
      }
    };
  }, [touchStart, longPressTimer, threshold, longPressDelay, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown, onLongPress]);

  return elementRef;
};
```

## 📱 **МОБИЛЬНАЯ ОПТИМИЗАЦИЯ**

### **Responsive Breakpoints**
```css
/* styles/responsive.css */
:root {
  --mobile: 320px;
  --tablet: 768px;
  --desktop: 1200px;
}

/* Мобильные устройства */
@media (max-width: 767px) {
  .checklist-view {
    padding: 16px;
  }
  
  .question-block {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .options-list {
    gap: 8px;
  }
  
  .option-item {
    padding: 16px;
    min-height: 44px;
  }
}

/* Планшеты */
@media (min-width: 768px) and (max-width: 1199px) {
  .checklist-view {
    padding: 24px;
  }
  
  .question-block {
    padding: 20px;
  }
}

/* Десктоп */
@media (min-width: 1200px) {
  .checklist-view {
    padding: 32px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .question-block {
    padding: 24px;
  }
}
```

### **Touch-friendly элементы**
```css
/* styles/touch-friendly.css */
.touch-friendly {
  min-height: 44px;
  min-width: 44px;
  padding: 12px 16px;
  font-size: 16px;
  border-radius: 8px;
  border: 2px solid transparent;
  transition: all 200ms ease;
}

.touch-friendly:active {
  transform: scale(0.98);
}

.touch-friendly:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

/* Увеличенные кнопки для мобильных */
@media (max-width: 767px) {
  .btn {
    min-height: 48px;
    font-size: 16px;
    padding: 12px 20px;
  }
  
  .option-item {
    min-height: 48px;
  }
}
```

## 🧪 **ТЕСТИРОВАНИЕ**

### **Unit тесты для QuestionBlock**
```typescript
// tests/components/checklist/QuestionBlock.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { QuestionBlock } from '../../../components/checklist/QuestionBlock';
import { QuestionBlock as QuestionBlockType } from '../../../types/question';

const mockQuestion: QuestionBlockType = {
  id: 1,
  text: 'Какие у персонажа глаза?',
  type: 'single',
  options: ['большие', 'маленькие', 'глубоко посаженные'],
  hint: 'Обратите внимание на описание в тексте'
};

const mockResponse = {
  answer: 'маленькие',
  source_type: 'found_in_text' as const,
  comment: 'Автор прямо указывает'
};

describe('QuestionBlock', () => {
  it('отображает вопрос корректно', () => {
    render(
      <QuestionBlock
        question={mockQuestion}
        onAnswerChange={jest.fn()}
      />
    );

    expect(screen.getByText('Какие у персонажа глаза?')).toBeInTheDocument();
    expect(screen.getByText('большие')).toBeInTheDocument();
    expect(screen.getByText('маленькие')).toBeInTheDocument();
  });

  it('обрабатывает выбор варианта', () => {
    const onAnswerChange = jest.fn();
    
    render(
      <QuestionBlock
        question={mockQuestion}
        onAnswerChange={onAnswerChange}
      />
    );

    fireEvent.click(screen.getByText('маленькие'));
    
    expect(onAnswerChange).toHaveBeenCalledWith({
      answer: 'маленькие',
      source_type: 'imagined',
      comment: ''
    });
  });

  it('отображает текущий ответ', () => {
    render(
      <QuestionBlock
        question={mockQuestion}
        response={mockResponse}
        onAnswerChange={jest.fn()}
      />
    );

    const radioButton = screen.getByDisplayValue('маленькие') as HTMLInputElement;
    expect(radioButton.checked).toBe(true);
  });
});
```

Этот технический документ предоставляет детальную реализацию всех компонентов чеклиста с учетом современных практик разработки, производительности и пользовательского опыта. 
