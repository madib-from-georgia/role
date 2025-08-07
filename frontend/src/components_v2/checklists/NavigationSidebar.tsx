import React, { useState } from 'react';

interface NavigationSidebarProps {
  isOpen: boolean;
  questions: any[];
  currentIndex: number;
  onQuestionSelect: (index: number) => void;
  onClose: () => void;
}

export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({
  isOpen,
  questions,
  currentIndex,
  onQuestionSelect,
  onClose
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [bookmarkedQuestions, setBookmarkedQuestions] = useState<Set<number>>(new Set());
  const [filterMode, setFilterMode] = useState<'all' | 'unanswered' | 'bookmarked'>('all');

  // Group questions by section/subsection
  const groupedQuestions = React.useMemo(() => {
    const groups: { [key: string]: any[] } = {};
    
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
    let filtered: { [key: string]: any[] } = {};
    
    Object.entries(groupedQuestions).forEach(([groupKey, groupQuestions]) => {
      let matchingQuestions = groupQuestions;
      
      // Apply filter mode
      switch (filterMode) {
        case 'unanswered':
          matchingQuestions = matchingQuestions.filter(q => !q.current_response?.answer);
          break;
        case 'bookmarked':
          matchingQuestions = matchingQuestions.filter(q => bookmarkedQuestions.has(q.index));
          break;
        default:
          // 'all' - no additional filtering
          break;
      }
      
      // Apply search filter
      if (searchTerm) {
        matchingQuestions = matchingQuestions.filter(q => 
          q.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
          q.sectionTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
          q.subsectionTitle.toLowerCase().includes(searchTerm.toLowerCase())
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

  const getQuestionStatus = (question: any) => {
    if (question.current_response?.answer) {
      return 'answered';
    }
    return 'unanswered';
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

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="navigation-sidebar__backdrop" onClick={onClose} />
      
      {/* Sidebar */}
      <div className="navigation-sidebar">
        <div className="sidebar-header">
          <h3>Навигация по вопросам</h3>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        {/* Search */}
        <div className="sidebar-search">
          <input
            type="text"
            placeholder="Поиск вопросов..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button
              className="clear-search"
              onClick={() => setSearchTerm('')}
            >
              ×
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="sidebar-filters">
          <div className="filter-buttons">
            <button
              className={`filter-btn ${filterMode === 'all' ? 'active' : ''}`}
              onClick={() => setFilterMode('all')}
            >
              Все ({questions.length})
            </button>
            <button
              className={`filter-btn ${filterMode === 'unanswered' ? 'active' : ''}`}
              onClick={() => setFilterMode('unanswered')}
            >
              Неотвеченные ({questions.filter(q => !q.current_response?.answer).length})
            </button>
            <button
              className={`filter-btn ${filterMode === 'bookmarked' ? 'active' : ''}`}
              onClick={() => setFilterMode('bookmarked')}
            >
              ⭐ Закладки ({bookmarkedQuestions.size})
            </button>
          </div>
        </div>

        {/* Quick stats */}
        <div className="sidebar-stats">
          <div className="stat-item">
            <span className="stat-number">{questions.filter(q => q.current_response?.answer).length}</span>
            <span className="stat-label">отвечено</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{questions.length - questions.filter(q => q.current_response?.answer).length}</span>
            <span className="stat-label">осталось</span>
          </div>
        </div>

        {/* Question tree */}
        <div className="sidebar-content">
          {Object.entries(filteredGroups).map(([groupKey, groupQuestions]) => {
            const isExpanded = expandedSections.has(groupKey);
            const answeredInGroup = groupQuestions.filter(q => q.current_response?.answer).length;
            
            return (
              <div key={groupKey} className="question-group">
                <button
                  className="group-header"
                  onClick={() => toggleSection(groupKey)}
                >
                  <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▶</span>
                  <span className="group-title">{groupKey}</span>
                  <span className="group-progress">
                    {answeredInGroup}/{groupQuestions.length}
                  </span>
                </button>
                
                {isExpanded && (
                  <div className="group-questions">
                    {groupQuestions.map((question) => {
                      const status = getQuestionStatus(question);
                      const isActive = question.index === currentIndex;
                      
                      return (
                        <div
                          key={question.index}
                          className={`question-item-container ${isActive ? 'active' : ''}`}
                        >
                          <button
                            className={`question-item ${status}`}
                            onClick={() => onQuestionSelect(question.index)}
                          >
                            <div className="question-status">
                              {status === 'answered' ? '✓' : '○'}
                            </div>
                            <div className="question-text">
                              <span className="question-number">
                                {question.index + 1}.
                              </span>
                              <span className="question-content">
                                {question.text.length > 50 
                                  ? `${question.text.substring(0, 50)}...` 
                                  : question.text
                                }
                              </span>
                            </div>
                          </button>
                          <button
                            className={`bookmark-btn ${bookmarkedQuestions.has(question.index) ? 'bookmarked' : ''}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleBookmark(question.index);
                            }}
                            title={bookmarkedQuestions.has(question.index) ? 'Убрать из закладок' : 'Добавить в закладки'}
                          >
                            {bookmarkedQuestions.has(question.index) ? '⭐' : '☆'}
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
          <button 
            className="btn btn-sm"
            onClick={() => {
              const nextUnanswered = questions.findIndex((q, index) => 
                index > currentIndex && !q.current_response?.answer
              );
              if (nextUnanswered !== -1) {
                onQuestionSelect(nextUnanswered);
              }
            }}
          >
            ➡️ Следующий неотвеченный
          </button>
          
          {bookmarkedQuestions.size > 0 && (
            <button 
              className="btn btn-sm btn-highlight"
              onClick={() => {
                const nextBookmark = questions.findIndex((_, index) => 
                  index > currentIndex && bookmarkedQuestions.has(index)
                );
                if (nextBookmark !== -1) {
                  onQuestionSelect(nextBookmark);
                } else {
                  // If no bookmarks after current, go to first bookmark
                  const firstBookmark = Math.min(...Array.from(bookmarkedQuestions));
                  onQuestionSelect(firstBookmark);
                }
              }}
            >
              ⭐ Следующая закладка
            </button>
          )}
          
          <button 
            className="btn btn-sm btn-secondary"
            onClick={() => {
              // Expand all sections for easier navigation
              setExpandedSections(new Set(Object.keys(groupedQuestions)));
            }}
          >
            📂 Развернуть все
          </button>
        </div>
      </div>
    </>
  );
};
