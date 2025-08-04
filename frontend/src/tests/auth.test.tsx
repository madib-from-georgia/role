import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'

import { AuthProvider, useAuth } from '../contexts/AuthContext'
import LoginForm from '../components/auth/LoginForm'
import RegisterForm from '../components/auth/RegisterForm'
import ProtectedRoute from '../components/auth/ProtectedRoute'
import AuthGuard from '../components/auth/AuthGuard'
import { authApi } from '../services/api/auth'

// Mock API
vi.mock('../services/api/auth', () => ({
  authApi: {
    login: vi.fn(),
    register: vi.fn(),
    logout: vi.fn(),
    refreshToken: vi.fn(),
    getProfile: vi.fn(),
    updateProfile: vi.fn(),
  }
}))

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
global.localStorage = localStorageMock

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}

// Helper component to access auth context
const AuthTestComponent: React.FC = () => {
  const auth = useAuth()
  return (
    <div>
      <div data-testid="is-authenticated">{auth.isAuthenticated.toString()}</div>
      <div data-testid="is-loading">{auth.isLoading.toString()}</div>
      <div data-testid="user-email">{auth.user?.email || 'none'}</div>
      <button data-testid="login-btn" onClick={() => auth.login('test@test.com', 'password')}>
        Login
      </button>
      <button data-testid="logout-btn" onClick={() => auth.logout()}>
        Logout
      </button>
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('should start with unauthenticated state', async () => {
    render(
      <TestWrapper>
        <AuthTestComponent />
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
    })

    expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('user-email')).toHaveTextContent('none')
  })

  it('should authenticate user on successful login', async () => {
    const mockTokens = {
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 3600
    }

    const mockUser = {
      id: 1,
      email: 'test@test.com',
      username: 'testuser',
      full_name: 'Test User',
      is_active: true,
      created_at: '2023-01-01'
    }

    authApi.login.mockResolvedValue(mockTokens)
    authApi.getProfile.mockResolvedValue(mockUser)

    render(
      <TestWrapper>
        <AuthTestComponent />
      </TestWrapper>
    )

    // Wait for initial loading to complete
    await waitFor(() => {
      expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
    })

    // Click login button
    fireEvent.click(screen.getByTestId('login-btn'))

    await waitFor(() => {
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true')
    })

    expect(screen.getByTestId('user-email')).toHaveTextContent('test@test.com')
    expect(authApi.login).toHaveBeenCalledWith('test@test.com', 'password')
    expect(authApi.getProfile).toHaveBeenCalledWith('access-token')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', 'access-token')
    expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', 'refresh-token')
  })

  it('should logout user and clear tokens', async () => {
    // First setup authenticated state
    const mockTokens = {
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 3600
    }

    const mockUser = {
      id: 1,
      email: 'test@test.com',
      username: 'testuser',
      full_name: 'Test User',
      is_active: true,
      created_at: '2023-01-01'
    }

    authApi.login.mockResolvedValue(mockTokens)
    authApi.getProfile.mockResolvedValue(mockUser)
    authApi.logout.mockResolvedValue({ message: 'Success', success: true })

    render(
      <TestWrapper>
        <AuthTestComponent />
      </TestWrapper>
    )

    // Login first
    await waitFor(() => {
      expect(screen.getByTestId('is-loading')).toHaveTextContent('false')
    })

    fireEvent.click(screen.getByTestId('login-btn'))

    await waitFor(() => {
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true')
    })

    // Now logout
    fireEvent.click(screen.getByTestId('logout-btn'))

    await waitFor(() => {
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false')
    })

    expect(screen.getByTestId('user-email')).toHaveTextContent('none')
    expect(authApi.logout).toHaveBeenCalledWith('access-token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
  })
})

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render login form fields', () => {
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    )

    expect(screen.getByText('Вход в систему')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Войти' })).toBeInTheDocument()
  })

  it('should show validation for empty fields', () => {
    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    )

    const submitBtn = screen.getByRole('button', { name: 'Войти' })
    expect(submitBtn).toBeDisabled()

    // Fill email only
    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@test.com' }
    })

    expect(submitBtn).toBeDisabled()

    // Fill password too
    fireEvent.change(screen.getByLabelText('Пароль'), {
      target: { value: 'password123' }
    })

    expect(submitBtn).not.toBeDisabled()
  })

  it('should call onSuccess on successful login', async () => {
    const mockOnSuccess = vi.fn()
    const mockTokens = {
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 3600
    }

    const mockUser = {
      id: 1,
      email: 'test@test.com',
      username: 'testuser',
      full_name: 'Test User',
      is_active: true,
      created_at: '2023-01-01'
    }

    authApi.login.mockResolvedValue(mockTokens)
    authApi.getProfile.mockResolvedValue(mockUser)

    render(
      <TestWrapper>
        <LoginForm onSuccess={mockOnSuccess} />
      </TestWrapper>
    )

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@test.com' }
    })
    fireEvent.change(screen.getByLabelText('Пароль'), {
      target: { value: 'password123' }
    })

    fireEvent.click(screen.getByRole('button', { name: 'Войти' }))

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('should show error on failed login', async () => {
    authApi.login.mockRejectedValue(new Error('Invalid credentials'))

    render(
      <TestWrapper>
        <LoginForm />
      </TestWrapper>
    )

    fireEvent.change(screen.getByLabelText('Email'), {
      target: { value: 'test@test.com' }
    })
    fireEvent.change(screen.getByLabelText('Пароль'), {
      target: { value: 'wrongpassword' }
    })

    fireEvent.click(screen.getByRole('button', { name: 'Войти' }))

    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument()
    })
  })
})

