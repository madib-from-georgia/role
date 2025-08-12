import React, { useState } from "react";
import {
  Label,
  Text,
  Button,
  Radio,
  Checkbox,
  TextInput,
  TextArea,
  SegmentedRadioGroup,
  Breadcrumbs
} from "@gravity-ui/uikit";
import { NavigationSidebar } from "./NavigationSidebar";
import { ChecklistQuestion, ChecklistAnswer, Gender } from "../../types/checklist";

interface QuestionCardProps {
  question: ChecklistQuestion;
  characterGender: Gender;
  onAnswerUpdate: (questionId: number, data: {
    answer_id?: number;
    answer_text?: string;
    source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    comment?: string;
  }) => void;
  onAnswerDelete?: (responseId: number) => void;
  isLoading: boolean;
  // New props for NavigationSidebar
  allQuestions: ChecklistQuestion[];
  currentQuestionIndex: number;
  onQuestionSelect: (index: number) => void;
  completionPercentage: number;
}

// CheckIcon.jsx
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
        stroke-opacity="0.5"
      />
      <path
        opacity="0.7"
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M8.46436 9.92432H7.09473C7.09115 9.72738 7.08936 9.60742 7.08936 9.56445C7.08936 9.12044 7.16276 8.75521 7.30957 8.46875C7.45638 8.18229 7.75 7.86003 8.19043 7.50195C8.63086 7.14388 8.89404 6.90934 8.97998 6.79834C9.11247 6.62288 9.17871 6.42953 9.17871 6.21826C9.17871 5.92464 9.06144 5.6731 8.8269 5.46362C8.59237 5.25415 8.27637 5.14941 7.87891 5.14941C7.49577 5.14941 7.17529 5.25863 6.91748 5.47705C6.65967 5.69548 6.48242 6.02848 6.38574 6.47607L5 6.3042C5.03939 5.66325 5.31242 5.11898 5.81909 4.67139C6.32577 4.22379 6.99088 4 7.81445 4C8.68099 4 9.37028 4.22648 9.88232 4.67944C10.3944 5.13241 10.6504 5.65966 10.6504 6.26123C10.6504 6.59424 10.5564 6.90934 10.3684 7.20654C10.1804 7.50375 9.77849 7.90836 9.1626 8.42041C8.84391 8.68539 8.64608 8.89844 8.56909 9.05957C8.49211 9.2207 8.45719 9.50895 8.46436 9.92432ZM7.09473 11.9546V10.4453H8.604V11.9546H7.09473Z"
        fill="red"
      />
    </svg>
  );
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  characterGender,
  onAnswerUpdate,
  onAnswerDelete,
  allQuestions,
  currentQuestionIndex,
  onQuestionSelect,
  completionPercentage,
}) => {
  // Состояние для текущего ответа
  const [selectedAnswerId, setSelectedAnswerId] = useState<number | null>(
    question?.current_response?.answer_id || null
  );
  const [selectedAnswerIds, setSelectedAnswerIds] = useState<number[]>([]);
  const [customAnswerText, setCustomAnswerText] = useState(
    question?.current_response?.answer_text || ""
  );
  const [localComment, setLocalComment] = useState(
    question?.current_response?.comment || ""
  );
  const [sourceType, setSourceType] = useState(
    question?.current_response?.source_type || "FOUND_IN_TEXT"
  );
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Refs для debouncing
  const customTextTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);
  const answerChangeTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);
  const commentTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);
  
  // Ref для отслеживания инициализации
  const isInitializedRef = React.useRef<boolean>(false);
  const currentQuestionIdRef = React.useRef<number | null>(null);

  // Получить отображаемое значение ответа в зависимости от пола персонажа
  const getAnswerDisplayValue = (answer: ChecklistAnswer): string => {
    return characterGender === 'male' ? answer.value_male : answer.value_female;
  };

  // Update all form states when question changes
  React.useEffect(() => {
    const response = question?.current_response;

    if (response) {
      // Инициализация на основе существующего ответа
      if (response.answer_id) {
        if (question.answer_type === 'single') {
          setSelectedAnswerId(response.answer_id);
        } else if (question.answer_type === 'multiple') {
          // Для множественного выбора нужно парсить answer_text или использовать отдельное поле
          // Пока используем простую логику - один ID
          setSelectedAnswerIds([response.answer_id]);
        }
      }

      // Обновляем customAnswerText только если нет активного таймера (пользователь не печатает)
      if (!customTextTimeoutRef.current) {
        if (response.answer_text) {
          setCustomAnswerText(response.answer_text);
        } else {
          setCustomAnswerText("");
        }
      }

      setLocalComment(response.comment || "");
      setSourceType(response.source_type || "FOUND_IN_TEXT");
    } else {
      // Сброс состояния для нового вопроса
      setSelectedAnswerId(null);
      setSelectedAnswerIds([]);
      setCustomAnswerText("");
      setLocalComment("");
      setSourceType("FOUND_IN_TEXT");
    }
  }, [question?.id, question?.current_response]);

  // Cleanup timeouts on unmount
  React.useEffect(() => {
    return () => {
      if (customTextTimeoutRef.current) {
        clearTimeout(customTextTimeoutRef.current);
      }
      if (answerChangeTimeoutRef.current) {
        clearTimeout(answerChangeTimeoutRef.current);
      }
      if (commentTimeoutRef.current) {
        clearTimeout(commentTimeoutRef.current);
      }
    };
  }, []);

  // Debounced auto-save for comment field
  const handleCommentChange = (text: string) => {
    setLocalComment(text);

    // Clear previous timeout
    if (commentTimeoutRef.current) {
      clearTimeout(commentTimeoutRef.current);
    }

    commentTimeoutRef.current = setTimeout(() => {
      handleSave();
      // Очищаем таймер после сохранения
      commentTimeoutRef.current = null;
    }, 1000);
  };

  // Debounced auto-save for custom text
  const handleCustomTextChange = (text: string) => {
    setCustomAnswerText(text);

    // Clear previous timeout
    if (customTextTimeoutRef.current) {
      clearTimeout(customTextTimeoutRef.current);
    }

    customTextTimeoutRef.current = setTimeout(() => {
      handleSave();
      // Очищаем таймер после сохранения
      customTextTimeoutRef.current = null;
    }, 1000);
  };

  if (!question) {
    return (
      <div className="question-card question-card--empty">
        <div className="question-card__content">
          <p>Вопрос не найден</p>
        </div>
      </div>
    );
  }

  const handleSave = () => {
    const data: any = {
      comment: localComment,
      source_type: sourceType,
    };

    // Определяем тип данных для отправки в зависимости от типа вопроса
    if (question.answer_type === 'single') {
      if (selectedAnswerId) {
        const selectedAnswer = question.answers?.find(answer => answer.id === selectedAnswerId);
        const isCustomAnswer = selectedAnswer?.external_id === "custom";
        
        if (isCustomAnswer && customAnswerText.trim()) {
          // Для варианта "свой ответ" отправляем и ID варианта, и текст
          data.answer_id = selectedAnswerId;
          data.answer_text = customAnswerText.trim();
        } else if (!isCustomAnswer) {
          // Для обычных ответов отправляем только ID
          data.answer_id = selectedAnswerId;
        }
      } else if (customAnswerText.trim()) {
        data.answer_text = customAnswerText.trim();
      }
    } else if (question.answer_type === 'multiple') {
      if (selectedAnswerIds.length > 0) {
        // Для множественного выбора пока используем первый выбранный ответ
        // В будущем можно расширить API для поддержки множественных answer_id
        data.answer_id = selectedAnswerIds[0];
      } else if (customAnswerText.trim()) {
        data.answer_text = customAnswerText.trim();
      }
    } else {
      // text
      if (customAnswerText.trim()) {
        data.answer_text = customAnswerText.trim();
      }
    }

    // Отправляем данные только если есть что сохранять
    if (data.answer_id || data.answer_text || data.comment?.trim()) {
      onAnswerUpdate(question.id, data);
    }
  };

  const handleSingleChoiceChange = (answerId: number) => {
    setSelectedAnswerId(answerId);
    
    // Проверяем, выбран ли вариант "свой ответ"
    const selectedAnswer = question.answers?.find(answer => answer.id === answerId);
    const isCustomAnswer = selectedAnswer?.external_id === "custom";
    
    if (!isCustomAnswer) {
      setCustomAnswerText(""); // Очищаем кастомный текст при выборе предопределенного ответа
    }

    // Clear previous timeout
    if (answerChangeTimeoutRef.current) {
      clearTimeout(answerChangeTimeoutRef.current);
    }

    // Debounced auto-save (только для не-кастомных ответов)
    if (!isCustomAnswer) {
      answerChangeTimeoutRef.current = setTimeout(() => {
        const data = {
          answer_id: answerId,
          comment: localComment,
          source_type: sourceType,
        };
        onAnswerUpdate(question.id, data);
      }, 500);
    }
  };

  const handleMultipleChoiceChange = (answerId: number, checked: boolean) => {
    let newSelectedIds: number[];

    if (checked) {
      newSelectedIds = [...selectedAnswerIds, answerId];
    } else {
      newSelectedIds = selectedAnswerIds.filter(id => id !== answerId);
    }

    setSelectedAnswerIds(newSelectedIds);
    setCustomAnswerText(""); // Очищаем кастомный текст при выборе предопределенных ответов

    // Clear previous timeout
    if (answerChangeTimeoutRef.current) {
      clearTimeout(answerChangeTimeoutRef.current);
    }

    // Debounced auto-save
    answerChangeTimeoutRef.current = setTimeout(() => {
      if (newSelectedIds.length > 0) {
        // Пока используем первый выбранный ответ
        const data = {
          answer_id: newSelectedIds[0],
          comment: localComment,
          source_type: sourceType,
        };
        onAnswerUpdate(question.id, data);
      }
    }, 500);
  };

  const renderQuestionInput = () => {
    const questionType = question.answer_type;

    // Render custom option input if "свой вариант" is selected
    const renderCustomOptionInput = () => {
      // Проверяем, выбран ли вариант "свой ответ" (external_id === "custom")
      const isCustomAnswerSelected = question.answers?.find(answer =>
        answer.external_id === "custom" && selectedAnswerId === answer.id
      );
      
      if (isCustomAnswerSelected || customAnswerText.trim() !== "") {
        return (
          <TextInput
            value={customAnswerText}
            onUpdate={handleCustomTextChange}
            onFocus={() => {
              // При фокусе на поле ввода выбираем вариант "свой ответ"
              const customAnswer = question.answers?.find(answer => answer.external_id === "custom");
              if (customAnswer) {
                setSelectedAnswerId(customAnswer.id);
              }
            }}
            placeholder="Введите свой вариант..."
            className="custom-answer-input"
          />
        );
      }
      return null;
    };

    switch (questionType) {
      case "single":
        return (
          <>
            <div className="question-options">
              {question.answers?.map((answer: ChecklistAnswer) => (
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
            {renderCustomOptionInput()}
          </>
        );

      case "multiple":
        return (
          <>
            <div className="question-options">
              {question.answers?.map((answer: ChecklistAnswer) => (
                <Checkbox
                  key={answer.id}
                  size="l"
                  checked={selectedAnswerIds.includes(answer.id)}
                  onChange={(event) => handleMultipleChoiceChange(answer.id, event.target.checked)}
                  content={getAnswerDisplayValue(answer)}
                />
              ))}
            </div>
            {renderCustomOptionInput()}
          </>
        );

      case "text":
      default:
        return (
          <div className="question-text-input">
            <TextArea
              value={customAnswerText}
              onUpdate={handleCustomTextChange}
              onBlur={handleSave}
              placeholder="Введите ваш ответ..."
              className="answer-textarea"
            />
          </div>
        );
    }
  };

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
        <Text variant="header-1">
          {question.text}
        </Text>

        <div className="question-input">{renderQuestionInput()}</div>
      </div>

      <div className="question-card__additional">
        <div className="source-selection">
          <div className="field-label">Источник ответа:</div>
          <SegmentedRadioGroup
            value={sourceType}
            onUpdate={(value) => setSourceType(value)}
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
            value={localComment}
            onUpdate={(value) => handleCommentChange(value)}
            onBlur={handleSave}
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
          >
            Сохранить
          </Button>

          {question.current_response && onAnswerDelete && (
            <div className="question-card__delete">
              <Button
                onClick={() => onAnswerDelete(question.current_response!.id)}
                title="Удалить ответ"
                view="normal"
                size="m"
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
