"""LearnLoop Agent — FastAPI 应用入口。"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import init_db
from app.api.routes import users, domains, learn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库。"""
    logger.info("🚀 LearnLoop Agent 启动中...")
    await init_db()
    logger.info("✅ 数据库初始化完成")
    yield
    logger.info("👋 LearnLoop Agent 关闭")


settings = get_settings()

app = FastAPI(
    title="LearnLoop Agent",
    description="通用垂类知识学习 Agent 平台 — 诊断→教学→练习→验证 闭环",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(users.router, prefix="/api/v1")
app.include_router(domains.router, prefix="/api/v1")
app.include_router(learn.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "LearnLoop Agent",
        "version": "0.1.0",
        "description": "通用垂类知识学习 Agent 平台",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/models")
async def list_models():
    """列出可用的 LLM 模型。"""
    from app.core.llm_client import list_available_models
    models = await list_available_models()
    return {"models": models}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port, reload=settings.app_debug)
