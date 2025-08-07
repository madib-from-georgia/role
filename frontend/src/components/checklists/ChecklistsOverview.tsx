import React from 'react';
import { useQuery } from 'react-query';
import { useParams, useNavigate } from 'react-router-dom';

import { checklistApi, charactersApi } from '../../services/api';
import { RecommendedNextStep } from './RecommendedNextStep';
import { ChecklistGroup } from './ChecklistGroup';
import { OverallProgress } from './OverallProgress';
import { ChecklistSwitcher } from './ChecklistSwitcher';

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

  // Группировка чеклистов по типам (всегда должна быть после всех хуков)
  const groupedChecklists = React.useMemo(() => {
    if (!checklists) {
      return { basic: [], advanced: [], psychological: [] };
    }

    const basic: any[] = [];
    const advanced: any[] = [];
    const psychological: any[] = [];

    checklists.forEach((checklist: any) => {
      const slug = checklist.slug.toLowerCase();
      
      // Базовый анализ
      if (slug.includes('physical') || slug.includes('emotional') || slug.includes('speech')) {
        basic.push(checklist);
      }
      // Углубленный анализ  
      else if (slug.includes('internal') || slug.includes('motivation') || slug.includes('relationships') || 
               slug.includes('biography') || slug.includes('social') || slug.includes('scenes') || 
               slug.includes('tasks') || slug.includes('exercises')) {
        advanced.push(checklist);
      }
      // Психологический анализ
      else if (slug.includes('subtext') || slug.includes('tempo') || slug.includes('personality') || 
               slug.includes('defense') || slug.includes('trauma') || slug.includes('archetypes') || 
               slug.includes('emotional-intelligence') || slug.includes('cognitive') || slug.includes('attachment')) {
        psychological.push(checklist);
      }
      // Все остальные в базовый
      else {
        basic.push(checklist);
      }
    });

    return { basic, advanced, psychological };
  }, [checklists]);

  // Проверки на ошибки и загрузку после всех хуков
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
        
        {/* Overall Progress */}
        <OverallProgress 
          progress={progress}
          character={character}
        />

        {/* Recommended Next Step */}
        <RecommendedNextStep 
          progress={progress}
          checklists={checklists}
          characterId={parseInt(characterId)}
        />

        {/* Checklist Groups */}
        <div className="checklist-groups">
          <ChecklistGroup
            title="Базовый анализ"
            description="Фундаментальные аспекты персонажа: внешность, эмоции, речь"
            checklists={groupedChecklists.basic}
            progress={progress}
            characterId={parseInt(characterId)}
            type="basic"
          />
          
          <ChecklistGroup
            title="Углубленный анализ"
            description="Детальное изучение характера: мотивация, отношения, биография"
            checklists={groupedChecklists.advanced}
            progress={progress}
            characterId={parseInt(characterId)}
            type="advanced"
          />
          
          <ChecklistGroup
            title="Психологический анализ"
            description="Глубинные психологические аспекты: подтекст, защиты, травмы"
            checklists={groupedChecklists.psychological}
            progress={progress}
            characterId={parseInt(characterId)}
            type="psychological"
          />
        </div>

        {/* Quick Checklist Switcher */}
        <ChecklistSwitcher 
          characterId={parseInt(characterId)}
          currentChecklist={null}
        />

      </div>
    </div>
  );
};
