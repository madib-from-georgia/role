import React from 'react';

interface OverallProgressProps {
  progress: any[];
  character: any;
}

export const OverallProgress: React.FC<OverallProgressProps> = ({
  progress,
  character
}) => {
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
  const notStartedChecklists = progress.filter(p => p.completion_percentage === 0).length;

  // Estimate time to completion (assuming 15 seconds per question)
  const remainingQuestions = totalQuestions - answeredQuestions;
  const estimatedMinutes = Math.ceil(remainingQuestions * 15 / 60);
  
  const getProgressMessage = () => {
    if (overallPercentage === 100) {
      return "Анализ завершен! Отличная работа!";
    } else if (overallPercentage >= 75) {
      return "Почти готово! Последний рывок!";
    } else if (overallPercentage >= 50) {
      return "Половина пути пройдена!";
    } else if (overallPercentage >= 25) {
      return "Хорошее начало! Продолжайте!";
    } else if (overallPercentage > 0) {
      return "Анализ начат. Продолжайте работу!";
    }
    return "Готовы начать анализ?";
  };

  return (
    <div className="overall-progress">
      <div className="overall-progress__header">
        <div className="overall-progress__character">
          <h2>Анализ персонажа: {character?.name}</h2>
          <div className="character-importance">
            {character?.importance_score && (
              <span>Важность: {Math.round(character.importance_score * 100)}%</span>
            )}
          </div>
        </div>
        <div className="overall-progress__message">
          {getProgressMessage()}
        </div>
      </div>

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
        
        {remainingQuestions > 0 && (
          <div className="progress-stat">
            <div className="stat-number">~{estimatedMinutes}</div>
            <div className="stat-label">мин осталось</div>
          </div>
        )}
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
          <div className="breakdown-item">
            <span className="dot not-started"></span>
            {notStartedChecklists} не начато
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
  );
};
