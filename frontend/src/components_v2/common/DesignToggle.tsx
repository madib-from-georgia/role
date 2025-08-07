import React, { useState, useEffect } from 'react';

const DESIGN_VERSION_KEY = 'checklist_design_version';

export const useDesignVersion = () => {
  const [isV2, setIsV2] = useState(() => {
    const saved = localStorage.getItem(DESIGN_VERSION_KEY);
    return saved === 'v2';
  });

  const toggleVersion = () => {
    const newVersion = !isV2;
    setIsV2(newVersion);
    localStorage.setItem(DESIGN_VERSION_KEY, newVersion ? 'v2' : 'v1');
  };

  return { isV2, toggleVersion };
};

export const DesignToggle: React.FC = () => {
  const { isV2, toggleVersion } = useDesignVersion();

  // Only show in development
  if (process.env.NODE_ENV === 'production') {
    return null;
  }

  return (
    <div className="design-toggle">
      <label className="design-toggle__label">
        <span>v2 Design</span>
        <div 
          className={`design-toggle__switch ${isV2 ? 'active' : ''}`}
          onClick={toggleVersion}
        >
          <div className="design-toggle__handle" />
        </div>
      </label>
    </div>
  );
};