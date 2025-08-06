import React, { useState } from 'react';

export interface ChecklistQuestionData {
  id: number;
  text: string;
  hint?: string;
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
  const [formData, setFormData] = useState({
    answer: question.current_response?.answer || '',
    source_type: question.current_response?.source_type || 'IMAGINED' as const,
    comment: question.current_response?.comment || ''
  });

  const hasResponse = !!question.current_response?.answer;
  const hasHistory = question.response_history && question.response_history.length > 0;

  const handleSave = () => {
    onAnswerUpdate(question.id, formData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setFormData({
      answer: question.current_response?.answer || '',
      source_type: question.current_response?.source_type || 'IMAGINED',
      comment: question.current_response?.comment || ''
    });
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
            
            <div className="question-content">
              <p className="question-text">{question.text}</p>
              
              {/* Индикатор статуса */}
              <div className="question-status">
                {hasResponse ? (
                  <>
                    <span className={`status-badge ${sourceTypeLabels[question.current_response!.source_type!].color}`}>
                      {sourceTypeLabels[question.current_response!.source_type!].label}
                    </span>
                    {question.current_response?.version && question.current_response.version > 1 && (
                      <span className="version-badge">
                        v.{question.current_response.version}
                      </span>
                    )}
                  </>
                ) : (
                  <span className="status-badge unanswered">
                    Не отвечен
                  </span>
                )}
              </div>
            </div>
          </div>
          
          {/* Кнопки действий */}
          {hasResponse && (
            <div className="question-actions">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  startEditing();
                }}
                className="action-btn edit-btn"
                title="Редактировать ответ"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              {hasHistory && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowHistory(!showHistory);
                    setIsOpen(true);
                  }}
                  className="action-btn history-btn"
                  title="История изменений"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </button>
              )}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete();
                }}
                className="action-btn delete-btn"
                title="Удалить ответ"
              >
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Развернутое содержимое */}
      {isOpen && (
        <div className="question-body">
          {/* Подсказка */}
          {question.hint && (
            <div className="question-hint">
              <div className="hint-content">
                <span className="hint-label">Подсказка:</span> {question.hint}
              </div>
            </div>
          )}

          {/* Текущий ответ или форма */}
          {isEditing ? (
            <div className="question-form">
              {/* Поле ответа */}
              <div className="form-group">
                <label className="form-label">Ответ</label>
                <textarea
                  value={formData.answer}
                  onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
                  className="form-textarea"
                  placeholder="Введите ваш ответ..."
                />
              </div>

              {/* Источник ответа */}
              <div className="form-group">
                <label className="form-label">Источник ответа</label>
                <select
                  value={formData.source_type}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    source_type: e.target.value as 'found_in_text' | 'logically_derived' | 'imagined'
                  })}
                  className="form-input"
                >
                  <option value="found_in_text">Найдено в тексте</option>
                  <option value="logically_derived">Логически выведено</option>
                  <option value="imagined">Придумано</option>
                </select>
              </div>

              {/* Комментарий */}
              <div className="form-group">
                <label className="form-label">Комментарий</label>
                <textarea
                  value={formData.comment}
                  onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
                  className="form-textarea comment-textarea"
                  placeholder="Цитата, обоснование или комментарий..."
                />
              </div>

              {/* Кнопки */}
              <div className="form-actions">
                <button onClick={handleCancel} className="btn btn-secondary">
                  Отмена
                </button>
                <button onClick={handleSave} className="btn btn-primary">
                  Сохранить
                </button>
              </div>
            </div>
          ) : hasResponse ? (
            <div className="question-answer">
              {/* Ответ */}
              <div className="answer-section">
                <h4 className="answer-label">Ответ:</h4>
                <p className="answer-text">{question.current_response?.answer}</p>
              </div>

              {/* Комментарий */}
              {question.current_response?.comment && (
                <div className="comment-section">
                  <h4 className="comment-label">Комментарий:</h4>
                  <p className="comment-text">{question.current_response.comment}</p>
                </div>
              )}

              {/* Метаданные */}
              {question.current_response?.updated_at && (
                <div className="answer-meta">
                  Обновлено: {new Date(question.current_response.updated_at).toLocaleString('ru-RU')}
                </div>
              )}
            </div>
          ) : (
            <div className="no-answer">
              <div className="no-answer-content">
                <p className="no-answer-text">Ответ еще не добавлен</p>
                <button onClick={startEditing} className="btn btn-primary">
                  Добавить ответ
                </button>
              </div>
            </div>
          )}

          {/* История изменений */}
          {showHistory && hasHistory && (
            <div className="question-history">
              <h4 className="history-title">История изменений</h4>
              <div className="history-list">
                {question.response_history?.map((historyItem) => (
                  <div key={historyItem.id} className="history-item">
                    {historyItem.previous_answer && (
                      <div className="history-answer">
                        <p className="history-label">Предыдущий ответ:</p>
                        <p className="history-text">{historyItem.previous_answer}</p>
                      </div>
                    )}
                    
                    {historyItem.previous_source_type && (
                      <div className="history-source">
                        <span className={`status-badge ${sourceTypeLabels[historyItem.previous_source_type].color}`}>
                          {sourceTypeLabels[historyItem.previous_source_type].label}
                        </span>
                      </div>
                    )}
                    
                    <div className="history-date">
                      {new Date(historyItem.created_at).toLocaleString('ru-RU')}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
