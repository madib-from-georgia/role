import React from 'react';
import { useNavigate } from 'react-router-dom';

interface RecommendedNextStepProps {
  progress: any[];
  checklists: any[];
  characterId: number;
}

export const RecommendedNextStep: React.FC<RecommendedNextStepProps> = ({
  progress,
  checklists,
  characterId
}) => {
  const navigate = useNavigate();

  // TODO: Implement smart recommendation logic
  const getRecommendedStep = () => {
    if (!progress || !checklists) return null;
    
    // Simple logic for now - find first incomplete checklist
    const incompleteChecklists = progress.filter(p => p.completion_percentage < 100);
    if (incompleteChecklists.length === 0) return null;
    
    const firstIncomplete = incompleteChecklists[0];
    const checklist = checklists.find(c => c.id === firstIncomplete.checklist_id);
    
    return {
      checklist,
      progress: firstIncomplete,
      reason: "Продолжить с места последней работы"
    };
  };

  const recommendedStep = getRecommendedStep();

  if (!recommendedStep) {
    return (
      <div className="recommended-step recommended-step--completed">
        <div className="recommended-step__content">
          <div className="recommended-step__icon">🎉</div>
          <div className="recommended-step__text">
            <h3>Анализ завершен!</h3>
            <p>Все чеклисты заполнены. Отличная работа!</p>
          </div>
        </div>
      </div>
    );
  }

  const handleStartStep = () => {
    navigate(`/characters/${characterId}/checklists/${recommendedStep.checklist.slug}`);
  };

  return (
    <div className="recommended-step">
      <div className="recommended-step__header">
        <h2>Рекомендуемый следующий шаг</h2>
        <span className="recommended-step__badge">Smart AI</span>
      </div>
      
      <div className="recommended-step__content">
        <div className="recommended-step__info">
          <div className="recommended-step__icon">
            {recommendedStep.checklist.icon || '📝'}
          </div>
          
          <div className="recommended-step__text">
            <h3>{recommendedStep.checklist.title}</h3>
            <p className="recommended-step__reason">
              {recommendedStep.reason}
            </p>
            <div className="recommended-step__progress">
              Прогресс: {recommendedStep.progress.completion_percentage}%
              ({recommendedStep.progress.answered_questions} из {recommendedStep.progress.total_questions} вопросов)
            </div>
          </div>
        </div>
        
        <div className="recommended-step__actions">
          <button 
            onClick={handleStartStep}
            className="btn btn-primary btn-large"
          >
            Продолжить →
          </button>
          <div className="recommended-step__time-estimate">
            ≈ {Math.max(1, Math.ceil((recommendedStep.progress.total_questions - recommendedStep.progress.answered_questions) / 4))} мин
          </div>
        </div>
      </div>
    </div>
  );
};