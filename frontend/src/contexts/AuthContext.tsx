import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, AuthContextType, LoginRequest, RegisterRequest } from '../types/auth'
import { authApi } from '../services/api/auth'

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

  const isAuthenticated = !!user && !!tokens?.access

  // Загрузка токенов из localStorage при инициализации
  useEffect(() => {
    const loadTokensFromStorage = () => {
      try {
        const accessToken = localStorage.getItem('access_token')
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (accessToken && refreshToken) {
          setTokens({ access: accessToken, refresh: refreshToken })
          // Загружаем профиль пользователя
          loadUserProfile(accessToken)
        } else {
          setIsLoading(false)
        }
      } catch (error) {
        console.error('Error loading tokens from storage:', error)
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
      setIsLoading(true)
      const tokenData = await authApi.login({ email, password })
      
      saveTokens(tokenData)
      await loadUserProfile(tokenData.access_token)
    } catch (error) {
      clearTokens()
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (data: RegisterRequest) => {
    try {
      setIsLoading(true)
      await authApi.register(data)
      // После регистрации автоматически логинимся
      await login(data.email, data.password)
    } catch (error) {
      clearTokens()
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      if (tokens?.access) {
        await authApi.logout(tokens.access)
      }
    } catch (error) {
      console.error('Error during logout:', error)
    } finally {
      clearTokens()
    }
  }

  const refreshToken = async () => {
    if (!tokens?.refresh) {
      throw new Error('No refresh token available')
    }

    try {
      const tokenData = await authApi.refreshToken(tokens.refresh)
      saveTokens(tokenData)
    } catch (error) {
      // Если refresh токен недействителен, выходим из системы
      await logout()
      throw error
    }
  }

  const getAuthHeader = (): string | null => {
    return tokens?.access ? `Bearer ${tokens.access}` : null
  }

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
    getAuthHeader
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}