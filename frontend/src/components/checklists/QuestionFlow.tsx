import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "react-query";
import { checklistApi, charactersApi, api } from "../../services/api";
import { Button, Text } from "@gravity-ui/uikit";
import { useNavigate } from "react-router-dom";

// Import subcomponents
import { QuestionCard } from "./QuestionCard";
import { ProgressBar } from "./ProgressBar";
import { QuestionNavigation } from "./QuestionNavigation";
import { ChecklistSwitcher } from "./ChecklistSwitcher";
import { ExportDialog } from "./ExportDialog";

// Import types
import { Checklist, ChecklistQuestion, Gender, ChecklistAnswer } from "../../types/checklist";

interface QuestionFlowProps {
  checklistSlug: string;
  characterId: number;
}

// API Response types
interface ResponseData {
  id: number;
  question_id: number;
  character_id: number;
  answer_id?: number;
  answer_text?: string;
  source_type?: "FOUND_IN_TEXT" | "LOGICALLY_DERIVED" | "IMAGINED";
  comment?: string;
  version: number;
  created_at: string;
  updated_at: string;
  answer?: unknown;
}

interface MutationVariables {
  questionId: number;
  data: {
    answer_id?: number;
    answer_text?: string;
    source_type?: "FOUND_IN_TEXT" | "LOGICALLY_DERIVED" | "IMAGINED";
    comment?: string;
  };
}

// Удалил неиспользуемый интерфейс SectionData

