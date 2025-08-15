import React, { useState, useEffect, useCallback } from "react";
import {
  Label,
  Text,
  Button,
  Radio,
  Checkbox,
  TextArea,
  SegmentedRadioGroup,
  Breadcrumbs,
} from "@gravity-ui/uikit";
import { NavigationSidebar } from "./NavigationSidebar";
import { QuestionNavigation } from "./QuestionNavigation";
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
  characterGender,
  characterId,
  onAnswerUpdate,
  onMultipleAnswersUpdate,
  onAnswerDelete,
  allQuestions,
  currentQuestionIndex,
  onQuestionSelect,
  completionPercentage,
  onPrevious,
  onNext,
  canGoBack,
  canGoForward,
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
  // Только id и answer_type!
  // Не включаем question, current_response и current_responses чтобы избежать моргания чекбоксов
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [question?.id, question?.answer_type]); 

  // Убираем второй useEffect полностью - он вызывает конфликты

  // Получение отображаемого значения ответа в зависимости от пола
  const getAnswerDisplayValue = useCallback((answer: ChecklistAnswer): string => {
    return characterGender === "male" ? answer.value_male : answer.value_female;
  }, [characterGender]);

  // Обработчики изменений
  const handleSingleChoiceChange = useCallback((answerId: number) => {
    if (question?.answer_type !== "single") {
      return null;
    }

    setFormState(prev => {
      const newState = {
        ...prev,
        selectedAnswerId: answerId,
        customText: "", // Очищаем текст при выборе любого варианта
      };

      // Автосохранение для радиокнопок - вызываем после обновления состояния
      setTimeout(() => {
        const baseData = {
          comment: newState.comment,
          source_type: newState.sourceType,
        };

        if (newState.selectedAnswerId) {
          const data = {
            ...baseData,
            answer_id: newState.selectedAnswerId,
          };

          onAnswerUpdate(question.id, data);
        }
      }, 0);

      return newState;
    });
  }, [question, onAnswerUpdate]);

  const handleMultipleChoiceChange = useCallback((answerId: number, checked: boolean) => {
      if (question?.answer_type !== "multiple") {
        return null;
      }

      setFormState(prev => {
        const newSelectedIds = checked
          ? [...prev.selectedAnswerIds, answerId]
          : prev.selectedAnswerIds.filter(id => id !== answerId);

        const newState = {
          ...prev,
          selectedAnswerIds: newSelectedIds,
          customText: "", // Очищаем кастомный текст при любом изменении
        };

        // Немедленно отправляем обновление на сервер
        onMultipleAnswersUpdate(
          question.id,
          characterId,
          newSelectedIds,
          newState.comment,
          newState.sourceType
        );

        return newState;
      });
  }, [question, characterId, onMultipleAnswersUpdate]);

  const handleCustomTextChange = useCallback((text: string) => {
    setFormState(prev => ({
      ...prev,
      customText: text,
    }));
  }, []);

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
        const data = {
          ...baseData,
          answer_id: formState.selectedAnswerId,
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
      onMultipleAnswersUpdate(
        question.id,
        characterId,
        formState.selectedAnswerIds,
        formState.comment,
        formState.sourceType
      );
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


  // Рендер вариантов ответов
  const renderAnswerOptions = useCallback(() => {
    if (!question?.answers) return null;

    // Сортируем ответы по order_index и фильтруем кастомные варианты
    const sortedAnswers = [...question.answers]
      .filter(answer => answer.external_id !== "custom")
      .sort((a, b) => a.order_index - b.order_index);

    if (question.answer_type === "single") {
      return (
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
      );
    } else if (question.answer_type === "multiple") {
      return (
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
  ]);

  // Рендер текстового поля для типа "text"
  const renderTextInput = useCallback(() => {
    if (question?.answer_type !== "text") return null;

    return (
      <div className="question-text-input">
        <TextArea
          value={formState.customText}
          onUpdate={handleCustomTextChange}
          onBlur={handleSave}
          placeholder="Введите ваш ответ..."
          className="answer-textarea"
        />
      </div>
    );
  }, [question?.answer_type, formState.customText, handleCustomTextChange, handleSave]);

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

        {question.current_response && onAnswerDelete && (
          <div className="question-card__delete">
            <Label theme="success" type="close" onCloseClick={handleDelete} size="m" title="Очистить ответ">
              {`Сохранено ${new Date(question.current_response.updated_at).toLocaleString("ru")}`}
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
            onBlur={handleSave}
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
