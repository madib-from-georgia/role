import React, { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { projectsApi, textsApi, charactersApi } from '../services/api'
import { Project } from '../../../shared/types'

// Фактический тип ответа загрузки файла от backend
interface FileUploadResponse {
  success: boolean
  text_id: number
  filename: string
  format: string
  content_length: number
  metadata: Record<string, any>
  created_at: string
  message?: string
}

// Фактический тип данных текста, которые возвращает API /projects/{id}/texts
interface ProjectText {
  id: number
  filename: string
  original_format: string
  processed_at?: string
  created_at: string
}

// Интерфейс для персонажа
interface Character {
  id: number
  name: string
  aliases?: string[]
  importance_score?: number
  speech_attribution?: any
  created_at?: string
}

const fetchProject = async (id: string): Promise<Project> => {
  return await projectsApi.getById(id)
}

const fetchProjectTexts = async (projectId: string): Promise<ProjectText[]> => {
  return await textsApi.getByProject(projectId)
}

const uploadText = async (projectId: string, file: File): Promise<FileUploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  return await textsApi.upload(projectId, formData)
}

const deleteProject = async (id: string): Promise<void> => {
  await projectsApi.delete(id)
}

const fetchCharacters = async (textId: string): Promise<Character[]> => {
  return await charactersApi.getByText(textId)
}

// Компонент для отображения секции текста с персонажами
const TextSection: React.FC<{ text: ProjectText; onCharacterClick: (character: Character) => void }> = ({ text, onCharacterClick }) => {
  const { data: characters, isLoading: charactersLoading, error: charactersError } = useQuery(
    ['text-characters', text.id],
    () => fetchCharacters(text.id.toString()),
    { 
      enabled: !!text.processed_at, // Загружаем персонажей только если текст обработан
      staleTime: 5 * 60 * 1000 // 5 минут
    }
  )

  return (
    <div className="text-section">
      <div className="text-header">
        <h3>{text.filename}</h3>
        <span className={`status-badge ${text.processed_at ? 'processed' : 'pending'}`}>
          {text.processed_at ? 'Обработан' : 'В ожидании'}
        </span>
      </div>

      <div className="file-status-info">
        {text.processed_at ? (
          <div className="processed-info">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Файл успешно обработан</span>
            <small>{new Date(text.processed_at).toLocaleString('ru-RU')}</small>
          </div>
        ) : (
          <div className="pending-info">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Ожидает обработки</span>
          </div>
        )}
      </div>

      {/* Отображение персонажей только для обработанных текстов */}
      {text.processed_at && (
        <>
          {charactersLoading && (
            <div className="characters-loading">
              <div className="spinner"></div>
              <span>Загрузка персонажей...</span>
            </div>
          )}

          {charactersError && (
            <div className="error-state">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <p>Ошибка загрузки персонажей</p>
            </div>
          )}

          {characters && characters.length > 0 && (
            <div className="characters-grid">
              {characters.slice(0, 10).map((character) => (
                <div 
                  key={character.id} 
                  className="character-item"
                  onClick={() => onCharacterClick(character)}
                >
                  <div className="character-header">
                    <h4>{character.name}</h4>
                    {character.importance_score && (
                      <span className="importance-score">
                        {Math.round(character.importance_score * 100)}%
                      </span>
                    )}
                  </div>
                  
                  {character.aliases && character.aliases.length > 0 && (
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

          {characters && characters.length === 0 && (
            <div className="empty-characters">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <p>Персонажи не найдены</p>
            </div>
          )}
        </>
      )}
    </div>
  )
}

const ProjectDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

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

  const { data: texts } = useQuery(
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

  const handleCharacterClick = (character: Character) => {
    navigate(`/characters/${character.id}/checklists`)
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
                  <strong>Файл успешно загружен</strong>
                  <div className="upload-stats">
                    <p>Имя файла: {uploadMutation.data.filename}</p>
                    <p>Формат: {uploadMutation.data.format?.toUpperCase()}</p>
                    <p>Размер содержимого: {uploadMutation.data.content_length?.toLocaleString() || 'N/A'} символов</p>
                    <p className="upload-note">
                      💡 Файл загружен. Анализ персонажей будет доступен после обработки текста.
                    </p>
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
                <TextSection 
                  key={text.id} 
                  text={text} 
                  onCharacterClick={handleCharacterClick} 
                />
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
                <span>Обработано:</span>
                <strong>{texts?.filter(text => text.processed_at).length || 0}</strong>
              </div>
              <div className="stat-item">
                <span>Форматы:</span>
                <strong>{texts ? [...new Set(texts.map(t => t.original_format))].join(', ').toUpperCase() : 'Нет'}</strong>
              </div>
            </div>

            {/* Список файлов */}
            {texts && texts.length > 0 && (
              <div className="files-list">
                <h4>Загруженные файлы:</h4>
                {texts.map((text) => (
                  <div key={text.id} className="file-item">
                    <div className="file-info">
                      <div className="filename">{text.filename}</div>
                      <div className="file-details">
                        <span className="format">{text.original_format.toUpperCase()}</span>
                        <span className={`status ${text.processed_at ? 'processed' : 'pending'}`}>
                          {text.processed_at ? '✓ Обработан' : '⏳ В ожидании'}
                        </span>
                      </div>
                      {text.processed_at && (
                        <div className="processed-date">
                          {new Date(text.processed_at).toLocaleDateString('ru-RU')}
                        </div>
                      )}
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
                <li className={texts && texts.some(t => t.processed_at) ? 'completed' : ''}>
                  Дождитесь обработки файлов
                </li>
                <li>Запустите анализ персонажей</li>
                <li>Выберите персонажей для детального анализа</li>
              </ul>
            </div>
          </div>
        </div>
      </div>


    </div>
  )
}

export default ProjectDetail
