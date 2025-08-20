import React, { useState } from 'react'
import { Button, TextInput } from "@gravity-ui/uikit";
import { useAuth } from '../../contexts/AuthContext'
import { isValidEmail } from '../../utils/errorHandling'

interface LoginFormProps {
  onSuccess?: () => void
  onSwitchToRegister?: () => void
  onForgotPassword?: () => void
}

const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onSwitchToRegister, onForgotPassword }) => {
  const { login } = useAuth()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<{email?: string, password?: string}>({})
  const [showRegistrationSuggestion, setShowRegistrationSuggestion] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setFieldErrors({})
    setShowRegistrationSuggestion(false)

    // Валидация перед отправкой
    const newFieldErrors: {email?: string, password?: string} = {}

    if (!formData.email) {
      newFieldErrors.email = 'Email обязателен для заполнения'
    } else if (!isValidEmail(formData.email)) {
      newFieldErrors.email = 'Неверный формат email адреса'
    }

    if (!formData.password) {
      newFieldErrors.password = 'Пароль обязателен для заполнения'
    }

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors)
      return
    }

    try {
      setIsLoading(true)
      await login(formData.email, formData.password)
      onSuccess?.()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Ошибка входа в систему'
      setError(errorMessage)

      // Показываем предложение регистрации если пользователь не найден
      if (errorMessage.includes('не найден') || errorMessage.includes('Проверьте email или зарегистрируйтесь')) {
        setShowRegistrationSuggestion(true)
      }
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
      setShowRegistrationSuggestion(false)
    }
  }

  return (
    <div className="auth-form">
      <div className="auth-form-header">
        <h2>Авторизация</h2>
        <p>Войдите в свой аккаунт для доступа к проектам</p>
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

        {showRegistrationSuggestion && (
          <div className="auth-suggestion">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p><strong>Нет аккаунта?</strong></p>
              <p>Похоже, пользователь с таким email не зарегистрирован.</p>
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="auth-suggestion-btn"
                disabled={isLoading}
              >
                Зарегистрироваться сейчас
              </button>
            </div>
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
            autoComplete="new-email"
            className={fieldErrors.email ? 'error' : ''}
          />
          {fieldErrors.email && (
            <div className="field-error">{fieldErrors.email}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="password">Пароль</label>
          <TextInput
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Введите пароль"
            autoComplete="new-password"
            className={fieldErrors.password ? 'error' : ''}
          />
          {fieldErrors.password && (
            <div className="field-error">{fieldErrors.password}</div>
          )}
        </div>

        <Button
          type="submit"
          className="auth-submit-btn"
          disabled={isLoading || !formData.email || !formData.password}
        >
          {isLoading ? (
            <>
              <svg className="auth-loading-spinner" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Входим...
            </>
          ) : (
            'Войти'
          )}
        </Button>
      </form>

      <div className="auth-form-footer">
        Нет аккаунта?{' '}
        <Button
          type="button"
          onClick={onSwitchToRegister}
          className="auth-link-btn"
          disabled={isLoading}
        >
          Зарегистрироваться
        </Button>
      </div>

      <div className="auth-form-footer">
        <Button
          type="button"
          onClick={onForgotPassword}
          className="auth-link-btn"
          disabled={isLoading}
        >
          Забыли пароль?
        </Button>
      </div>
    </div>
  )
}

export default LoginForm
