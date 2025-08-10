import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "react-query";
import { checklistApi } from "../../services/api";
import { Button, ArrowToggle } from "@gravity-ui/uikit";

interface ChecklistSwitcherProps {
  characterId: number;
  currentChecklist?: string | null;
}

export const ChecklistSwitcher: React.FC<ChecklistSwitcherProps> = ({
  characterId,
  currentChecklist,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const { data: checklists } = useQuery({
    queryKey: ["checklists", characterId],
    queryFn: () => checklistApi.getAll(characterId),
    staleTime: 10 * 60 * 1000, // 10 минут
  });

  const { data: progress } = useQuery({
    queryKey: ["checklist-progress", characterId],
    queryFn: () => checklistApi.getCharacterProgress(characterId),
    staleTime: 2 * 60 * 1000, // 2 минуты
  });

  const handleChecklistSelect = (checklistSlug: string) => {
    if (checklistSlug === "overview") {
      navigate(`/characters/${characterId}/checklists`);
    } else {
      navigate(`/characters/${characterId}/checklists/${checklistSlug}`);
    }
    setIsOpen(false);
  };

  const getChecklistProgress = (checklistId: number) => {
    const checklistProgress = progress?.find(
      (p: any) => p.checklist_id === checklistId
    );
    return checklistProgress?.completion_percentage || 0;
  };

  // Если нет чеклистов, не рендерим компонент
  if (!checklists) {
    return null;
  }

  return (
    <div className="checklist-switcher">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        title={currentChecklist ? "Переключить чеклист" : "Список чеклистов"}
        view="normal"
        size="m"
      >
        Чеклисты
      </Button>

      {/* Full-screen sidebar */}
      <div className={`checklist-switcher-wrapper ${isOpen ? "open" : "closed"}`}>
        {/* Backdrop */}
        <div className="checklist-switcher__backdrop" onClick={() => setIsOpen(false)} />

        {/* Sidebar */}
        <div className="checklist-switcher-sidebar">
          <div className="switcher-sidebar-header">
            <h3>Чеклисты</h3>
            <Button onClick={() => setIsOpen(false)} view="normal" size="l">
              ×
            </Button>
          </div>

          <div className="switcher-sidebar-content">
            {/* Overview option */}
            <div
              className={`switcher-item ${!currentChecklist ? "active" : ""}`}
              onClick={() => handleChecklistSelect("overview")}
            >
              <div className="switcher-item__icon">🏠</div>
              <div className="switcher-item__content">
                <div className="switcher-item__title">Все чеклисты</div>
                <div className="switcher-item__subtitle">
                  Стартовая страница
                </div>
              </div>
            </div>

            <div className="switcher-divider"></div>

            {/* Checklist options */}
            {checklists.map((checklist: any) => {
              const completionPercentage = getChecklistProgress(checklist.id);
              const isActive = currentChecklist === checklist.slug;

              return (
                <div
                  key={checklist.id}
                  className={`switcher-item ${isActive ? "active" : ""}`}
                  onClick={() => handleChecklistSelect(checklist.slug)}
                >
                  <div className="switcher-item__icon">
                    {checklist.icon || "📝"}
                  </div>

                  <div className="switcher-item__content">
                    <div className="switcher-item__title">
                      {checklist.title}
                    </div>
                    <div className="switcher-item__progress">
                      <div className="mini-progress-bar">
                        <div
                          className="mini-progress-fill"
                          style={{ width: `${completionPercentage}%` }}
                        />
                      </div>
                      <span className="progress-text">
                        {completionPercentage}%
                      </span>
                    </div>
                  </div>

                  <div className="switcher-item__status">
                    {completionPercentage === 100 ? (
                      <span className="status-icon completed">✓</span>
                    ) : completionPercentage > 0 ? (
                      <span className="status-icon in-progress">⏱</span>
                    ) : (
                      <span className="status-icon not-started">○</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick actions */}
          <div className="switcher-sidebar-actions">
            <Button
              onClick={() => setIsOpen(false)}
              view="action"
              size="l"
            >
              Закрыть
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
