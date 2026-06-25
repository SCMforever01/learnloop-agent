"""学习路由 — 会话管理、诊断、教学、练习、验证的完整闭环。"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.domain import Domain, Concept, ConceptPrerequisite, LearningSession, LearnerProfile
from app.agents.orchestrator import AgentOrchestrator
from app.api.schemas.schemas import (
    ApiResponse,
    StartSessionRequest,
    StartSessionResponse,
    ChatMessageRequest,
    DiagnosisResponse,
    SubmitAnswerRequest,
    SubmitVerificationRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/learn", tags=["学习"])


async def _get_domain_knowledge_graph(db: AsyncSession, domain_id: str) -> tuple[str, str]:
    """获取领域的知识图谱描述。返回 (domain_name, knowledge_graph_text)。"""
    domain_result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = domain_result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="领域不存在")

    concept_result = await db.execute(
        select(Concept)
        .where(Concept.domain_id == domain_id)
        .order_by(Concept.level, Concept.sort_order)
    )
    concepts = concept_result.scalars().all()

    prereq_result = await db.execute(
        select(ConceptPrerequisite)
        .where(ConceptPrerequisite.concept_id.in_([c.id for c in concepts]))
    )
    prereqs = prereq_result.scalars().all()
    prereq_map: dict[str, list[str]] = {}
    for p in prereqs:
        prereq_map.setdefault(p.concept_id, []).append(p.prerequisite_id)

    # 生成知识图谱文本
    lines = [f"# {domain.name} 知识图谱\n"]
    for c in concepts:
        prereq_names = prereq_map.get(c.id, [])
        prereq_str = f"（前置：{', '.join(prereq_names)}）" if prereq_names else ""
        lines.append(f"- [{c.level}级] {c.name}: {c.description or '无描述'} {prereq_str}")

    return domain.name, "\n".join(lines)


async def _get_concept_info(
    db: AsyncSession, domain_id: str, concept_id: str
) -> dict[str, Any]:
    """获取概念的详细信息。"""
    concept_result = await db.execute(
        select(Concept).where(Concept.id == concept_id, Concept.domain_id == domain_id)
    )
    concept = concept_result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail=f"概念不存在: {concept_id}")

    prereq_result = await db.execute(
        select(ConceptPrerequisite).where(ConceptPrerequisite.concept_id == concept_id)
    )
    prereq_ids = [p.prerequisite_id for p in prereq_result.scalars().all()]

    # 获取前置概念名称
    prereq_names = []
    if prereq_ids:
        prereq_concepts_result = await db.execute(
            select(Concept).where(Concept.id.in_(prereq_ids))
        )
        prereq_names = [c.name for c in prereq_concepts_result.scalars().all()]

    return {
        "id": concept.id,
        "name": concept.name,
        "description": concept.description or "",
        "level": concept.level,
        "prerequisites": ", ".join(prereq_names) if prereq_names else "无",
    }


# ========== 会话管理 ==========

@router.post("/sessions", response_model=ApiResponse)
async def start_session(
    req: StartSessionRequest,
    user_id: str = "demo-user",  # 简化：生产环境应从 JWT 获取
    db: AsyncSession = Depends(get_db),
):
    """创建新的学习会话。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.start_session(user_id, req.domain_id)

    return ApiResponse(data=StartSessionResponse(
        session_id=session.id,
        domain_id=session.domain_id,
        phase=session.phase,
    ).model_dump())


@router.get("/sessions/{session_id}", response_model=ApiResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """获取学习会话状态。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return ApiResponse(data={
        "session_id": session.id,
        "domain_id": session.domain_id,
        "phase": session.phase,
        "current_concept_id": session.current_concept_id,
        "session_data": session.session_data,
    })


# ========== 诊断 ==========

@router.post("/sessions/{session_id}/diagnose/start", response_model=ApiResponse)
async def start_diagnosis(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """开始诊断。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_name, knowledge_graph = await _get_domain_knowledge_graph(db, session.domain_id)
    reply = await orchestrator.start_diagnosis(session_id, domain_name, knowledge_graph)

    return ApiResponse(data={"reply": reply})


@router.post("/sessions/{session_id}/diagnose/answer", response_model=ApiResponse)
async def answer_diagnosis(
    session_id: str,
    req: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
):
    """回答诊断题目。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_name, knowledge_graph = await _get_domain_knowledge_graph(db, session.domain_id)
    result = await orchestrator.process_diagnosis_answer(
        session_id, domain_name, knowledge_graph, req.message
    )

    return ApiResponse(data={
        "reply": result["reply"],
        "diagnosis": result["diagnosis"],
        "phase": "learn" if result["diagnosis"] else "diagnose",
    })


# ========== 教学 ==========

@router.post("/sessions/{session_id}/teach/start", response_model=ApiResponse)
async def start_teaching(
    session_id: str,
    concept_id: str,
    db: AsyncSession = Depends(get_db),
):
    """开始教一个概念。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_result = await db.execute(select(Domain).where(Domain.id == session.domain_id))
    domain = domain_result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="领域不存在")

    concept_info = await _get_concept_info(db, session.domain_id, concept_id)

    reply = await orchestrator.start_teaching(
        session_id=session_id,
        domain_name=domain.name,
        concept_id=concept_id,
        concept_name=concept_info["name"],
        concept_description=concept_info["description"],
        prerequisites=concept_info["prerequisites"],
        target_audience="学生",
        knowledge_context="",
    )

    return ApiResponse(data={"reply": reply, "concept_id": concept_id})


