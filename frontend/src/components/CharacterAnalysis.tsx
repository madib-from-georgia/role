import React, { useState } from 'react'
import { useMutation } from 'react-query'
import { Button } from "@gravity-ui/uikit"
import axios from 'axios'
import { FullCharacterAnalysis, CharacterAnalysisResult } from '../../../shared/types'

interface CharacterAnalysisProps {
  projectId: string;
  textId: string;
  characterName: string;
  onClose?: () => void;
}

const analyzeCharacter = async (projectId: string, textId: string, characterName: string): Promise<FullCharacterAnalysis> => {
  const response = await axios.post(`/api/projects/${projectId}/texts/${textId}/analyze/${characterName}`)
  return response.data
}

const CharacterAnalysis: React.FC<CharacterAnalysisProps> = ({ 
  projectId, 
  textId, 
  characterName, 
  onClose 
}) => {
  const [analysisResult, setAnalysisResult] = useState<FullCharacterAnalysis | null>(null)


  const analysisMutation = useMutation(
    () => analyzeCharacter(projectId, textId, characterName),
    {
      onSuccess: (data) => {
        setAnalysisResult(data)
      },
      onError: (error) => {
        console.error('Ошибка анализа персонажа:', error)
      }
    }
  )

  const handleStartAnalysis = () => {
    analysisMutation.mutate()
  }

  const renderAnalysisResult = (result: CharacterAnalysisResult, title: string) => {
    if (!result) return null

    return (
      <div className="analysis-result">
        <div className="analysis-header">
          <h4>{title}</h4>
          <span className={`analysis-status ${result.success ? 'success' : 'error'}`}>
            {result.success ? (
              <>
                <svg fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Успешно
              </>
            ) : (
              <>
                <svg fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                Ошибка
              </>
            )}
          </span>
        </div>

        {result.success && result.data ? (
          <div className="analysis-content">
            {/* Физический портрет */}
            {result.analysis_type === 'physical_portrait' && (
              <div className="analysis-grid">
                {'height' in result.data && result.data.height && (
                  <div className="analysis-item">
                    <span className="analysis-label">Рост:</span>
                    <span className="analysis-value">{result.data.height}</span>
                  </div>
                )}
                {'build' in result.data && result.data.build && (
                  <div className="analysis-item">
                    <span className="analysis-label">Телосложение:</span>
                    <span className="analysis-value">{result.data.build}</span>
                  </div>
                )}
                {'hair' in result.data && result.data.hair && (
                  <div className="analysis-item">
                    <span className="analysis-label">Волосы:</span>
                    <span className="analysis-value">{result.data.hair}</span>
                  </div>
                )}
                {'eyes' in result.data && result.data.eyes && (
                  <div className="analysis-item">
                    <span className="analysis-label">Глаза:</span>
                    <span className="analysis-value">{result.data.eyes}</span>
                  </div>
                )}
                {'age' in result.data && result.data.age && (
                  <div className="analysis-item">
                    <span className="analysis-label">Возраст:</span>
                    <span className="analysis-value">{result.data.age}</span>
                  </div>
                )}
                {'clothing_style' in result.data && result.data.clothing_style && (
                  <div className="analysis-item">
                    <span className="analysis-label">Стиль одежды:</span>
                    <span className="analysis-value">{result.data.clothing_style}</span>
                  </div>
                )}
              </div>
            )}

            {/* Эмоциональный профиль */}
            {result.analysis_type === 'emotional_profile' && (
              <div className="analysis-content">
                {'dominant_emotions' in result.data && result.data.dominant_emotions && (
                  <div className="analysis-item">
                    <span className="analysis-label">Доминирующие эмоции:</span>
                    <div className="emotion-tags">
                      {result.data.dominant_emotions.map((emotion, index) => (
                        <span key={index} className="emotion-tag">
                          {emotion}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {'emotional_range' in result.data && result.data.emotional_range && (
                  <div className="analysis-item">
                    <span className="analysis-label">Эмоциональный диапазон:</span>
                    <span className="analysis-value">{result.data.emotional_range}</span>
                  </div>
                )}
                {'emotional_stability' in result.data && result.data.emotional_stability && (
                  <div className="analysis-item">
                    <span className="analysis-label">Эмоциональная стабильность:</span>
                    <span className="analysis-value">{result.data.emotional_stability}</span>
                  </div>
                )}
              </div>
            )}

            {/* Речевые характеристики */}
            {result.analysis_type === 'speech_characteristics' && (
              <div className="analysis-content">
                {'vocabulary_level' in result.data && result.data.vocabulary_level && (
                  <div className="analysis-item">
                    <span className="analysis-label">Уровень словаря:</span>
                    <span className="analysis-value">{result.data.vocabulary_level}</span>
                  </div>
                )}
                {'speech_patterns' in result.data && result.data.speech_patterns && (
                  <div className="analysis-item">
                    <span className="analysis-label">Речевые паттерны:</span>
                    <div className="speech-tags">
                      {result.data.speech_patterns.map((pattern, index) => (
                        <span key={index} className="speech-tag">
                          {pattern}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {'formality_level' in result.data && result.data.formality_level && (
                  <div className="analysis-item">
                    <span className="analysis-label">Уровень формальности:</span>
                    <span className="analysis-value">{result.data.formality_level}</span>
                  </div>
                )}
              </div>
            )}

            {/* Уверенность */}
            <div className="confidence-section">
              <div className="confidence-item">
                <span className="confidence-label">Уверенность анализа:</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill"
                    style={{ width: `${result.data.confidence_score * 100}%` }}
                  ></div>
                </div>
                <span className="confidence-value">
                  {(result.data.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="analysis-error">
            {result.error || 'Неизвестная ошибка'}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="character-analysis">
      <div className="modal-header">
        <h3>Анализ персонажа: {characterName}</h3>
        {onClose && (
          <Button onClick={onClose} view="flat" size="s" className="close-btn">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </Button>
        )}
      </div>

      <div className="modal-body">
        {!analysisResult ? (
          <div className="analysis-start">
            <div className="start-icon">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h4>Готов к анализу</h4>
            <p>Запустите полный анализ персонажа всеми доступными модулями</p>
            <Button
              onClick={handleStartAnalysis}
              disabled={analysisMutation.isLoading}
              view="action"
              size="l"
              className="start-btn"
            >
              {analysisMutation.isLoading ? (
                <>
                  <div className="spinner small"></div>
                  Анализ в процессе...
                </>
              ) : (
                'Начать анализ'
              )}
            </Button>
          </div>
        ) : (
          <div className="analysis-results">
            {/* Общая статистика */}
            <div className="analysis-summary">
              <h4>Сводка анализа</h4>
              <div className="summary-stats">
                <div className="summary-stat">
                  <div className="stat-number success">
                    {analysisResult.summary.successful_modules}
                  </div>
                  <div className="stat-label">Успешно</div>
                </div>
                <div className="summary-stat">
                  <div className="stat-number error">
                    {analysisResult.summary.failed_modules}
                  </div>
                  <div className="stat-label">Ошибки</div>
                </div>
                <div className="summary-stat">
                  <div className="stat-number">
                    {(analysisResult.summary.overall_confidence * 100).toFixed(0)}%
                  </div>
                  <div className="stat-label">Уверенность</div>
                </div>
              </div>
            </div>

            {/* Результаты модулей */}
            <div className="analysis-modules">
              {analysisResult.analyses.physical_portrait && 
                renderAnalysisResult(analysisResult.analyses.physical_portrait, 'Физический портрет')}
              
              {analysisResult.analyses.emotional_profile && 
                renderAnalysisResult(analysisResult.analyses.emotional_profile, 'Эмоциональный профиль')}
              
              {analysisResult.analyses.speech_characteristics && 
                renderAnalysisResult(analysisResult.analyses.speech_characteristics, 'Речевые характеристики')}
            </div>

            {/* Кнопка повторного анализа */}
            <div className="analysis-actions">
              <Button
                onClick={handleStartAnalysis}
                disabled={analysisMutation.isLoading}
                view="outlined"
                size="m"
              >
                {analysisMutation.isLoading ? 'Анализ в процессе...' : 'Повторить анализ'}
              </Button>
            </div>
          </div>
        )}

        {analysisMutation.isError && (
          <div className="error-message">
            <strong>Ошибка анализа</strong>
            <p>Не удалось выполнить анализ персонажа. Попробуйте еще раз.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CharacterAnalysis 
