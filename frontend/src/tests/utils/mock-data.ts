import { faker } from '@faker-js/faker'

// Types for mock data
type MockOverrides = Record<string, unknown>;

// Mock project data
export const createMockProject = (overrides: MockOverrides = {}) => ({
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
export const createMockCharacter = (overrides: MockOverrides = {}) => ({
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
export const createMockChecklist = (overrides: MockOverrides = {}) => ({
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
export const createMockQuestion = (overrides: MockOverrides = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  external_id: faker.string.uuid(),
  text: faker.lorem.sentence() + '?',
  order_index: faker.number.int({ min: 0, max: 10 }),
  answer_type: 'text' as 'single' | 'multiple' | 'text',
  source_type: 'FOUND_IN_TEXT' as 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED',
  answers: [],
  current_response: undefined,
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  // Контекстная информация для отображения
  sectionTitle: faker.lorem.words(2),
  subsectionTitle: faker.lorem.words(2),
  groupTitle: undefined,
  ...overrides
})

// Mock checklist question group
export const createMockQuestionGroup = (overrides: MockOverrides = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  external_id: faker.string.uuid(),
  title: faker.lorem.words(3),
  order_index: faker.number.int({ min: 0, max: 10 }),
  questions: [],
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
})

// Mock checklist answer
export const createMockAnswer = (overrides: MockOverrides = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  external_id: faker.string.uuid(),
  value_male: faker.lorem.words(2),
  value_female: faker.lorem.words(2),
  order_index: faker.number.int({ min: 1, max: 10 }),
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
})

// Mock checklist response
export const createMockResponse = (overrides: MockOverrides = {}) => ({
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
export const createMockUser = (overrides: MockOverrides = {}) => ({
  id: faker.number.int({ min: 1, max: 1000 }),
  email: faker.internet.email(),
  username: faker.internet.userName(),
  full_name: faker.person.fullName(),
  is_active: true,
  created_at: faker.date.past().toISOString(),
  ...overrides
})

// Mock pagination data
export const createMockPagination = (items: unknown[], page = 1, limit = 10) => ({
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
export const createMockFile = (overrides: MockOverrides = {}) => ({
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

export const createMockResponses = (characterId: number, checklistId: number, questions: Array<{ id: number }>) =>
  questions.slice(0, faker.number.int({ min: 0, max: questions.length }))
    .map(q => createMockResponse({
      character_id: characterId,
      checklist_id: checklistId,
      question_id: q.id
    }))
