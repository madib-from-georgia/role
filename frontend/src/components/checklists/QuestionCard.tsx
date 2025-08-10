import React, { useState } from "react";
import {
  Alert,
  Text,
  Button,
  Radio,
  Checkbox,
  TextInput,
  TextArea,
  SegmentedRadioGroup,
  Breadcrumbs,
  Tooltip,
  Icon,
} from "@gravity-ui/uikit";
import { NavigationSidebar } from "./NavigationSidebar";

interface QuestionCardProps {
  question: any;
  onAnswerUpdate: (questionId: number, data: any) => void;
  onAnswerDelete?: (responseId: number) => void;
  isLoading: boolean;
  // New props for NavigationSidebar
  allQuestions: any[];
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
  onAnswerUpdate,
  onAnswerDelete,
  isLoading,
  allQuestions,
  currentQuestionIndex,
  onQuestionSelect,
  completionPercentage,
}) => {
  const [localAnswer, setLocalAnswer] = useState(
    question?.current_response?.answer || ""
  );
  const [localComment, setLocalComment] = useState(
    question?.current_response?.comment || ""
  );
  const [sourceType, setSourceType] = useState(
    question?.current_response?.source_type || "FOUND_IN_TEXT"
  );
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [customOptionText, setCustomOptionText] = useState("");
  const lastAnswerRef = React.useRef<string | null>(null);
  const customOptionTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);
  const optionChangeTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);
  const commentTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);

  // Determine question type from either 'type' or 'option_type' field
  const getQuestionType = () => {
    return (
      question.type ||
      (question.option_type === "single"
        ? "SINGLE_CHOICE"
        : question.option_type === "multiple"
        ? "MULTIPLE_CHOICE"
        : "OPEN_TEXT")
    );
  };

  // Update all form states when question changes
  React.useEffect(() => {
    setLocalAnswer(question?.current_response?.answer || "");
    setLocalComment(question?.current_response?.comment || "");
    setSourceType(question?.current_response?.source_type || "FOUND_IN_TEXT");
    setCustomOptionText("");
    lastAnswerRef.current = null; // Reset to trigger answer initialization
  }, [question?.id]);

  // Initialize selected options from existing answer
  React.useEffect(() => {
    const currentAnswer = question?.current_response?.answer || "";

    // Only update if the answer has actually changed from external source
    if (currentAnswer !== lastAnswerRef.current) {
      lastAnswerRef.current = currentAnswer;

      if (currentAnswer) {
        const questionType = getQuestionType();

        if (
          questionType === "SINGLE_CHOICE" ||
          questionType === "MULTIPLE_CHOICE"
        ) {
          // Check if the answer is a custom option (not starting with any predefined option)
          const predefinedOptions = question.options || [];
          const isCustomAnswer =
            currentAnswer &&
            !predefinedOptions.some((opt: string) =>
              currentAnswer.includes(opt)
            );

          if (isCustomAnswer) {
            // This is a custom answer, set it as custom text and select "свой вариант"
            setCustomOptionText(currentAnswer);
            setSelectedOptions(["свой вариант"]);
          } else {
            // This is a regular option selection
            const options = currentAnswer
              .split(", ")
              .filter((opt: string) => opt.trim());
            setSelectedOptions(options);
          }
        }
      } else {
        // Clear selection if no answer exists
        setSelectedOptions([]);
      }
    }
  }, [question?.current_response?.answer]);

  // Cleanup timeouts on unmount
  React.useEffect(() => {
    return () => {
      if (customOptionTimeoutRef.current) {
        clearTimeout(customOptionTimeoutRef.current);
      }
      if (optionChangeTimeoutRef.current) {
        clearTimeout(optionChangeTimeoutRef.current);
      }
      if (commentTimeoutRef.current) {
        clearTimeout(commentTimeoutRef.current);
      }
    };
  }, []);

  // Debounced auto-save for text fields
  const handleCommentChange = (text: string) => {
    setLocalComment(text);

    // Clear previous timeout
    if (commentTimeoutRef.current) {
      clearTimeout(commentTimeoutRef.current);
    }

    commentTimeoutRef.current = setTimeout(() => {
      if (text.trim() || localAnswer.trim()) {
        handleSave();
      }
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

    const questionType = getQuestionType();

    // Handle different question types
    if (
      questionType === "SINGLE_CHOICE" ||
      questionType === "MULTIPLE_CHOICE"
    ) {
      // If "свой вариант" is selected, send the custom text instead
      if (selectedOptions.includes("свой вариант")) {
        data.answer = customOptionText;
      } else {
        data.answer = selectedOptions.join(", ");
      }
    } else {
      data.answer = localAnswer;
    }

    onAnswerUpdate(question.id, data);
  };

  const handleOptionChange = (
    option: string,
    checked: boolean | React.ChangeEvent<HTMLInputElement>
  ) => {
    // Handle both boolean (from gravity-ui components) and ChangeEvent (from native inputs)
    const isChecked =
      typeof checked === "boolean" ? checked : checked.target.checked;
    const questionType = getQuestionType();
    let newOptions: string[] = [];

    if (questionType === "SINGLE_CHOICE") {
      newOptions = isChecked ? [option] : [];
      setSelectedOptions(newOptions);
    } else if (questionType === "MULTIPLE_CHOICE") {
      newOptions = isChecked
        ? [...selectedOptions, option]
        : selectedOptions.filter((o) => o !== option);
      setSelectedOptions(newOptions);
    }

    // Clear previous timeout
    if (optionChangeTimeoutRef.current) {
      clearTimeout(optionChangeTimeoutRef.current);
    }

    // Debounced auto-save for options with the new selection
    optionChangeTimeoutRef.current = setTimeout(() => {
      const data: any = {
        comment: localComment,
        source_type: sourceType,
      };

      // If "свой вариант" is selected, send the custom text instead
      if (newOptions.includes("свой вариант")) {
        data.answer = customOptionText;
      } else {
        data.answer = newOptions.join(", ");
      }

      if (newOptions.length > 0 || question?.current_response?.answer) {
        onAnswerUpdate(question.id, data);
      }
    }, 500); // Increased delay to 500ms
  };

  const handleCustomOptionChange = (text: string) => {
    setCustomOptionText(text);

    // Clear previous timeout
    if (customOptionTimeoutRef.current) {
      clearTimeout(customOptionTimeoutRef.current);
    }

    // Debounced auto-save with the custom text as the answer
    customOptionTimeoutRef.current = setTimeout(() => {
      const data: any = {
        comment: localComment,
        source_type: sourceType,
        answer: text.trim(),
      };

      if (text.trim() || question?.current_response?.answer) {
        onAnswerUpdate(question.id, data);
      }
    }, 1000); // Increased delay to 1 second
  };

  const renderQuestionInput = () => {
    const questionType = getQuestionType();

    // Render custom option input if "свой вариант" is selected
    const renderCustomOptionInput = () => {
      if (selectedOptions.includes("свой вариант")) {
        return (
          <TextInput
            value={customOptionText}
            onUpdate={(value) => handleCustomOptionChange(value)}
            placeholder="Введите свой вариант..."
            className="custom-option-text-input"
          />
        );
      }
      return null;
    };

    switch (questionType) {
      case "SINGLE_CHOICE":
        return (
          <>
            <div className="question-options">
              {question.options?.map((option: string, index: number) => (
                <Radio
                  key={index}
                  value={option}
                  size="l"
                  checked={selectedOptions.includes(option)}
                  onChange={() =>
                    handleOptionChange(
                      option,
                      !selectedOptions.includes(option)
                    )
                  }
                  content={option}
                />
              ))}
            </div>
            {renderCustomOptionInput()}
          </>
        );

      case "MULTIPLE_CHOICE":
        return (
          <>
            <div className="question-options">
              {question.options?.map((option: string, index: number) => (
                <Checkbox
                  key={index}
                  size="l"
                  checked={selectedOptions.includes(option)}
                  onChange={(checked) => handleOptionChange(option, checked)}
                  content={option}
                />
              ))}
            </div>
            {renderCustomOptionInput()}
          </>
        );

      case "OPEN_TEXT":
      default:
        return (
          <div className="question-text-input">
            <TextArea
              value={localAnswer}
              onUpdate={(value) => setLocalAnswer(value)}
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
          {question.hint ? (
            <Tooltip content={question.hint} openDelay={0}>
              <Icon data={CheckIcon} size={16} className="question-text-icon" />
            </Tooltip>
          ) : null}
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
        <div className="action-buttons">
          <Button
            onClick={handleSave}
            disabled={isLoading}
            view="action"
            size="xl"
          >
            {isLoading ? "Сохранение..." : "Сохранить"}
          </Button>

          {question.current_response && onAnswerDelete && (
            <div className="question-card__delete">
              <Button
                onClick={() => onAnswerDelete(question.current_response.id)}
                title="Удалить ответ"
                view="normal"
                size="l"
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
        {question.current_response && (
          <Alert
            theme="success"
            // title="Сохранено"
            message={`Сохранено ${new Date(
              question.current_response.updated_at
            ).toLocaleString("ru")}`}
          />
        )}
      </div>
    </div>
  );
};
