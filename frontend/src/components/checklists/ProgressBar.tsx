import React from "react";
import { Progress, Text } from "@gravity-ui/uikit";
import { ChecklistItem } from "../../types/common";

interface ProgressBarProps {
  currentIndex: number;
  totalQuestions: number;
  checklist: ChecklistItem;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ checklist }) => {
  const completionPercentage =
    checklist?.completion_stats?.completion_percentage || 0;

  return (
    <div className="progress-bar-container">
      <div className="progress-header-compact">
        <Text variant="header-1">
          {checklist?.icon && (
            <span className="checklist-icon">{checklist.icon}</span>
          )}
          {checklist?.title}
        </Text>

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
