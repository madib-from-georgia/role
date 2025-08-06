import React, { useState } from 'react';

export interface ChecklistQuestionData {
  id: number;
  text: string;
  hint?: string;
  options?: string[];  // Варианты ответов
  option_type?: 'single' | 'multiple' | 'none';  // Тип вариантов
  current_response?: {
    id: number;
    answer?: string;
    source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    comment?: string;
    version: number;
    updated_at?: string;
  };
  response_history?: Array<{
    id: number;
    previous_answer?: string;
    previous_source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    previous_comment?: string;
    created_at: string;
  }>;
}

interface ChecklistQuestionProps {
  question: ChecklistQuestionData;
  onAnswerUpdate: (questionId: number, data: {
    answer?: string;
    source_type?: 'found_in_text' | 'logically_derived' | 'imagined';
    comment?: string;
  }) => void;
  onAnswerDelete: (responseId: number) => void;
  isExpanded?: boolean;
}

const sourceTypeLabels = {
  FOUND_IN_TEXT: { label: 'Найдено в тексте', color: 'source-found' },
  LOGICALLY_DERIVED: { label: 'Логически выведено', color: 'source-derived' },
  IMAGINED: { label: 'Придумано', color: 'source-imagined' }
};

export const ChecklistQuestion: React.FC<ChecklistQuestionProps> = ({
  question,
  onAnswerUpdate,
  onAnswerDelete,
  isExpanded = false
}) => {
  const [isOpen, setIsOpen] = useState(isExpanded);
  const [isEditing, setIsEditing] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showCustomAnswer, setShowCustomAnswer] = useState(false);
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [customAnswer, setCustomAnswer] = useState('');
  
  const [formData, setFormData] = useState({
    answer: question.current_response?.answer || '',
    source_type: question.current_response?.source_type || 'IMAGINED' as const,
    comment: question.current_response?.comment || ''
  });

  const hasResponse = !!question.current_response?.answer;
  const hasHistory = question.response_history && question.response_history.length > 0;
  const hasOptions = question.options && question.options.length > 0;

  // Инициализация выбранных вариантов из текущего ответа
  React.useEffect(() => {
    if (question.current_response?.answer && hasOptions) {
      if (question.option_type === 'multiple') {
        setSelectedOptions(question.current_response.answer.split(', '));
      } else {
        setSelectedOptions([question.current_response.answer]);
      }
    }
  }, [question.current_response?.answer, hasOptions, question.option_type]);

  const handleOptionChange = (option: string, checked: boolean) => {
    if (question.option_type === 'single') {
      if (option === 'отвечу сам') {
        setShowCustomAnswer(checked);
        if (checked) {
          setSelectedOptions([]);
          setFormData(prev => ({ ...prev, answer: '' }));
        } else {
          setCustomAnswer('');
          setFormData(prev => ({ ...prev, answer: '' }));
        }
      } else {
        setShowCustomAnswer(false);
        setCustomAnswer('');
        setSelectedOptions(checked ? [option] : []);
      }
    } else if (question.option_type === 'multiple') {
      if (option === 'отвечу сам') {
        setShowCustomAnswer(checked);
        if (checked) {
          setCustomAnswer('');
          setFormData(prev => ({ ...prev, answer: '' }));
        } else {
          setCustomAnswer('');
          setFormData(prev => ({ ...prev, answer: '' }));
        }
      } else {
        setSelectedOptions(prev => 
          checked 
            ? [...prev, option]
            : prev.filter(o => o !== option)
        );
      }
    }
  };

  const handleCustomAnswerChange = (value: string) => {
    setCustomAnswer(value);
    if (value.trim()) {
      setFormData(prev => ({ ...prev, answer: value.trim() }));
    }
  };

  const handleSave = () => {
    let finalAnswer = '';
    
    if (showCustomAnswer && customAnswer.trim()) {
      finalAnswer = customAnswer.trim();
    } else if (selectedOptions.length > 0) {
      // Исключаем "отвечу сам" из финального ответа
      const filteredOptions = selectedOptions.filter(opt => opt !== 'отвечу сам');
      finalAnswer = filteredOptions.join(', ');
    }
    
    onAnswerUpdate(question.id, {
      ...formData,
      answer: finalAnswer,
      source_type: formData.source_type.toLowerCase() as 'found_in_text' | 'logically_derived' | 'imagined'
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setFormData({
      answer: question.current_response?.answer || '',
      source_type: question.current_response?.source_type || 'IMAGINED',
      comment: question.current_response?.comment || ''
    });
    setSelectedOptions([]);
    setCustomAnswer('');
    setShowCustomAnswer(false);
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (question.current_response?.id && 
        window.confirm('Вы уверены, что хотите удалить ответ? Он будет сохранен в истории.')) {
      onAnswerDelete(question.current_response.id);
    }
  };

  const startEditing = () => {
    setIsEditing(true);
    setIsOpen(true);
  };

  return (
    <div className="checklist-question">
      {/* Заголовок вопроса */}
      <div className="question-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="question-header-content">
          <div className="question-toggle">
            <button className="toggle-btn">
              <svg 
                className={`toggle-icon ${isOpen ? 'open' : ''}`} 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
            
            <div className="question-info">
              <h3 className="question-title">{question.text}</h3>
              
              {/* Статус ответа */}
              <div className="question-status">
                {hasResponse ? (
                  <span className="status-badge answered">
                    ✓ Отвечено
                  </span>
                ) : (
                  <span className="status-badge not-answered">
                    ○ Не отвечено
                  </span>
                )}
                
                {/* Источник ответа */}
                {question.current_response?.source_type && (
                  <span className={`source-badge ${sourceTypeLabels[question.current_response.source_type].color}`}>
                    {sourceTypeLabels[question.current_response.source_type].label}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Действия */}
          <div className="question-actions">
            {hasResponse ? (
              <>
                <button className="action-btn edit" onClick={startEditing}>
                  ✏️
                </button>
                <button className="action-btn delete" onClick={handleDelete}>
                  🗑️
                </button>
              </>
            ) : (
              <button className="action-btn add" onClick={startEditing}>
                +
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Содержимое вопроса */}
      {isOpen && (
        <div className="question-content">
          {/* Подсказка */}
          {question.hint && (
            <div className="question-hint">
              <em>{question.hint}</em>
            </div>
          )}

          {/* Форма редактирования */}
          {isEditing && (
            <div className="question-form">
              {/* Варианты ответов */}
              {hasOptions && question.options && (
                <div className="options-section">
                  <h4>Варианты ответов:</h4>
                  <div className="options-list">
                    {question.options.map((option, index) => (
                      <label key={index} className="option-item">
                        <input
                          type={question.option_type === 'multiple' ? 'checkbox' : 'radio'}
                          name={`question-${question.id}`}
                          value={option}
                          checked={selectedOptions.includes(option)}
                          onChange={(e) => handleOptionChange(option, e.target.checked)}
                        />
                        <span className="option-text">{option}</span>
                      </label>
                    ))}
                    
                    {/* Вариант "отвечу сам" */}
                    <label className="option-item custom-answer">
                      <input
                        type={question.option_type === 'multiple' ? 'checkbox' : 'radio'}
                        name={`question-${question.id}`}
                        checked={showCustomAnswer}
                        onChange={(e) => handleOptionChange('отвечу сам', e.target.checked)}
                      />
                      <span className="option-text">Отвечу сам</span>
                    </label>
                  </div>
                </div>
              )}

              {/* Поле для собственного ответа */}
              {(showCustomAnswer || !hasOptions) && (
                <div className="custom-answer-section">
                  <label className="form-label">
                    Ваш ответ:
                    <textarea
                      className="form-textarea"
                      value={customAnswer}
                      onChange={(e) => handleCustomAnswerChange(e.target.value)}
                      placeholder="Введите ваш ответ..."
                      rows={3}
                    />
                  </label>
                </div>
              )}

              {/* Источник ответа */}
              <div className="source-type-section">
                <label className="form-label">
                  Источник ответа:
                  <select
                    className="form-select"
                    value={formData.source_type}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      source_type: e.target.value as 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED'
                    }))}
                  >
                    <option value="IMAGINED">Придумано</option>
                    <option value="FOUND_IN_TEXT">Найдено в тексте</option>
                    <option value="LOGICALLY_DERIVED">Логически выведено</option>
                  </select>
                </label>
              </div>

              {/* Комментарий */}
              <div className="comment-section">
                <label className="form-label">
                  Комментарий (необязательно):
                  <textarea
                    className="form-textarea"
                    value={formData.comment}
                    onChange={(e) => setFormData(prev => ({ ...prev, comment: e.target.value }))}
                    placeholder="Добавьте комментарий к ответу..."
                    rows={2}
                  />
                </label>
              </div>

              {/* Кнопки действий */}
              <div className="form-actions">
                <button className="btn btn-primary" onClick={handleSave}>
                  Сохранить
                </button>
                <button className="btn btn-secondary" onClick={handleCancel}>
                  Отмена
                </button>
              </div>
            </div>
          )}

          {/* Текущий ответ */}
          {!isEditing && hasResponse && question.current_response && (
            <div className="current-response">
              <div className="response-content">
                <strong>Ответ:</strong> {question.current_response.answer}
              </div>
              
              {question.current_response.comment && (
                <div className="response-comment">
                  <strong>Комментарий:</strong> {question.current_response.comment}
                </div>
              )}
              
              <div className="response-meta">
                <span className="response-source">
                  {sourceTypeLabels[question.current_response.source_type || 'IMAGINED'].label}
                </span>
                {question.current_response.updated_at && (
                  <span className="response-date">
                    Обновлено: {new Date(question.current_response.updated_at).toLocaleDateString('ru-RU')}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* История ответов */}
          {hasHistory && question.response_history && (
            <div className="response-history">
              <button 
                className="history-toggle"
                onClick={() => setShowHistory(!showHistory)}
              >
                {showHistory ? 'Скрыть историю' : 'Показать историю'} ({question.response_history.length})
              </button>
              
              {showHistory && (
                <div className="history-list">
                  {question.response_history.map((history, index) => (
                    <div key={history.id} className="history-item">
                      <div className="history-content">
                        <strong>Предыдущий ответ:</strong> {history.previous_answer}
                      </div>
                      {history.previous_comment && (
                        <div className="history-comment">
                          <strong>Комментарий:</strong> {history.previous_comment}
                        </div>
                      )}
                      <div className="history-meta">
                        <span className="history-source">
                          {sourceTypeLabels[history.previous_source_type || 'IMAGINED'].label}
                        </span>
                        <span className="history-date">
                          {new Date(history.created_at).toLocaleDateString('ru-RU')}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
