import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { authApi } from '../services/api/auth'

interface ChangePasswordFormProps {
  onSuccess?: () => void
  onCancel?: () => void
}

const ChangePasswordForm: React.FC<ChangePasswordFormProps> = ({
  onSuccess,
  onCancel
}) => {
  const { getAuthHeader, clearAuth } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  })
  
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
    setError(null)
  }

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }))
  }

  const validateForm = (): boolean => {
    if (!formData.currentPassword) {
      setError('Введите текущий пароль')
      return false
    }
    
    if (!formData.newPassword) {
      setError('Введите новый пароль')
      return false
    }
    
    if (formData.newPassword.length < 8) {
      setError('Новый пароль должен содержать минимум 8 символов')
      return false
    }
    
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Пароли не совпадают')
      return false
    }
    
    if (formData.currentPassword === formData.newPassword) {
      setError('Новый пароль должен отличаться от текущего')
      return false
    }
    
    return true
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const authHeader = getAuthHeader()
      if (!authHeader) {
        throw new Error('Токен авторизации не найден')
      }

      await authApi.changePassword(
        authHeader.replace('Bearer ', ''),
        formData.currentPassword,
        formData.newPassword
      )

      // Успех - показываем сообщение и выходим из системы
      alert('Пароль успешно изменен! Вы будете перенаправлены на страницу входа.')
      
      if (onSuccess) {
        onSuccess()
      }
      
      // Выходим из системы без вызова API logout, так как токены уже отозваны
      // Просто очищаем локальное состояние
      clearAuth()
      
    } catch (err: unknown) {
      console.error('Change password error:', err)
      setError(err instanceof Error ? err.message : 'Ошибка смены пароля')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    setError(null)
    if (onCancel) {
      onCancel()
    }
  }

  return (
    <div className="change-password-form">
      <h3>Смена пароля</h3>
      
      {error && (
        <div className="alert alert-error">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Текущий пароль</label>
          <div className="password-input-group">
            <input
              type={showPasswords.current ? 'text' : 'password'}
              name="currentPassword"
              value={formData.currentPassword}
              onChange={handleChange}
              disabled={isLoading}
              required
              minLength={8}
              placeholder="Введите текущий пароль"
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => togglePasswordVisibility('current')}
              disabled={isLoading}
            >
              {showPasswords.current ? (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L12 12m-2.122-2.122L7.757 7.757M9.878 9.878l4.242 4.242m0 0L12 12m2.121-2.122L16.243 7.757" />
                </svg>
              ) : (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Новый пароль</label>
          <div className="password-input-group">
            <input
              type={showPasswords.new ? 'text' : 'password'}
              name="newPassword"
              value={formData.newPassword}
              onChange={handleChange}
              disabled={isLoading}
              required
              minLength={8}
              placeholder="Введите новый пароль (минимум 8 символов)"
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => togglePasswordVisibility('new')}
              disabled={isLoading}
            >
              {showPasswords.new ? (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L12 12m-2.122-2.122L7.757 7.757M9.878 9.878l4.242 4.242m0 0L12 12m2.121-2.122L16.243 7.757" />
                </svg>
              ) : (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Подтвердите новый пароль</label>
          <div className="password-input-group">
            <input
              type={showPasswords.confirm ? 'text' : 'password'}
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              disabled={isLoading}
              required
              minLength={8}
              placeholder="Повторите новый пароль"
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => togglePasswordVisibility('confirm')}
              disabled={isLoading}
            >
              {showPasswords.confirm ? (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L12 12m-2.122-2.122L7.757 7.757M9.878 9.878l4.242 4.242m0 0L12 12m2.121-2.122L16.243 7.757" />
                </svg>
              ) : (
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Изменение...' : 'Изменить пароль'}
          </button>
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={handleCancel}
            disabled={isLoading}
          >
            Отмена
          </button>
        </div>
      </form>

      <div className="password-requirements">
        <h4>Требования к паролю:</h4>
        <ul>
          <li>Минимум 8 символов</li>
          <li>Должен отличаться от текущего пароля</li>
          <li>Рекомендуется использовать комбинацию букв, цифр и символов</li>
        </ul>
      </div>
    </div>
  )
}

export default ChangePasswordForm
