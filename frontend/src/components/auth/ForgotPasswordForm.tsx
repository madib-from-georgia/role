import React, { useState } from 'react'
import { Button, TextInput } from "@gravity-ui/uikit";
import { isValidEmail } from '../../utils/errorHandling'

interface ForgotPasswordFormProps {
  onSuccess?: () => void
  onBackToLogin?: () => void
}

const ForgotPasswordForm: React.FC<ForgotPasswordFormProps> = ({ onSuccess, onBackToLogin }) => {
  const [formData, setFormData] = useState({
    email: ''
  })
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<{email?: string}>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setFieldErrors({})

    // Валидация перед отправкой
    const newFieldErrors: {email?: string} = {}

    if (!formData.email) {
      newFieldErrors.email = 'Email обязателен для заполнения'
    } else if (!isValidEmail(formData.email)) {
      newFieldErrors.email = 'Неверный формат email адреса'
    }

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors)
      return
    }

    try {
      setIsLoading(true)
      
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: formData.email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Ошибка при отправке запроса')
      }

      setIsSuccess(true)
      onSuccess?.()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Ошибка при отправке запроса'
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

  if (isSuccess) {
    return (
      <div className="auth-form">
        <div className="auth-form-header">
          <h2>Письмо отправлено</h2>
          <p>Проверьте вашу электронную почту</p>
        </div>

        <div className="auth-form-content">
          <div className="auth-success">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p><strong>Инструкции отправлены</strong></p>
              <p>Если пользователь с email <strong>{formData.email}</strong> существует, на него будет отправлено письмо с инструкциями по сбросу пароля.</p>
              <p>Проверьте папку "Спам", если письмо не пришло в течение нескольких минут.</p>
            </div>
          </div>
        </div>

        <div className="auth-form-footer">
          <p>
            <Button
              type="button"
              onClick={onBackToLogin}
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
        <h2>Забыли пароль?</h2>
        <p>Введите ваш email для получения инструкций по сбросу пароля</p>
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
          <label htmlFor="email">Email</label>
          <TextInput
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="example@email.com"
            autoComplete="email"
            className={fieldErrors.email ? 'error' : ''}
          />
          {fieldErrors.email && (
            <div className="field-error">{fieldErrors.email}</div>
          )}
        </div>

        <Button
          type="submit"
          className="auth-submit-btn"
          disabled={isLoading || !formData.email}
        >
          {isLoading ? (
            <>
              <svg className="auth-loading-spinner" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Отправляем...
            </>
          ) : (
            'Отправить инструкции'
          )}
        </Button>
      </form>

      <div className="auth-form-footer">
        <p>
          Вспомнили пароль?{' '}
          <Button
            type="button"
            onClick={onBackToLogin}
            className="auth-link-btn"
            disabled={isLoading}
          >
            Войти
          </Button>
        </p>
      </div>
    </div>
  )
}

export default ForgotPasswordForm
