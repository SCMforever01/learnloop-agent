export interface Domain {
  id: string;
  name: string;
  category: string;
  description: string;
  icon: string;
  concept_count: number;
}

export interface Concept {
  id: string;
  domain_id: string;
  name: string;
  description: string;
  level: number;
  tags: string[];
  prerequisites: string[];
  mastery_score: number;
  mastery_confidence: number;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
}

export interface LearningSession {
  session_id: string;
  domain_id: string;
  phase: string;
}

export interface DiagnosisResult {
  overall_level: string;
  strengths: string[];
  weaknesses: string[];
  recommended_start: string;
  estimated_study_hours: number;
  diagnosis_summary: string;
}

export interface PracticeQuestion {
  id: string;
  type: string;
  content: string;
  options: string[];
  answer: string;
  explanation: string;
  difficulty: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  agent_type: string;
  content: string;
  created_at?: string;
}

export interface LearningPath {
  learning_path: {
    step: number;
    concept_id: string;
    concept_name: string;
    action: string;
    estimated_minutes: number;
    reason: string;
  }[];
  total_estimated_minutes: number;
  milestones: { step: number; description: string; verification: string }[];
}
