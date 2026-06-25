"""通用工具函数。"""

from __future__ import annotations

import uuid
from datetime import datetime


def gen_id() -> str:
    """生成 UUID。"""
    return str(uuid.uuid4())


def now() -> datetime:
    """当前 UTC 时间。"""
    return datetime.utcnow()


def truncate(text: str, max_len: int = 200) -> str:
    """截断文本。"""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."
