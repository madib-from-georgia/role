import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, AuthContextType, RegisterRequest } from '../types/auth'
import { authApi } from '../services/api/auth'
import { handleAuthError, handleRegistrationError, isValidEmail, validatePassword } from '../utils/errorHandling'
import { config } from '../config'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [tokens, setTokens] = useState<{access: string, refresh: string} | null>(null)

  const isAuthenticated = !!user && (!!tokens?.access || !config.authEnabled)

  // Загрузка токенов из localStorage при инициализации
  useEffect(() => {
    const loadTokensFromStorage = async () => {
      try {
        // Если авторизация отключена, используем mock пользователя
        if (!config.authEnabled) {
          setUser(config.mockUser)
          setIsLoading(false)
          return
        }
        
        const accessToken = localStorage.getItem('access_token')
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (accessToken && refreshToken) {
          setTokens({ access: accessToken, refresh: refreshToken })
          // Загружаем профиль пользователя
          await loadUserProfile(accessToken)
        } else {
          setIsLoading(false)
        }
      } catch (error) {
        console.error('Error loading tokens from storage:', error)
        clearTokens()
        setIsLoading(false)
      }
    }

    loadTokensFromStorage()
  }, [])

  // Загрузка профиля пользователя
  const loadUserProfile = async (token: string) => {
    try {
      const userData = await authApi.getProfile(token)
      setUser(userData)
    } catch (error) {
      console.error('Error loading user profile:', error)
      // Если токен недействителен, очищаем авторизацию
      await logout()
    } finally {
      setIsLoading(false)
    }
  }

  // Сохранение токенов
  const saveTokens = (tokenData: { access_token: string, refresh_token: string }) => {
    localStorage.setItem('access_token', tokenData.access_token)
    localStorage.setItem('refresh_token', tokenData.refresh_token)
    setTokens({ access: tokenData.access_token, refresh: tokenData.refresh_token })
  }

  // Очистка токенов
  const clearTokens = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setTokens(null)
    setUser(null)
  }

  const login = async (email: string, password: string) => {
    try {
      // Если авторизация отключена, просто устанавливаем mock пользователя
      if (!config.authEnabled) {
        setUser(config.mockUser)
        return
      }
      
      // НЕ меняем isLoading чтобы избежать перемонтирования компонентов!
      
      // Валидация email
      if (!isValidEmail(email)) {
        throw new Error('Неверный формат email адреса')
      }
      
      // Валидация пароля
      if (!password || password.length < 1) {
        throw new Error('Пароль не может быть пустым')
      }
      
      const tokenData = await authApi.login({ email, password })
      
      saveTokens(tokenData)
      await loadUserProfile(tokenData.access_token)
    } catch (error) {
      clearTokens()
      // Используем улучшенную обработку ошибок
      const errorMessage = handleAuthError(error)
      throw new Error(errorMessage)
    }
  }

  const register = async (data: RegisterRequest) => {
    try {
      // Если авторизация отключена, просто устанавливаем mock пользователя
      if (!config.authEnabled) {
        setUser(config.mockUser)
        return
      }
      
      setIsLoading(true)
      
      // Валидация email
      if (!isValidEmail(data.email)) {
        throw new Error('Неверный формат email адреса')
      }
      
      // Валидация пароля
      const passwordValidation = validatePassword(data.password)
      if (!passwordValidation.isValid) {
        throw new Error(passwordValidation.message)
      }
      
      // Валидация username
      if (!data.username || data.username.length < 3) {
        throw new Error('Имя пользователя должно содержать минимум 3 символа')
      }
      
      await authApi.register(data)
      // После регистрации автоматически логинимся
      await login(data.email, data.password)
    } catch (error) {
      clearTokens()
      // Используем улучшенную обработку ошибок для регистрации
      const errorMessage = handleRegistrationError(error)
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      // Если авторизация отключена, просто очищаем состояние
      if (!config.authEnabled) {
        clearTokens()
        return
      }
      
      if (tokens?.access) {
        await authApi.logout(tokens.access)
      }
    } catch (error) {
      console.error('Error during logout:', error)
    } finally {
      clearTokens()
    }
  }

  const clearAuth = () => {
    clearTokens()
    setIsLoading(false)
  }

  const refreshToken = async () => {
    try {
      // Если авторизация отключена, ничего не делаем
      if (!config.authEnabled) {
        return
      }
      
      if (!tokens?.refresh) {
        throw new Error('No refresh token available')
      }
      
      const newTokens = await authApi.refreshToken(tokens.refresh)
      saveTokens(newTokens)
    } catch (error) {
      console.error('Error refreshing token:', error)
      clearTokens()
      throw error
    }
  }

  const getAuthHeader = (): string | null => {
    // Если авторизация отключена, возвращаем null
    if (!config.authEnabled) {
      return null
    }
    
    return tokens?.access ? `Bearer ${tokens.access}` : null
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    clearAuth,
    refreshToken,
    getAuthHeader
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
