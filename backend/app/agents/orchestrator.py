"""Agent 编排器 — 统一调度诊断/教学/练习/验证/路径规划五个 Agent。"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import (
    ChatMessage,
    ConceptMastery,
    LearnerProfile,
    LearningSession,
)
from app.agents.diagnose import (
    run_diagnose_step,
    extract_diagnosis_result,
    generate_initial_diagnosis,
)
from app.agents.teach import run_teach_step, generate_concept_intro
from app.agents.practice import generate_practice_questions, evaluate_answer
from app.agents.verify import generate_verification_questions, evaluate_verification
from app.agents.path_planner import generate_learning_path

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Agent 编排器，管理学习会话的生命周期。"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 会话管理 ==========

    async def start_session(self, user_id: str, domain_id: str) -> LearningSession:
        """创建新的学习会话。"""
        session = LearningSession(
            user_id=user_id,
            domain_id=domain_id,
            phase="diagnose",
            session_data={},
        )
        self.db.add(session)
        await self.db.flush()

        # 确保学习者画像存在
        profile = await self._get_or_create_profile(user_id, domain_id)

        return session

    async def get_session(self, session_id: str) -> LearningSession | None:
        """获取学习会话。"""
        result = await self.db.execute(
            select(LearningSession).where(LearningSession.id == session_id)
        )
        return result.scalar_one_or_none()

    # ========== 诊断阶段 ==========

    async def start_diagnosis(
        self, session_id: str, domain_name: str, knowledge_graph: str
    ) -> str:
        """开始诊断，返回第一条诊断消息。"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        session.phase = "diagnose"

        # 生成诊断开场白 + 第一道题
        first_message = await generate_initial_diagnosis(domain_name, knowledge_graph)

        # 保存消息
        await self._save_message(
            user_id=session.user_id,
            session_id=session_id,
            role="assistant",
            agent_type="diagnose",
            content=first_message,
        )

        return first_message

    async def process_diagnosis_answer(
        self,
        session_id: str,
        domain_name: str,
        knowledge_graph: str,
        user_answer: str,
    ) -> dict[str, Any]:
        """处理用户的诊断回答。

        Returns:
            {"reply": "Agent回复", "diagnosis": {...} or None}
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        # 保存用户消息
        await self._save_message(
            user_id=session.user_id,
            session_id=session_id,
            role="user",
            agent_type="diagnose",
            content=user_answer,
        )

        # 获取对话历史
        history = await self._get_conversation_history(session_id)

        # 调用诊断 Agent
        reply = await run_diagnose_step(
            domain_name=domain_name,
            knowledge_graph=knowledge_graph,
            conversation_history=history[:-1],  # 不包含刚保存的用户消息
            user_answer=user_answer,
        )

        # 保存 Agent 回复
        await self._save_message(
            user_id=session.user_id,
            session_id=session_id,
            role="assistant",
            agent_type="diagnose",
            content=reply,
        )

        # 尝试提取诊断结果
        diagnosis = await extract_diagnosis_result(reply)

        if diagnosis:
            # 诊断完成，更新会话状态
            session.phase = "learn"
            session.session_data = {**session.session_data, "diagnosis": diagnosis}

            # 更新学习者画像
            await self._update_profile_from_diagnosis(
                session.user_id, session.domain_id, diagnosis
            )

        return {"reply": reply, "diagnosis": diagnosis}

    # ========== 教学阶段 ==========

    async def start_teaching(
        self,
        session_id: str,
        domain_name: str,
        concept_id: str,
        concept_name: str,
        concept_description: str,
        prerequisites: str,
        target_audience: str,
        knowledge_context: str,
    ) -> str:
        """开始教一个新概念。"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        session.phase = "learn"
        session.current_concept_id = concept_id

        # 获取掌握度
        profile = await self._get_or_create_profile(session.user_id, session.domain_id)
        mastery = await self._get_concept_mastery(profile.id, concept_id)
        mastery_score = mastery.score if mastery else 0.0

        # 生成概念介绍
        intro = await generate_concept_intro(
            domain_name=domain_name,
            concept_name=concept_name,
            concept_description=concept_description,
            prerequisites=prerequisites,
            target_audience=target_audience,
            knowledge_context=knowledge_context,
        )

        await self._save_message(
            user_id=session.user_id,
            session_id=session_id,
            role="assistant",
            agent_type="teach",
            content=intro,
        )

        return intro

    async def process_teaching_reply(
        self,
        session_id: str,
        domain_name: str,
        concept_id: str,
        concept_name: str,
        concept_description: str,
        prerequisites: str,
        target_audience: str,
        knowledge_context: str,
        user_message: str,
    ) -> dict[str, Any]:
        """处理用户在教学阶段的回复。

        Returns:
            {"reply": "...", "concept_mastered": true/false}
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        await self._save_message(
            user_id=session.user_id,
            session_id=session_id,
            role="user",
            agent_type="teach",
            content=user_message,
        )

        profile = await self._get_or_create_profile(session.user_id, session.domain_id)
        mastery = await self._get_concept_mastery(profile.id, concept_id)
        mastery_score = mastery.score if mastery else 0.0

        history = await self._get_conversation_history(session_id)

        reply = await run_teach_step(
            domain_name=domain_name,
            concept_name=concept_name,
            concept_description=concept_description,
            prerequisites=prerequisites,
            mastery_score=mastery_score,
            target_audience=target_audience,
            knowledge_context=knowledge_context,
            conversation_history=history[:-1],
            user_message=user_message,
        )

        await self._save_message(
            user_id=session.user_id,
            session_id=session_id,
            role="assistant",
            agent_type="teach",
            content=reply,
        )

        concept_mastered = "[CONCEPT_MASTERED]" in reply

        return {"reply": reply, "concept_mastered": concept_mastered}

    # ========== 练习阶段 ==========

    async def generate_practice(
        self,
        session_id: str,
        domain_name: str,
        concept_id: str,
        concept_name: str,
        count: int = 3,
    ) -> dict[str, Any]:
        """生成练习题。"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        session.phase = "practice"

        profile = await self._get_or_create_profile(session.user_id, session.domain_id)
        mastery = await self._get_concept_mastery(profile.id, concept_id)
        mastery_score = mastery.score if mastery else 0.0
        error_patterns = mastery.error_patterns if mastery else []

        result = await generate_practice_questions(
            domain_name=domain_name,
            concept_name=concept_name,
            mastery_score=mastery_score,
            error_patterns=error_patterns,
            prerequisites="",
            count=count,
        )

        # 保存到会话数据
        session.session_data = {
            **session.session_data,
            "practice_questions": result.get("questions", []),
        }

        return result

    async def submit_practice_answer(
        self,
        session_id: str,
        domain_name: str,
        question_index: int,
        user_answer: str,
    ) -> dict[str, Any]:
        """提交练习答案并评估。"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        questions = session.session_data.get("practice_questions", [])
        if question_index >= len(questions):
            return {"error": "题目索引越界"}

        question = questions[question_index]
        evaluation = await evaluate_answer(domain_name, question, user_answer)

        # 更新掌握度
        profile = await self._get_or_create_profile(session.user_id, session.domain_id)
        concept_id = question.get("concept_id", session.current_concept_id)
        if concept_id:
            await self._update_concept_mastery(
                profile_id=profile.id,
                concept_id=concept_id,
                correct=evaluation.get("correct", False),
                error_type=evaluation.get("error_type", ""),
            )

        return evaluation

    # ========== 验证阶段 ==========

    async def start_verification(
        self,
        session_id: str,
        domain_name: str,
        concept_id: str,
        concept_name: str,
        prerequisites: str,
    ) -> dict[str, Any]:
        """开始验证阶段。"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        session.phase = "verify"

        profile = await self._get_or_create_profile(session.user_id, session.domain_id)
        study_minutes = profile.study_time_minutes

        questions = await generate_verification_questions(
            domain_name=domain_name,
            concept_name=concept_name,
            prerequisites=prerequisites,
            study_minutes=study_minutes,
        )

        session.session_data = {
            **session.session_data,
            "verification_questions": questions.get("questions", []),
        }

        return questions

    async def submit_verification(
        self,
        session_id: str,
        domain_name: str,
        answers: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """提交验证答案并评估。

        Args:
            answers: [{"question_index": 0, "user_answer": "A"}, ...]
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        questions = session.session_data.get("verification_questions", [])
        results = []

        for ans in answers:
            idx = ans.get("question_index", 0)
            if idx < len(questions):
                q = questions[idx]
                eval_result = await evaluate_answer(domain_name, q, ans.get("user_answer", ""))
                results.append({
                    "question": q,
                    "user_answer": ans.get("user_answer", ""),
                    "correct": eval_result.get("correct", False),
                })

        # 评估整体结果
        evaluation = await evaluate_verification(domain_name, results)

        # 更新学习者画像
        profile = await self._get_or_create_profile(session.user_id, session.domain_id)
        correct_count = sum(1 for r in results if r.get("correct"))
        profile.total_questions += len(results)
        profile.correct_count += correct_count

        return evaluation

    # ========== 路径规划 ==========

    async def plan_learning_path(
        self,
        session_id: str,
        domain_name: str,
        knowledge_graph: str,
    ) -> dict[str, Any]:
        """根据诊断结果生成学习路径。"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"会话不存在: {session_id}")

        diagnosis = session.session_data.get("diagnosis", {})

        path = await generate_learning_path(
            domain_name=domain_name,
            overall_level=diagnosis.get("overall_level", "beginner"),
            strengths=diagnosis.get("strengths", []),
            weaknesses=diagnosis.get("weaknesses", []),
            recommended_start=diagnosis.get("recommended_start", ""),
            estimated_hours=diagnosis.get("estimated_study_hours", 10),
            knowledge_graph=knowledge_graph,
        )

        session.session_data = {**session.session_data, "learning_path": path}
        return path

    # ========== 内部方法 ==========

    async def _get_or_create_profile(
        self, user_id: str, domain_id: str
    ) -> LearnerProfile:
        """获取或创建学习者画像。"""
        result = await self.db.execute(
            select(LearnerProfile).where(
                LearnerProfile.user_id == user_id,
                LearnerProfile.domain_id == domain_id,
            )
        )
        profile = result.scalar_one_or_none()
        if not profile:
            profile = LearnerProfile(user_id=user_id, domain_id=domain_id)
            self.db.add(profile)
            await self.db.flush()
        return profile

    async def _get_concept_mastery(
        self, profile_id: int, concept_id: str
    ) -> ConceptMastery | None:
        """获取概念掌握度。"""
        result = await self.db.execute(
            select(ConceptMastery).where(
                ConceptMastery.learner_profile_id == profile_id,
                ConceptMastery.concept_id == concept_id,
            )
        )
        return result.scalar_one_or_none()

    async def _update_concept_mastery(
        self, profile_id: int, concept_id: str, correct: bool, error_type: str
    ) -> None:
        """更新概念掌握度。"""
        mastery = await self._get_concept_mastery(profile_id, concept_id)
        if not mastery:
            mastery = ConceptMastery(
                learner_profile_id=profile_id,
                concept_id=concept_id,
                score=0.0,
                confidence=0.1,
            )
            self.db.add(mastery)

        mastery.attempts += 1
        if correct:
            mastery.correct_count += 1
            mastery.score = min(1.0, mastery.score + (1 - mastery.score) * 0.3)
        else:
            mastery.score = max(0.0, mastery.score - mastery.score * 0.4)
            if error_type and error_type not in (mastery.error_patterns or []):
                mastery.error_patterns = (mastery.error_patterns or []) + [error_type]

        # 置信度随测试次数增加
        mastery.confidence = min(1.0, 0.1 + mastery.attempts * 0.1)

    async def _update_profile_from_diagnosis(
        self, user_id: str, domain_id: str, diagnosis: dict[str, Any]
    ) -> None:
        """根据诊断结果更新学习者画像。"""
        profile = await self._get_or_create_profile(user_id, domain_id)
        profile.overall_level = diagnosis.get("overall_level", "beginner")

    async def _save_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        agent_type: str,
        content: str,
    ) -> None:
        """保存聊天消息。"""
        msg = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            role=role,
            agent_type=agent_type,
            content=content,
        )
        self.db.add(msg)

    async def _get_conversation_history(
        self, session_id: str, limit: int = 20
    ) -> list[dict[str, str]]:
        """获取对话历史。"""
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return [{"role": m.role, "content": m.content} for m in messages]
