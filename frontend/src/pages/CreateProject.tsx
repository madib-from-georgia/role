import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from 'react-query'
import { Button, TextArea } from "@gravity-ui/uikit";
import { projectsApi } from '../services/api'

interface CreateProjectData {
  title: string
  description?: string
  [key: string]: unknown;
}

interface CreatedProject {
  id: string;
  [key: string]: unknown;
}

const createProject = async (data: CreateProjectData): Promise<CreatedProject> => {
  return await projectsApi.create(data as CreateProjectData & { [key: string]: unknown }) as CreatedProject
}

const CreateProject: React.FC = () => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const mutation = useMutation<CreatedProject, Error, CreateProjectData>(createProject, {
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
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title" className="form-label">
                  Название проекта *
                </label>
                <TextArea
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Например: Роль романа 'Война и мир'"
                />
              </div>

              <div className="form-group">
                <label htmlFor="description" className="form-label">
                  Описание проекта
                </label>
                <TextArea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={4}
                  placeholder="Опишите цели анализа, особенности произведения..."
                />
              </div>

              <div className="form-actions">
                <Button
                  onClick={() => navigate('/')}
                >
                  Отмена
                </Button>
                <Button
                  type="submit"
                  disabled={!title.trim() || mutation.isLoading}
                >
                  {mutation.isLoading ? (
                    <>
                      <div className="spinner small"></div>
                      Создаем...
                    </>
                  ) : (
                    'Создать проект'
                  )}
                </Button>
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
                  <h4>Создайте проект</h4>
                  <p>Опишите, для чего этот проект: подготовка учебного отрывка, спектакля...</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>Загрузите текст</h4>
                  <p>Добавьте файл произведения в формате TXT, FB2, EPUB</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>Подождите предобработку</h4>
                  <p>Система найдет персонажей и их реплики</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h4>Создайте персонаж вручную</h4>
                  <p>Если атоматическое распознавание сработало плохо</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">5</div>
                <div className="step-content">
                  <h4>Перейдите в карточку персонажа</h4>
                  <p>Заполните опросники для детального анализа</p>
                </div>
              </li>
              <li className="step">
                <div className="step-number">6</div>
                <div className="step-content">
                  <h4>Получите результаты</h4>
                  <p>Экспортируйте подробный анализ персонажа</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CreateProject