export const QuestionFlow: React.FC<QuestionFlowProps> = ({
  checklistSlug,
  characterId,
}) => {
  const queryClient = useQueryClient();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [localData, setLocalData] = useState<Checklist | null>(null);
  const [isExportDialogOpen, setIsExportDialogOpen] = useState(false);
  const navigate = useNavigate();

  // Загружаем данные персонажа
  const { data: character } = useQuery<{ name: string; gender?: string; description?: string; [key: string]: unknown }>({
    queryKey: ["character", characterId],
    queryFn: () => charactersApi.getById(String(characterId!)) as Promise<{ name: string; gender?: string; description?: string; [key: string]: unknown }>,
    enabled: !!characterId,
  });

  // Загрузка чеклиста
  const {
    data: checklistData,
    isLoading,
    error,
  } = useQuery<Checklist>({
    queryKey: ["checklist", checklistSlug, characterId],
    queryFn: () =>
      api.get(`/api/checklists/${checklistSlug}/character/${characterId}`) as Promise<Checklist>,
    staleTime: 5 * 60 * 1000, // 5 минут
  });

  // Синхронизация с локальным состоянием
  useEffect(() => {
    if (checklistData) {
      setLocalData(checklistData);
    }
  }, [checklistData]);

  // Мутация для обновления ответа
  const updateAnswerMutation = useMutation<ResponseData, Error, MutationVariables>({
    mutationFn: async ({
      questionId,
      data,
    }: MutationVariables) => {
      const response = await checklistApi.createOrUpdateResponse({
        question_id: questionId,
        character_id: characterId,
        ...data,
      });
      return response as ResponseData;
    },
    onSuccess: (response: ResponseData, variables: MutationVariables) => {
      // Обновляем только локальное состояние, не перезагружаем данные
      if (localData && response) {
        const updatedData = { ...localData };

        // Безопасное обновление структуры
        updatedData.sections?.forEach((section) => {
          section.subsections?.forEach((subsection) => {
            subsection.question_groups?.forEach((group) => {
              const question = group.questions?.find(
                (q) => q?.id === variables.questionId
              );
              if (question) {
                question.current_response = {
                  id: response.id,
                  question_id: response.question_id,
                  character_id: response.character_id,
                  answer_id: response.answer_id,
                  answer_text: response.answer_text,
                  source_type: response.source_type,
                  comment: response.comment,
                  version: response.version,
                  created_at: response.created_at,
                  updated_at: response.updated_at,
                  answer: response.answer as ChecklistAnswer | undefined,
                };
              }
            });
          });
        });

        setLocalData(updatedData);
      }
      console.log("Ответ успешно сохранен локально");
    },
    onError: (error: Error) => {
      console.error("Ошибка при обновлении ответа:", error);
    },
  });

  // Мутация для удаления ответа
  const deleteAnswerMutation = useMutation({
    mutationFn: (responseId: number) => checklistApi.deleteResponse(responseId),
    onSuccess: (_response: unknown, responseId: number) => {
      // Update local data
      if (localData) {
        const updatedData = { ...localData };

        // Find and remove answer in hierarchical structure
        updatedData.sections?.forEach((section) => {
          section.subsections?.forEach((subsection) => {
            subsection.question_groups?.forEach((group) => {
              group.questions?.forEach((question) => {
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
        queryKey: ["checklist", checklistSlug, characterId],
      });
    },
    onError: (error: Error) => {
      console.error("Ошибка при удалении ответа:", error);
    },
  });

  // Convert hierarchical data to flat question array
  const getAllQuestions = (): ChecklistQuestion[] => {
    if (!localData) return [];

    const questions: ChecklistQuestion[] = [];

    // Сортируем секции по order_index
    const sortedSections = [...(localData.sections || [])].sort((a, b) => a.order_index - b.order_index);

    sortedSections.forEach((section) => {
      // Сортируем подсекции по order_index
      const sortedSubsections = [...(section.subsections || [])].sort((a, b) => a.order_index - b.order_index);
      
      sortedSubsections.forEach((subsection) => {
        // Сортируем группы вопросов по order_index
        const sortedGroups = [...(subsection.question_groups || [])].sort((a, b) => a.order_index - b.order_index);
        
        sortedGroups.forEach((group) => {
          // Сортируем вопросы по order_index
          const sortedQuestions = [...(group.questions || [])].sort((a, b) => a.order_index - b.order_index);
          
          sortedQuestions.forEach((question) => {
            questions.push({
              ...question,
              sectionTitle: section.title,
              subsectionTitle: subsection.title,
              groupTitle: group.title,
            });
          });
        });
      });
    });

    return questions;
  };

  const allQuestions = getAllQuestions();
  const currentQuestion = allQuestions[currentQuestionIndex];

  const handleAnswerUpdate = (questionId: number, data: {
    answer_id?: number;
    answer_text?: string;
    source_type?: "FOUND_IN_TEXT" | "LOGICALLY_DERIVED" | "IMAGINED";
    comment?: string;
  }) => {
    updateAnswerMutation.mutate({ questionId, data });
  };

  const handleMultipleAnswersUpdate = async (
    questionId: number,
    characterId: number,
    selectedAnswerIds: number[],
    comment?: string,
    sourceType?: "FOUND_IN_TEXT" | "LOGICALLY_DERIVED" | "IMAGINED",
    customText?: string
  ) => {
    try {
      await checklistApi.manageMultipleResponses({
        question_id: questionId,
        character_id: characterId,
        selected_answer_ids: selectedAnswerIds,
        comment,
        source_type: sourceType,
        custom_text: customText,
      });

      // Обновляем локальные данные после успешного сохранения
      queryClient.invalidateQueries({
        queryKey: ["checklist", checklistSlug, characterId],
      });

      console.log("Множественные ответы успешно обновлены");
    } catch (error) {
      console.error("Ошибка при обновлении множественных ответов:", error);
    }
  };

  const handleAnswerDelete = (responseId: number) => {
    deleteAnswerMutation.mutate(responseId);
  };

  const handleNext = () => {
    if (currentQuestionIndex < allQuestions.length - 1) {
      setCurrentQuestionIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prev) => prev - 1);
    }
  };

  const handleJumpToQuestion = (index: number) => {
    if (index >= 0 && index < allQuestions.length) {
      setCurrentQuestionIndex(index);
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
            <p>
              Не удалось загрузить чеклист:{" "}
              {error instanceof Error ? error.message : "Неизвестная ошибка"}
            </p>
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
        <div className="question-flow__controls">
          <Button onClick={() => navigate(-1)} view="outlined">
            ←
          </Button>

          <ChecklistSwitcher
            characterId={characterId}
            currentChecklist={checklistSlug}
          />
        </div>

        <div className="character-info">
          <Text variant="header-1" ellipsis={true}>
            {character?.name}
          </Text>
          {character?.description && <p>{character.description}</p>}
        </div>

        <div className="question-flow__controls">
          <Button
            onClick={() => setIsExportDialogOpen(true)}
            title="Экспорт чеклиста"
            view="outlined"
            size="m"
          >
            📄 Экспорт
          </Button>
        </div>
      </div>

      {/* Main content area */}
      <div className="question-flow__content">
        {/* Question area */}
        <div className="question-flow__main">
          <ProgressBar
            currentIndex={currentQuestionIndex}
            totalQuestions={allQuestions.length}
            checklist={localData}
          />
          <QuestionCard
            question={currentQuestion}
            characterGender={(character?.gender as Gender) || 'male'}
            characterId={characterId}
            onAnswerUpdate={handleAnswerUpdate}
            onMultipleAnswersUpdate={handleMultipleAnswersUpdate}
            onAnswerDelete={handleAnswerDelete}
            isLoading={updateAnswerMutation.isLoading}
            allQuestions={allQuestions}
            currentQuestionIndex={currentQuestionIndex}
            onQuestionSelect={handleJumpToQuestion}
            completionPercentage={
              localData?.completion_stats?.completion_percentage || 0
            }
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

      {/* Export Dialog */}
      {localData && (
        <ExportDialog
          characterId={characterId}
          characterName={localData.character?.name || "Персонаж"}
          isOpen={isExportDialogOpen}
          onClose={() => setIsExportDialogOpen(false)}
        />
      )}
    </div>
  );
};
