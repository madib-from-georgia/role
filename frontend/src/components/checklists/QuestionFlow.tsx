import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { checklistApi } from '../../services/api';

// Import subcomponents
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
        
        // Find and update question in hierarchical structure
        updatedData.sections?.forEach((section: any) => {
          section.subsections?.forEach((subsection: any) => {
            subsection.question_groups?.forEach((group: any) => {
              const question = group.questions?.find((q: any) => q.id === variables.questionId);
              if (question) {
                question.current_response = {
                  id: response.id,
                  answer: response.answer,
                  source_type: response.source_type,
                  comment: response.comment,
                  version: response.version,
                  updated_at: response.updated_at
                };
              }
            });
          });
        });
        
        setLocalData(updatedData);
      }
      
      // Invalidate cache
      queryClient.invalidateQueries({ 
        queryKey: ['checklist', checklistSlug, characterId] 
      });
    }
  });

  // Мутация для удаления ответа
  const deleteAnswerMutation = useMutation({
    mutationFn: (responseId: number) => checklistApi.deleteResponse(responseId),
    onSuccess: (_response: any, responseId: number) => {
      // Update local data
      if (localData) {
        const updatedData = { ...localData };
        
        // Find and remove answer in hierarchical structure
        updatedData.sections?.forEach((section: any) => {
          section.subsections?.forEach((subsection: any) => {
            subsection.question_groups?.forEach((group: any) => {
              group.questions?.forEach((question: any) => {
                if (question.current_response?.id === responseId) {
                  question.current_response = undefined;
                }
              });
            });
          });
        });
        
        setLocalData(updatedData);
      }
      
      // Invalidate cache
      queryClient.invalidateQueries({ 
        queryKey: ['checklist', checklistSlug, characterId] 
      });
    },
    onError: (error: any) => {
      console.error('Ошибка при удалении ответа:', error);
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

  const handleAnswerDelete = (responseId: number) => {
    deleteAnswerMutation.mutate(responseId);
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
          <div className="loading-spinner">
            <div className="spinner large"></div>
          </div>
          <div className="loading-text">
            <h2>Загрузка чеклиста...</h2>
            <p>Подготавливаем вопросы для анализа персонажа</p>
          </div>
          <div className="loading-progress">
            <div className="loading-bar">
              <div className="loading-fill"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="question-flow question-flow--error">
        <div className="error-content">
          <div className="error-icon">⚠️</div>
          <div className="error-details">
            <h2>Ошибка загрузки чеклиста</h2>
            <p>Не удалось загрузить чеклист: {error instanceof Error ? error.message : 'Неизвестная ошибка'}</p>
            <div className="error-actions">
              <button 
                className="btn btn-primary"
                onClick={() => window.location.reload()}
              >
                🔄 Попробовать снова
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => window.history.back()}
              >
                ← Вернуться назад
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!localData || allQuestions.length === 0) {
    return (
      <div className="question-flow question-flow--empty">
        <div className="empty-content">
          <div className="empty-icon">📝</div>
          <div className="empty-details">
            <h2>Чеклист пуст</h2>
            <p>В этом чеклисте пока нет вопросов для заполнения</p>
            <div className="empty-actions">
              <button 
                className="btn btn-primary"
                onClick={() => window.history.back()}
              >
                ← Вернуться к списку чеклистов
              </button>
            </div>
          </div>
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
            onAnswerDelete={handleAnswerDelete}
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
