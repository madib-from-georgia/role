import React, { useState, useEffect } from "react";
import { Button, TextInput, Progress, Label, ArrowToggle } from "@gravity-ui/uikit";
import { ChecklistQuestion } from "../../types/checklist";

interface QuestionWithIndex extends ChecklistQuestion {
  index: number;
}

interface NavigationSidebarProps {
  isOpen: boolean;
  questions: ChecklistQuestion[];
  currentIndex: number;
  completionPercentage: number;
  onQuestionSelect: (index: number) => void;
  onClose: () => void;
}

export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({
  isOpen,
  questions,
  currentIndex,
  completionPercentage,
  onQuestionSelect,
  onClose,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set()
  );
  const [bookmarkedQuestions, setBookmarkedQuestions] = useState<Set<number>>(
    new Set()
  );
  const [filterMode, setFilterMode] = useState<
    "all" | "unanswered" | "bookmarked"
  >("all");

  // Group questions by section/subsection
  const groupedQuestions = React.useMemo(() => {
    const groups: { [key: string]: QuestionWithIndex[] } = {};

    questions.forEach((question, index) => {
      const groupKey = `${question.sectionTitle} → ${question.subsectionTitle}`;
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push({ ...question, index });
    });

    return groups;
  }, [questions]);

  // Filter questions based on search and filter mode
  const filteredGroups = React.useMemo(() => {
    const filtered: { [key: string]: QuestionWithIndex[] } = {};

    Object.entries(groupedQuestions).forEach(([groupKey, groupQuestions]) => {
      let matchingQuestions = groupQuestions;

      // Apply filter mode
      switch (filterMode) {
        case "unanswered":
          matchingQuestions = matchingQuestions.filter(
            (q) => !q.current_response?.answer
          );
          break;
        case "bookmarked":
          matchingQuestions = matchingQuestions.filter((q) =>
            bookmarkedQuestions.has(q.index)
          );
          break;
        default:
          // 'all' - no additional filtering
          break;
      }

      // Apply search filter
      if (searchTerm) {
        matchingQuestions = matchingQuestions.filter(
          (q) =>
            q.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (q.sectionTitle && q.sectionTitle.toLowerCase().includes(searchTerm.toLowerCase())) ||
            (q.subsectionTitle && q.subsectionTitle.toLowerCase().includes(searchTerm.toLowerCase()))
        );
      }

      if (matchingQuestions.length > 0) {
        filtered[groupKey] = matchingQuestions;
      }
    });

    return filtered;
  }, [groupedQuestions, searchTerm, filterMode, bookmarkedQuestions]);

  const toggleSection = (sectionKey: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionKey)) {
      newExpanded.delete(sectionKey);
    } else {
      newExpanded.add(sectionKey);
    }
    setExpandedSections(newExpanded);
  };

  const getQuestionStatus = (question: QuestionWithIndex) => {
    if (question.current_response?.answer) {
      return "answered";
    }
    return "unanswered";
  };

  const toggleBookmark = (questionIndex: number) => {
    const newBookmarks = new Set(bookmarkedQuestions);
    if (newBookmarks.has(questionIndex)) {
      newBookmarks.delete(questionIndex);
    } else {
      newBookmarks.add(questionIndex);
    }
    setBookmarkedQuestions(newBookmarks);
  };

  const answeredQuestions = questions.filter(
    (q) => q.current_response?.answer
  ).length;

  // Handle Esc key
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
        // Remove focus from the button to avoid outline
        (document.activeElement as HTMLElement)?.blur();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscKey);
    }

    return () => {
      document.removeEventListener('keydown', handleEscKey);
    };
  }, [isOpen, onClose]);

  return (
    <div className={`navigation-sidebar-wrapper ${isOpen ? "open" : "closed"}`} onClick={onClose}>
      {/* Sidebar */}
      <div className="navigation-sidebar" onClick={(e) => e.stopPropagation()}>
        <div className="sidebar-header">
          <h3>Навигация по вопросам</h3>
          <Button onClick={onClose} view="normal" size="l">
            ×
          </Button>
        </div>

        {/* Search */}
        <div className="sidebar-search">
          <TextInput
            value={searchTerm}
            onUpdate={(value) => setSearchTerm(value)}
            placeholder="Поиск вопросов..."
          />
          {searchTerm && (
            <Button
              onClick={() => setSearchTerm("")}
              view="flat"
              size="s"
              className="clear-search"
            >
              ×
            </Button>
          )}
        </div>

        {/* Filters */}
        <div className="sidebar-filters">
          <div className="filter-buttons">
            <Button
              onClick={() => setFilterMode("all")}
              view={filterMode === "all" ? "action" : "outlined"}
              size="s"
            >
              Все ({questions.length})
            </Button>
            <Button
              onClick={() => setFilterMode("unanswered")}
              view={filterMode === "unanswered" ? "action" : "outlined"}
              size="s"
            >
              Неотвеченные (
              {questions.filter((q) => !q.current_response?.answer).length})
            </Button>
            <Button
              onClick={() => setFilterMode("bookmarked")}
              view={filterMode === "bookmarked" ? "action" : "outlined"}
              size="s"
            >
              ⭐ Закладки ({bookmarkedQuestions.size})
            </Button>
          </div>
        </div>

        {/* Quick stats */}
        <div className="sidebar-stats">
          <Progress
            value={completionPercentage}
            theme="success"
            text={`${answeredQuestions} из ${questions.length}`}
          />
        </div>

        {/* Question tree */}
        <div className="sidebar-content">
          {Object.entries(filteredGroups).map(([groupKey, groupQuestions]) => {
            const isExpanded = expandedSections.has(groupKey);
            const answeredInGroup = groupQuestions.filter(
              (q) => q.current_response?.answer
            ).length;

            return (
              <div key={groupKey} className="question-group">
                <div
                  className="group-header"
                  onClick={() => toggleSection(groupKey)}
                >
                  <ArrowToggle direction={isExpanded ? "bottom" : "right"} /> 

                  <span className="group-title">{groupKey}</span>
                  <Label
                    theme={
                      answeredInGroup === 0
                        ? "danger"
                        : answeredInGroup === groupQuestions.length
                        ? "success"
                        : "info"
                    }
                  >
                    {answeredInGroup}/{groupQuestions.length}
                  </Label>
                </div>

                {isExpanded && (
                  <div className="group-questions">
                    {groupQuestions.map((question) => {
                      const status = getQuestionStatus(question);
                      const isActive = question.index === currentIndex;

                      return (
                        <div
                          key={question.index}
                          className={`question-item-container ${
                            isActive ? "active" : ""
                          }`}
                        >
                          <div
                            className={`question-item ${status}`}
                            onClick={() => onQuestionSelect(question.index)}
                          >
                            <div className="question-status">
                              {status === "answered" ? "✓" : "○"}
                            </div>
                            <div className="question-text">
                              <span className="question-number">
                                {question.index + 1}.
                              </span>
                              <span className="question-content">
                                {question.text.length > 50
                                  ? `${question.text.substring(0, 50)}...`
                                  : question.text}
                              </span>
                            </div>
                          </div>
                          <button
                            className={`bookmark-btn ${
                              bookmarkedQuestions.has(question.index)
                                ? "bookmarked"
                                : ""
                            }`}
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleBookmark(question.index);
                            }}
                            title={
                              bookmarkedQuestions.has(question.index)
                                ? "Убрать из закладок"
                                : "Добавить в закладки"
                            }
                          >
                            {bookmarkedQuestions.has(question.index)
                              ? "⭐"
                              : "☆"}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}

          {Object.keys(filteredGroups).length === 0 && searchTerm && (
            <div className="no-results">
              <p>Ничего не найдено по запросу "{searchTerm}"</p>
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="sidebar-actions">
          <Button
            onClick={() => {
              const nextUnanswered = questions.findIndex(
                (q, index) =>
                  index > currentIndex && !q.current_response?.answer
              );
              if (nextUnanswered !== -1) {
                onQuestionSelect(nextUnanswered);
              }
            }}
            view="action"
            size="l"
          >
            ➡️ Следующий неотвеченный
          </Button>

          {bookmarkedQuestions.size > 0 && (
            <Button
              onClick={() => {
                const nextBookmark = questions.findIndex(
                  (_, index) =>
                    index > currentIndex && bookmarkedQuestions.has(index)
                );
                if (nextBookmark !== -1) {
                  onQuestionSelect(nextBookmark);
                } else {
                  // If no bookmarks after current, go to first bookmark
                  const firstBookmark = Math.min(
                    ...Array.from(bookmarkedQuestions)
                  );
                  onQuestionSelect(firstBookmark);
                }
              }}
              view="normal"
              size="l"
            >
              ⭐ Следующая закладка
            </Button>
          )}

          <Button
            onClick={() => {
              // Expand all sections for easier navigation
              setExpandedSections(new Set(Object.keys(groupedQuestions)));
            }}
            view="normal"
            size="l"
          >
            📂 Развернуть все
          </Button>
        </div>
      </div>
    </div>
  );
};
