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
    
    // Если нет прогресса вообще, рекомендуем первый чеклист
    if (progress.length === 0) {
      const firstChecklist = checklists.find(c => c.slug === 'physical') || checklists[0];
      if (!firstChecklist) return null;
      
      return {
        type: 'start',
        checklist: firstChecklist,
        progress: null,
        reason: "Начните анализ персонажа с базового чеклиста"
      };
    }
    
    // Ищем незавершенные чеклисты
    const incompleteChecklists = progress.filter(p => p.completion_percentage < 100);
    
    // Если все завершены
    if (incompleteChecklists.length === 0) {
      return {
        type: 'completed',
        checklist: null,
        progress: null,
        reason: "Все чеклисты заполнены"
      };
    }
    
    // Есть незавершенные - рекомендуем первый
    const firstIncomplete = incompleteChecklists[0];
    const checklist = checklists.find(c => c.id === firstIncomplete.checklist_id);
    
    // Если чеклист не найден, возвращаем null
    if (!checklist) return null;
    
    return {
      type: 'continue',
      checklist,
      progress: firstIncomplete,
      reason: "Продолжить с места последней работы"
    };
  };

  const recommendedStep = getRecommendedStep();

  if (!recommendedStep) {
    return null; // Не показываем компонент если нет данных
  }

  // Если все завершено
  if (recommendedStep.type === 'completed') {
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
    if (recommendedStep.checklist?.slug) {
      navigate(`/characters/${characterId}/checklists/${recommendedStep.checklist.slug}`);
    }
  };

  // Определяем заголовок и текст кнопки в зависимости от типа
  const headerText = recommendedStep.type === 'start' ? 'Начните анализ персонажа' : 'Рекомендуемый следующий шаг';
  const buttonText = recommendedStep.type === 'start' ? 'Начать анализ →' : 'Продолжить →';

  return (
    <div className="recommended-step">
      <div className="recommended-step__header">
        <h2>{headerText}</h2>
        <span className="recommended-step__badge">Smart AI</span>
      </div>
      
      <div className="recommended-step__content">
        <div className="recommended-step__info">
          <div className="recommended-step__icon">
            {recommendedStep.checklist?.icon || '📝'}
          </div>
          
          <div className="recommended-step__text">
            <h3>{recommendedStep.checklist?.title || 'Неизвестный чеклист'}</h3>
            <p className="recommended-step__reason">
              {recommendedStep.reason}
            </p>
            
            {/* Показываем прогресс только если есть данные */}
            {recommendedStep.progress && (
              <div className="recommended-step__progress">
                Прогресс: {recommendedStep.progress.completion_percentage || 0}%
                ({recommendedStep.progress.answered_questions || 0} из {recommendedStep.progress.total_questions || 0} вопросов)
              </div>
            )}
          </div>
        </div>
        
        <div className="recommended-step__actions">
          <button 
            onClick={handleStartStep}
            className="btn btn-primary btn-large"
          >
            {buttonText}
          </button>
          
          {/* Показываем оценку времени только если есть прогресс */}
          {recommendedStep.progress && (
            <div className="recommended-step__time-estimate">
              ≈ {Math.max(1, Math.ceil(((recommendedStep.progress.total_questions || 0) - (recommendedStep.progress.answered_questions || 0)) / 4))} мин
            </div>
          )}
          
          {/* Для нового пользователя показываем другую информацию */}
          {recommendedStep.type === 'start' && (
            <div className="recommended-step__time-estimate">
              ≈ 10-15 мин на чеклист
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
