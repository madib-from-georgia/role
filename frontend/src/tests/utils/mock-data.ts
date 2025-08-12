import { faker } from '@faker-js/faker'

// Mock project data
export const createMockProject = (overrides: any = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  title: faker.lorem.words(3),
  description: faker.lorem.paragraph(),
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  user_id: 1,
  texts: [],
  ...overrides
})

// Mock character data
export const createMockCharacter = (overrides: any = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  name: faker.person.fullName(),
  description: faker.lorem.paragraph(),
  project_id: faker.number.int({ min: 1, max: 10 }),
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  analysis_status: faker.helpers.arrayElement(['pending', 'processing', 'completed', 'failed']),
  analysis_data: {
    physical_traits: Array.from({ length: 3 }, () => faker.lorem.sentence()),
    personality_traits: Array.from({ length: 4 }, () => faker.lorem.sentence()),
    relationships: Array.from({ length: 2 }, () => ({
      character: faker.person.firstName(),
      relationship: faker.helpers.arrayElement(['friend', 'enemy', 'lover', 'family'])
    })),
    key_moments: Array.from({ length: 3 }, () => faker.lorem.sentence())
  },
  ...overrides
})

// Mock checklist data
export const createMockChecklist = (overrides: any = {}) => ({
  id: faker.number.int({ min: 1, max: 20 }),
  title: faker.lorem.words(3),
  description: faker.lorem.paragraph(),
  order: faker.number.int({ min: 1, max: 20 }),
  questions: Array.from({ length: faker.number.int({ min: 5, max: 15 }) }, (_, i) => ({
    id: i + 1,
    text: faker.lorem.sentence() + '?',
    checklist_id: faker.number.int({ min: 1, max: 20 }),
    order: i + 1,
    source: 'system'
  })),
  ...overrides
})

// Mock checklist question
export const createMockQuestion = (overrides: any = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  text: faker.lorem.sentence() + '?',
  answer_type: 'text' as 'single' | 'multiple' | 'text',
  checklist_id: faker.number.int({ min: 1, max: 20 }),
  order: faker.number.int({ min: 1, max: 20 }),
  source: 'system',
  answers: [],
  current_response: null,
  sectionTitle: faker.lorem.words(2),
  subsectionTitle: faker.lorem.words(2),
  groupTitle: null,
  ...overrides
})

// Mock checklist response
export const createMockResponse = (overrides: any = {}) => ({
  id: faker.string.uuid(),
  character_id: faker.number.int({ min: 1, max: 100 }),
  checklist_id: faker.number.int({ min: 1, max: 20 }),
  question_id: faker.number.int({ min: 1, max: 100 }),
  response: faker.lorem.paragraph(),
  created_at: faker.date.recent().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
})

// Mock user data
export const createMockUser = (overrides: any = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  email: faker.internet.email(),
  username: faker.internet.userName(),
  full_name: faker.person.fullName(),
  is_active: true,
  created_at: faker.date.past().toISOString(),
  ...overrides
})

// Mock pagination data
export const createMockPagination = (items: any[], page = 1, limit = 10) => ({
  items: items.slice((page - 1) * limit, page * limit),
  total: items.length,
  page,
  limit,
  pages: Math.ceil(items.length / limit)
})

// Mock API error response
export const createMockApiError = (message = 'An error occurred', status = 400) => ({
  detail: message,
  status
})

// Mock file data
export const createMockFile = (overrides: any = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  title: faker.lorem.words(2),
  filename: faker.system.fileName(),
  content_preview: faker.lorem.sentences(2),
  upload_date: faker.date.recent().toISOString(),
  project_id: faker.number.int({ min: 1, max: 10 }),
  ...overrides
})

// Generate arrays of mock data
export const createMockProjects = (count = 5) => 
  Array.from({ length: count }, () => createMockProject())

export const createMockCharacters = (count = 3) => 
  Array.from({ length: count }, () => createMockCharacter())

export const createMockChecklists = (count = 10) => 
  Array.from({ length: count }, () => createMockChecklist())

export const createMockQuestions = (count = 10, checklistId = 1) => 
  Array.from({ length: count }, (_, i) => createMockQuestion({ 
    id: i + 1, 
    checklist_id: checklistId, 
    order: i + 1 
  }))

export const createMockResponses = (characterId: number, checklistId: number, questions: any[]) =>
  questions.slice(0, faker.number.int({ min: 0, max: questions.length }))
    .map(q => createMockResponse({
      character_id: characterId,
      checklist_id: checklistId,
      question_id: q.id
    }))
