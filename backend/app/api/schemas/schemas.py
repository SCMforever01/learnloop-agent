"""API Schemas — 请求/响应的 Pydantic 模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ========== 通用 ==========

class ApiResponse(BaseModel):
    success: bool = True
    message: str = "ok"
    data: Any = None


class PaginatedResponse(BaseModel):
    items: list[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20


# ========== 用户 ==========

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: str = ""
    email: str = ""


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    nickname: str
    email: str
    avatar_url: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ========== 领域 ==========

class DomainResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    icon: str
    concept_count: int = 0

    class Config:
        from_attributes = True


class ConceptResponse(BaseModel):
    id: str
    domain_id: str
    name: str
    description: str
    level: int
    tags: list[str]
    prerequisites: list[str] = []

    class Config:
        from_attributes = True


class ConceptDetailResponse(ConceptResponse):
    question_count: int = 0
    mastery_score: float = 0.0
    mastery_confidence: float = 0.0


# ========== 学习会话 ==========

class StartSessionRequest(BaseModel):
    domain_id: str


class StartSessionResponse(BaseModel):
    session_id: str
    domain_id: str
    phase: str


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str


class ChatMessageResponse(BaseModel):
    role: str
    agent_type: str
    content: str
    created_at: datetime


class DiagnosisResult(BaseModel):
    overall_level: str = "beginner"
    strengths: list[str] = []
    weaknesses: list[str] = []
    recommended_start: str = ""
    estimated_study_hours: int = 10
    diagnosis_summary: str = ""


class DiagnosisResponse(BaseModel):
    reply: str
    diagnosis: Optional[DiagnosisResult] = None


class LearningPathStep(BaseModel):
    step: int
    concept_id: str
    concept_name: str
    action: str
    estimated_minutes: int
    reason: str


class LearningPathResponse(BaseModel):
    learning_path: list[LearningPathStep] = []
    total_estimated_minutes: int = 0
    milestones: list[dict[str, Any]] = []


# ========== 练习 ==========

class PracticeQuestion(BaseModel):
    id: str
    type: str
    content: str
    options: list[str] = []
    difficulty: int = 5


class PracticeResponse(BaseModel):
    questions: list[PracticeQuestion] = []


class SubmitAnswerRequest(BaseModel):
    question_index: int
    user_answer: str


class AnswerEvaluation(BaseModel):
    correct: bool = False
    feedback: str = ""
    error_type: str = ""


# ========== 验证 ==========

class VerificationResponse(BaseModel):
    questions: list[PracticeQuestion] = []


class SubmitVerificationRequest(BaseModel):
    answers: list[SubmitAnswerRequest]


class VerificationResult(BaseModel):
    passed: bool = False
    accuracy: float = 0.0
    feedback: str = ""
    strengths: list[str] = []
    weaknesses: list[str] = []
    recommendation: str = ""
