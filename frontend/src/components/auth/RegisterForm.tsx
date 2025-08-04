import React, { useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { RegisterRequest } from '../../types/auth'

interface RegisterFormProps {
  onSuccess?: () => void
  onSwitchToLogin?: () => void
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onSwitchToLogin }) => {
  const { register, isLoading } = useAuth()
  const [formData, setFormData] = useState<RegisterRequest>({
    email: '',
    username: '',
    password: '',
    full_name: ''
  })
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Проверка совпадения паролей
    if (formData.password !== confirmPassword) {
      setError('Пароли не совпадают')
      return
    }

    // Проверка длины пароля
    if (formData.password.length < 8) {
      setError('Пароль должен содержать минимум 8 символов')
      return
    }

    try {
      const registrationData = {
        ...formData,
        full_name: formData.full_name || undefined
      }
      await register(registrationData)
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка регистрации')
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    
    if (name === 'confirmPassword') {
      setConfirmPassword(value)
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const isFormValid = 
    formData.email && 
    formData.username && 
    formData.password && 
    confirmPassword &&
    formData.password === confirmPassword &&
    formData.password.length >= 8 &&
    formData.username.length >= 3

  return (
    <div className="auth-form">
      <div className="auth-form-header">
        <h2>Регистрация</h2>
        <p>Создайте аккаунт для анализа персонажей</p>
      </div>

      <form onSubmit={handleSubmit} className="auth-form-content">
        {error && (
          <div className="auth-error">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="email">Email *</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            disabled={isLoading}
            placeholder="example@email.com"
          />
        </div>

        <div className="form-group">
          <label htmlFor="username">Имя пользователя *</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
            disabled={isLoading}
            placeholder="Минимум 3 символа"
            minLength={3}
          />
        </div>

        <div className="form-group">
          <label htmlFor="full_name">Полное имя</label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Ваше имя и фамилия"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Пароль *</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            disabled={isLoading}
            placeholder="Минимум 8 символов"
            minLength={8}
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Подтвердите пароль *</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={confirmPassword}
            onChange={handleChange}
            required
            disabled={isLoading}
            placeholder="Повторите пароль"
            minLength={8}
          />
          {confirmPassword && formData.password !== confirmPassword && (
            <div className="field-error">Пароли не совпадают</div>
          )}
        </div>

        <button 
          type="submit" 
          className="auth-submit-btn"
          disabled={isLoading || !isFormValid}
        >
          {isLoading ? (
            <>
              <svg className="auth-loading-spinner" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Регистрируемся...
            </>
          ) : (
            'Зарегистрироваться'
          )}
        </button>
      </form>

      <div className="auth-form-footer">
        <p>
          Уже есть аккаунт?{' '}
          <button 
            type="button" 
            onClick={onSwitchToLogin}
            className="auth-link-btn"
            disabled={isLoading}
          >
            Войти
          </button>
        </p>
      </div>
    </div>
  )
}

export default RegisterForm
