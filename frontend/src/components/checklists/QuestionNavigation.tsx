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
  // Refs for touch handling
  const nextButtonRef = React.useRef<HTMLButtonElement>(null);
  const prevButtonRef = React.useRef<HTMLButtonElement>(null);

  // Touch event handlers to prevent double-tap issues on mobile
  const handleTouchStart = React.useCallback((callback: () => void) => {
    return (event: React.TouchEvent) => {
      event.preventDefault();
      callback();
    };
  }, []);

  // Click handlers with touch prevention
  const handleNextClick = React.useCallback((event: React.MouseEvent) => {
    // Prevent click if it was triggered by touch
    if (event.detail === 0) return;
    onNext();
  }, [onNext]);

  const handlePrevClick = React.useCallback((event: React.MouseEvent) => {
    // Prevent click if it was triggered by touch
    if (event.detail === 0) return;
    onPrevious();
  }, [onPrevious]);
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
          ref={prevButtonRef}
          onClick={handlePrevClick}
          onTouchStart={canGoBack ? handleTouchStart(onPrevious) : undefined}
          disabled={!canGoBack}
          view="action"
          size="xl"
          title="Предыдущий вопрос (Ctrl+←)"
          className="navigation-content__button"
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
          ref={nextButtonRef}
          onClick={handleNextClick}
          onTouchStart={canGoForward ? handleTouchStart(onNext) : undefined}
          disabled={!canGoForward}
          view="action"
          size="xl"
          title="Следующий вопрос (Ctrl+→)"
          className="navigation-content__button"
        >
          <span className="nav-text">
            {currentIndex === totalQuestions - 1 ? "Завершить" : "Вперёд"}
          </span>
          <span className="nav-icon">→</span>
        </Button>
      </div>
    </div>
  );
};
