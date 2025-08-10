import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from 'react-query'
import { projectsApi } from '../services/api'

interface CreateProjectData {
  title: string
  description?: string
}

const createProject = async (data: CreateProjectData) => {
  return await projectsApi.create(data)
}

const CreateProject: React.FC = () => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const mutation = useMutation(createProject, {
    onSuccess: (data) => {
      queryClient.invalidateQueries('projects')
      navigate(`/projects/${data.id}`)
    },
    onError: (error) => {
      console.error('Ошибка создания проекта:', error)
    }
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (title.trim()) {
      mutation.mutate({
        title: title.trim(),
        description: description.trim() || undefined
      })
    }
  }

  return (
    <div className="container">
      <div className="create-project-header">
        <h1>Создать новый проект</h1>
        <p>Настройте проект для анализа персонажей художественного произведения</p>
      </div>

      <div className="create-project-content">
        <div className="form-section">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Основная информация</h2>
            </div>

            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title" className="form-label">
                  Название проекта *
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="form-input"
                  placeholder="Например: Анализ персонажей романа 'Война и мир'"
                  required
                />
                <div className="form-help">
                  Выберите понятное название для идентификации проекта
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="description" className="form-label">
                  Описание проекта
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="form-textarea"
                  rows={4}
                  placeholder="Опишите цели анализа, особенности произведения..."
                />
                <div className="form-help">
                  Детальное описание поможет организовать работу
                </div>
              </div>

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => navigate('/')}
                  className="btn btn-secondary"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  disabled={!title.trim() || mutation.isLoading}
                  className="btn btn-primary"
                >
                  {mutation.isLoading ? (
                    <>
                      <div className="spinner small"></div>
                      Создаем...
                    </>
                  ) : (
                    'Создать проект'
                  )}
                </button>
              </div>

              {mutation.isError && (
                <div className="error-message">
                  <strong>Ошибка создания проекта</strong>
                  <p>Не удалось создать проект. Проверьте подключение и попробуйте снова.</p>
                </div>
              )}
            </form>
          </div>
        </div>

        <div className="info-section">
          <div className="info-card">
            <h3>Процесс работы</h3>
            <ul className="steps-list">
              <li className="step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h4>Загрузите текст</h4>
                  <p>Добавьте файл произведения в формате TXT</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>Подождите предобработку</h4>
                  <p>Система найдет персонажей и их реплики</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>Выберите персонажа</h4>
                  <p>Заполните опросники для детального анализа</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h4>Получите результаты</h4>
                  <p>Экспортируйте подробный анализ персонажа</p>
                </div>
              </li>
            </ul>
          </div>

          <div className="info-card">
            <h3>Модули анализа</h3>
            <ul className="features-list">
              <li>
                <strong>Физический портрет</strong>
                <span>Внешность, возраст, особенности облика</span>
              </li>
              <li>
                <strong>Эмоциональный профиль</strong>
                <span>Характер, темперамент, реакции</span>
              </li>
              <li>
                <strong>Речевые особенности</strong>
                <span>Манера речи, словарь, стиль</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CreateProject