@router.post("/sessions/{session_id}/teach/reply", response_model=ApiResponse)
async def teach_reply(
    session_id: str,
    req: ChatMessageRequest,
    concept_id: str = "",
    db: AsyncSession = Depends(get_db),
):
    """在教学阶段回复。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    cid = concept_id or session.current_concept_id
    if not cid:
        raise HTTPException(status_code=400, detail="未指定概念")

    domain_result = await db.execute(select(Domain).where(Domain.id == session.domain_id))
    domain = domain_result.scalar_one_or_none()
    concept_info = await _get_concept_info(db, session.domain_id, cid)

    result = await orchestrator.process_teaching_reply(
        session_id=session_id,
        domain_name=domain.name,
        concept_id=cid,
        concept_name=concept_info["name"],
        concept_description=concept_info["description"],
        prerequisites=concept_info["prerequisites"],
        target_audience="学生",
        knowledge_context="",
        user_message=req.message,
    )

    return ApiResponse(data=result)


# ========== 练习 ==========

@router.post("/sessions/{session_id}/practice/generate", response_model=ApiResponse)
async def generate_practice(
    session_id: str,
    concept_id: str,
    count: int = 3,
    db: AsyncSession = Depends(get_db),
):
    """生成练习题。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_result = await db.execute(select(Domain).where(Domain.id == session.domain_id))
    domain = domain_result.scalar_one_or_none()
    concept_info = await _get_concept_info(db, session.domain_id, concept_id)

    result = await orchestrator.generate_practice(
        session_id=session_id,
        domain_name=domain.name,
        concept_id=concept_id,
        concept_name=concept_info["name"],
        count=count,
    )

    return ApiResponse(data=result)


@router.post("/sessions/{session_id}/practice/submit", response_model=ApiResponse)
async def submit_practice(
    session_id: str,
    req: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
):
    """提交练习答案。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_result = await db.execute(select(Domain).where(Domain.id == session.domain_id))
    domain = domain_result.scalar_one_or_none()

    result = await orchestrator.submit_practice_answer(
        session_id=session_id,
        domain_name=domain.name,
        question_index=req.question_index,
        user_answer=req.user_answer,
    )

    return ApiResponse(data=result)


# ========== 验证 ==========

@router.post("/sessions/{session_id}/verify/start", response_model=ApiResponse)
async def start_verification(
    session_id: str,
    concept_id: str,
    db: AsyncSession = Depends(get_db),
):
    """开始验证。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_result = await db.execute(select(Domain).where(Domain.id == session.domain_id))
    domain = domain_result.scalar_one_or_none()
    concept_info = await _get_concept_info(db, session.domain_id, concept_id)

    result = await orchestrator.start_verification(
        session_id=session_id,
        domain_name=domain.name,
        concept_id=concept_id,
        concept_name=concept_info["name"],
        prerequisites=concept_info["prerequisites"],
    )

    return ApiResponse(data=result)


@router.post("/sessions/{session_id}/verify/submit", response_model=ApiResponse)
async def submit_verification(
    session_id: str,
    req: SubmitVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """提交验证答案。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_result = await db.execute(select(Domain).where(Domain.id == session.domain_id))
    domain = domain_result.scalar_one_or_none()

    answers = [{"question_index": a.question_index, "user_answer": a.user_answer} for a in req.answers]
    result = await orchestrator.submit_verification(session_id, domain.name, answers)

    return ApiResponse(data=result)


# ========== 路径规划 ==========

@router.post("/sessions/{session_id}/plan", response_model=ApiResponse)
async def plan_path(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """生成学习路径。"""
    orchestrator = AgentOrchestrator(db)
    session = await orchestrator.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    domain_name, knowledge_graph = await _get_domain_knowledge_graph(db, session.domain_id)
    result = await orchestrator.plan_learning_path(session_id, domain_name, knowledge_graph)

    return ApiResponse(data=result)
