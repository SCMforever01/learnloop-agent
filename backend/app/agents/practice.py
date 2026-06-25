"""练习 Agent — 根据用户掌握度生成针对性练习题。"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_client import chat_completion, chat_completion_json

logger = logging.getLogger(__name__)

PRACTICE_SYSTEM_PROMPT = """你是一位 {domain_name} 练习出题官。你的任务是根据用户当前的掌握程度，生成高质量的练习题。

## 出题规则
1. 题目难度 = 用户当前掌握度 + 1（在舒适区边缘挑战）
2. 每组 3-5 道题，覆盖当前概念 + 前置概念巩固
3. 题型多样化：选择题、填空题、简答题
4. 选择题要设置合理的干扰项（基于常见错误模式）
5. 每道题都要有标准答案和详细解析

## 当前上下文
- 领域：{domain_name}
- 考察概念：{concept_name}
- 用户掌握度：{mastery_score}
- 用户常见错误：{error_patterns}
- 前置概念：{prerequisites}

## 输出格式
输出 JSON 格式的题目列表：
```json
{{
  "questions": [
    {{
      "id": "q1",
      "type": "choice",
      "content": "题目内容",
      "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
      "answer": "A",
      "explanation": "详细解析",
      "difficulty": 5,
      "concept_id": "concept_id"
    }}
  ]
}}
```
"""


async def generate_practice_questions(
    domain_name: str,
    concept_name: str,
    mastery_score: float,
    error_patterns: list[str],
    prerequisites: str,
    count: int = 3,
) -> dict[str, Any]:
    """生成练习题。

    Returns:
        包含 questions 列表的字典
    """
    system_prompt = PRACTICE_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        concept_name=concept_name,
        mastery_score=f"{mastery_score:.0%}",
        error_patterns=", ".join(error_patterns) if error_patterns else "暂无",
        prerequisites=prerequisites,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请生成 {count} 道练习题，覆盖「{concept_name}」及其前置概念。"},
    ]

    result = await chat_completion_json(messages, temperature=0.5, max_tokens=2048)
    return result


async def evaluate_answer(
    domain_name: str,
    question: dict[str, Any],
    user_answer: str,
) -> dict[str, Any]:
    """评估用户的答案。

    Returns:
        {{"correct": true/false, "feedback": "反馈内容", "error_type": "错误类型"}}
    """
    messages = [
        {"role": "system", "content": f"""你是一位 {domain_name} 的阅卷老师。请评判用户答案是否正确。

题目：{question.get('content', '')}
标准答案：{question.get('answer', '')}
解析：{question.get('explanation', '')}

请输出 JSON：
```json
{{
  "correct": true/false,
  "feedback": "详细的反馈，告诉用户为什么对/错",
  "error_type": "如果错了，错误类型是什么（概念不清/计算错误/粗心/理解偏差）"
}}
```
"""},
        {"role": "user", "content": f"用户的答案是：{user_answer}"},
    ]

    result = await chat_completion_json(messages, temperature=0.3, max_tokens=512)
    return result
