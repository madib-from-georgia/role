import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';

import { ChecklistView } from '../components/ChecklistView';
import { charactersApi } from '../services/api';

interface Character {
  id: number;
  name: string;
  description?: string;
  importance_score?: number;
  text_id: number;
}

const CharacterChecklistDetail: React.FC = () => {
  const { characterId, checklistSlug } = useParams<{ 
    characterId: string; 
    checklistSlug: string 
  }>();
  const navigate = useNavigate();

  // Загружаем данные персонажа
  const { data: character, isLoading: characterLoading } = useQuery({
    queryKey: ['character', characterId],
    queryFn: () => charactersApi.getById(characterId!),
    enabled: !!characterId
  });

  if (!characterId || !checklistSlug || isNaN(parseInt(characterId))) {
    return (
      <div className="page-error">
        <div className="error-content centered">
          <h1 className="error-title">Неверные параметры</h1>
          <p className="error-message">
            Неверный ID персонажа или slug чеклиста
          </p>
          <button
            onClick={() => navigate('/')}
            className="btn btn-primary"
          >
            Вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  if (characterLoading) {
    return (
      <div className="page-loading">
        <div className="loading-content centered">
          <div className="spinner"></div>
          <span className="loading-text">Загрузка данных персонажа...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="checklist-page">
      <div className="page-header">
        <div className="container">
          <div className="header-nav">
            <button
              onClick={() => navigate(`/characters/${characterId}/checklists`)}
              className="btn btn-secondary"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Назад к списку чеклистов
            </button>
            
            <div className="header-title centered">
              <h1>{character?.name}</h1>
            </div>
            
            <div className="header-spacer"></div>
          </div>
        </div>
      </div>
      
      <ChecklistView 
        checklistSlug={checklistSlug}
        characterId={parseInt(characterId)}
      />
    </div>
  );
};

export default CharacterChecklistDetail; 