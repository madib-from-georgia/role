import React, { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { Button, TextInput, Select, Text, Card } from "@gravity-ui/uikit";
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { projectsApi } from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import AuthModal from '../components/auth/AuthModal'
import { config } from '../config'

interface Project {
  id: string
  title: string
  description?: string
  created_at: string
  updated_at: string
}

const fetchProjects = async (): Promise<Project[]> => {
  const projects = await projectsApi.getAll()
  return projects as Project[]
}

const deleteProject = async (id: string): Promise<void> => {
  await projectsApi.delete(id)
}

const ProjectList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterValue, setFilterValue] = useState('Все')
  const [showAuthModal, setShowAuthModal] = useState(false)

  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const queryClient = useQueryClient()
  
  // Делаем запрос только если пользователь авторизован или авторизация отключена
  const shouldFetchProjects = !config.authEnabled || isAuthenticated
  
  const { data: projects, isLoading, error } = useQuery<Project[]>(
    'projects', 
    fetchProjects,
    {
      enabled: shouldFetchProjects && !authLoading
    }
  )

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

  // Фильтрация и поиск проектов
  const filteredProjects = useMemo(() => {
    if (!projects) return []

    let filtered = projects

    // Применяем поиск
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      filtered = filtered.filter(project =>
        project.title.toLowerCase().includes(query) ||
        (project.description && project.description.toLowerCase().includes(query))
      )
    }

    // Применяем фильтр по статусу
    if (filterValue !== 'Все') {
      const now = new Date()
      const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      
      switch (filterValue) {
        case 'Недавние':
          filtered = filtered.filter(project =>
            new Date(project.updated_at) >= sevenDaysAgo
          )
          break
        case 'Завершенные': {
          // Пока что считаем завершенными проекты старше 30 дней без обновлений
          const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          filtered = filtered.filter(project =>
            new Date(project.updated_at) < thirtyDaysAgo
          )
          break
        }
        case 'В работе': {
          // Проекты, обновленные в последние 30 дней (активные проекты)
          const thirtyDaysAgoActive = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          filtered = filtered.filter(project =>
            new Date(project.updated_at) >= thirtyDaysAgoActive
          )
          break
        }
      }
    }

    return filtered
  }, [projects, searchQuery, filterValue])

  // Показываем загрузку если загружается авторизация или проекты
  if (authLoading || isLoading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    )
  }

  // Если авторизация включена и пользователь не авторизован
  if (config.authEnabled && !isAuthenticated) {
    return (
      <>
        <div className="container">
          <div className="empty-state">
            <div className="empty-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="empty-title">Добро пожаловать в Роль!</h3>
            <p className="empty-description">
              Система анализа персонажей для актеров и режиссеров. 
              Войдите в систему чтобы начать работу с проектами.
            </p>
            <Button 
              view='action' 
              size='l'
              onClick={() => setShowAuthModal(true)}
            >
              Войти в систему
            </Button>
          </div>
        </div>
        
        <AuthModal 
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      </>
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
          <Text variant='header-1'>Ваши проекты</Text>
          <p>Управляйте проектами анализа персонажей и создавайте новые исследования</p>
        </div>
        <Link to="/projects/new">
          <Button view='action' size='l'>
              Создать проект
          </Button>
        </Link>
      </div>

      {!projects || projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="empty-title">Добро пожаловать в Роль!</h3>
          <p className="empty-description">
            Здесь будут отображаться ваши проекты анализа персонажей. 
            Создайте первый проект, чтобы начать исследование литературных героев.
          </p>
          <Link to="/projects/new">
            <Button view='action' size='l'>
              Создать первый проект
            </Button>
          </Link>
        </div>
      ) : (
        <div>
          {/* Поиск и фильтры */}
          <div className="search-bar">
            <TextInput
                placeholder="Поиск проектов..."
                value={searchQuery}
                onUpdate={setSearchQuery}
            />
            <div className='filter-select'>
              <Select
                size="m"
                width="max"
                placeholder="Проекты"
                value={[filterValue]}
                onUpdate={(values) => setFilterValue(values[0] || 'Все')}
              >
                <Select.Option value="Все">Все</Select.Option>
                <Select.Option value="Недавние">Недавние</Select.Option>
                <Select.Option value="Завершенные">Завершенные</Select.Option>
                <Select.Option value="В работе">В работе</Select.Option>
              </Select>
            </div>
          </div>

          {/* Результаты поиска */}
          {filteredProjects.length === 0 && (searchQuery.trim() || filterValue !== 'Все') ? (
            <div className="empty-state">
              <div className="empty-icon">
                <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="empty-title">Проекты не найдены</h3>
              <p className="empty-description">
                {searchQuery.trim()
                  ? `По запросу "${searchQuery}" ничего не найдено. Попробуйте изменить поисковый запрос.`
                  : `Нет проектов в категории "${filterValue}". Попробуйте выбрать другой фильтр.`
                }
              </p>
              <Button
                onClick={() => {
                  setSearchQuery('')
                  setFilterValue('Все')
                }}
                view="outlined"
              >
                Сбросить фильтры
              </Button>
            </div>
          ) : (
            /* Сетка проектов */
            <div className="grid grid-3">
              {filteredProjects.map((project) => (
                <Card type='container' view='raised' size='l'  key={project.id}>
                  <div className="project-card-wrapper">
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
                    <Button
                      className="delete-project-btn"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDeleteProject(project.id, project.title);
                      }}
                      disabled={deleteMutation.isLoading}
                      title="Удалить проект"
                      view='flat'
                    >
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ProjectList
