import { rest } from 'msw'
import { faker } from '@faker-js/faker'

// Generate mock character data
const generateMockCharacter = (id: number, projectId: number) => ({
  id,
  name: faker.person.fullName(),
  description: faker.lorem.paragraph(),
  project_id: projectId,
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  analysis_status: faker.helpers.arrayElement(['pending', 'processing', 'completed', 'failed'])
})

// Mock characters for different projects
const mockCharacters: Record<number, Array<Record<string, unknown>>> = {}
for (let projectId = 1; projectId <= 10; projectId++) {
  mockCharacters[projectId] = Array.from(
    { length: faker.number.int({ min: 1, max: 5 }) },
    (_, i) => generateMockCharacter(i + 1 + (projectId - 1) * 10, projectId)
  )
}

export const characterHandlers = [
  // Get characters for a project
  rest.get('/api/projects/:projectId/characters', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const projectId = parseInt(req.params.projectId as string)
    const characters = mockCharacters[projectId] || []
    
    return res(ctx.json(characters))
  }),

  // Get single character
  rest.get('/api/characters/:characterId', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const characterId = parseInt(req.params.characterId as string)
    
    // Find character across all projects
    let character = null
    for (const projectChars of Object.values(mockCharacters)) {
      const found = projectChars.find(c => c.id === characterId)
      if (found) {
        character = found
        break
      }
    }
    
    if (!character) {
      return res(
        ctx.status(404),
        ctx.json({ detail: 'Character not found' })
      )
    }
    
    return res(ctx.json(character))
  })
]
