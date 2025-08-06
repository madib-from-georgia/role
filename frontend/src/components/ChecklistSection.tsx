import React, { useState } from 'react';
import { ChecklistSubsection, ChecklistSubsectionData } from './ChecklistSubsection';

export interface ChecklistSectionData {
  id: number;
  title: string;
  number?: string;
  icon?: string;
  subsections: ChecklistSubsectionData[];
}

interface ChecklistSectionProps {
  section: ChecklistSectionData;
  onAnswerUpdate: (questionId: number, data: {
    answer?: string;
    source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
    comment?: string;
  }) => void;
  onAnswerDelete: (responseId: number) => void;
  isExpanded?: boolean;
}

export const ChecklistSection: React.FC<ChecklistSectionProps> = ({
  section,
  onAnswerUpdate,
  onAnswerDelete,
  isExpanded = true
}) => {
  const [isOpen, setIsOpen] = useState(isExpanded);

  // Статистика секции
  const totalQuestions = section.subsections.reduce(
    (total, subsection) => total + subsection.question_groups.reduce(
      (subTotal, group) => subTotal + group.questions.length,
      0
    ),
    0
  );

  const answeredQuestions = section.subsections.reduce(
    (total, subsection) => total + subsection.question_groups.reduce(
      (subTotal, group) => subTotal + group.questions.filter(q => q.current_response?.answer).length,
      0
    ),
    0
  );

  const completionPercentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;

  return (
    <div className="checklist-section">
      {/* Заголовок секции */}
      <div className="section-header" onClick={() => setIsOpen(!isOpen)}>
        <div className="section-header-content">
          <div className="section-toggle">
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
            
            <div className="section-title-container">
              {section.icon && (
                <span className="section-icon">{section.icon}</span>
              )}
              <div className="section-info">
                <h1 className="section-title">
                  {section.number && (
                    <span className="section-number">{section.number}.</span>
                  )}
                  {section.title}
                </h1>
                
                <div className="section-stats">
                  <span className="stat-text">
                    {section.subsections.length} подразделов, {totalQuestions} вопросов
                  </span>
                  <span className="stat-text">
                    Выполнено: {answeredQuestions} из {totalQuestions}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="section-status-container">
            {/* Прогресс-бар */}
            <div className="progress-container large">
              <div className="progress-bar extra-large">
                <div 
                  className={`progress-fill ${
                    completionPercentage === 100 ? 'completed' : 
                    completionPercentage > 50 ? 'in-progress' : 'started'
                  }`}
                  style={{ width: `${completionPercentage}%` }}
                />
              </div>
              <span className="progress-text large">{completionPercentage}%</span>
            </div>
            
            {/* Статус секции */}
            {completionPercentage === 100 ? (
              <span className="status-badge completed large with-icon">
                ✓ Завершено
              </span>
            ) : completionPercentage > 0 ? (
              <span className="status-badge in-progress large with-icon">
                ⚡ В работе
              </span>
            ) : (
              <span className="status-badge not-started large with-icon">
                ○ Не начато
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Подсекции */}
      {isOpen && (
        <div className="section-body">
          <div className="section-subsections">
            {section.subsections.map((subsection) => (
              <ChecklistSubsection
                key={subsection.id}
                subsection={subsection}
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