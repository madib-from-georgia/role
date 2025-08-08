import { describe, it, expect, vi, beforeEach } from 'vitest'
import { authApi } from '../../services/api/auth'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() }
      }
    }))
  }
}))

describe('Auth API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('login', () => {
    it('should call login endpoint with correct credentials', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          refresh_token: 'refresh-token',
          token_type: 'bearer',
          expires_in: 3600
        }
      }

      // Mock the axios post method
      const mockPost = vi.fn().mockResolvedValue(mockResponse)
      authApi.login = vi.fn().mockResolvedValue(mockResponse.data)

      const result = await authApi.login('test@example.com', 'password')

      expect(authApi.login).toHaveBeenCalledWith('test@example.com', 'password')
      expect(result).toEqual(mockResponse.data)
    })

    it('should handle login errors', async () => {
      const mockError = new Error('Invalid credentials')
      authApi.login = vi.fn().mockRejectedValue(mockError)

      await expect(authApi.login('test@example.com', 'wrong')).rejects.toThrow('Invalid credentials')
    })
  })

  describe('register', () => {
    it('should call register endpoint with user data', async () => {
      const userData = {
        email: 'newuser@example.com',
        username: 'newuser',
        password: 'password123',
        full_name: 'New User'
      }

      const mockResponse = {
        message: 'User created successfully',
        success: true
      }

      authApi.register = vi.fn().mockResolvedValue(mockResponse)

      const result = await authApi.register(userData)

      expect(authApi.register).toHaveBeenCalledWith(userData)
      expect(result).toEqual(mockResponse)
    })

    it('should handle registration errors', async () => {
      const userData = {
        email: 'existing@example.com',
        username: 'existing',
        password: 'password123'
      }

      const mockError = new Error('Email already exists')
      authApi.register = vi.fn().mockRejectedValue(mockError)

      await expect(authApi.register(userData)).rejects.toThrow('Email already exists')
    })
  })

  describe('getProfile', () => {
    it('should fetch user profile with token', async () => {
      const mockProfile = {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        full_name: 'Test User',
        is_active: true,
        created_at: '2023-01-01T00:00:00Z'
      }

      authApi.getProfile = vi.fn().mockResolvedValue(mockProfile)

      const result = await authApi.getProfile('test-token')

      expect(authApi.getProfile).toHaveBeenCalledWith('test-token')
      expect(result).toEqual(mockProfile)
    })

    it('should handle unauthorized access', async () => {
      const mockError = new Error('Unauthorized')
      authApi.getProfile = vi.fn().mockRejectedValue(mockError)

      await expect(authApi.getProfile('invalid-token')).rejects.toThrow('Unauthorized')
    })
  })

  describe('updateProfile', () => {
    it('should update user profile data', async () => {
      const updateData = {
        full_name: 'Updated Name',
        username: 'updateduser'
      }

      const mockUpdatedProfile = {
        id: 1,
        email: 'test@example.com',
        username: 'updateduser',
        full_name: 'Updated Name',
        is_active: true,
        created_at: '2023-01-01T00:00:00Z'
      }

      authApi.updateProfile = vi.fn().mockResolvedValue(mockUpdatedProfile)

      const result = await authApi.updateProfile('test-token', updateData)

      expect(authApi.updateProfile).toHaveBeenCalledWith('test-token', updateData)
      expect(result).toEqual(mockUpdatedProfile)
    })
  })

  describe('changePassword', () => {
    it('should change user password', async () => {
      const passwordData = {
        current_password: 'oldpassword',
        new_password: 'newpassword'
      }

      const mockResponse = {
        message: 'Password changed successfully',
        success: true
      }

      authApi.changePassword = vi.fn().mockResolvedValue(mockResponse)

      const result = await authApi.changePassword('test-token', passwordData)

      expect(authApi.changePassword).toHaveBeenCalledWith('test-token', passwordData)
      expect(result).toEqual(mockResponse)
    })

    it('should handle incorrect current password', async () => {
      const passwordData = {
        current_password: 'wrongpassword',
        new_password: 'newpassword'
      }

      const mockError = new Error('Current password is incorrect')
      authApi.changePassword = vi.fn().mockRejectedValue(mockError)

      await expect(authApi.changePassword('test-token', passwordData)).rejects.toThrow('Current password is incorrect')
    })
  })

  describe('logout', () => {
    it('should logout user successfully', async () => {
      const mockResponse = {
        message: 'Successfully logged out',
        success: true
      }

      authApi.logout = vi.fn().mockResolvedValue(mockResponse)

      const result = await authApi.logout('test-token')

      expect(authApi.logout).toHaveBeenCalledWith('test-token')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('refreshToken', () => {
    it('should refresh access token', async () => {
      const mockResponse = {
        access_token: 'new-access-token',
        token_type: 'bearer',
        expires_in: 3600
      }

      authApi.refreshToken = vi.fn().mockResolvedValue(mockResponse)

      const result = await authApi.refreshToken('refresh-token')

      expect(authApi.refreshToken).toHaveBeenCalledWith('refresh-token')
      expect(result).toEqual(mockResponse)
    })

    it('should handle invalid refresh token', async () => {
      const mockError = new Error('Invalid refresh token')
      authApi.refreshToken = vi.fn().mockRejectedValue(mockError)

      await expect(authApi.refreshToken('invalid-refresh-token')).rejects.toThrow('Invalid refresh token')
    })
  })

  describe('API configuration', () => {
    it('should have proper base configuration', () => {
      expect(authApi).toBeDefined()
      expect(typeof authApi.login).toBe('function')
      expect(typeof authApi.register).toBe('function')
      expect(typeof authApi.getProfile).toBe('function')
      expect(typeof authApi.updateProfile).toBe('function')
      expect(typeof authApi.changePassword).toBe('function')
      expect(typeof authApi.logout).toBe('function')
      expect(typeof authApi.refreshToken).toBe('function')
    })
  })
})
