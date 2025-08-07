import React, { useState } from 'react';

interface QuestionCardProps {
  question: any;
  onAnswerUpdate: (questionId: number, data: any) => void;
  isLoading: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  onAnswerUpdate,
  isLoading
}) => {
  const [localAnswer, setLocalAnswer] = useState(question?.current_response?.answer || '');
  const [localComment, setLocalComment] = useState(question?.current_response?.comment || '');
  const [sourceType, setSourceType] = useState(question?.current_response?.source_type || 'LOGICALLY_DERIVED');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);

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

    // Handle different question types
    if (question.type === 'SINGLE_CHOICE' || question.type === 'MULTIPLE_CHOICE') {
      data.answer = selectedOptions.join(', ');
    } else {
      data.answer = localAnswer;
    }

    onAnswerUpdate(question.id, data);
  };

  const handleOptionChange = (option: string, checked: boolean) => {
    if (question.type === 'SINGLE_CHOICE') {
      setSelectedOptions(checked ? [option] : []);
    } else if (question.type === 'MULTIPLE_CHOICE') {
      setSelectedOptions(prev => 
        checked 
          ? [...prev, option]
          : prev.filter(o => o !== option)
      );
    }
  };

  const renderQuestionInput = () => {
    switch (question.type) {
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
            placeholder="Добавьте заметки или обоснование..."
            rows={2}
            className="comment-textarea"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="question-card__actions">
        <button
          onClick={handleSave}
          disabled={isLoading}
          className="btn btn-primary btn-large"
        >
          {isLoading ? 'Сохранение...' : 'Сохранить ответ'}
        </button>
        
        {question.current_response && (
          <div className="save-status">
            <span className="save-icon">✓</span>
            <span className="save-text">Сохранено</span>
          </div>
        )}
      </div>
    </div>
  );
};