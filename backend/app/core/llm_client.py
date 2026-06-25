"""LLM 客户端 — 统一接口，支持 DeepSeek / GPT / GLM / MiMo。"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# ========== 模型配置表 ==========

MODEL_CONFIGS: dict[str, dict[str, str]] = {
    "deepseek-chat": {
        "api_key_field": "deepseek_api_key",
        "base_url_field": "deepseek_base_url",
        "model_name": "deepseek-chat",
        "display_name": "DeepSeek V3",
    },
    "deepseek-reasoner": {
        "api_key_field": "deepseek_api_key",
        "base_url_field": "deepseek_base_url",
        "model_name": "deepseek-reasoner",
        "display_name": "DeepSeek R1",
    },
    "gpt-5.5": {
        "api_key_field": "openai_api_key",
        "base_url_field": "openai_base_url",
        "model_name": "ppio/pa/gpt-5.5",
        "display_name": "GPT-5.5 (PPIO)",
    },
    "glm-5.2": {
        "api_key_field": "zhipu_api_key",
        "base_url_field": "zhipu_base_url",
        "model_name": "zhipu/glm-5.2",
        "display_name": "GLM-5.2 (智谱)",
    },
    "mimo-v2.5-pro": {
        "api_key_field": "mimo_api_key",
        "base_url_field": "mimo_base_url",
        "model_name": "mimo-v2.5-pro",
        "display_name": "MiMo V2.5 Pro (小米)",
    },
}


def _get_client(model_key: str) -> tuple[AsyncOpenAI, str]:
    """根据模型 key 返回 (客户端, 模型名称)。"""
    settings = get_settings()
    config = MODEL_CONFIGS.get(model_key)
    if not config:
        raise ValueError(f"未知模型: {model_key}，可选: {list(MODEL_CONFIGS.keys())}")

    api_key = getattr(settings, config["api_key_field"])
    base_url = getattr(settings, config["base_url_field"])

    if not api_key or api_key == "sk-xxx" or api_key == "xxx":
        # 如果 key 未配置，降级到 DeepSeek
        logger.warning(f"模型 {model_key} API Key 未配置，降级到 deepseek-chat")
        config = MODEL_CONFIGS["deepseek-chat"]
        api_key = getattr(settings, config["api_key_field"])
        base_url = getattr(settings, config["base_url_field"])

    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return client, config["model_name"]


# ========== 对外接口 ==========

async def chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    json_mode: bool = False,
) -> str:
    """统一的聊天完成接口。

    Args:
        messages: OpenAI 格式的消息列表 [{"role": "user", "content": "..."}]
        model: 模型 key（如 "deepseek-chat", "gpt-5.5"），默认用配置的 default_model
        temperature: 温度
        max_tokens: 最大 token 数
        json_mode: 是否强制 JSON 输出

    Returns:
        模型回复的文本内容
    """
    settings = get_settings()
    model_key = model or settings.default_model

    client, model_name = _get_client(model_key)

    kwargs: dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or ""
        logger.info(f"LLM [{model_key}] 输入 {len(messages)} 条消息，输出 {len(content)} 字符")
        return content
    except Exception as e:
        logger.error(f"LLM [{model_key}] 调用失败: {e}")
        raise


async def chat_completion_json(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> dict[str, Any]:
    """聊天完成并解析 JSON 返回。"""
    content = await chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        json_mode=True,
    )
    # 尝试从 markdown code block 中提取 JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.warning(f"JSON 解析失败，原始内容: {content[:200]}")
        return {"raw": content, "error": "json_parse_failed"}


async def list_available_models() -> list[dict[str, str]]:
    """列出所有已配置 API Key 的可用模型。"""
    settings = get_settings()
    available = []
    for key, config in MODEL_CONFIGS.items():
        api_key = getattr(settings, config["api_key_field"])
        is_configured = api_key and api_key not in ("sk-xxx", "xxx", "")
        available.append({
            "key": key,
            "name": config["display_name"],
            "available": is_configured,
        })
    return available
