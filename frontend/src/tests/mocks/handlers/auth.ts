import { rest } from 'msw'
import { faker } from '@faker-js/faker'

// Mock user data
const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  full_name: 'Test User',
  is_active: true,
  created_at: '2023-01-01T00:00:00Z'
}

const mockTokens = {
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  token_type: 'bearer',
  expires_in: 3600
}

export const authHandlers = [
  // Login
  rest.post('/api/auth/login', async (req, res, ctx) => {
    const body = await req.json() as { email: string; password: string }
    
    if (body.email === 'test@example.com' && body.password === 'password') {
      return res(ctx.json(mockTokens))
    }
    
    if (body.email === 'fail@example.com') {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Incorrect email or password' })
      )
    }
    
    return res(ctx.json(mockTokens))
  }),

  // Register
  rest.post('/api/auth/register', async (req, res, ctx) => {
    const body = await req.json() as {
      email: string
      username: string
      password: string
      full_name?: string
    }
    
    if (body.email === 'existing@example.com') {
      return res(
        ctx.status(400),
        ctx.json({ detail: 'Email already registered' })
      )
    }
    
    return res(
      ctx.json({
        message: 'User created successfully',
        success: true
      })
    )
  }),

  // Get profile
  rest.get('/api/auth/me', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    return res(ctx.json(mockUser))
  }),

  // Update profile
  rest.put('/api/auth/me', async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const body = await req.json() as Partial<typeof mockUser>
    const updatedUser = { ...mockUser, ...body }
    
    return res(ctx.json(updatedUser))
  }),

  // Change password
  rest.post('/api/auth/change-password', async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const body = await req.json() as {
      current_password: string
      new_password: string
    }
    
    if (body.current_password === 'wrongpassword') {
      return res(
        ctx.status(400),
        ctx.json({ detail: 'Current password is incorrect' })
      )
    }
    
    return res(
      ctx.json({
        message: 'Password changed successfully',
        success: true
      })
    )
  }),

  // Logout
  rest.post('/api/auth/logout', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    return res(
      ctx.json({
        message: 'Successfully logged out',
        success: true
      })
    )
  }),

  // Refresh token
  rest.post('/api/auth/refresh', async (req, res, ctx) => {
    const body = await req.json() as { refresh_token: string }
    
    if (body.refresh_token === 'invalid-token') {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Invalid refresh token' })
      )
    }
    
    return res(
      ctx.json({
        access_token: 'new-access-token',
        token_type: 'bearer',
        expires_in: 3600
      })
    )
  })
]
