// Общие типы для frontend и backend

export interface Project {
  id: string;
  title: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Text {
  id: string;
  project_id: string;
  filename: string;
  original_format: 'txt' | 'pdf' | 'fb2' | 'epub';
  content: string;
  metadata?: Record<string, any>;
  processed_at?: string;
  created_at: string;
}

export interface Character {
  id: string;
  text_id: string;
  name: string;
  aliases?: string[];
  mentions_count: number;
  first_mention: number;
  importance_score: number;
  created_at: string;
}

export interface CharacterAnalysis {
  id: string;
  character_id: string;
  analysis_type: AnalysisType;
  content: Record<string, any>;
  ai_service: AIProvider;
  confidence_score: number;
  created_at: string;
  updated_at: string;
}

export interface Quote {
  id: string;
  character_id: string;
  text: string;
  context?: string;
  position: number;
  quote_type: 'self_description' | 'others_about' | 'actions';
  analysis_id?: string;
  created_at: string;
}

export enum AnalysisType {
  PHYSICAL_PORTRAIT = 'physical_portrait',
  EMOTIONAL_PROFILE = 'emotional_profile',
  SPEECH_CHARACTERISTICS = 'speech_characteristics',
  INTERNAL_CONFLICTS = 'internal_conflicts',
  MOTIVATION_GOALS = 'motivation_goals',
  CHARACTER_RELATIONSHIPS = 'character_relationships',
  BIOGRAPHY_BACKSTORY = 'biography_backstory',
  SOCIAL_STATUS = 'social_status',
  KEY_SCENES = 'key_scenes',
  ACTING_TASKS = 'acting_tasks',
  PRACTICAL_EXERCISES = 'practical_exercises',
  SUBTEXT_ANALYSIS = 'subtext_analysis',
  TEMPO_RHYTHM = 'tempo_rhythm',
  PERSONALITY_TYPE = 'personality_type',
  DEFENSE_MECHANISMS = 'defense_mechanisms',
  TRAUMA_PTSD = 'trauma_ptsd',
  ARCHETYPES = 'archetypes',
  EMOTIONAL_INTELLIGENCE = 'emotional_intelligence',
  COGNITIVE_DISTORTIONS = 'cognitive_distortions',
  ATTACHMENT_STYLES = 'attachment_styles'
}

export enum AIProvider {
  YANDEX_GPT = 'yandex_gpt',
  CLAUDE = 'claude',
  GPT4 = 'gpt4',
  SPECIALIZED = 'specialized'
}

export enum DeploymentStage {
  MVP = 'mvp',
  EXTENDED = 'extended',
  FULL = 'full'
}

// API Response types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// NLP Processing types
export interface NLPResult {
  characters: Character[];
  speech_attribution: SpeechAttribution[];
  emotional_markup: EmotionalMarkup[];
  context_markup: ContextMarkup[];
  quality_metrics: QualityMetrics;
}

export interface SpeechAttribution {
  character_id: string;
  text: string;
  position: number;
  speech_type: 'dialogue' | 'monologue' | 'internal' | 'author';
  confidence: number;
}

export interface EmotionalMarkup {
  text: string;
  position: number;
  emotion: string;
  intensity: number;
  confidence: number;
}

export interface ContextMarkup {
  text: string;
  position: number;
  context_type: string;
  description: string;
}

export interface QualityMetrics {
  character_extraction_accuracy: number;
  speech_attribution_accuracy: number;
  dialogue_coverage: number;
  processing_time: number;
}

// Analysis Results types
export interface PhysicalPortraitResult {
  height?: string;
  build?: string;
  hair?: string;
  eyes?: string;
  age?: string;
  distinctive_features?: string[];
  clothing_style?: string;
  posture?: string;
  gestures?: string[];
  confidence_score: number;
}

// Text Processing Results types
export interface TextProcessingResult {
  text_id: string;
  filename: string;
  file_size: number;
  encoding: string;
  word_count: number;
  character_count: number;
  processing_status: 'processing' | 'completed' | 'failed';
  characters_found: number;
  characters: ProcessedCharacter[];
  nlp_metrics: QualityMetrics;
  processing_time: number;
  error_message?: string;
  processed_at: string;
}

export interface ProcessedCharacter {
  name: string;
  aliases: string[];
  mentions_count: number;
  first_mention: number;
  importance_score: number;
}

// Upload Response type
export interface UploadResponse {
  success: boolean;
  text_id: string;
  processing_result: TextProcessingResult;
  message?: string;
  error?: string;
}



export interface EmotionalProfileResult {
  dominant_emotions: string[];
  emotional_range: string;
  emotional_stability: string;
  triggers: string[];
  coping_mechanisms: string[];
  emotional_intelligence_level: string;
  confidence_score: number;
}

export interface SpeechCharacteristicsResult {
  vocabulary_level: string;
  speech_patterns: string[];
  favorite_expressions: string[];
  speech_tempo: string;
  intonation_patterns: string[];
  dialect_accent?: string;
  formality_level: string;
  confidence_score: number;
}

// Full Character Analysis types
export interface CharacterAnalysisResult {
  success: boolean;
  character_name: string;
  analysis_type: string;
  data?: PhysicalPortraitResult | EmotionalProfileResult | SpeechCharacteristicsResult;
  error?: string;
  metadata?: {
    ai_service?: string;
    model?: string;
    nlp_quality_metrics?: QualityMetrics;
    [key: string]: any;
  };
}

export interface FullCharacterAnalysis {
  character_name: string;
  text_id: string;
  project_id: string;
  analyses: {
    physical_portrait?: CharacterAnalysisResult;
    emotional_profile?: CharacterAnalysisResult;
    speech_characteristics?: CharacterAnalysisResult;
  };
  summary: {
    total_modules: number;
    successful_modules: number;
    failed_modules: number;
    overall_confidence: number;
  };
}
