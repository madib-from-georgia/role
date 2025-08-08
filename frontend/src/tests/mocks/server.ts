import { setupServer } from 'msw/node'
import { authHandlers } from './handlers/auth'
import { projectHandlers } from './handlers/projects'
import { checklistHandlers } from './handlers/checklists'
import { characterHandlers } from './handlers/characters'

// Combine all handlers
export const handlers = [
  ...authHandlers,
  ...projectHandlers,
  ...checklistHandlers,
  ...characterHandlers,
]

// Setup MSW server
export const server = setupServer(...handlers)
