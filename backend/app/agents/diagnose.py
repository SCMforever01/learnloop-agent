"""诊断 Agent — 通过精选题目评估用户对某领域的掌握程度。"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_client import chat_completion, chat_completion_json

logger = logging.getLogger(__name__)

DIAGNOSE_SYSTEM_PROMPT = """你是一位专业的 {domain_name} 诊断师。你的任务是通过对话式题目，快速评估用户对该领域的掌握程度。

## 规则
1. 从最基础的概念开始，逐步增加难度
2. 每次只出一道题，等用户回答后再出下一题
3. 根据用户的回答质量动态调整难度（答对则加难，答错则降难或换个角度）
4. 5-8 道题后给出诊断报告
5. 题型可以多样化：选择题、填空题、简答题
6. 语气鼓励、友好

## 当前领域知识图谱
{knowledge_graph}

## 输出格式
当你完成诊断后，必须输出以下 JSON 格式的诊断报告（用 ```json 包裹）：
```json
{{
  "overall_level": "beginner|intermediate|advanced",
  "strengths": ["掌握较好的概念1", "概念2"],
  "weaknesses": ["需要加强的概念1", "概念2"],
  "recommended_start": "建议从哪个概念开始学习",
  "estimated_study_hours": 20,
  "diagnosis_summary": "一句话总结"
}}
```
"""

DIAGNOSE_USER_PROMPT = """用户选择了领域：{domain_name}
用户当前回答：{user_answer}

请根据用户的回答：
1. 评判对错并简要说明
2. 出下一道诊断题（如果还没完成诊断）
3. 如果已经诊断了 5 道题以上，可以给出诊断报告

注意：直接输出，不要有多余的开场白。"""


async def run_diagnose_step(
    domain_name: str,
    knowledge_graph: str,
    conversation_history: list[dict[str, str]],
    user_answer: str,
) -> str:
    """执行一步诊断。

    Args:
        domain_name: 领域名称
        knowledge_graph: 该领域的知识图谱描述
        conversation_history: 之前的对话历史
        user_answer: 用户当前的回答

    Returns:
        Agent 的回复（包含下一道题或诊断报告）
    """
    system_prompt = DIAGNOSE_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        knowledge_graph=knowledge_graph,
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({
        "role": "user",
        "content": DIAGNOSE_USER_PROMPT.format(
            domain_name=domain_name,
            user_answer=user_answer,
        ),
    })

    response = await chat_completion(messages, temperature=0.7, max_tokens=1024)
    return response


async def extract_diagnosis_result(agent_response: str) -> dict[str, Any] | None:
    """从 Agent 回复中提取诊断报告 JSON。"""
    if "```json" in agent_response:
        json_str = agent_response.split("```json")[1].split("```")[0].strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    return None


async def generate_initial_diagnosis(domain_name: str, knowledge_graph: str) -> str:
    """生成诊断的第一条消息（欢迎 + 第一道题）。"""
    system_prompt = DIAGNOSE_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        knowledge_graph=knowledge_graph,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"用户选择了学习 {domain_name}，请开始诊断，出第一道题。"},
    ]

    response = await chat_completion(messages, temperature=0.7, max_tokens=512)
    return response
