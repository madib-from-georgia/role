// Типы для новой структуры чеклистов с поддержкой ответов по полу

export interface ChecklistAnswer {
  id: number;
  external_id: string;
  value_male: string;
  value_female: string;
  exported_value_male?: string;
  exported_value_female?: string;
  hint?: string;
  order_index: number;
  created_at: string;
  updated_at?: string;
}

export interface ChecklistQuestion {
  id: number;
  external_id: string;
  text: string;
  answer_type: 'single' | 'multiple' | 'text';
  source_type: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
  answers: ChecklistAnswer[];
  current_response?: ChecklistResponse;
  created_at: string;
  updated_at: string;
  // Контекстная информация для отображения
  sectionTitle?: string;
  subsectionTitle?: string;
  groupTitle?: string;
}

export interface ChecklistQuestionGroup {
  id: number;
  external_id: string;
  title: string;
  questions: ChecklistQuestion[];
  created_at: string;
  updated_at: string;
}

export interface ChecklistSubsection {
  id: number;
  external_id: string;
  title: string;
  question_groups: ChecklistQuestionGroup[];
  created_at: string;
  updated_at: string;
}

export interface ChecklistSection {
  id: number;
  external_id: string;
  title: string;
  subsections: ChecklistSubsection[];
  created_at: string;
  updated_at: string;
}

export interface ChecklistResponse {
  id: number;
  question_id: number;
  character_id: number;
  answer_id?: number;
  answer_text?: string;
  source_type: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
  comment?: string;
  version: number;
  created_at: string;
  updated_at: string;
  // Связанный ответ для отображения значений
  answer?: ChecklistAnswer;
}

export interface Checklist {
  id: number;
  slug: string;
  title: string;
  description?: string;
  file_hash: string;
  external_id: string;
  sections: ChecklistSection[];
  completion_stats?: {
    total_questions: number;
    answered_questions: number;
    completion_percentage: number;
  };
  character?: {
    id: number;
    name: string;
    description?: string;
    gender: 'male' | 'female';
  };
  created_at: string;
  updated_at: string;
}

// Типы для API запросов
export interface CreateResponseRequest {
  question_id: number;
  character_id: number;
  answer_id?: number;
  answer_text?: string;
  source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
  comment?: string;
}

export interface UpdateResponseRequest {
  answer_id?: number;
  answer_text?: string;
  source_type?: 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
  comment?: string;
  change_reason?: string;
}

// Типы для версионирования
export interface ChecklistVersion {
  id: number;
  checklist_id: number;
  version_number: number;
  file_hash: string;
  change_summary?: string;
  created_at: string;
}

export interface VersionComparisonResult {
  added_questions: number;
  removed_questions: number;
  modified_questions: number;
  added_answers: number;
  removed_answers: number;
  modified_answers: number;
}

// Утилитарные типы
export type AnswerType = 'single' | 'multiple' | 'text';
export type SourceType = 'FOUND_IN_TEXT' | 'LOGICALLY_DERIVED' | 'IMAGINED';
export type Gender = 'male' | 'female';

// Типы для экспорта (совместимость с существующим кодом)
export interface ExportRequest {
  character_id: number;
  format: 'pdf' | 'docx';
  export_type?: 'detailed' | 'summary' | 'compact';
  include_checklists?: string[];
  include_empty_responses?: boolean;
}

export interface ExportResponse {
  data: Blob;
  fileName: string;
  contentType: string;
}