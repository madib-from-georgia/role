import React, { useState, useEffect } from 'react'
import { Button, TextInput } from "@gravity-ui/uikit";
import { useSearchParams, useNavigate } from 'react-router-dom'

interface ResetPasswordFormProps {
  onSuccess?: () => void
}

const ResetPasswordForm: React.FC<ResetPasswordFormProps> = ({ onSuccess }) => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  })
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<{newPassword?: string, confirmPassword?: string}>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  useEffect(() => {
    if (!token) {
      setError('Отсутствует токен для сброса пароля')
    }
  }, [token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setFieldErrors({})

    if (!token) {
      setError('Отсутствует токен для сброса пароля')
      return
    }

    // Валидация перед отправкой
    const newFieldErrors: {newPassword?: string, confirmPassword?: string} = {}

    if (!formData.newPassword) {
      newFieldErrors.newPassword = 'Новый пароль обязателен для заполнения'
    } else if (formData.newPassword.length < 8) {
      newFieldErrors.newPassword = 'Пароль должен содержать минимум 8 символов'
    }

    if (!formData.confirmPassword) {
      newFieldErrors.confirmPassword = 'Подтверждение пароля обязательно'
    } else if (formData.newPassword !== formData.confirmPassword) {
      newFieldErrors.confirmPassword = 'Пароли не совпадают'
    }

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors)
      return
    }

    try {
      setIsLoading(true)
      
      const response = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          token: token,
          new_password: formData.newPassword 
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Ошибка при сбросе пароля')
      }

      setIsSuccess(true)
      onSuccess?.()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Ошибка при сбросе пароля'
      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target

    setFormData(prev => ({
      ...prev,
      [name]: value
    }))

    // Очищаем ошибки при изменении поля
    if (fieldErrors[name as keyof typeof fieldErrors]) {
      setFieldErrors(prev => ({
        ...prev,
        [name]: undefined
      }))
    }

    // Очищаем общую ошибку если пользователь начал изменять данные
    if (error) {
      setError(null)
    }
  }

  const handleBackToLogin = () => {
    navigate('/')
  }

  if (isSuccess) {
    return (
      <div className="auth-form">
        <div className="auth-form-header">
          <h2>Пароль изменен</h2>
          <p>Ваш пароль был успешно изменен</p>
        </div>

        <div className="auth-form-content">
          <div className="auth-success">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p><strong>Пароль успешно изменен</strong></p>
              <p>Теперь вы можете войти в систему с новым паролем.</p>
              <p>Все ваши активные сессии были завершены для безопасности.</p>
            </div>
          </div>
        </div>

        <div className="auth-form-footer">
          <p>
            <Button
              type="button"
              onClick={handleBackToLogin}
              className="auth-submit-btn"
            >
              Войти в систему
            </Button>
          </p>
        </div>
      </div>
    )
  }

  if (!token) {
    return (
      <div className="auth-form">
        <div className="auth-form-header">
          <h2>Ошибка</h2>
          <p>Неверная ссылка для сброса пароля</p>
        </div>

        <div className="auth-form-content">
          <div className="auth-error">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p><strong>Неверная ссылка</strong></p>
              <p>Ссылка для сброса пароля неверна или устарела.</p>
              <p>Попробуйте запросить новую ссылку для сброса пароля.</p>
            </div>
          </div>
        </div>

        <div className="auth-form-footer">
          <p>
            <Button
              type="button"
              onClick={handleBackToLogin}
              className="auth-link-btn"
            >
              ← Вернуться к входу
            </Button>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-form">
      <div className="auth-form-header">
        <h2>Новый пароль</h2>
        <p>Введите новый пароль для вашего аккаунта</p>
      </div>

      <form onSubmit={handleSubmit} className="auth-form-content" autoComplete="off">
        {error && (
          <div className="auth-error">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="newPassword">Новый пароль</label>
          <TextInput
            type="password"
            id="newPassword"
            name="newPassword"
            value={formData.newPassword}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Введите новый пароль"
            autoComplete="new-password"
            className={fieldErrors.newPassword ? 'error' : ''}
          />
          {fieldErrors.newPassword && (
            <div className="field-error">{fieldErrors.newPassword}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Подтвердите пароль</label>
          <TextInput
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Повторите новый пароль"
            autoComplete="new-password"
            className={fieldErrors.confirmPassword ? 'error' : ''}
          />
          {fieldErrors.confirmPassword && (
            <div className="field-error">{fieldErrors.confirmPassword}</div>
          )}
        </div>

        <Button
          type="submit"
          className="auth-submit-btn"
          disabled={isLoading || !formData.newPassword || !formData.confirmPassword}
        >
          {isLoading ? (
            <>
              <svg className="auth-loading-spinner" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Изменяем пароль...
            </>
          ) : (
            'Изменить пароль'
          )}
        </Button>
      </form>

      <div className="auth-form-footer">
        <p>
          <Button
            type="button"
            onClick={handleBackToLogin}
            className="auth-link-btn"
            disabled={isLoading}
          >
            ← Вернуться к входу
          </Button>
        </p>
      </div>
    </div>
  )
}

export default ResetPasswordForm
