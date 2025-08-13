// Общие типы для замены any

export interface Question {
  id: string | number
  text: string
  type: 'OPEN_TEXT' | 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE'
  sectionTitle?: string
  subsectionTitle?: string
  hint?: string
  options?: string[]
  answers?: Answer[]
  current_response?: QuestionResponse | null
  answer_type?: string
}

export interface Answer {
  id: number
  value_male: string
  value_female: string
  external_id: string
}

export interface QuestionResponse {
  id: number
  answer?: string
  answer_text?: string
  comment?: string
  source_type?: string
  updated_at: string
}

export interface Checklist {
  id: string | number
  title: string
  description?: string
  questions: Question[]
}

export interface Character {
  id: string | number
  name: string
  gender?: string
  [key: string]: unknown
}

export interface Project {
  id: string
  title: string
  description?: string
  created_at: string
  updated_at: string
}

export interface ApiError {
  message: string
  status?: number
  response?: {
    status: number
    data?: unknown
  }
  [key: string]: unknown
}

export interface FormData {
  [key: string]: string | number | boolean | undefined
}

// Типы для прогресса чеклистов
export interface ChecklistProgress {
  checklist_id: string | number
  completion_percentage: number
  answered_questions?: number
  total_questions?: number
}

export interface ChecklistStats {
  completion_percentage: number
}

export interface ChecklistItem {
  id: string | number
  title: string
  description?: string
  slug: string
  icon?: string
  completion_stats?: ChecklistStats
}

// Типы для событий
export interface ChangeEvent {
  target: {
    value: string
    name?: string
  }
}

export interface SelectEvent {
  target: {
    value: string | string[]
  }
}