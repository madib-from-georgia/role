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
  const completionPercentage = checklist?.completion_stats?.completion_percentage || 0;

  return (
    <div className="progress-bar-container">
      {/* Compact header with main info */}
      <div className="progress-header-compact">
        {/* Title on full width */}
        <h1 className="checklist-title-compact">
          {checklist?.icon && <span className="checklist-icon">{checklist.icon}</span>}
          {checklist?.title}
        </h1>
        
        {/* Two columns below */}
        <div className="progress-content-row">
          <div className="progress-summary">
            <span className="current-question">
              {currentIndex + 1}/{totalQuestions}
            </span>
            <span className="progress-dot">•</span>
            <span className="completion-rate">{completionPercentage}%</span>
            <span className="progress-dot">•</span>
            <span className="time-estimate">
              ≈{Math.max(1, Math.ceil((totalQuestions - currentIndex) / 4))}мин
            </span>
          </div>

          {/* Compact progress bar */}
          <div className="progress-bar-compact">
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
            <div className="progress-percentage">{progressPercentage}%</div>
          </div>
        </div>
      </div>
    </div>
  );
};
