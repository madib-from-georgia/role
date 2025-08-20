import React, { useState, useCallback } from 'react'
import { Button } from "@gravity-ui/uikit";
import LoginForm from './LoginForm'
import RegisterForm from './RegisterForm'
import ForgotPasswordForm from './ForgotPasswordForm'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  initialMode?: 'login' | 'register' | 'forgot-password'
}

const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  initialMode = 'login'
}) => {
  const [mode, setMode] = useState<'login' | 'register' | 'forgot-password'>(initialMode)

  const handleSuccess = useCallback(() => {
    onClose()
  }, [onClose])

  const handleSwitchMode = useCallback(() => {
    setMode(prev => prev === 'login' ? 'register' : 'login')
  }, [])

  const handleForgotPassword = useCallback(() => {
    setMode('forgot-password')
  }, [])

  const handleBackToLogin = useCallback(() => {
    setMode('login')
  }, [])

  if (!isOpen) return null

  return (
    <div className="auth-modal-overlay" onClick={onClose} data-testid="auth-modal-overlay">
      <div className="auth-modal" onClick={(e) => e.stopPropagation()} data-testid="auth-modal-content">
        <Button
          className="auth-modal-close"
          onClick={onClose}
        >
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </Button>

        {mode === 'login' ? (
          <LoginForm
            onSuccess={handleSuccess}
            onSwitchToRegister={handleSwitchMode}
            onForgotPassword={handleForgotPassword}
          />
        ) : mode === 'register' ? (
          <RegisterForm
            onSuccess={handleSuccess}
            onSwitchToLogin={handleSwitchMode}
          />
        ) : (
          <ForgotPasswordForm
            onSuccess={handleSuccess}
            onBackToLogin={handleBackToLogin}
          />
        )}
      </div>
    </div>
  )
}

export default AuthModal
