import React, { useState } from 'react';
import { ChecklistQuestion, ChecklistQuestionData } from './ChecklistQuestion';

export interface ChecklistQuestionGroupData {
  id: number;
  title: string;
  questions: ChecklistQuestionData[];
}

interface ChecklistQuestionGroupProps {
  group: ChecklistQuestionGroupData;
  onAnswerUpdate: (questionId: number, data: {
    answer?: string;
    source_type?: 'found_in_text' | 'logically_derived' | 'imagined';
    comment?: string;
  }) => void;
  onAnswerDelete: (responseId: number) => void;
  isExpanded?: boolean;
}

export const ChecklistQuestionGroup: React.FC<ChecklistQuestionGroupProps> = ({
  group,
  onAnswerUpdate,
  onAnswerDelete,
  isExpanded = false
}) => {
  const [isOpen, setIsOpen] = useState(isExpanded);

  console.log(group);
  // Статистика группы
  const totalQuestions = group.questions.length;
  const answeredQuestions = group.questions.filter(q => q.current_response?.answer).length;
  const completionPercentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;

  return (
    <div className="checklist-group">
      {/* Заголовок группы */}
      <div className="group-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="group-header-content">
          <div className="group-toggle">
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
            
            <div className="group-info">
              <h3 className="group-title">{group.title}</h3>
              <div className="group-stats">
                <span className="stat-text">
                  {answeredQuestions} из {totalQuestions} вопросов
                </span>
                <div className="progress-container">
                  <div className="progress-bar">
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
          
          {/* Статус группы */}
          <div className="group-status">
            {completionPercentage === 100 ? (
              <span className="status-badge completed">
                Завершено
              </span>
            ) : completionPercentage > 0 ? (
              <span className="status-badge in-progress">
                В процессе
              </span>
            ) : (
              <span className="status-badge not-started">
                Не начато
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Вопросы группы */}
      {isOpen && (
        <div className="group-body">
          <div className="group-questions">
            {group.questions.map((question) => (
              <ChecklistQuestion
                key={question.id}
                question={question}
                onAnswerUpdate={onAnswerUpdate}
                onAnswerDelete={onAnswerDelete}
                isExpanded={false}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
