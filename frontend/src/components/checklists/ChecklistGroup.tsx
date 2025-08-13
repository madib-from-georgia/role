import React from "react";
import { useNavigate } from "react-router-dom";
import { Label } from "@gravity-ui/uikit";
import { ChecklistItem, ChecklistProgress } from "../../types/common";

interface ChecklistGroupProps {
  title: string;
  description: string;
  checklists: ChecklistItem[];
  progress: ChecklistProgress[];
  characterId: number;
  type: "basic" | "advanced" | "psychological";
}

export const ChecklistGroup: React.FC<ChecklistGroupProps> = ({
  title,
  description,
  checklists,
  progress,
  characterId,
  type,
}) => {
  const navigate = useNavigate();

  // TODO: Implement unlocking logic based on progress
  const isGroupUnlocked = () => {
    if (type === "basic") return true;
    if (type === "advanced") {
      // Require 70% completion of basic checklists
      return true; // Simplified for now
    }
    if (type === "psychological") {
      // Require completion of basic + 50% of advanced
      return true; // Simplified for now
    }
    return false;
  };

  const getGroupProgress = () => {
    if (!checklists.length) return 0;

    const groupProgress = checklists.map((checklist) => {
      const checklistProgress = progress?.find(
        (p) => p.checklist_id === checklist.id
      );
      return checklistProgress?.completion_percentage || 0;
    });

    return Math.round(
      groupProgress.reduce((sum, p) => sum + p, 0) / groupProgress.length
    );
  };

  const handleChecklistClick = (checklist: ChecklistItem) => {
    navigate(`/characters/${characterId}/checklists/${checklist.slug}`);
  };

  const unlocked = isGroupUnlocked();
  const groupProgress = getGroupProgress();

  return (
    <div
      className={`checklist-group ${
        !unlocked ? "checklist-group--locked" : ""
      }`}
    >
      <div className="checklist-group__header">
        <div className="checklist-group__title-row">
          <h3 className="checklist-group__title">{title}</h3>
          {!unlocked && <span className="checklist-group__lock">🔒</span>}
          <Label
            theme={
              groupProgress === 0
                ? "danger"
                : groupProgress >= 80
                ? "success"
                : "info"
            }
          >
            {groupProgress}%
          </Label>
        </div>
        <p className="checklist-group__description">{description}</p>

        {checklists.length > 0 && (
          <div className="checklist-group__progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${groupProgress}%` }}
            />
          </div>
        )}
      </div>

      {!unlocked && (
        <div className="checklist-group__unlock-requirements">
          <p>Для разблокировки этой группы:</p>
          <ul>
            {type === "advanced" && <li>Завершите 70% базового анализа</li>}
            {type === "psychological" && (
              <>
                <li>Завершите базовый анализ</li>
                <li>Завершите 50% углубленного анализа</li>
              </>
            )}
          </ul>
        </div>
      )}

      {unlocked && (
        <div className="checklist-group__items">
          {checklists.map((checklist) => {
            const checklistProgress = progress?.find(
              (p) => p.checklist_id === checklist.id
            );
            const completionPercentage =
              checklist?.completion_stats?.completion_percentage || 0;

            return (
              <div
                key={checklist.id}
                className="checklist-item"
                onClick={() => handleChecklistClick(checklist)}
              >
                <div className="checklist-item__icon">
                  {checklist.icon || "📝"}
                </div>

                <div className="checklist-item__content">
                  <h4 className="checklist-item__title">{checklist.title}</h4>
                  {checklist.description && (
                    <p className="checklist-item__description">
                      {checklist.description}
                    </p>
                  )}

                  {checklistProgress && (
                    <div className="checklist-item__progress">
                      <span className="progress-text">
                        {checklistProgress.answered_questions} из{" "}
                        {checklistProgress.total_questions} вопросов
                      </span>
                      <div className="progress-visual">
                        <div className="progress-bar small">
                          <div
                            className={`progress-fill ${
                              completionPercentage === 100
                                ? "completed"
                                : completionPercentage > 50
                                ? "in-progress"
                                : "started"
                            }`}
                            style={{ width: `${completionPercentage}%` }}
                          />
                        </div>
                        <span className="progress-percentage">
                          {completionPercentage}%
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                <div className="checklist-item__status">
                  {completionPercentage === 100 ? (
                    <span className="status-icon completed">✓</span>
                  ) : null}
                  <span className="status-text">Открыть →</span>
                </div>
              </div>
            );
          })}

          {checklists.length === 0 && (
            <div className="checklist-group__empty">
              <p>Чеклисты в этой группе еще не созданы</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
