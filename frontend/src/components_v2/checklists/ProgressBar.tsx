import React from 'react';

interface ProgressBarProps {
  currentIndex: number;
  totalQuestions: number;
  checklist: any;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  currentIndex,
  totalQuestions,
  checklist
}) => {
  const progressPercentage = totalQuestions > 0 ? Math.round((currentIndex / totalQuestions) * 100) : 0;
  const answeredQuestions = checklist?.completion_stats?.answered_questions || 0;
  const completionPercentage = checklist?.completion_stats?.completion_percentage || 0;

  return (
    <div className="progress-bar-container">
      {/* Checklist info */}
      <div className="progress-header">
        <div className="checklist-info">
          <h1 className="checklist-title">
            {checklist?.icon && <span className="checklist-icon">{checklist.icon}</span>}
            {checklist?.title}
          </h1>
          <div className="question-position">
            Вопрос {currentIndex + 1} из {totalQuestions}
          </div>
        </div>
        
        <div className="progress-stats">
          <div className="stat-item">
            <span className="stat-label">Текущий прогресс:</span>
            <span className="stat-value">{progressPercentage}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Заполнено:</span>
            <span className="stat-value">{answeredQuestions} вопросов</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Общий прогресс:</span>
            <span className="stat-value">{completionPercentage}%</span>
          </div>
        </div>
      </div>

      {/* Progress visualization */}
      <div className="progress-visualization">
        {/* Main progress bar */}
        <div className="main-progress">
          <div className="progress-track">
            <div 
              className="progress-fill current-position"
              style={{ width: `${progressPercentage}%` }}
            />
            <div 
              className="progress-fill answered-questions"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
          <div className="progress-markers">
            <span className="marker start">Начало</span>
            <span className="marker current" style={{ left: `${progressPercentage}%` }}>
              Сейчас
            </span>
            <span className="marker end">Конец</span>
          </div>
        </div>

        {/* Section breakdown */}
        {checklist?.sections && (
          <div className="section-breakdown">
            {checklist.sections.map((section: any, index: number) => {
              const sectionQuestions = section.subsections?.reduce((total: number, sub: any) => {
                return total + (sub.question_groups?.reduce((groupTotal: number, group: any) => {
                  return groupTotal + (group.questions?.length || 0);
                }, 0) || 0);
              }, 0) || 0;
              
              const sectionWidth = totalQuestions > 0 ? (sectionQuestions / totalQuestions) * 100 : 0;
              
              return (
                <div 
                  key={section.id} 
                  className="section-segment"
                  style={{ width: `${sectionWidth}%` }}
                  title={`${section.title}: ${sectionQuestions} вопросов`}
                >
                  <div className="segment-label">{section.title}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Quick stats */}
      <div className="quick-stats">
        <div className="stat-badge">
          <span className="badge-icon">⏱</span>
          <span className="badge-text">
            ≈ {Math.max(1, Math.ceil((totalQuestions - currentIndex) / 4))} мин
          </span>
        </div>
        
        {completionPercentage >= 50 && (
          <div className="stat-badge success">
            <span className="badge-icon">🎯</span>
            <span className="badge-text">Больше половины!</span>
          </div>
        )}
        
        {completionPercentage >= 90 && (
          <div className="stat-badge celebration">
            <span className="badge-icon">🚀</span>
            <span className="badge-text">Почти готово!</span>
          </div>
        )}
      </div>
    </div>
  );
};