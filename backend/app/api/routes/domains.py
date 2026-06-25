"""领域路由 — 领域列表/概念列表/概念详情。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.domain import Domain, Concept, ConceptPrerequisite, Question, ConceptMastery, LearnerProfile
from app.api.schemas.schemas import ApiResponse, DomainResponse, ConceptResponse, ConceptDetailResponse

router = APIRouter(prefix="/domains", tags=["领域"])


@router.get("", response_model=ApiResponse)
async def list_domains(db: AsyncSession = Depends(get_db)):
    """获取所有可用领域。"""
    result = await db.execute(
        select(Domain).where(Domain.is_active == True).order_by(Domain.sort_order)
    )
    domains = result.scalars().all()

    items = []
    for d in domains:
        # 统计概念数量
        count_result = await db.execute(
            select(func.count()).select_from(Concept).where(Concept.domain_id == d.id)
        )
        concept_count = count_result.scalar() or 0

        items.append(DomainResponse(
            id=d.id,
            name=d.name,
            category=d.category,
            description=d.description or "",
            icon=d.icon or "📚",
            concept_count=concept_count,
        ).model_dump())

    return ApiResponse(data=items)


@router.get("/{domain_id}", response_model=ApiResponse)
async def get_domain(domain_id: str, db: AsyncSession = Depends(get_db)):
    """获取领域详情。"""
    result = await db.execute(select(Domain).where(Domain.id == domain_id))
    domain = result.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="领域不存在")

    return ApiResponse(data=DomainResponse(
        id=domain.id,
        name=domain.name,
        category=domain.category,
        description=domain.description or "",
        icon=domain.icon or "📚",
    ).model_dump())


@router.get("/{domain_id}/concepts", response_model=ApiResponse)
async def list_concepts(
    domain_id: str,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """获取领域的所有概念。可选传入 user_id 以获取掌握度。"""
    result = await db.execute(
        select(Concept)
        .where(Concept.domain_id == domain_id)
        .order_by(Concept.sort_order, Concept.level)
    )
    concepts = result.scalars().all()

    # 获取前置关系
    prereq_result = await db.execute(
        select(ConceptPrerequisite)
        .where(ConceptPrerequisite.concept_id.in_([c.id for c in concepts]))
    )
    prereqs = prereq_result.scalars().all()
    prereq_map: dict[str, list[str]] = {}
    for p in prereqs:
        prereq_map.setdefault(p.concept_id, []).append(p.prerequisite_id)

    # 获取用户掌握度（如果有）
    mastery_map: dict[str, float] = {}
    confidence_map: dict[str, float] = {}
    if user_id:
        profile_result = await db.execute(
            select(LearnerProfile).where(
                LearnerProfile.user_id == user_id,
                LearnerProfile.domain_id == domain_id,
            )
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            mastery_result = await db.execute(
                select(ConceptMastery).where(
                    ConceptMastery.learner_profile_id == profile.id
                )
            )
            for m in mastery_result.scalars().all():
                mastery_map[m.concept_id] = m.score
                confidence_map[m.concept_id] = m.confidence

    items = []
    for c in concepts:
        items.append(ConceptDetailResponse(
            id=c.id,
            domain_id=c.domain_id,
            name=c.name,
            description=c.description or "",
            level=c.level,
            tags=c.tags or [],
            prerequisites=prereq_map.get(c.id, []),
            mastery_score=mastery_map.get(c.id, 0.0),
            mastery_confidence=confidence_map.get(c.id, 0.0),
        ).model_dump())

    return ApiResponse(data=items)


@router.get("/{domain_id}/concepts/{concept_id:path}", response_model=ApiResponse)
async def get_concept(
    domain_id: str,
    concept_id: str,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """获取概念详情。"""
    result = await db.execute(
        select(Concept).where(Concept.id == concept_id, Concept.domain_id == domain_id)
    )
    concept = result.scalar_one_or_none()
    if not concept:
        raise HTTPException(status_code=404, detail="概念不存在")

    # 获取前置关系
    prereq_result = await db.execute(
        select(ConceptPrerequisite).where(ConceptPrerequisite.concept_id == concept_id)
    )
    prereqs = [p.prerequisite_id for p in prereq_result.scalars().all()]

    # 统计题目数量
    q_count_result = await db.execute(
        select(func.count()).select_from(Question).where(Question.concept_id == concept_id)
    )
    question_count = q_count_result.scalar() or 0

    # 获取掌握度
    mastery_score = 0.0
    mastery_confidence = 0.0
    if user_id:
        profile_result = await db.execute(
            select(LearnerProfile).where(
                LearnerProfile.user_id == user_id,
                LearnerProfile.domain_id == domain_id,
            )
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            mastery_result = await db.execute(
                select(ConceptMastery).where(
                    ConceptMastery.learner_profile_id == profile.id,
                    ConceptMastery.concept_id == concept_id,
                )
            )
            mastery = mastery_result.scalar_one_or_none()
            if mastery:
                mastery_score = mastery.score
                mastery_confidence = mastery.confidence

    return ApiResponse(data=ConceptDetailResponse(
        id=concept.id,
        domain_id=concept.domain_id,
        name=concept.name,
        description=concept.description or "",
        level=concept.level,
        tags=concept.tags or [],
        prerequisites=prereqs,
        question_count=question_count,
        mastery_score=mastery_score,
        mastery_confidence=mastery_confidence,
    ).model_dump())
