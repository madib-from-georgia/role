import React from 'react';

interface QuestionNavigationProps {
  currentIndex: number;
  totalQuestions: number;
  onPrevious: () => void;
  onNext: () => void;
  canGoBack: boolean;
  canGoForward: boolean;
}

export const QuestionNavigation: React.FC<QuestionNavigationProps> = ({
  currentIndex,
  totalQuestions,
  onPrevious,
  onNext,
  canGoBack,
  canGoForward
}) => {
  // Keyboard shortcuts
  React.useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'ArrowLeft':
            event.preventDefault();
            if (canGoBack) onPrevious();
            break;
          case 'ArrowRight':
            event.preventDefault();
            if (canGoForward) onNext();
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [canGoBack, canGoForward, onPrevious, onNext]);

  return (
    <div className="question-navigation">
      <div className="navigation-content">
        {/* Previous button */}
        <button
          onClick={onPrevious}
          disabled={!canGoBack}
          className="nav-button nav-button--previous"
          title="Предыдущий вопрос (Ctrl+←)"
        >
          <span className="nav-icon">←</span>
          <span className="nav-text">Назад</span>
        </button>

        {/* Position indicator */}
        <div className="position-indicator">
          <div className="position-dots">
            {Array.from({ length: Math.min(totalQuestions, 7) }, (_, index) => {
              let dotIndex: number;
              
              if (totalQuestions <= 7) {
                dotIndex = index;
              } else {
                // Smart positioning for large question sets
                if (currentIndex <= 3) {
                  dotIndex = index;
                } else if (currentIndex >= totalQuestions - 3) {
                  dotIndex = totalQuestions - 7 + index;
                } else {
                  dotIndex = currentIndex - 3 + index;
                }
              }
              
              const isActive = dotIndex === currentIndex;
              const isPast = dotIndex < currentIndex;
              
              return (
                <div
                  key={`dot-${index}`}
                  className={`position-dot ${
                    isActive ? 'active' : isPast ? 'completed' : 'upcoming'
                  }`}
                  title={`Вопрос ${dotIndex + 1}`}
                />
              );
            })}
          </div>
          
          <div className="position-text">
            {currentIndex + 1} / {totalQuestions}
          </div>
        </div>

        {/* Next button */}
        <button
          onClick={onNext}
          disabled={!canGoForward}
          className="nav-button nav-button--next"
          title="Следующий вопрос (Ctrl+→)"
        >
          <span className="nav-text">
            {currentIndex === totalQuestions - 1 ? 'Завершить' : 'Далее'}
          </span>
          <span className="nav-icon">→</span>
        </button>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="keyboard-shortcuts">
        <div className="shortcut-hint">
          <span className="shortcut-key">Ctrl + ←/→</span>
          <span className="shortcut-description">Навигация по вопросам</span>
        </div>
      </div>

      {/* Progress indicators */}
      <div className="navigation-progress">
        <div className="progress-track">
          <div 
            className="progress-fill"
            style={{ width: `${((currentIndex + 1) / totalQuestions) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
};