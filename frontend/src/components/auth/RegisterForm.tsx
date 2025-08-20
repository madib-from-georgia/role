import React, { useState } from 'react'
import { Button, TextInput } from "@gravity-ui/uikit";
import { useAuth } from '../../contexts/AuthContext'
import { RegisterRequest } from '../../types/auth'
import { isValidEmail, validatePassword } from '../../utils/errorHandling'

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
  const [fieldErrors, setFieldErrors] = useState<{
    email?: string
    username?: string
    password?: string
    confirmPassword?: string
  }>({})

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setFieldErrors({})

    // Комплексная валидация формы
    const newFieldErrors: typeof fieldErrors = {}

    // Валидация email
    if (!formData.email) {
      newFieldErrors.email = 'Email обязателен для заполнения'
    } else if (!isValidEmail(formData.email)) {
      newFieldErrors.email = 'Неверный формат email адреса'
    }

    // Валидация username
    if (!formData.username) {
      newFieldErrors.username = 'Имя пользователя обязательно для заполнения'
    } else if (formData.username.length < 3) {
      newFieldErrors.username = 'Имя пользователя должно содержать минимум 3 символа'
    } else if (!/^[a-zA-Z0-9_.-]+$/.test(formData.username)) {
      newFieldErrors.username = 'Имя пользователя может содержать только буквы, цифры, точки, подчеркивания и дефисы'
    }

    // Валидация пароля
    if (!formData.password) {
      newFieldErrors.password = 'Пароль обязателен для заполнения'
    } else {
      const passwordValidation = validatePassword(formData.password)
      if (!passwordValidation.isValid) {
        newFieldErrors.password = passwordValidation.message
      }
    }

    // Проверка совпадения паролей
    if (!confirmPassword) {
      newFieldErrors.confirmPassword = 'Подтверждение пароля обязательно'
    } else if (formData.password !== confirmPassword) {
      newFieldErrors.confirmPassword = 'Пароли не совпадают'
    }

    // Если есть ошибки валидации, показываем их
    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors)
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
          <TextInput
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="example@email.com"
            className={fieldErrors.email ? 'error' : ''}
          />
          {fieldErrors.email && (
            <div className="field-error">{fieldErrors.email}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="username">Имя пользователя *</label>
          <TextInput
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Минимум 3 символа"
            className={fieldErrors.username ? 'error' : ''}
          />
          {fieldErrors.username && (
            <div className="field-error">{fieldErrors.username}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="full_name">Полное имя</label>
          <TextInput
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
          <TextInput
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Минимум 8 символов"
            className={fieldErrors.password ? 'error' : ''}
          />
          {fieldErrors.password && (
            <div className="field-error">{fieldErrors.password}</div>
          )}
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Подтвердите пароль *</label>
          <TextInput
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={confirmPassword}
            onChange={handleChange}
            disabled={isLoading}
            placeholder="Повторите пароль"
            className={fieldErrors.confirmPassword ? 'error' : ''}
          />
          {fieldErrors.confirmPassword && (
            <div className="field-error">{fieldErrors.confirmPassword}</div>
          )}
        </div>

        <Button
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
        </Button>
      </form>

      <div className="auth-form-footer">
        <p>
          Уже есть аккаунт?{' '}
          <Button
            type="button"
            onClick={onSwitchToLogin}
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

export default RegisterForm
