import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { projectsApi } from '../services/api'

interface Project {
  id: string
  title: string
  description?: string
  created_at: string
  updated_at: string
}

const fetchProjects = async (): Promise<Project[]> => {
  const response = await projectsApi.getAll()
  return response.projects
}

const deleteProject = async (id: string): Promise<void> => {
  await projectsApi.delete(id)
}

const ProjectList: React.FC = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { data: projects, isLoading, error } = useQuery('projects', fetchProjects)

  const deleteMutation = useMutation(deleteProject, {
    onSuccess: () => {
      // Обновляем список проектов после удаления
      queryClient.invalidateQueries('projects')
    },
    onError: (error) => {
      console.error('Ошибка удаления проекта:', error)
      alert('Не удалось удалить проект. Попробуйте еще раз.')
    }
  })

  const handleDeleteProject = (id: string, title: string) => {
    if (window.confirm(`Вы уверены, что хотите удалить проект "${title}"? Это действие нельзя отменить.`)) {
      deleteMutation.mutate(id)
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

  if (error) {
    return (
      <div className="container">
        <div className="empty-state">
          <div className="empty-icon">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="empty-title">Ошибка загрузки</h3>
          <p className="empty-description">
            Не удалось загрузить список проектов. Проверьте подключение к серверу.
          </p>
          <button onClick={() => window.location.reload()} className="btn btn-primary">
            Попробовать снова
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="project-header">
        <div>
          <h1>Ваши проекты</h1>
          <p>Управляйте проектами анализа персонажей и создавайте новые исследования</p>
        </div>
        <Link to="/projects/new" className="btn btn-primary">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Создать проект
        </Link>
      </div>

      {/* Статистика проектов */}
      {projects && projects.length > 0 && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{projects.length}</div>
            <div className="stat-label">Всего проектов</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">
              {projects.filter(p => new Date(p.updated_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)).length}
            </div>
            <div className="stat-label">Активных за неделю</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">
              {Math.max(1, new Date().getFullYear() - Math.min(...projects.map(p => new Date(p.created_at).getFullYear())) + 1)}
            </div>
            <div className="stat-label">Лет работы</div>
          </div>
        </div>
      )}

      {!projects || projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="empty-title">Добро пожаловать в Analyse Text!</h3>
          <p className="empty-description">
            Здесь будут отображаться ваши проекты анализа персонажей. 
            Создайте первый проект, чтобы начать исследование литературных героев с помощью ИИ.
          </p>
          <Link to="/projects/new" className="btn btn-primary">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Создать первый проект
          </Link>
        </div>
      ) : (
        <div>
          {/* Поиск и фильтры */}
          <div className="search-bar">
            <div className="search-input">
              <svg className="search-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Поиск проектов..."
                className="form-input"
              />
            </div>
            <select className="filter-select">
              <option>Все проекты</option>
              <option>Недавние</option>
              <option>Завершенные</option>
              <option>В работе</option>
            </select>
          </div>

          {/* Сетка проектов */}
          <div className="grid grid-3">
            {projects.map((project) => (
              <div key={project.id} className="project-card-wrapper">
                <Link
                  to={`/projects/${project.id}`}
                  className="project-card"
                >
                  <div className="project-header">
                    <div>
                      <h3 className="project-title">{project.title}</h3>
                      <div className="project-date">
                        {new Date(project.created_at).toLocaleDateString('ru-RU')}
                      </div>
                    </div>
                    <svg className="project-arrow" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                  
                  {project.description && (
                    <p className="project-description">
                      {project.description}
                    </p>
                  )}
                  
                  <div className="project-footer">
                    <div className="project-status">
                      <div className="status-dot"></div>
                      <span>Активный</span>
                    </div>
                    <span>
                      {Math.ceil((new Date().getTime() - new Date(project.updated_at).getTime()) / (1000 * 60 * 60 * 24))} дней назад
                    </span>
                  </div>
                </Link>
                <button
                  className="delete-project-btn"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleDeleteProject(project.id, project.title);
                  }}
                  disabled={deleteMutation.isLoading}
                  title="Удалить проект"
                >
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProjectList
