import React from 'react';
import { Card } from "@gravity-ui/uikit";

interface OverallProgressProps {
  progress: any[];
  character: any;
}

export const OverallProgress: React.FC<OverallProgressProps> = ({ progress}) => {
  if (!progress || progress.length === 0) {
    return (
      <div className="overall-progress overall-progress--empty">
        <div className="overall-progress__content">
          <h2>Начните анализ персонажа</h2>
          <p>Заполните чеклисты, чтобы увидеть прогресс</p>
        </div>
      </div>
    );
  }

  // Calculate overall stats
  const totalQuestions = progress.reduce((sum, p) => sum + p.total_questions, 0);
  const answeredQuestions = progress.reduce((sum, p) => sum + p.answered_questions, 0);
  const overallPercentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;
  
  const completedChecklists = progress.filter(p => p.completion_percentage === 100).length;
  const inProgressChecklists = progress.filter(p => p.completion_percentage > 0 && p.completion_percentage < 100).length;

  return (
    <Card type='container' view='raised' size='l'>
    <div className="overall-progress">
      <div className="overall-progress__stats">
        <div className="progress-stat">
          <div className="stat-number">{overallPercentage}%</div>
          <div className="stat-label">Общий прогресс</div>
        </div>
        
        <div className="progress-stat">
          <div className="stat-number">{answeredQuestions}</div>
          <div className="stat-label">из {totalQuestions} вопросов</div>
        </div>
        
        <div className="progress-stat">
          <div className="stat-number">{completedChecklists}</div>
          <div className="stat-label">завершено</div>
        </div>
      </div>

      <div className="overall-progress__visual">
        <div className="progress-bar large">
          <div 
            className={`progress-fill ${
              overallPercentage === 100 ? 'completed' : 
              overallPercentage > 50 ? 'in-progress' : 'started'
            }`}
            style={{ width: `${overallPercentage}%` }}
          />
        </div>
        
        <div className="progress-breakdown">
          <div className="breakdown-item">
            <span className="dot completed"></span>
            {completedChecklists} завершено
          </div>
          <div className="breakdown-item">
            <span className="dot in-progress"></span>
            {inProgressChecklists} в работе
          </div>
        </div>
      </div>

      {overallPercentage === 100 && (
        <div className="overall-progress__celebration">
          <div className="celebration-content">
            🎉 Поздравляем! Анализ персонажа завершен на 100%! 🎉
          </div>
        </div>
      )}
      </div>
    </Card>
  );
};
