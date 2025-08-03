import React, { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import axios from 'axios'
import { Project, TextProcessingResult, UploadResponse } from '../../../shared/types'
import CharacterAnalysis from '../components/CharacterAnalysis'

const fetchProject = async (id: string): Promise<Project> => {
  const response = await axios.get(`/api/projects/${id}`)
  return response.data
}

const fetchProjectTexts = async (projectId: string): Promise<TextProcessingResult[]> => {
  const response = await axios.get(`/api/projects/${projectId}/texts`)
  return response.data
}

const uploadText = async (projectId: string, file: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await axios.post(`/api/projects/${projectId}/texts`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

const deleteProject = async (id: string): Promise<void> => {
  await axios.delete(`/api/projects/${id}`)
}

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedCharacter, setSelectedCharacter] = useState<{
    name: string;
    textId: string;
  } | null>(null)
  const queryClient = useQueryClient()

  const deleteMutation = useMutation(deleteProject, {
    onSuccess: () => {
      // Перенаправляем пользователя на список проектов после удаления
      queryClient.invalidateQueries('projects')
      navigate('/')
    },
    onError: (error) => {
      console.error('Ошибка удаления проекта:', error)
      alert('Не удалось удалить проект. Попробуйте еще раз.')
    }
  })
  
  const { data: project, isLoading, error } = useQuery(
    ['project', id],
    () => fetchProject(id!),
    { enabled: !!id }
  )

  const { data: texts, isLoading: textsLoading } = useQuery(
    ['project-texts', id],
    () => fetchProjectTexts(id!),
    { enabled: !!id }
  )

  const uploadMutation = useMutation(
    (file: File) => uploadText(id!, file),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['project', id])
        queryClient.invalidateQueries(['project-texts', id])
        setSelectedFile(null)
      },
      onError: (error) => {
        console.error('Ошибка загрузки файла:', error)
      }
    }
  )

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file && (file.type === 'text/plain' || file.name.toLowerCase().endsWith('.fb2'))) {
      setSelectedFile(file)
    } else {
      alert('Пожалуйста, выберите файл в формате TXT или FB2')
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile)
    }
  }

  const handleCharacterClick = (characterName: string, textId: string) => {
    setSelectedCharacter({ name: characterName, textId })
  }

  const handleCloseAnalysis = () => {
    setSelectedCharacter(null)
  }

  const handleDeleteProject = () => {
    if (!project) return;
    
    if (window.confirm(`Вы уверены, что хотите удалить проект "${project.title}"? Это действие нельзя отменить и все данные проекта будут удалены.`)) {
      deleteMutation.mutate(id!)
    }
  }

  if (isLoading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="container">
        <div className="empty-state">
          <div className="empty-icon">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="empty-title">Проект не найден</h3>
          <p className="empty-description">Проект с указанным ID не существует</p>
          <Link to="/" className="btn btn-primary">Вернуться к проектам</Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="project-detail-header">
        <div className="project-detail-header-top">
          <div>
            <h1>{project.title}</h1>
            {project.description && (
              <p>{project.description}</p>
            )}
          </div>
          <button
            className="btn btn-secondary"
            onClick={handleDeleteProject}
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? (
              <>
                <div className="spinner small"></div>
                Удаление...
              </>
            ) : (
              'Удалить проект'
            )}
          </button>
        </div>
        <div className="project-meta">
          <span>Создан: {new Date(project.created_at).toLocaleDateString('ru-RU')}</span>
          <span>•</span>
          <span>Обновлен: {new Date(project.updated_at).toLocaleDateString('ru-RU')}</span>
        </div>
      </div>

      <div className="project-content">
        <div className="main-section">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Загрузка текста</h2>
            </div>
            
            <div className="file-upload">
              <div className="upload-area">
                <div className="upload-icon">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div className="upload-content">
                  <label htmlFor="file-upload" className="upload-label">
                    {selectedFile ? selectedFile.name : 'Перетащите файл сюда или нажмите для выбора'}
                  </label>
                  <input
                    id="file-upload"
                    type="file"
                    accept=".txt,.fb2"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                  />
                  <p className="upload-help">Поддерживаются файлы TXT и FB2 до 10MB</p>
                </div>
              </div>

              <button
                className="btn btn-primary upload-btn"
                disabled={!selectedFile || uploadMutation.isLoading}
                onClick={handleUpload}
              >
                {uploadMutation.isLoading ? (
                  <>
                    <div className="spinner small"></div>
                    Обработка файла...
                  </>
                ) : (
                  'Загрузить и обработать текст'
                )}
              </button>

              {uploadMutation.isError && (
                <div className="error-message">
                  <strong>Ошибка загрузки файла</strong>
                  <p>Не удалось загрузить и обработать файл. Попробуйте еще раз.</p>
                </div>
              )}

              {uploadMutation.isSuccess && uploadMutation.data && (
                <div className="success-message">
                  <strong>Файл успешно обработан</strong>
                  <div className="processing-stats">
                    <p>Найдено персонажей: {uploadMutation.data.processing_result.characters_found}</p>
                    <p>Время обработки: {uploadMutation.data.processing_result.processing_time.toFixed(2)} сек</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Секция найденных персонажей */}
          {texts && texts.length > 0 && (
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Найденные персонажи</h2>
              </div>
              
              {texts.map((text) => (
                <div key={text.text_id} className="text-section">
                  <div className="text-header">
                    <h3>{text.filename}</h3>
                    <span className={`status-badge ${text.processing_status}`}>
                      {text.processing_status === 'completed' ? 'Обработан' :
                       text.processing_status === 'processing' ? 'Обрабатывается' : 'Ошибка'}
                    </span>
                  </div>

                  {text.processing_status === 'completed' && text.characters.length > 0 && (
                    <div className="characters-grid">
                      {text.characters.slice(0, 10).map((character, index) => (
                        <div 
                          key={index} 
                          className="character-item"
                          onClick={() => handleCharacterClick(character.name, text.text_id)}
                        >
                          <div className="character-header">
                            <h4>{character.name}</h4>
                          </div>
                          
                          {character.aliases.length > 0 && (
                            <div className="character-aliases">
                              <span>Алиасы: {character.aliases.join(', ')}</span>
                            </div>
                          )}
                          
                          <button className="analyze-btn">
                            Анализировать →
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {text.processing_status === 'completed' && text.characters.length === 0 && (
                    <div className="empty-characters">
                      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      <p>Персонажи не найдены</p>
                    </div>
                  )}

                  {text.processing_status === 'failed' && (
                    <div className="error-state">
                      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <p>Ошибка обработки файла</p>
                      {text.error_message && <p>{text.error_message}</p>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="sidebar">
          <div className="card">
            <h3>Статистика проекта</h3>
            
            <div className="stats-list">
              <div className="stat-item">
                <span>Загружено текстов:</span>
                <strong>{texts?.length || 0}</strong>
              </div>
              <div className="stat-item">
                <span>Найдено персонажей:</span>
                <strong>{texts?.reduce((sum, text) => sum + text.characters_found, 0) || 0}</strong>
              </div>
              <div className="stat-item">
                <span>Проанализировано:</span>
                <strong>{texts?.filter(text => text.processing_status === 'completed').length || 0}</strong>
              </div>
            </div>

            {/* Метрики качества NLP */}
            {texts && texts.length > 0 && (
              <div className="quality-metrics">
                <h4>Качество обработки:</h4>
                {texts.map((text) => (
                  <div key={text.text_id} className="quality-item">
                    <div className="quality-filename">{text.filename}</div>
                    <div className="quality-stats">
                      <div className="quality-metric">
                        <span>Извлечение персонажей:</span>
                        <span className={`quality-value ${
                          text.nlp_metrics.character_extraction_accuracy >= 0.9 ? 'high' :
                          text.nlp_metrics.character_extraction_accuracy >= 0.7 ? 'medium' : 'low'
                        }`}>
                          {(text.nlp_metrics.character_extraction_accuracy * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="quality-metric">
                        <span>Атрибуция речи:</span>
                        <span className={`quality-value ${
                          text.nlp_metrics.speech_attribution_accuracy >= 0.95 ? 'high' :
                          text.nlp_metrics.speech_attribution_accuracy >= 0.8 ? 'medium' : 'low'
                        }`}>
                          {(text.nlp_metrics.speech_attribution_accuracy * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="next-steps">
              <h4>Следующие шаги:</h4>
              <ul>
                <li className={texts && texts.length > 0 ? 'completed' : ''}>
                  Загрузите текст произведения
                </li>
                <li className={texts && texts.some(t => t.characters_found > 0) ? 'completed' : ''}>
                  Дождитесь извлечения персонажей
                </li>
                <li>Выберите персонажей для анализа</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Modal для анализа персонажа */}
      {selectedCharacter && (
        <div className="modal-overlay" onClick={handleCloseAnalysis}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <CharacterAnalysis
              projectId={id!}
              textId={selectedCharacter.textId}
              characterName={selectedCharacter.name}
              onClose={handleCloseAnalysis}
            />
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectDetail
