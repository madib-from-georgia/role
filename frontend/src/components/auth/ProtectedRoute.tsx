import React, { useEffect, useState } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import AuthModal from './AuthModal'

interface ProtectedRouteProps {
  children: React.ReactNode
  redirectPath?: string
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  redirectPath 
}) => {
  const { isAuthenticated, isLoading } = useAuth()
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [pendingPath, setPendingPath] = useState<string | null>(null)

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      // Сохраняем текущий путь для возврата после авторизации
      setPendingPath(window.location.pathname)
      setShowAuthModal(true)
    }
  }, [isAuthenticated, isLoading])

  useEffect(() => {
    // Если пользователь авторизовался и есть отложенный путь
    if (isAuthenticated && pendingPath) {
      setPendingPath(null)
      setShowAuthModal(false)
    }
  }, [isAuthenticated, pendingPath])

  if (isLoading) {
    return (
      <div className="auth-loading">
        <div className="auth-loading-content">
          <svg className="auth-loading-spinner" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>Проверяем авторизацию...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <>
        <div className="auth-required">
          <div className="auth-required-content">
            <div className="auth-required-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h2>Требуется авторизация</h2>
            <p>Для доступа к этой странице необходимо войти в систему</p>
            <button 
              className="auth-required-btn"
              onClick={() => setShowAuthModal(true)}
            >
              Войти в систему
            </button>
          </div>
        </div>

        <AuthModal 
          isOpen={showAuthModal}
          onClose={() => {
            setShowAuthModal(false)
            // При закрытии модального окна без авторизации, 
            // перенаправляем на главную страницу
            if (redirectPath) {
              window.location.href = redirectPath
            }
          }}
        />
      </>
    )
  }

  return <>{children}</>
}

export default ProtectedRoute
