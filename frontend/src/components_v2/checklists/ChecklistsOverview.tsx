import React from 'react';
import { useQuery } from 'react-query';
import { useParams, useNavigate } from 'react-router-dom';

import { checklistApi, charactersApi } from '../../services/api';
// import { RecommendedNextStep } from './RecommendedNextStep';
// import { ChecklistGroup } from './ChecklistGroup';
// import { OverallProgress } from './OverallProgress';
// import { ChecklistSwitcher } from './ChecklistSwitcher';

interface ChecklistsOverviewProps {}

export const ChecklistsOverview: React.FC<ChecklistsOverviewProps> = () => {
  const { characterId } = useParams<{ characterId: string }>();
  const navigate = useNavigate();

  // Загружаем данные персонажа
  const { data: character, isLoading: characterLoading } = useQuery({
    queryKey: ['character', characterId],
    queryFn: () => charactersApi.getById(characterId!),
    enabled: !!characterId
  });

  // Загружаем список доступных чеклистов
  const { data: checklists, isLoading: checklistsLoading } = useQuery({
    queryKey: ['checklists'],
    queryFn: () => checklistApi.getAll(),
    staleTime: 10 * 60 * 1000, // 10 минут
  });

  // Загружаем прогресс по чеклистам для персонажа
  const { data: progress } = useQuery({
    queryKey: ['checklist-progress', characterId],
    queryFn: () => checklistApi.getCharacterProgress(parseInt(characterId!)),
    enabled: !!characterId,
    staleTime: 2 * 60 * 1000, // 2 минуты
  });

  if (!characterId || isNaN(parseInt(characterId))) {
    return (
      <div className="checklists-overview__error">
        <div className="error-content">
          <h1>Неверный ID персонажа</h1>
          <button onClick={() => navigate('/')} className="btn btn-primary">
            Вернуться на главную
          </button>
        </div>
      </div>
    );
  }

  if (characterLoading || checklistsLoading) {
    return (
      <div className="checklists-overview__loading">
        <div className="loading-content">
          <div className="spinner"></div>
          <span>Загрузка данных персонажа...</span>
        </div>
      </div>
    );
  }

  // TODO: Implement checklist grouping logic
  const groupedChecklists = {
    basic: [],
    advanced: [],
    psychological: []
  };

  return (
    <div className="checklists-overview">
      {/* Header */}
      <div className="checklists-overview__header">
        <button
          onClick={() => navigate(-1)}
          className="btn btn-secondary"
        >
          ← Назад
        </button>
        
        <div className="character-info">
          <h1>{character?.name}</h1>
          {character?.description && <p>{character.description}</p>}
        </div>
      </div>

      {/* Main Content */}
      <div className="checklists-overview__content">
        
        {/* Temporary content - will be replaced with components */}
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>🎨 New Design v2 is Loading...</h2>
          <p>Базовая структура создана. Компоненты будут добавлены по очереди.</p>
          
          <div style={{ marginTop: '2rem', padding: '1rem', background: '#f3f4f6', borderRadius: '0.5rem' }}>
            <h3>Планируемые компоненты:</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              <li>📊 OverallProgress - общий прогресс</li>
              <li>🎯 RecommendedNextStep - рекомендуемый шаг</li>
              <li>📋 ChecklistGroup - группы чеклистов</li>
              <li>🔄 ChecklistSwitcher - переключатель чеклистов</li>
            </ul>
          </div>
          
          {character && (
            <div style={{ marginTop: '2rem', padding: '1rem', background: '#dbeafe', borderRadius: '0.5rem' }}>
              <h4>Данные персонажа загружены:</h4>
              <p><strong>{character.name}</strong></p>
              {character.description && <p>{character.description}</p>}
            </div>
          )}
          
          {checklists && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: '#d1fae5', borderRadius: '0.5rem' }}>
              <h4>Доступно чеклистов: {checklists.length}</h4>
            </div>
          )}
          
          {progress && (
            <div style={{ marginTop: '1rem', padding: '1rem', background: '#fef3c7', borderRadius: '0.5rem' }}>
              <h4>Прогресс данные загружены: {progress.length} записей</h4>
            </div>
          )}
        </div>

        {/* Components will be uncommented as they're implemented
        <OverallProgress 
          progress={progress}
          character={character}
        />

        <RecommendedNextStep 
          progress={progress}
          checklists={checklists}
          characterId={parseInt(characterId)}
        />

        <div className="checklist-groups">
          <ChecklistGroup
            title="Базовый анализ"
            description="Фундаментальные аспекты персонажа"
            checklists={groupedChecklists.basic}
            progress={progress}
            characterId={parseInt(characterId)}
            type="basic"
          />
          
          <ChecklistGroup
            title="Углубленный анализ"
            description="Детальное изучение характера"
            checklists={groupedChecklists.advanced}
            progress={progress}
            characterId={parseInt(characterId)}
            type="advanced"
          />
          
          <ChecklistGroup
            title="Психологический анализ"
            description="Глубинные психологические аспекты"
            checklists={groupedChecklists.psychological}
            progress={progress}
            characterId={parseInt(characterId)}
            type="psychological"
          />
        </div>

        <ChecklistSwitcher 
          characterId={parseInt(characterId)}
          currentChecklist={null}
        />
        */}
      </div>
    </div>
  );
};
