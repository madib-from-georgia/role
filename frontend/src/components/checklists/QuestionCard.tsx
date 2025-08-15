import React, { useState, useEffect, useCallback } from "react";
import {
  Label,
  Text,
  Button,
  Radio,
  Checkbox,
  TextInput,
  TextArea,
  SegmentedRadioGroup,
  Breadcrumbs,
} from "@gravity-ui/uikit";
import { NavigationSidebar } from "./NavigationSidebar";
import {
  ChecklistQuestion,
  ChecklistAnswer,
  Gender,
  SourceType,
} from "../../types/checklist";

interface QuestionCardProps {
  question: ChecklistQuestion;
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
  onMultipleAnswersUpdate?: (
    questionId: number,
    characterId: number,
    selectedAnswerIds: number[],
    comment?: string,
    sourceType?: SourceType,
    customText?: string
  ) => void;
  onAnswerDelete?: (responseId: number) => void;
  isLoading: boolean;
  allQuestions: ChecklistQuestion[];
  currentQuestionIndex: number;
  onQuestionSelect: (index: number) => void;
  completionPercentage: number;
}

// CheckIcon компонент (оставляем как есть)
export function CheckIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      width="16"
      height="16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M15.5 8C15.5 12.1421 12.1421 15.5 8 15.5C3.85786 15.5 0.5 12.1421 0.5 8C0.5 3.85786 3.85786 0.5 8 0.5C12.1421 0.5 15.5 3.85786 15.5 8Z"
        stroke="currentColor"
        strokeOpacity="0.5"
      />
      <path
        opacity="0.7"
        fillRule="evenodd"
        clipRule="evenodd"
        d="M8.46436 9.92432H7.09473C7.09115 9.72738 7.08936 9.60742 7.08936 9.56445C7.08936 9.12044 7.16276 8.75521 7.30957 8.46875C7.45638 8.18229 7.75 7.86003 8.19043 7.50195C8.63086 7.14388 8.89404 6.90934 8.97998 6.79834C9.11247 6.62288 9.17871 6.42953 9.17871 6.21826C9.17871 5.92464 9.06144 5.6731 8.8269 5.46362C8.59237 5.25415 8.27637 5.14941 7.87891 5.14941C7.49577 5.14941 7.17529 5.25863 6.91748 5.47705C6.65967 5.69548 6.48242 6.02848 6.38574 6.47607L5 6.3042C5.03939 5.66325 5.31242 5.11898 5.81909 4.67139C6.32577 4.22379 6.99088 4 7.81445 4C8.68099 4 9.37028 4.22648 9.88232 4.67944C10.3944 5.13241 10.6504 5.65966 10.6504 6.26123C10.6504 6.59424 10.5564 6.90934 10.3684 7.20654C10.1804 7.50375 9.77849 7.90836 9.1626 8.42041C8.84391 8.68539 8.64608 8.89844 8.56909 9.05957C8.49211 9.2207 8.45719 9.50895 8.46436 9.92432ZM7.09473 11.9546V10.4453H8.604V11.9546H7.09473Z"
        fill="red"
      />
    </svg>
  );
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  characterGender,
  characterId,
  onAnswerUpdate,
  onMultipleAnswersUpdate,
  onAnswerDelete,
  isLoading,
  allQuestions,
  currentQuestionIndex,
  onQuestionSelect,
  completionPercentage,
}) => {
  // Состояние формы
  const [formState, setFormState] = useState({
    selectedAnswerId: null as number | null,
    selectedAnswerIds: [] as number[],
    customText: "",
    comment: "",
    sourceType: "FOUND_IN_TEXT" as SourceType,
  });

  // Состояние UI
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Инициализация состояния при смене вопроса
  useEffect(() => {
    if (!question) return;

    const response = question.current_response;
    const responses = question.current_responses || [];

    // Для множественного выбора ищем ответ с текстом среди всех ответов
    let customText = "";
    if (question.answer_type === "multiple") {
      // Ищем ответ с answer_text среди всех ответов
      const responseWithText = responses.find(r => r.answer_text);
      customText = responseWithText?.answer_text || "";
    } else if (response || responses.length > 0) {
      // Для single и text берем из основного ответа
      const primaryResponse = response || responses[0];
      customText = primaryResponse?.answer_text || "";
    }

    if (response || responses.length > 0) {
      // Инициализация на основе существующих ответов
      const primaryResponse = response || responses[0];
      
      setFormState({
        selectedAnswerId: question.answer_type === "single" ? (primaryResponse?.answer_id || null) : null,
        selectedAnswerIds: question.answer_type === "multiple"
          ? responses.map(r => r.answer_id).filter(Boolean) as number[]
          : [],
        customText,
        comment: primaryResponse?.comment || "",
        sourceType: primaryResponse?.source_type || "FOUND_IN_TEXT",
      });
    } else {
      // Полный сброс состояния для нового вопроса без ответов
      setFormState({
        selectedAnswerId: null,
        selectedAnswerIds: [],
        customText: "",
        comment: "",
        sourceType: "FOUND_IN_TEXT",
      });
    }
  }, [question, question.id, question.answer_type]);

  // Отдельный useEffect для обновления данных ответов без сброса состояния
  useEffect(() => {
    if (!question) return;

    const response = question.current_response;
    const responses = question.current_responses || [];

    if (response || responses.length > 0) {
      const primaryResponse = response || responses[0];
      
      setFormState(prev => {
        // Для множественного выбора ищем ответ с текстом среди всех ответов
        let customText = prev.customText;
        if (!customText) {
          if (question.answer_type === "multiple") {
            // Ищем ответ с answer_text среди всех ответов
            const responseWithText = responses.find(r => r.answer_text);
            customText = responseWithText?.answer_text || "";
          } else {
            // Для single и text берем из основного ответа
            customText = primaryResponse?.answer_text || "";
          }
        }

        return {
          ...prev,
          // Обновляем только комментарий и источник, не трогая выбранные ответы
          comment: primaryResponse?.comment || prev.comment,
          sourceType: primaryResponse?.source_type || prev.sourceType,
          // Обновляем customText только если он пустой в текущем состоянии
          customText,
        };
      });
    }
  }, [question, question.current_response, question.current_responses]);

  // Получение отображаемого значения ответа в зависимости от пола
  const getAnswerDisplayValue = useCallback((answer: ChecklistAnswer): string => {
    return characterGender === "male" ? answer.value_male : answer.value_female;
  }, [characterGender]);

  // Поиск варианта "свой ответ"
  const customAnswer = question?.answers?.find(answer => answer.external_id === "custom");

  // Проверка, выбран ли вариант "свой ответ"
  const isCustomAnswerSelected = useCallback(() => {
    if (!customAnswer) return false;
    
    if (question.answer_type === "single") {
      return formState.selectedAnswerId === customAnswer.id;
    } else if (question.answer_type === "multiple") {
      return formState.selectedAnswerIds.includes(customAnswer.id);
    }
    return false;
  }, [customAnswer, formState.selectedAnswerId, formState.selectedAnswerIds, question?.answer_type]);

  // Обработчики изменений
  const handleSingleChoiceChange = useCallback((answerId: number) => {
    const selectedAnswer = question.answers?.find(answer => answer.id === answerId);
    const isCustom = selectedAnswer?.external_id === "custom";

    setFormState(prev => ({
      ...prev,
      selectedAnswerId: answerId,
      customText: isCustom ? prev.customText : "", // Очищаем текст только если не "свой вариант"
    }));
  }, [question.answers]);

  const handleMultipleChoiceChange = useCallback((answerId: number, checked: boolean) => {
    setFormState(prev => {
      const newSelectedIds = checked 
        ? [...prev.selectedAnswerIds, answerId]
        : prev.selectedAnswerIds.filter(id => id !== answerId);

      // Очищаем кастомный текст только если не выбран "свой вариант"
      const hasCustomAnswer = customAnswer && newSelectedIds.includes(customAnswer.id);
      
      return {
        ...prev,
        selectedAnswerIds: newSelectedIds,
        customText: hasCustomAnswer ? prev.customText : "",
      };
    });
  }, [customAnswer]);

  const handleCustomTextChange = useCallback((text: string) => {
    setFormState(prev => ({
      ...prev,
      customText: text,
    }));

    // Автоматически выбираем "свой вариант" при вводе текста
    if (text.trim() && customAnswer) {
      if (question.answer_type === "single" && formState.selectedAnswerId !== customAnswer.id) {
        setFormState(prev => ({
          ...prev,
          selectedAnswerId: customAnswer.id,
        }));
      } else if (question.answer_type === "multiple" && !formState.selectedAnswerIds.includes(customAnswer.id)) {
        setFormState(prev => ({
          ...prev,
          selectedAnswerIds: [...prev.selectedAnswerIds, customAnswer.id],
        }));
      }
    }
  }, [customAnswer, formState.selectedAnswerId, formState.selectedAnswerIds, question?.answer_type]);

  const handleCommentChange = useCallback((text: string) => {
    setFormState(prev => ({
      ...prev,
      comment: text,
    }));
  }, []);

  const handleSourceTypeChange = useCallback((sourceType: SourceType) => {
    setFormState(prev => ({
      ...prev,
      sourceType,
    }));
  }, []);

  // Сохранение ответа
  const handleSave = useCallback(() => {
    if (!question) return;

    const baseData = {
      comment: formState.comment,
      source_type: formState.sourceType,
    };

    if (question.answer_type === "single") {
      // Одиночный выбор
      if (formState.selectedAnswerId) {
        const selectedAnswer = question.answers?.find(answer => answer.id === formState.selectedAnswerId);
        const isCustom = selectedAnswer?.external_id === "custom";

        const data = {
          ...baseData,
          answer_id: formState.selectedAnswerId,
          ...(isCustom && formState.customText.trim() && { answer_text: formState.customText.trim() }),
        };

        onAnswerUpdate(question.id, data);
      } else if (formState.customText.trim()) {
        // Только текст без выбранного варианта
        onAnswerUpdate(question.id, {
          ...baseData,
          answer_text: formState.customText.trim(),
        });
      }
    } else if (question.answer_type === "multiple") {
      // Множественный выбор - используем специальный API метод
      if (onMultipleAnswersUpdate) {
        onMultipleAnswersUpdate(
          question.id,
          characterId,
          formState.selectedAnswerIds,
          formState.comment,
          formState.sourceType,
          formState.customText.trim() || undefined
        );
      } else {
        // Fallback к старому методу
        if (formState.selectedAnswerIds.length > 0) {
          formState.selectedAnswerIds.forEach(answerId => {
            const selectedAnswer = question.answers?.find(answer => answer.id === answerId);
            const isCustom = selectedAnswer?.external_id === "custom";

            const data = {
              ...baseData,
              answer_id: answerId,
              ...(isCustom && formState.customText.trim() && { answer_text: formState.customText.trim() }),
            };

            onAnswerUpdate(question.id, data);
          });
        } else if (formState.customText.trim()) {
          // Только текст без выбранных вариантов
          onAnswerUpdate(question.id, {
            ...baseData,
            answer_text: formState.customText.trim(),
          });
        }
      }
    } else {
      // Текстовый ответ
      if (formState.customText.trim()) {
        onAnswerUpdate(question.id, {
          ...baseData,
          answer_text: formState.customText.trim(),
        });
      }
    }
  }, [question, formState, onAnswerUpdate, characterId, onMultipleAnswersUpdate]);

  // Удаление ответа
  const handleDelete = useCallback(() => {
    if (question?.current_response && onAnswerDelete) {
      onAnswerDelete(question.current_response.id);
    }
  }, [question?.current_response, onAnswerDelete]);

  // Рендер поля для ввода кастомного ответа
  const renderCustomInput = useCallback(() => {
    const shouldShow = isCustomAnswerSelected() || formState.customText.trim() !== "";
    
    if (!shouldShow) return null;

    return (
      <TextInput
        value={formState.customText}
        onUpdate={handleCustomTextChange}
        placeholder="Введите свой вариант..."
        className="custom-answer-input"
      />
    );
  }, [isCustomAnswerSelected, formState.customText, handleCustomTextChange]);

  // Рендер вариантов ответов
  const renderAnswerOptions = useCallback(() => {
    if (!question?.answers) return null;

    // Сортируем ответы по order_index
    const sortedAnswers = [...question.answers].sort((a, b) => a.order_index - b.order_index);

    if (question.answer_type === "single") {
      return (
        <>
          <div className="question-options">
            {sortedAnswers.map((answer: ChecklistAnswer) => (
              <Radio
                key={answer.id}
                value={answer.id.toString()}
                size="l"
                checked={formState.selectedAnswerId === answer.id}
                onChange={() => handleSingleChoiceChange(answer.id)}
                content={getAnswerDisplayValue(answer)}
              />
            ))}
          </div>
          {renderCustomInput()}
        </>
      );
    } else if (question.answer_type === "multiple") {
      return (
        <>
          <div className="question-options">
            {sortedAnswers.map((answer: ChecklistAnswer) => (
              <Checkbox
                key={answer.id}
                size="l"
                checked={formState.selectedAnswerIds.includes(answer.id)}
                onChange={(event) => handleMultipleChoiceChange(answer.id, event.target.checked)}
                content={getAnswerDisplayValue(answer)}
              />
            ))}
          </div>
          {renderCustomInput()}
        </>
      );
    }

    return null;
  }, [
    question?.answers,
    question?.answer_type,
    formState.selectedAnswerId,
    formState.selectedAnswerIds,
    handleSingleChoiceChange,
    handleMultipleChoiceChange,
    getAnswerDisplayValue,
    renderCustomInput,
  ]);

  // Рендер текстового поля для типа "text"
  const renderTextInput = useCallback(() => {
    if (question?.answer_type !== "text") return null;

    return (
      <div className="question-text-input">
        <TextArea
          value={formState.customText}
          onUpdate={handleCustomTextChange}
          placeholder="Введите ваш ответ..."
          className="answer-textarea"
        />
      </div>
    );
  }, [question?.answer_type, formState.customText, handleCustomTextChange]);

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
      {/* Sidebar */}
      <NavigationSidebar
        isOpen={isSidebarOpen}
        questions={allQuestions}
        currentIndex={currentQuestionIndex}
        onQuestionSelect={onQuestionSelect}
        completionPercentage={completionPercentage}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Question context */}
      <div className="question-card__context">
        <Button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          title="Навигация по вопросам"
          view="outlined"
          size="m"
        >
          ☰
        </Button>

        <div className="question-card__breadcrumbs">
          <Breadcrumbs>
            <Breadcrumbs.Item>{question.sectionTitle}</Breadcrumbs.Item>
            <Breadcrumbs.Item>{question.subsectionTitle}</Breadcrumbs.Item>
            {question.groupTitle && (
              <Breadcrumbs.Item>{question.groupTitle}</Breadcrumbs.Item>
            )}
          </Breadcrumbs>
        </div>
      </div>

      <div className="question-card__main">
        <Text variant="header-1">{question.text}</Text>

        <div className="question-input">
          {renderAnswerOptions()}
          {renderTextInput()}
        </div>
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
                title: "Логически выведено на основе фактов и обстоятельств в первоисточнике",
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
            placeholder="Цитаты, обоснование, свои мысли..."
          />
        </div>
      </div>

      <div className="question-card__actions">
        {question.current_response && (
          <Label theme="success" size="m">
            {`Сохранено ${new Date(question.current_response.updated_at).toLocaleString("ru")}`}
          </Label>
        )}

        <div className="action-buttons">
          <Button 
            onClick={handleSave} 
            view="normal" 
            size="m"
            loading={isLoading}
          >
            Сохранить
          </Button>

          {question.current_response && onAnswerDelete && (
            <div className="question-card__delete">
              <Button
                onClick={handleDelete}
                title="Удалить ответ"
                view="normal"
                size="m"
                loading={isLoading}
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
