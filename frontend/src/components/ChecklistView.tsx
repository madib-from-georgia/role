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
    onSuccess: (_: any, responseId: any) => {
      // Обновляем локальные данные
      if (localData) {
        const updatedData = { ...localData };
        
        // Находим и удаляем ответ
        for (const section of updatedData.sections) {
          for (const subsection of section.subsections) {
            for (const group of subsection.question_groups) {
              const question = group.questions.find(q => q.current_response?.id === responseId);
              if (question) {
                question.current_response = undefined;
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
      <div className="checklist-loading">
        <div className="loading-content">
          <div className="spinner"></div>
          <span className="loading-text">Загрузка чеклиста...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="checklist-error">
        <div className="error-content">
          <div className="error-title">Ошибка при загрузке чеклиста</div>
          <p className="error-message">
            {error instanceof Error ? error.message : 'Неизвестная ошибка'}
          </p>
        </div>
      </div>
    );
  }

  if (!localData) {
    return (
      <div className="checklist-empty">
        <p className="empty-message">Чеклист не найден</p>
      </div>
    );
  }

  const stats = localData.completion_stats;

  return (
    <div className="checklist-view">
      {/* Заголовок чеклиста */}
      <div className="checklist-header">
        <div className="header-content">
          {localData.icon && (
            <span className="checklist-icon">{localData.icon}</span>
          )}
          <div className="header-info">
            <h1 className="checklist-title">{localData.title}</h1>
            {localData.description && (
              <p className="checklist-description">{localData.description}</p>
            )}
          </div>
        </div>

        {/* Общая статистика */}
        {stats && (
          <div className="checklist-stats">
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-number primary">
                  {stats.answered_questions}
                </div>
                <div className="stat-label">из {stats.total_questions}</div>
                <div className="stat-sublabel">отвечено</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-number success">
                  {stats.completion_percentage}%
                </div>
                <div className="stat-sublabel">завершено</div>
              </div>
              
              <div className="stat-card">
                <div className="stat-number">
                  {Object.entries(stats.answers_by_source).length}
                </div>
                <div className="stat-sublabel">типов источников</div>
              </div>
              
              <div className="stat-card">
                {stats.last_updated && (
                  <>
                    <div className="stat-date">
                      {new Date(stats.last_updated).toLocaleDateString('ru-RU')}
                    </div>
                    <div className="stat-sublabel">обновлено</div>
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Прогресс-бар */}
        {stats && (
          <div className="overall-progress">
            <div className="progress-header">
              <span className="progress-label">Общий прогресс</span>
              <span className="progress-value">{stats.completion_percentage}%</span>
            </div>
            <div className="progress-bar overall">
              <div 
                className={`progress-fill ${
                  stats.completion_percentage === 100 ? 'completed' : 
                  stats.completion_percentage > 50 ? 'in-progress' : 'started'
                }`}
                style={{ width: `${stats.completion_percentage}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Секции чеклиста */}
      <div className="checklist-sections">
        {localData.sections.map((section) => (
          <ChecklistSection
            key={section.id}
            section={section}
            onAnswerUpdate={handleAnswerUpdate}
            onAnswerDelete={handleAnswerDelete}
            isExpanded={true}
          />
        ))}
      </div>

      {/* Индикатор загрузки при обновлении */}
      {(updateAnswerMutation.isLoading || deleteAnswerMutation.isLoading) && (
        <div className="loading-indicator">
          <div className="loading-indicator-content">
            <div className="spinner small"></div>
            <span className="loading-indicator-text">
              {updateAnswerMutation.isLoading ? 'Сохранение...' : 'Удаление...'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
