import React, { useState } from 'react';

interface QuestionCardProps {
  question: any;
  onAnswerUpdate: (questionId: number, data: any) => void;
  onAnswerDelete?: (responseId: number) => void;
  isLoading: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  onAnswerUpdate,
  onAnswerDelete,
  isLoading
}) => {
  const [localAnswer, setLocalAnswer] = useState(question?.current_response?.answer || '');
  const [localComment, setLocalComment] = useState(question?.current_response?.comment || '');
  const [sourceType, setSourceType] = useState(question?.current_response?.source_type || 'LOGICALLY_DERIVED');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const lastAnswerRef = React.useRef<string | null>(null);

  // Determine question type from either 'type' or 'option_type' field
  const getQuestionType = () => {
    return question.type || (question.option_type === 'single' ? 'SINGLE_CHOICE' : 
                            question.option_type === 'multiple' ? 'MULTIPLE_CHOICE' : 'OPEN_TEXT');
  };

  // Initialize selected options from existing answer
  React.useEffect(() => {
    const currentAnswer = question?.current_response?.answer || '';
    
    // Only update if the answer has actually changed from external source
    if (currentAnswer !== lastAnswerRef.current) {
      lastAnswerRef.current = currentAnswer;
      
      if (currentAnswer) {
        const questionType = getQuestionType();
        
        if (questionType === 'SINGLE_CHOICE' || questionType === 'MULTIPLE_CHOICE') {
          const options = currentAnswer.split(', ').filter((opt: string) => opt.trim());
          setSelectedOptions(options);
        }
      } else {
        // Clear selection if no answer exists
        setSelectedOptions([]);
      }
    }
  }, [question?.current_response?.answer]);

  // Auto-save on blur for text fields
  const handleAutoSave = () => {
    if (localAnswer.trim() || localComment.trim()) {
      handleSave();
    }
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
      source_type: sourceType
    };

    const questionType = getQuestionType();

    // Handle different question types
    if (questionType === 'SINGLE_CHOICE' || questionType === 'MULTIPLE_CHOICE') {
      data.answer = selectedOptions.join(', ');
    } else {
      data.answer = localAnswer;
    }

    onAnswerUpdate(question.id, data);
  };

  const handleOptionChange = (option: string, checked: boolean) => {
    const questionType = getQuestionType();
    let newOptions: string[] = [];
    
    if (questionType === 'SINGLE_CHOICE') {
      newOptions = checked ? [option] : [];
      setSelectedOptions(newOptions);
    } else if (questionType === 'MULTIPLE_CHOICE') {
      newOptions = checked 
        ? [...selectedOptions, option]
        : selectedOptions.filter(o => o !== option);
      setSelectedOptions(newOptions);
    }
    
    // Auto-save for options with the new selection
    setTimeout(() => {
      const data: any = {
        comment: localComment,
        source_type: sourceType,
        answer: newOptions.join(', ')
      };
      
      if (newOptions.length > 0 || question?.current_response?.answer) {
        onAnswerUpdate(question.id, data);
      }
    }, 100);
  };

  const renderQuestionInput = () => {
    const questionType = getQuestionType();
    
    switch (questionType) {
      case 'SINGLE_CHOICE':
        return (
          <div className="question-options">
            {question.options?.map((option: string, index: number) => (
              <label key={index} className="option-item">
                <input
                  type="radio"
                  name={`question-${question.id}`}
                  value={option}
                  checked={selectedOptions.includes(option)}
                  onChange={(e) => handleOptionChange(option, e.target.checked)}
                />
                <span className="option-text">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'MULTIPLE_CHOICE':
        return (
          <div className="question-options">
            {question.options?.map((option: string, index: number) => (
              <label key={index} className="option-item">
                <input
                  type="checkbox"
                  value={option}
                  checked={selectedOptions.includes(option)}
                  onChange={(e) => handleOptionChange(option, e.target.checked)}
                />
                <span className="option-text">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'OPEN_TEXT':
      default:
        return (
          <div className="question-text-input">
            <textarea
              value={localAnswer}
              onChange={(e) => setLocalAnswer(e.target.value)}
              onBlur={handleAutoSave}
              placeholder="Введите ваш ответ..."
              rows={4}
              className="answer-textarea"
            />
          </div>
        );
    }
  };

  return (
    <div className="question-card">
      {/* Question context */}
      <div className="question-card__context">
        <div className="context-breadcrumb">
          <span className="context-section">{question.sectionTitle}</span>
          <span className="context-separator">→</span>
          <span className="context-subsection">{question.subsectionTitle}</span>
          {question.groupTitle && (
            <>
              <span className="context-separator">→</span>
              <span className="context-group">{question.groupTitle}</span>
            </>
          )}
        </div>
      </div>

      {/* Main question */}
      <div className="question-card__main">
        <div className="question-text">
          <h2>{question.text}</h2>
          {question.hint && (
            <div className="question-hint">
              <span className="hint-icon">💡</span>
              <span className="hint-text">{question.hint}</span>
            </div>
          )}
        </div>

        {/* Answer input */}
        <div className="question-input">
          {renderQuestionInput()}
        </div>
      </div>

      {/* Additional fields */}
      <div className="question-card__additional">
        {/* Source type selection */}
        <div className="source-selection">
          <label className="field-label">Источник информации:</label>
          <div className="source-options">
            <label className="source-option">
              <input
                type="radio"
                value="FOUND_IN_TEXT"
                checked={sourceType === 'FOUND_IN_TEXT'}
                onChange={(e) => setSourceType(e.target.value as any)}
              />
              <span>Найдено в тексте</span>
            </label>
            <label className="source-option">
              <input
                type="radio"
                value="LOGICALLY_DERIVED"
                checked={sourceType === 'LOGICALLY_DERIVED'}
                onChange={(e) => setSourceType(e.target.value as any)}
              />
              <span>Логически выведено</span>
            </label>
            <label className="source-option">
              <input
                type="radio"
                value="IMAGINED"
                checked={sourceType === 'IMAGINED'}
                onChange={(e) => setSourceType(e.target.value as any)}
              />
              <span>Домыслено</span>
            </label>
          </div>
        </div>

        {/* Comment field */}
        <div className="comment-field">
          <label className="field-label">Заметки (опционально):</label>
          <textarea
            value={localComment}
            onChange={(e) => setLocalComment(e.target.value)}
            onBlur={handleAutoSave}
            placeholder="Добавьте заметки или обоснование..."
            rows={2}
            className="comment-textarea"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="question-card__actions">
        <div className="action-buttons">
          <button
            onClick={handleSave}
            disabled={isLoading}
            className="btn btn-primary btn-large"
          >
            {isLoading ? 'Сохранение...' : 'Сохранить ответ'}
          </button>
          
          {question.current_response && onAnswerDelete && (
            <button
              onClick={() => onAnswerDelete(question.current_response.id)}
              className="btn btn-secondary"
              title="Удалить ответ"
            >
              🗑 Удалить
            </button>
          )}
        </div>
        
        {question.current_response && (
          <div className="save-status">
            <span className="save-icon">✓</span>
            <span className="save-text">Сохранено</span>
            <span className="save-date">
              {new Date(question.current_response.updated_at).toLocaleString('ru')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
