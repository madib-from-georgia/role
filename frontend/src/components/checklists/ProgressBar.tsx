import React from "react";
import { Progress, Text, Button } from "@gravity-ui/uikit";
import { ChecklistItem } from "../../types/common";

interface ProgressBarProps {
  checklist: ChecklistItem;
  onChecklistClick: (isOpen: boolean) => void;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  checklist,
  onChecklistClick,
}) => {
  const completionPercentage =
    checklist?.completion_stats?.completion_percentage || 0;

  return (
    <div className="progress-bar-container">
      <div className="progress-header-compact">
        <div className="progress-header-title">
          <Button
            onClick={() => onChecklistClick(true)}
            title="Навигация по вопросам"
            view="outlined"
            size="m"
          >
            ☰
          </Button>

          <Text variant="header-1" className="progress-header-title-text">
            {checklist?.icon && (
              <span className="checklist-icon">{checklist.icon}</span>
            )}
            {checklist?.title}
          </Text>
        </div>

        {/* Two columns below */}
        <div className="progress-bar-compact">
          <Progress
            value={completionPercentage}
            text={`${completionPercentage}%`}
            theme="success"
          />
        </div>
      </div>
    </div>
  );
};
