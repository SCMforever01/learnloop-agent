import type { ApiResponse, Domain, Concept, LearningSession, DiagnosisResult, PracticeQuestion, LearningPath } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  const json: ApiResponse<T> = await res.json();
  if (!json.success) throw new Error(json.message);
  return json.data;
}

// ===== 领域 =====
export async function fetchDomains(): Promise<Domain[]> {
  return apiFetch<Domain[]>("/api/v1/domains");
}

export async function fetchDomain(domainId: string): Promise<Domain> {
  return apiFetch<Domain>(`/api/v1/domains/${domainId}`);
}

export async function fetchConcepts(domainId: string): Promise<Concept[]> {
  return apiFetch<Concept[]>(`/api/v1/domains/${domainId}/concepts`);
}

// ===== 学习会话 =====
export async function createSession(domainId: string): Promise<LearningSession> {
  return apiFetch<LearningSession>("/api/v1/learn/sessions", {
    method: "POST",
    body: JSON.stringify({ domain_id: domainId }),
  });
}

export async function getSession(sessionId: string) {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}`);
}

// ===== 诊断 =====
export async function startDiagnosis(sessionId: string): Promise<{ reply: string }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/diagnose/start`, { method: "POST" });
}

export async function answerDiagnosis(sessionId: string, message: string): Promise<{ reply: string; diagnosis: DiagnosisResult | null; phase: string }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/diagnose/answer`, {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, message }),
  });
}

// ===== 教学 =====
export async function startTeaching(sessionId: string, conceptId: string): Promise<{ reply: string; concept_id: string }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/teach/start?concept_id=${encodeURIComponent(conceptId)}`, { method: "POST" });
}

export async function teachReply(sessionId: string, message: string, conceptId: string): Promise<{ reply: string; concept_mastered: boolean }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/teach/reply?concept_id=${encodeURIComponent(conceptId)}`, {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, message }),
  });
}

// ===== 练习 =====
export async function generatePractice(sessionId: string, conceptId: string, count = 3): Promise<{ questions: PracticeQuestion[] }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/practice/generate?concept_id=${encodeURIComponent(conceptId)}&count=${count}`, { method: "POST" });
}

export async function submitPractice(sessionId: string, questionIndex: number, userAnswer: string): Promise<{ correct: boolean; feedback: string; error_type: string }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/practice/submit`, {
    method: "POST",
    body: JSON.stringify({ question_index: questionIndex, user_answer: userAnswer }),
  });
}

// ===== 验证 =====
export async function startVerification(sessionId: string, conceptId: string): Promise<{ questions: PracticeQuestion[] }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/verify/start?concept_id=${encodeURIComponent(conceptId)}`, { method: "POST" });
}

export async function submitVerification(sessionId: string, answers: { question_index: number; user_answer: string }[]): Promise<{ passed: boolean; accuracy: number; feedback: string }> {
  return apiFetch(`/api/v1/learn/sessions/${sessionId}/verify/submit`, {
    method: "POST",
    body: JSON.stringify({ answers }),
  });
}

// ===== 路径规划 =====
export async function planPath(sessionId: string): Promise<LearningPath> {
  return apiFetch<LearningPath>(`/api/v1/learn/sessions/${sessionId}/plan`, { method: "POST" });
}

// ===== 模型 =====
export async function fetchModels() {
  return apiFetch("/api/v1/models");
}
