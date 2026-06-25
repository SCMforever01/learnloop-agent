"""SQLAlchemy ORM 模型 — 用户、领域、概念、学习记录。"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


# ========== 用户 ==========

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=True)
    password_hash = Column(String(256), nullable=False)
    nickname = Column(String(64), default="")
    avatar_url = Column(String(512), default="")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    learner_profiles = relationship("LearnerProfile", back_populates="user", lazy="selectin")
    chat_messages = relationship("ChatMessage", back_populates="user", lazy="selectin")


# ========== 领域 ==========

class Domain(Base):
    __tablename__ = "domains"

    id = Column(String(64), primary_key=True)  # 如 "python", "cpa-accounting"
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False, index=True)  # 编程/金融/医学/语言/K12
    description = Column(Text, default="")
    icon = Column(String(32), default="📚")
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    concepts = relationship("Concept", back_populates="domain", lazy="selectin")
    questions = relationship("Question", back_populates="domain", lazy="selectin")


# ========== 知识概念 ==========

class Concept(Base):
    __tablename__ = "concepts"

    id = Column(String(128), primary_key=True)  # 如 "python/variables"
    domain_id = Column(String(64), ForeignKey("domains.id"), nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    level = Column(Integer, default=1)  # 难度 1-10
    tags = Column(JSON, default=list)  # ["基础", "变量"]
    sort_order = Column(Integer, default=0)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    domain = relationship("Domain", back_populates="concepts")
    prerequisites = relationship(
        "ConceptPrerequisite",
        foreign_keys="ConceptPrerequisite.concept_id",
        back_populates="concept",
        lazy="selectin",
    )
    questions = relationship("Question", back_populates="concept", lazy="selectin")


class ConceptPrerequisite(Base):
    __tablename__ = "concept_prerequisites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    concept_id = Column(String(128), ForeignKey("concepts.id"), nullable=False, index=True)
    prerequisite_id = Column(String(128), ForeignKey("concepts.id"), nullable=False, index=True)
    strength = Column(Float, default=1.0)  # 关系强度 0-1

    concept = relationship("Concept", foreign_keys=[concept_id], back_populates="prerequisites")


# ========== 题目 ==========

class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    domain_id = Column(String(64), ForeignKey("domains.id"), nullable=False, index=True)
    concept_id = Column(String(128), ForeignKey("concepts.id"), nullable=False, index=True)
    question_type = Column(String(32), nullable=False)  # choice/fill/code/open/case_analysis
    content = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # 选择题选项
    answer = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    difficulty = Column(Integer, default=5)  # 1-10
    tags = Column(JSON, default=list)
    source = Column(String(128), default="")  # 数据来源
    created_at = Column(DateTime, default=datetime.utcnow)

    domain = relationship("Domain", back_populates="questions")
    concept = relationship("Concept", back_populates="questions")


# ========== 学习者画像 ==========

class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    domain_id = Column(String(64), ForeignKey("domains.id"), nullable=False, index=True)
    overall_level = Column(String(32), default="beginner")  # beginner/intermediate/advanced
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    study_time_minutes = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    last_study_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="learner_profiles")
    concept_masteries = relationship("ConceptMastery", back_populates="learner_profile", lazy="selectin")


class ConceptMastery(Base):
    __tablename__ = "concept_masteries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    learner_profile_id = Column(Integer, ForeignKey("learner_profiles.id"), nullable=False, index=True)
    concept_id = Column(String(128), ForeignKey("concepts.id"), nullable=False, index=True)
    score = Column(Float, default=0.0)  # 掌握度 0-1
    confidence = Column(Float, default=0.1)  # 置信度 0-1
    attempts = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    error_patterns = Column(JSON, default=list)  # 错误模式
    last_tested_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    learner_profile = relationship("LearnerProfile", back_populates="concept_masteries")


# ========== 聊天记录 ==========

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(36), nullable=False, index=True)  # 学习会话
    role = Column(String(16), nullable=False)  # user/assistant/system
    agent_type = Column(String(32), default="")  # diagnose/teach/practice/verify/path_planner
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_messages")


# ========== 学习会话 ==========

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    domain_id = Column(String(64), ForeignKey("domains.id"), nullable=False)
    current_concept_id = Column(String(128), nullable=True)
    phase = Column(String(32), default="diagnose")  # diagnose/learn/practice/verify
    session_data = Column(JSON, default=dict)  # 会话状态数据
    started_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