describe('RegisterForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render registration form fields', () => {
    render(
      <TestWrapper>
        <RegisterForm />
      </TestWrapper>
    )

    expect(screen.getByText('Регистрация')).toBeInTheDocument()
    expect(screen.getByLabelText('Email *')).toBeInTheDocument()
    expect(screen.getByLabelText('Имя пользователя *')).toBeInTheDocument()
    expect(screen.getByLabelText('Полное имя')).toBeInTheDocument()
    expect(screen.getByLabelText('Пароль *')).toBeInTheDocument()
    expect(screen.getByLabelText('Подтвердите пароль *')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Зарегистрироваться' })).toBeInTheDocument()
  })

  it('should validate password confirmation', () => {
    render(
      <TestWrapper>
        <RegisterForm />
      </TestWrapper>
    )

    fireEvent.change(screen.getByLabelText('Пароль *'), {
      target: { value: 'password123' }
    })
    fireEvent.change(screen.getByLabelText('Подтвердите пароль *'), {
      target: { value: 'different' }
    })

    expect(screen.getByText('Пароли не совпадают')).toBeInTheDocument()
  })

  it('should register user successfully', async () => {
    const mockOnSuccess = vi.fn()
    
    authApi.register.mockResolvedValue({ message: 'Success', success: true })
    authApi.login.mockResolvedValue({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 3600
    })
    authApi.getProfile.mockResolvedValue({
      id: 1,
      email: 'newuser@test.com',
      username: 'newuser',
      full_name: 'New User',
      is_active: true,
      created_at: '2023-01-01'
    })

    render(
      <TestWrapper>
        <RegisterForm onSuccess={mockOnSuccess} />
      </TestWrapper>
    )

    fireEvent.change(screen.getByLabelText('Email *'), {
      target: { value: 'newuser@test.com' }
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

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })

    expect(authApi.register).toHaveBeenCalledWith({
      email: 'newuser@test.com',
      username: 'newuser',
      password: 'password123',
      full_name: 'New User'
    })
  })
})

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('should show auth required for unauthenticated user', async () => {
    render(
      <TestWrapper>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('Требуется авторизация')).toBeInTheDocument()
    })

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('should show protected content for authenticated user', async () => {
    // Mock authenticated state
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'access_token') return 'access-token'
      if (key === 'refresh_token') return 'refresh-token'
      return null
    })

    authApi.getProfile.mockResolvedValue({
      id: 1,
      email: 'test@test.com',
      username: 'testuser',
      full_name: 'Test User',
      is_active: true,
      created_at: '2023-01-01'
    })

    render(
      <TestWrapper>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('Protected Content')).toBeInTheDocument()
    })

    expect(screen.queryByText('Требуется авторизация')).not.toBeInTheDocument()
  })
})

describe('AuthGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  it('should show fallback for unauthenticated user', async () => {
    render(
      <TestWrapper>
        <AuthGuard fallback={<div>Please login</div>}>
          <div>Authenticated Content</div>
        </AuthGuard>
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('Please login')).toBeInTheDocument()
    })

    expect(screen.queryByText('Authenticated Content')).not.toBeInTheDocument()
  })

  it('should show authenticated content for authenticated user', async () => {
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'access_token') return 'access-token'
      if (key === 'refresh_token') return 'refresh-token'
      return null
    })

    authApi.getProfile.mockResolvedValue({
      id: 1,
      email: 'test@test.com',
      username: 'testuser',
      full_name: 'Test User',
      is_active: true,
      created_at: '2023-01-01'
    })

    render(
      <TestWrapper>
        <AuthGuard fallback={<div>Please login</div>}>
          <div>Authenticated Content</div>
        </AuthGuard>
      </TestWrapper>
    )

    await waitFor(() => {
      expect(screen.getByText('Authenticated Content')).toBeInTheDocument()
    })

    expect(screen.queryByText('Please login')).not.toBeInTheDocument()
  })
})
