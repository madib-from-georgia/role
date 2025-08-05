import { User, LoginRequest, RegisterRequest, TokenResponse, AuthResponse } from '../../types/auth'

const API_BASE_URL = 'http://localhost:8000/api'

class AuthApi {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    const response = await fetch(url, config)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const error = new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      // Добавляем информацию для системы обработки ошибок
      ;(error as any).response = {
        status: response.status,
        data: errorData
      }
      ;(error as any).status = response.status
      ;(error as any).detail = errorData.detail
      throw error
    }

    return response.json()
  }

  async login(credentials: LoginRequest): Promise<TokenResponse> {
    return this.request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async logout(accessToken: string): Promise<AuthResponse> {
    return this.request<AuthResponse>('/auth/logout', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    return this.request<TokenResponse>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
  }

  async getProfile(accessToken: string): Promise<User> {
    return this.request<User>('/auth/me', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
  }

  async updateProfile(accessToken: string, data: Partial<User>): Promise<User> {
    return this.request<User>('/auth/me', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(data),
    })
  }

  async changePassword(
    accessToken: string, 
    currentPassword: string, 
    newPassword: string
  ): Promise<AuthResponse> {
    const requestBody = {
      current_password: currentPassword,
      new_password: newPassword,
    }
    
    const url = `${API_BASE_URL}/auth/change-password`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify(requestBody),
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const error = new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      ;(error as any).response = {
        status: response.status,
        data: errorData
      }
      ;(error as any).status = response.status
      ;(error as any).detail = errorData.detail
      throw error
    }

    return response.json()
  }
}

export const authApi = new AuthApi()
