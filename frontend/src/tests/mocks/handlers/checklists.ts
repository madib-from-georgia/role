import { rest } from 'msw'
import { faker } from '@faker-js/faker'

// Generate mock checklist data
const generateMockChecklist = (id: number) => ({
  id,
  title: faker.lorem.words(3),
  description: faker.lorem.paragraph(),
  order: id,
  questions: Array.from({ length: faker.number.int({ min: 5, max: 15 }) }, (_, i) => ({
    id: i + 1,
    text: faker.lorem.sentence() + '?',
    checklist_id: id,
    order: i + 1,
    source: 'system'
  }))
})

const mockChecklists = Array.from({ length: 20 }, (_, i) => generateMockChecklist(i + 1))

export const checklistHandlers = [
  // Get all checklists
  rest.get('/api/checklists', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    return res(ctx.json(mockChecklists))
  }),

  // Get checklist by ID
  rest.get('/api/checklists/:checklistId', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({ detail: 'Not authenticated' })
      )
    }
    
    const checklistId = parseInt(req.params.checklistId as string)
    const checklist = mockChecklists.find(c => c.id === checklistId)
    
    if (!checklist) {
      return res(
        ctx.status(404),
        ctx.json({ detail: 'Checklist not found' })
      )
    }
    
    return res(ctx.json(checklist))
  })
]
