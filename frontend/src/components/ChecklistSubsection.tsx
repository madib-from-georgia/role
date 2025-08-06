import React, { useState } from 'react';
import { ChecklistQuestionGroup, ChecklistQuestionGroupData } from './ChecklistQuestionGroup';

export interface ChecklistSubsectionData {
  id: number;
  title: string;
  number?: string;
  examples?: string;  // Примеры из литературы
  why_important?: string;  // Почему это важно
  question_groups: ChecklistQuestionGroupData[];
}

interface ChecklistSubsectionProps {
  subsection: ChecklistSubsectionData;
  onAnswerUpdate: (questionId: number, data: {
    answer?: string;
    source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    comment?: string;
  }) => void;
  onAnswerDelete: (responseId: number) => void;
  isExpanded?: boolean;
}

export const ChecklistSubsection: React.FC<ChecklistSubsectionProps> = ({
  subsection,
  onAnswerUpdate,
  onAnswerDelete,
  isExpanded = false
}) => {
  const [isOpen, setIsOpen] = useState(isExpanded);

  // Статистика подсекции
  const totalQuestions = subsection.question_groups.reduce(
    (total, group) => total + group.questions.length, 
    0
  );
  const answeredQuestions = subsection.question_groups.reduce(
    (total, group) => total + group.questions.filter(q => q.current_response?.answer).length,
    0
  );
  const completionPercentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;

  return (
    <div className="checklist-subsection">
      {/* Заголовок подсекции */}
      <div className="subsection-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="subsection-header-content">
          <div className="subsection-toggle">
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
            
            <div className="subsection-info">
              <h2 className="subsection-title">
                {subsection.number && (
                  <span className="subsection-number">{subsection.number}</span>
                )}
                {subsection.title}
              </h2>
              
              <div className="subsection-stats">
                <span className="stat-text">
                  {subsection.question_groups.length} групп, {totalQuestions} вопросов
                </span>
                <span className="stat-text">
                  Отвечено: {answeredQuestions} из {totalQuestions}
                </span>
                <div className="progress-container">
                  <div className="progress-bar large">
                    <div 
                      className={`progress-fill ${
                        completionPercentage === 100 ? 'completed' : 
                        completionPercentage > 50 ? 'in-progress' : 'started'
                      }`}
                      style={{ width: `${completionPercentage}%` }}
                    />
                  </div>
                  <span className="progress-text">{completionPercentage}%</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Статус подсекции */}
          <div className="subsection-status">
            {completionPercentage === 100 ? (
              <span className="status-badge completed with-icon">
                ✓ Завершено
              </span>
            ) : completionPercentage > 0 ? (
              <span className="status-badge in-progress with-icon">
                ◐ В процессе
              </span>
            ) : (
              <span className="status-badge not-started with-icon">
                ○ Не начато
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Содержимое подсекции */}
      {isOpen && (
        <div className="subsection-content">
          {/* Группы вопросов */}
          <div className="question-groups">
            {subsection.question_groups.map((group) => (
              <ChecklistQuestionGroup
                key={group.id}
                group={group}
                onAnswerUpdate={onAnswerUpdate}
                onAnswerDelete={onAnswerDelete}
              />
            ))}
          </div>

          {/* Примеры из литературы */}
          {subsection.examples && (
            <div className="subsection-examples">
              <h3>Примеры из литературы</h3>
              <div className="examples-content">
                {subsection.examples}
              </div>
            </div>
          )}

          {/* Почему это важно */}
          {subsection.why_important && (
            <div className="subsection-why-important">
              <h3>Почему это важно</h3>
              <div className="why-important-content">
                {subsection.why_important}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};