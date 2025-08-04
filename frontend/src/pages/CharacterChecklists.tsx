import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';

import { ChecklistView } from '../components/ChecklistView';
import { checklistApi, charactersApi } from '../services/api';

interface Character {
  id: number;
  name: string;
  description?: string;
  importance_score?: number;
  text_id: number;
}

interface ChecklistItem {
  id: number;
  title: string;
  slug: string;
  icon?: string;
  description?: string;
}

const CharacterChecklists: React.FC = () => {
  const { characterId } = useParams<{ characterId: string }>();
  const navigate = useNavigate();
  const [selectedChecklistSlug, setSelectedChecklistSlug] = useState<string | null>(null);

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
      <div className="page-error">
        <div className="error-content centered">
          <h1 className="error-title">Неверный ID персонажа</h1>
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

  if (characterLoading || checklistsLoading) {
    return (
      <div className="page-loading">
        <div className="loading-content centered">
          <div className="spinner"></div>
          <span className="loading-text">Загрузка данных персонажа...</span>
        </div>
      </div>
    );
  }

  // Если выбран конкретный чеклист, показываем его
  if (selectedChecklistSlug) {
    return (
      <div className="checklist-page">
        <div className="page-header">
          <div className="container">
            <div className="header-nav">
              <button
                onClick={() => setSelectedChecklistSlug(null)}
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
          checklistSlug={selectedChecklistSlug}
          characterId={parseInt(characterId)}
        />
      </div>
    );
  }

  // Показываем список чеклистов
  return (
    <div className="checklists-page">
      {/* Заголовок */}
      <div className="page-header">
        <div className="container">
          <div className="header-nav">
            <button
              onClick={() => navigate(-1)}
              className="btn btn-secondary"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Назад
            </button>
            
            <h1 className="page-title">Чеклисты для анализа персонажа</h1>
            
            <div className="header-spacer"></div>
          </div>
        </div>
      </div>

      <div className="container">
        <div className="checklists-content">
          {/* Информация о персонаже */}
          {character && (
            <div className="character-info">
              <div className="character-header">
                <div className="character-icon">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="character-details">
                  <h2 className="character-name">{character.name}</h2>
                  {character.description && (
                    <p className="character-description">{character.description}</p>
                  )}
                  <div className="character-meta">
                    {character.importance_score && (
                      <div className="importance-score">
                        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span>Важность: {Math.round(character.importance_score * 100)}%</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Общая статистика прогресса */}
          {progress && (
            <div className="progress-overview">
              <h3 className="section-title">Общий прогресс</h3>
              <div className="progress-grid">
                {progress.map((stat: any, index: number) => (
                  <div key={index} className="progress-card">
                    <div className="progress-percentage">
                      {stat.completion_percentage}%
                    </div>
                    <div className="progress-details">
                      {stat.answered_questions} из {stat.total_questions} вопросов
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Список чеклистов */}
          <div className="checklists-section">
            <h3 className="section-title">Доступные чеклисты</h3>
            
            <div className="checklists-list">
              {checklists?.map((checklist: ChecklistItem) => {
                const checklistProgress = progress?.find((p: any) => p.checklist_id === checklist.id);
                const completionPercentage = checklistProgress?.completion_percentage || 0;
                
                return (
                  <div
                    key={checklist.id}
                    className="checklist-card"
                    onClick={() => setSelectedChecklistSlug(checklist.slug)}
                  >
                    <div className="checklist-card-content">
                      <div className="checklist-info">
                        <div className="checklist-icon-container">
                          {checklist.icon ? (
                            <span className="checklist-emoji">{checklist.icon}</span>
                          ) : (
                            <div className="checklist-default-icon">
                              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                            </div>
                          )}
                        </div>
                        
                        <div className="checklist-details">
                          <h4 className="checklist-title">{checklist.title}</h4>
                          {checklist.description && (
                            <p className="checklist-description">{checklist.description}</p>
                          )}
                          
                          {/* Прогресс */}
                          {checklistProgress && (
                            <div className="checklist-progress">
                              <span className="progress-text">
                                {checklistProgress.answered_questions} из {checklistProgress.total_questions} вопросов
                              </span>
                              <div className="progress-visual">
                                <div className="progress-bar small">
                                  <div 
                                    className={`progress-fill ${
                                      completionPercentage === 100 ? 'completed' : 
                                      completionPercentage > 50 ? 'in-progress' : 'started'
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
                      </div>
                      
                      <div className="checklist-status">
                        {completionPercentage === 100 ? (
                          <svg className="status-icon completed" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        ) : completionPercentage > 0 ? (
                          <svg className="status-icon in-progress" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                          </svg>
                        ) : null}
                        
                        <span className="status-text">Открыть →</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {(!checklists || checklists.length === 0) && (
              <div className="empty-state">
                <div className="empty-icon">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="empty-title">Нет доступных чеклистов</h3>
                <p className="empty-description">
                  Чеклисты для анализа персонажей еще не созданы.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CharacterChecklists;
