import { rest } from 'msw'
import { faker } from '@faker-js/faker'

// Generate mock projects
const generateMockProject = (id: number) => ({
  id,
  title: faker.lorem.words(3),
  description: faker.lorem.paragraph(),
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  user_id: 1,
  texts: []
})

const mockProjects = Array.from({ length: 10 }, (_, i) => generateMockProject(i + 1))

export const projectHandlers = [
  // Get projects list
  rest.get('/api/projects', (req, res, ctx) => {
    const url = new URL(req.url)
    const page = parseInt(url.searchParams.get('page') || '1')
    const limit = parseInt(url.searchParams.get('limit') || '10')
    const skip = (page - 1) * limit
    
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const paginatedProjects = mockProjects.slice(skip, skip + limit)
    
    return res(
      ctx.json({
        items: paginatedProjects,
        total: mockProjects.length,
        page,
        limit,
        pages: Math.ceil(mockProjects.length / limit)
      })
    )
  }),

  // Get single project
  rest.get('/api/projects/:projectId', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const projectId = parseInt(req.params.projectId as string)
    const project = mockProjects.find(p => p.id === projectId)
    
    if (!project) {
      return res(
        ctx.status(404),
        ctx.json({ detail: 'Project not found' })
      )
    }
    
    return res(ctx.json(project))
  }),

  // Create project
  rest.post('/api/projects', async (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const body = await req.json() as {
      title: string
      description?: string
    }
    
    if (!body.title) {
      return res(
        ctx.status(400),
        ctx.json({ detail: 'Title is required' })
      )
    }
    
    const newProject = {
      id: mockProjects.length + 1,
      title: body.title,
      description: body.description || '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      user_id: 1,
      texts: []
    }
    
    mockProjects.push(newProject)
    
    return res(ctx.status(201), ctx.json(newProject))
  })
]
