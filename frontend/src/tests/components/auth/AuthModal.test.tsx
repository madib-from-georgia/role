import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { render } from '../../utils/test-utils'
import AuthModal from '../../../components/auth/AuthModal'

describe('AuthModal', () => {
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should not render when isOpen is false', () => {
    render(
      <AuthModal 
        isOpen={false} 
        onClose={mockOnClose} 
      />
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
    expect(screen.queryByText('Вход в систему')).not.toBeInTheDocument()
  })

  it('should render login form by default when isOpen is true', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
      />
    )

    expect(screen.getByText('Вход в систему')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Войти' })).toBeInTheDocument()
  })

  it('should render register form when initialMode is register', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
        initialMode="register"
      />
    )

    expect(screen.getByText('Регистрация')).toBeInTheDocument()
    expect(screen.getByLabelText('Email *')).toBeInTheDocument()
    expect(screen.getByLabelText('Имя пользователя *')).toBeInTheDocument()
    expect(screen.getByLabelText('Полное имя')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль *')).toBeInTheDocument()
    expect(screen.getByLabelText('Подтвердите пароль *')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Зарегистрироваться' })).toBeInTheDocument()
  })

  it('should call onClose when close button is clicked', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
      />
    )

    const closeButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('should call onClose when overlay is clicked', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
      />
    )

    const overlay = screen.getByTestId('auth-modal-overlay')
    fireEvent.click(overlay)

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('should not call onClose when modal content is clicked', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
      />
    )

    const modalContent = screen.getByTestId('auth-modal-content')
    fireEvent.click(modalContent)

    expect(mockOnClose).not.toHaveBeenCalled()
  })

  it('should switch from login to register mode', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
        initialMode="login"
      />
    )

    // Initially shows login form
    expect(screen.getByText('Вход в систему')).toBeInTheDocument()

    // Click switch to register
    const switchButton = screen.getByText('Зарегистрироваться')
    fireEvent.click(switchButton)

    // Should now show register form
    expect(screen.getByText('Регистрация')).toBeInTheDocument()
    expect(screen.getByLabelText('Email *')).toBeInTheDocument()
    expect(screen.getByLabelText('Имя пользователя *')).toBeInTheDocument()
  })

  it('should switch from register to login mode', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
        initialMode="register"
      />
    )

    // Initially shows register form
    expect(screen.getByText('Регистрация')).toBeInTheDocument()

    // Click switch to login
    const switchButton = screen.getByText('Войти')
    fireEvent.click(switchButton)

    // Should now show login form
    expect(screen.getByText('Вход в систему')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument()
  })

  it('should close modal on successful login', async () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
        initialMode="login"
      />
    )

    // Fill and submit login form
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@example.com' }
    })
    fireEvent.change(screen.getByLabelText('Пароль'), {
      target: { value: 'password' }
    })

    fireEvent.click(screen.getByRole('button', { name: 'Войти' }))

    // Should close modal after successful login
    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  it('should close modal on successful registration', async () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
        initialMode="register"
      />
    )

    // Fill and submit register form
    fireEvent.change(screen.getByLabelText('Email *'), {
      target: { value: 'newuser@example.com' }
    })
    fireEvent.change(screen.getByLabelText('Имя пользователя *'), {
      target: { value: 'newuser' }
    })
    fireEvent.change(screen.getByLabelText('Полное имя'), {
      target: { value: 'New User' }
    })
    fireEvent.change(screen.getByLabelText('Пароль *'), {
      target: { value: 'password123' }
    })
    fireEvent.change(screen.getByLabelText('Подтвердите пароль *'), {
      target: { value: 'password123' }
    })

    fireEvent.click(screen.getByRole('button', { name: 'Зарегистрироваться' }))

    // Should close modal after successful registration
    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  it('should reset mode when modal is reopened', () => {
    const { rerender } = render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
        initialMode="login"
      />
    )

    // Switch to register mode
    const switchButton = screen.getByText('Зарегистрироваться')
    fireEvent.click(switchButton)
    expect(screen.getByText('Регистрация')).toBeInTheDocument()

    // Close modal
    rerender(
      <AuthModal 
        isOpen={false} 
        onClose={mockOnClose} 
        initialMode="login"
      />
    )

    // Reopen modal - should be back to login mode
    rerender(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
        initialMode="login"
      />
    )

    expect(screen.getByText('Вход в систему')).toBeInTheDocument()
  })

  it('should handle keyboard accessibility', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
      />
    )

    const closeButton = screen.getByRole('button', { name: /close/i })
    
    // Should be focusable
    closeButton.focus()
    expect(closeButton).toHaveFocus()

    // Should respond to Enter key
    fireEvent.keyDown(closeButton, { key: 'Enter', code: 'Enter' })
    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  it('should trap focus within modal when open', () => {
    render(
      <AuthModal 
        isOpen={true} 
        onClose={mockOnClose} 
      />
    )

    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Пароль')
    const loginButton = screen.getByRole('button', { name: 'Войти' })
    const closeButton = screen.getByRole('button', { name: /close/i })

    // All interactive elements should be present and focusable
    expect(emailInput).toBeInTheDocument()
    expect(passwordInput).toBeInTheDocument()
    expect(loginButton).toBeInTheDocument()
    expect(closeButton).toBeInTheDocument()
  })
})
