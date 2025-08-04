import React, { useEffect } from 'react'
import { useAuth } from '../../contexts/AuthContext'

interface AuthGuardProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  onAuthRequired?: () => void
}

/**
 * AuthGuard проверяет авторизацию без блокировки рендера.
 * Используется для компонентов, которые могут показываться
 * как авторизованным, так и неавторизованным пользователям,
 * но с разной функциональностью.
 */
const AuthGuard: React.FC<AuthGuardProps> = ({ 
  children, 
  fallback = null,
  onAuthRequired 
}) => {
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !isAuthenticated && onAuthRequired) {
      onAuthRequired()
    }
  }, [isAuthenticated, isLoading, onAuthRequired])

  if (isLoading) {
    return (
      <div className="auth-guard-loading">
        <svg className="auth-loading-spinner small" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

export default AuthGuard
