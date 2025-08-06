import React, { useState, useEffect } from 'react';
import { ChecklistSection, ChecklistSectionData } from './ChecklistSection';
import { useMutation, useQuery, useQueryClient } from 'react-query';
import { checklistApi } from '../services/api';

export interface ChecklistData {
  id: number;
  title: string;
  description?: string;
  slug: string;
  icon?: string;
  goal?: string;  // Цель чеклиста
  how_to_use?: string;  // Как использовать этот блок
  sections: ChecklistSectionData[];
  completion_stats?: {
    total_questions: number;
    answered_questions: number;
    completion_percentage: number;
    answers_by_source: Record<string, number>;
    last_updated?: string;
  };
}

interface ChecklistViewProps {
  checklistSlug: string;
  characterId: number;
}

export const ChecklistView: React.FC<ChecklistViewProps> = ({
  checklistSlug,
  characterId
}) => {
  const queryClient = useQueryClient();
  const [localData, setLocalData] = useState<ChecklistData | null>(null);
  const [showHowToUse, setShowHowToUse] = useState(false);

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
      // Обновляем локальные данные
      if (localData) {
        const updatedData = { ...localData };
        
        // Находим и обновляем вопрос
        for (const section of updatedData.sections) {
          for (const subsection of section.subsections) {
            for (const group of subsection.question_groups) {
              const question = group.questions.find(q => q.id === variables.questionId);
              if (question) {
                question.current_response = {
                  id: response.id,
                  answer: response.answer,
                  source_type: response.source_type,
                  comment: response.comment,
                  version: response.version,
                  updated_at: response.updated_at
                };
                break;
              }
            }
          }
        }
        
        setLocalData(updatedData);
      }
      
      // Инвалидируем кэш
      queryClient.invalidateQueries({ 
        queryKey: ['checklist', checklistSlug, characterId] 
      });
    },
    onError: (error: any) => {
      console.error('Ошибка при обновлении ответа:', error);
    }
  });

  // Мутация для удаления ответа
  const deleteAnswerMutation = useMutation({
    mutationFn: (responseId: number) => checklistApi.deleteResponse(responseId),
    onSuccess: (response: any, responseId: number) => {
      // Обновляем локальные данные
      if (localData) {
        const updatedData = { ...localData };
        
        // Находим и удаляем ответ
        for (const section of updatedData.sections) {
          for (const subsection of section.subsections) {
            for (const group of subsection.question_groups) {
              for (const question of group.questions) {
                if (question.current_response?.id === responseId) {
                  question.current_response = undefined;
                  break;
                }
              }
            }
          }
        }
        
        setLocalData(updatedData);
      }
      
      // Инвалидируем кэш
      queryClient.invalidateQueries({ 
        queryKey: ['checklist', checklistSlug, characterId] 
      });
    },
    onError: (error: any) => {
      console.error('Ошибка при удалении ответа:', error);
    }
  });

  const handleAnswerUpdate = (questionId: number, data: {
    answer?: string;
    source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    comment?: string;
  }) => {
    updateAnswerMutation.mutate({ questionId, data });
  };

  const handleAnswerDelete = (responseId: number) => {
    deleteAnswerMutation.mutate(responseId);
  };

  if (isLoading) {
    return (
      <div className="checklist-view">
        <div className="loading">Загрузка чеклиста...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="checklist-view">
        <div className="error">Ошибка загрузки чеклиста: {error instanceof Error ? error.message : 'Неизвестная ошибка'}</div>
      </div>
    );
  }

  if (!localData) {
    return (
      <div className="checklist-view">
        <div className="error">Чеклист не найден</div>
      </div>
    );
  }

  return (
    <div className="checklist-view">
      {/* Заголовок чеклиста */}
      <div className="checklist-header">
        <h1 className="checklist-title">
          {localData.icon && <span className="checklist-icon">{localData.icon}</span>}
          {localData.title}
        </h1>
        {localData.description && (
          <p className="checklist-description">{localData.description}</p>
        )}
      </div>

      {/* Цель чеклиста */}
      {localData.goal && (
        <div className="checklist-goal">
          <h2>Цель чеклиста</h2>
          <div className="goal-content">
            {localData.goal}
          </div>
        </div>
      )}

      {/* Как использовать этот блок */}
      {localData.how_to_use && (
        <div className="checklist-how-to-use">
          <button 
            className="how-to-use-toggle"
            onClick={() => setShowHowToUse(!showHowToUse)}
          >
            {showHowToUse ? 'Скрыть инструкцию' : 'Как использовать этот блок'}
          </button>
          {showHowToUse && (
            <div className="how-to-use-content">
              {localData.how_to_use}
            </div>
          )}
        </div>
      )}

      {/* Статистика заполнения */}
      {localData.completion_stats && (
        <div className="completion-stats">
          <div className="stats-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${localData.completion_stats.completion_percentage}%` }}
            ></div>
          </div>
          <div className="stats-text">
            Заполнено: {localData.completion_stats.answered_questions} из {localData.completion_stats.total_questions} вопросов 
            ({localData.completion_stats.completion_percentage.toFixed(1)}%)
          </div>
        </div>
      )}

      {/* Секции чеклиста */}
      <div className="checklist-sections">
        {localData.sections.map((section) => (
          <ChecklistSection
            key={section.id}
            section={section}
            onAnswerUpdate={handleAnswerUpdate}
            onAnswerDelete={handleAnswerDelete}
          />
        ))}
      </div>
    </div>
  );
};
