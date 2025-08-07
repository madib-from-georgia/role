import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';

import { QuestionFlow } from '../components_v2/checklists/QuestionFlow';
import { charactersApi } from '../services/api';

// Import v2 styles
import '../styles_v2/index.css';

interface Character {
  id: number;
  name: string;
  description?: string;
  importance_score?: number;
  text_id: number;
}

const CharacterChecklistDetailV2: React.FC = () => {
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
        <div className="error-content">
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
        <div className="loading-content">
          <div className="spinner large"></div>
          <span className="loading-text">Загрузка данных персонажа...</span>
        </div>
      </div>
    );
  }

  return (
    <QuestionFlow 
      checklistSlug={checklistSlug}
      characterId={parseInt(characterId)}
    />
  );
};

export default CharacterChecklistDetailV2;