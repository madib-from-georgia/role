import React from "react";
import { Button } from "@gravity-ui/uikit";

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
  canGoForward,
}) => {
  // Enhanced keyboard shortcuts
  React.useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Don't trigger shortcuts when user is typing in input fields
      const activeElement = document.activeElement;
      const isTyping =
        activeElement &&
        (activeElement.tagName === "INPUT" ||
          activeElement.tagName === "TEXTAREA" ||
          (activeElement as HTMLElement).contentEditable === "true");

      if (isTyping) return;

      // Ctrl/Cmd + Arrow keys for navigation
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case "ArrowLeft":
            event.preventDefault();
            if (canGoBack) onPrevious();
            break;
          case "ArrowRight":
            event.preventDefault();
            if (canGoForward) onNext();
            break;
        }
      }

      // Additional shortcuts without modifiers
      switch (event.key) {
        case "ArrowLeft":
          if (!isTyping && canGoBack) {
            event.preventDefault();
            onPrevious();
          }
          break;
        case "ArrowRight":
          if (!isTyping && canGoForward) {
            event.preventDefault();
            onNext();
          }
          break;
        case "Home":
          event.preventDefault();
          // Navigate to first question (will be implemented)
          break;
        case "End":
          event.preventDefault();
          // Navigate to last question (will be implemented)
          break;
        case "Escape":
          // Close sidebar or other modals (will be handled by parent)
          break;
      }
    };

    document.addEventListener("keydown", handleKeyPress);
    return () => document.removeEventListener("keydown", handleKeyPress);
  }, [canGoBack, canGoForward, onPrevious, onNext]);

  return (
    <div className="question-navigation">
      <div className="navigation-content">
        {/* Previous button */}
        <Button
          onClick={onPrevious}
          disabled={!canGoBack}
          view="raised"
          size="xl"
          title="Предыдущий вопрос (Ctrl+←)"
        >
          <span className="nav-icon">←</span>
          <span className="nav-text">Назад</span>
        </Button>

        {/* Position indicator */}
        <div className="position-indicator">
          <div className="position-text">
            {currentIndex + 1} / {totalQuestions}
          </div>
        </div>

        {/* Next button */}
        <Button
          onClick={onNext}
          disabled={!canGoForward}
          view="raised"
          size="xl"
          title="Следующий вопрос (Ctrl+→)"
        >
          <span className="nav-text">
            {currentIndex === totalQuestions - 1 ? "Завершить" : "Далее"}
          </span>
          <span className="nav-icon">→</span>
        </Button>
      </div>

      {/* Enhanced keyboard shortcuts hint */}
      <div className="keyboard-shortcuts">
        <div className="shortcut-hint">
          <span className="shortcut-key">←/→</span>
          <span className="shortcut-description">Навигация</span>
        </div>
        <div className="shortcut-hint">
          <span className="shortcut-key">Ctrl + ←/→</span>
          <span className="shortcut-description">Быстрая навигация</span>
        </div>
        <div className="shortcut-hint">
          <span className="shortcut-key">Home/End</span>
          <span className="shortcut-description">В начало/конец</span>
        </div>
        <div className="shortcut-hint">
          <span className="shortcut-key">Esc</span>
          <span className="shortcut-description">Закрыть панели</span>
        </div>
      </div>
    </div>
  );
};
