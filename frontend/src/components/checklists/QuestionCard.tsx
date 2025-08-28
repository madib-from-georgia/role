import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Label,
  Text,
  Radio,
  Checkbox,
  TextArea,
  SegmentedRadioGroup,
  Breadcrumbs,
  ArrowToggle
} from "@gravity-ui/uikit";
import { QuestionNavigation } from "./QuestionNavigation";
import {
  ChecklistQuestion,
  ChecklistAnswer,
  Gender,
  SourceType,
  ChecklistQuestionGroup,
} from "../../types/checklist";

interface QuestionCardProps {
  question: ChecklistQuestion;
  questionGroup: ChecklistQuestionGroup;
  characterGender: Gender;
  characterId: number;
  onAnswerUpdate: (
    questionId: number,
    data: {
      answer_id?: number;
      answer_text?: string;
      source_type?: SourceType;
      comment?: string;
    }
  ) => void;
  onMultipleAnswersUpdate: (
    questionId: number,
    characterId: number,
    selectedAnswerIds: number[],
    comment?: string,
    sourceType?: SourceType
  ) => void;
  onAnswerDelete?: (responseId: number) => void;
  isLoading: boolean;
  allQuestions: ChecklistQuestion[];
  currentQuestionIndex: number;
  onQuestionSelect: (index: number) => void;
  completionPercentage: number;
  onPrevious: () => void;
  onNext: () => void;
  canGoBack: boolean;
  canGoForward: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  questionGroup,
  characterGender,
  characterId,
  onAnswerUpdate,
  onMultipleAnswersUpdate,
  onAnswerDelete,
  allQuestions,
  currentQuestionIndex,
  onPrevious,
  onNext,
  canGoBack,
  canGoForward,
}) => {
  // Состояние только для UI и комментариев
  const [formState, setFormState] = useState({
    comment: "",
    sourceType: "FOUND_IN_TEXT" as SourceType,
  });

  // Состояние для раскрытия exercise (hint больше не нужен)
  const [exerciseExpanded, setExerciseExpanded] = useState(false);

  // Получаем данные напрямую из пропсов с мемоизацией
  const response = question?.current_response;
  const responses = useMemo(() => {
    return question?.current_responses || [];
  }, [question?.current_responses]);
  const primaryResponse = response || responses[0];

  // Вычисляем состояние выбранных ответов из пропсов с useMemo
  const selectedAnswerId = useMemo(() => {
    return question?.answer_type === "single"
      ? response?.answer_id || null
      : null;
  }, [question?.answer_type, response?.answer_id]);

  const selectedAnswerIds = useMemo(() => {
    return question?.answer_type === "multiple"
      ? (responses.map((r) => r.answer_id).filter(Boolean) as number[])
      : [];
  }, [question?.answer_type, responses]);

  // Инициализация комментария и источника при смене вопроса
  useEffect(() => {
    if (!question) return;

    setFormState({
      comment: primaryResponse?.comment || "",
      sourceType: primaryResponse?.source_type || "FOUND_IN_TEXT",
    });

    // Сбрасываем состояние раскрытия exercise при смене вопроса
    setExerciseExpanded(false);
  }, [
    question?.id,
    question,
    primaryResponse?.comment,
    primaryResponse?.source_type,
  ]);

  // Обработчик для переключения раскрытия exercise
  const toggleExercise = useCallback(() => {
    setExerciseExpanded(prev => !prev);
  }, []);

  // Получение отображаемого значения ответа в зависимости от пола
  const getAnswerDisplayValue = useCallback(
    (answer: ChecklistAnswer): string => {
      return characterGender === "male"
        ? answer.value_male
        : answer.value_female;
    },
    [characterGender]
  );

  // Обработчики изменений
  const handleSingleChoiceChange = useCallback(
    (answerId: number) => {
      if (question?.answer_type !== "single") {
        return null;
      }

      // Немедленно отправляем обновление на сервер
      const data = {
        comment: formState.comment,
        source_type: formState.sourceType,
        answer_id: answerId,
      };

      onAnswerUpdate(question.id, data);
    },
    [question, formState.comment, formState.sourceType, onAnswerUpdate]
  );

  const handleMultipleChoiceChange = useCallback(
    (answerId: number, checked: boolean) => {
      if (question?.answer_type !== "multiple") {
        return null;
      }

      // Вычисляем новые выбранные ID на основе текущих данных из пропсов
      const newSelectedIds = checked
        ? [...selectedAnswerIds, answerId]
        : selectedAnswerIds.filter((id: number) => id !== answerId);

      // Немедленно отправляем обновление на сервер
      onMultipleAnswersUpdate(
        question.id,
        characterId,
        newSelectedIds,
        formState.comment,
        formState.sourceType
      );
    },
    [
      question,
      characterId,
      selectedAnswerIds,
      formState.comment,
      formState.sourceType,
      onMultipleAnswersUpdate,
    ]
  );

  const handleCommentChange = useCallback((text: string) => {
    setFormState((prev) => ({
      ...prev,
      comment: text,
    }));
  }, []);

  const handleSourceTypeChange = useCallback((sourceType: SourceType) => {
    setFormState((prev) => ({
      ...prev,
      sourceType,
    }));
  }, []);

  // Сохранение ответа
  const handleSave = useCallback(() => {
    if (!question) return;

    console.log("formState = ", formState);
    console.log("question = ", question);

    if (question.answer_type === "multiple") {
      onMultipleAnswersUpdate(
        question.id,
        characterId,
        selectedAnswerIds,
        formState.comment,
        formState.sourceType
      );
      return;
    }

    // single
    if (selectedAnswerId) {
      const data = {
        answer_id: selectedAnswerId,
        comment: formState.comment,
        source_type: formState.sourceType,
      };

      onAnswerUpdate(question.id, data);
    }
  }, [
    question,
    formState,
    selectedAnswerId,
    selectedAnswerIds,
    onAnswerUpdate,
    characterId,
    onMultipleAnswersUpdate,
  ]);

  // Удаление ответа
  const handleDelete = useCallback(() => {
    if (question?.current_response && onAnswerDelete) {
      onAnswerDelete(question.current_response.id);
    }
  }, [question?.current_response, onAnswerDelete]);

  // Рендер вариантов ответов
  const renderAnswerOptions = useCallback(() => {
    if (!question?.answers) return null;

    // Сортируем ответы по order_index и фильтруем кастомные варианты
    const sortedAnswers = [...question.answers]
      .filter((answer) => answer.external_id !== "custom")
      .sort((a, b) => a.order_index - b.order_index);

    if (question.answer_type === "single") {
      return (
        <div className="question-options">
          {sortedAnswers.map((answer: ChecklistAnswer) => (
            <Radio
              key={answer.id}
              value={answer.id.toString()}
              size="l"
              checked={selectedAnswerId === answer.id}
              onChange={() => handleSingleChoiceChange(answer.id)}
              content={getAnswerDisplayValue(answer)}
            />
          ))}
        </div>
      );
    } else if (question.answer_type === "multiple") {
      return (
        <div className="question-options">
          {sortedAnswers.map((answer: ChecklistAnswer) => (
            <Checkbox
              key={answer.id}
              size="l"
              checked={selectedAnswerIds.includes(answer.id)}
              onChange={(event) =>
                handleMultipleChoiceChange(answer.id, event.target.checked)
              }
              content={getAnswerDisplayValue(answer)}
            />
          ))}
        </div>
      );
    }

    return null;
  }, [
    question?.answers,
    question?.answer_type,
    selectedAnswerId,
    selectedAnswerIds,
    handleSingleChoiceChange,
    handleMultipleChoiceChange,
    getAnswerDisplayValue,
  ]);

  if (!question) {
    return (
      <div className="question-card question-card--empty">
        <div className="question-card__content">
          <p>Вопрос не найден</p>
        </div>
      </div>
    );
  }

  return (
    <div className="question-card">
      {/* Question context */}
      <div className="question-card__context">
        <div className="question-card__breadcrumbs">
          <Breadcrumbs>
            <Breadcrumbs.Item>{question.sectionTitle}</Breadcrumbs.Item>
            <Breadcrumbs.Item>{question.subsectionTitle}</Breadcrumbs.Item>
            {!questionGroup.external_id.includes("service-group-") && (
              <Breadcrumbs.Item>{questionGroup.title}</Breadcrumbs.Item>
            )}
          </Breadcrumbs>
        </div>
      </div>

      <div className="question-card__main">
        <Text variant="header-1">{question.text}</Text>

        <div className="question-input">{renderAnswerOptions()}</div>

        {/* Отображение hint для выбранных ответов */}
        {(() => {
          let selectedAnswers: ChecklistAnswer[] = [];
          
          if (question.answer_type === "single" && selectedAnswerId) {
            const answer = question.answers.find(a => a.id === selectedAnswerId);
            if (answer) selectedAnswers = [answer];
          } else if (question.answer_type === "multiple" && selectedAnswerIds.length > 0) {
            selectedAnswers = question.answers.filter(a => selectedAnswerIds.includes(a.id));
          }

          if (selectedAnswers.length === 0) return null;

          return (
            <>
              {(selectedAnswers.some(answer => answer.hint) || selectedAnswers.some(answer => answer.exercise)) && (
                <div className="question-hint">
                  <div className="hint-with-exercise">
                    {selectedAnswers.map(answer => (
                      answer.hint && (
                        <span key={`hint-${answer.id}`} className="question-hint-content">
                          {answer.hint}
                        </span>
                      )
                    ))}
                    
                    {selectedAnswers.some(answer => answer.exercise) && (
                      <span 
                        className={`exercise-toggle ${exerciseExpanded ? 'expanded' : ''}`}
                        onClick={toggleExercise}
                      >
                        {selectedAnswers.some(answer => answer.hint) && ' '}
                        См. упражнения<ArrowToggle direction={exerciseExpanded ? "bottom" : "right"} />
                      </span>
                    )}
                  </div>
                  
                  {exerciseExpanded && selectedAnswers.some(answer => answer.exercise) && (
                    <div className="expandable-content">
                      {selectedAnswers.map(answer => (
                        answer.exercise && (
                          <div key={`exercise-${answer.id}`} className="question-exercise-content">
                            {answer.exercise}
                          </div>
                        )
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          );
        })()}

        {question.current_response && onAnswerDelete && (
          <div className="question-card__delete">
            <Label
              theme="success"
              type="close"
              onCloseClick={handleDelete}
              size="m"
              title="Очистить ответ"
            >
              {`Сохранено ${new Date(
                question.current_response.updated_at
              ).toLocaleString("ru")}`}
            </Label>
          </div>
        )}
      </div>

      <div className="question-card__additional">
        <div className="source-selection">
          <div className="field-label">Источник ответа:</div>
          <SegmentedRadioGroup
            value={formState.sourceType}
            onUpdate={handleSourceTypeChange}
            size="m"
            options={[
              {
                value: "FOUND_IN_TEXT",
                content: "Текст",
                title: "Найдено точное указание в первоисточнике",
              },
              {
                value: "LOGICALLY_DERIVED",
                content: "Предположение",
                title:
                  "Логически выведено на основе фактов и обстоятельств в первоисточнике",
              },
              {
                value: "IMAGINED",
                content: "Фантазия",
                title: "Придумано безосновательно",
              },
            ]}
          />
        </div>

        <div className="comment-field">
          <div className="field-label">Дополнить ответ:</div>
          <TextArea
            value={formState.comment}
            onUpdate={handleCommentChange}
            onBlur={handleSave}
            disabled={
              (question.answer_type === "single" && !selectedAnswerId) ||
              (question.answer_type === "multiple" &&
                selectedAnswerIds.length === 0)
            }
            placeholder="Цитаты, обоснование, свои мысли..."
          />
        </div>
      </div>

      <div className="question-flow__footer">
        <QuestionNavigation
          currentIndex={currentQuestionIndex}
          totalQuestions={allQuestions.length}
          onPrevious={onPrevious}
          onNext={onNext}
          canGoBack={canGoBack}
          canGoForward={canGoForward}
        />
      </div>
    </div>
  );
};
