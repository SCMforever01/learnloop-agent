"""用户路由 — 注册/登录/信息。"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.database import get_db
from app.models.domain import User
from app.api.schemas.schemas import (
    ApiResponse,
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["用户"])


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _create_token(user_id: str) -> str:
    settings = get_settings()
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, settings.app_secret_key, algorithm="HS256")


@router.post("/register", response_model=ApiResponse)
async def register(req: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """注册新用户。"""
    # 检查用户名是否已存在
    existing = await db.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=req.username,
        password_hash=_hash_password(req.password),
        nickname=req.nickname or req.username,
        email=req.email,
    )
    db.add(user)
    await db.flush()

    token = _create_token(user.id)
    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email or "",
        avatar_url=user.avatar_url or "",
        created_at=user.created_at,
    )

    return ApiResponse(data=TokenResponse(
        access_token=token,
        user=user_resp,
    ).model_dump())


@router.post("/login", response_model=ApiResponse)
async def login(req: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录。"""
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user or user.password_hash != _hash_password(req.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = _create_token(user.id)
    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email or "",
        avatar_url=user.avatar_url or "",
        created_at=user.created_at,
    )

    return ApiResponse(data=TokenResponse(
        access_token=token,
        user=user_resp,
    ).model_dump())


@router.get("/me", response_model=ApiResponse)
async def get_me(user_id: str, db: AsyncSession = Depends(get_db)):
    """获取当前用户信息。"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return ApiResponse(data=UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        email=user.email or "",
        avatar_url=user.avatar_url or "",
        created_at=user.created_at,
    ).model_dump())
