import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { checklistApi } from '../../services/api';

// Import subcomponents (will be created later)
import { QuestionCard } from './QuestionCard';
import { ProgressBar } from './ProgressBar';
import { QuestionNavigation } from './QuestionNavigation';
import { NavigationSidebar } from './NavigationSidebar';
import { ChecklistSwitcher } from './ChecklistSwitcher';

interface QuestionFlowProps {
  checklistSlug: string;
  characterId: number;
}

export const QuestionFlow: React.FC<QuestionFlowProps> = ({
  checklistSlug,
  characterId
}) => {
  const queryClient = useQueryClient();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [localData, setLocalData] = useState<any>(null);

  // Загрузка чеклиста
  const { data: checklistData, isLoading, error } = useQuery({
    queryKey: ['checklist', checklistSlug, characterId],
    queryFn: () => checklistApi.getChecklistForCharacter(checklistSlug, characterId),
    staleTime: 5 * 60 * 1000, // 5 минут
  });

  // Синхронизация с локальным состоянием
  useEffect(() => {
    if (checklistData) {
      setLocalData(checklistData);
    }
  }, [checklistData]);

  // Мутация для обновления ответа
  const updateAnswerMutation = useMutation({
    mutationFn: ({ questionId, data }: {
      questionId: number;
      data: {
        answer?: string;
        source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
        comment?: string;
      }
    }) => checklistApi.createOrUpdateResponse({
      question_id: questionId,
      character_id: characterId,
      ...data
    }),
    onSuccess: (response: any, variables: any) => {
      // Update local data
      if (localData) {
        const updatedData = { ...localData };
        
        // Find and update question
        // TODO: Implement proper data structure transformation
        setLocalData(updatedData);
      }
      
      // Invalidate cache
      queryClient.invalidateQueries({ 
        queryKey: ['checklist', checklistSlug, characterId] 
      });
    }
  });

  // Convert hierarchical data to flat question array
  const getAllQuestions = () => {
    if (!localData) return [];
    
    const questions: any[] = [];
    
    localData.sections?.forEach((section: any) => {
      section.subsections?.forEach((subsection: any) => {
        subsection.question_groups?.forEach((group: any) => {
          group.questions?.forEach((question: any) => {
            questions.push({
              ...question,
              sectionTitle: section.title,
              subsectionTitle: subsection.title,
              groupTitle: group.title
            });
          });
        });
      });
    });
    
    return questions;
  };

  const allQuestions = getAllQuestions();
  const currentQuestion = allQuestions[currentQuestionIndex];

  const handleAnswerUpdate = (questionId: number, data: any) => {
    updateAnswerMutation.mutate({ questionId, data });
  };

  const handleNext = () => {
    if (currentQuestionIndex < allQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleJumpToQuestion = (index: number) => {
    if (index >= 0 && index < allQuestions.length) {
      setCurrentQuestionIndex(index);
      setIsSidebarOpen(false);
    }
  };

  if (isLoading) {
    return (
      <div className="question-flow question-flow--loading">
        <div className="loading-content">
          <div className="spinner large"></div>
          <span>Загрузка чеклиста...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="question-flow question-flow--error">
        <div className="error-content">
          <h2>Ошибка загрузки</h2>
          <p>Не удалось загрузить чеклист: {error instanceof Error ? error.message : 'Неизвестная ошибка'}</p>
        </div>
      </div>
    );
  }

  if (!localData || allQuestions.length === 0) {
    return (
      <div className="question-flow question-flow--empty">
        <div className="empty-content">
          <h2>Чеклист пуст</h2>
          <p>В этом чеклисте нет вопросов для заполнения</p>
        </div>
      </div>
    );
  }

  return (
    <div className="question-flow">
      {/* Header with progress and controls */}
      <div className="question-flow__header">
        <ProgressBar
          currentIndex={currentQuestionIndex}
          totalQuestions={allQuestions.length}
          checklist={localData}
        />
        
        <div className="question-flow__controls">
          <button
            className="btn btn-icon"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            title="Навигация по вопросам"
          >
            ☰
          </button>
          
          <ChecklistSwitcher
            characterId={characterId}
            currentChecklist={checklistSlug}
          />
        </div>
      </div>

      {/* Main content area */}
      <div className="question-flow__content">
        {/* Sidebar */}
        <NavigationSidebar
          isOpen={isSidebarOpen}
          questions={allQuestions}
          currentIndex={currentQuestionIndex}
          onQuestionSelect={handleJumpToQuestion}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Question area */}
        <div className="question-flow__main">
          <QuestionCard
            question={currentQuestion}
            onAnswerUpdate={handleAnswerUpdate}
            isLoading={updateAnswerMutation.isLoading}
          />
        </div>
      </div>

      {/* Navigation footer */}
      <div className="question-flow__footer">
        <QuestionNavigation
          currentIndex={currentQuestionIndex}
          totalQuestions={allQuestions.length}
          onPrevious={handlePrevious}
          onNext={handleNext}
          canGoBack={currentQuestionIndex > 0}
          canGoForward={currentQuestionIndex < allQuestions.length - 1}
        />
      </div>
    </div>
  );
};