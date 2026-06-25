"""验证 Agent — 学习单元结束时的综合验证。"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_client import chat_completion_json

logger = logging.getLogger(__name__)

VERIFY_SYSTEM_PROMPT = """你是一位 {domain_name} 学习效果评估师。在学习单元结束时，你需要进行综合验证。

## 验证规则
1. 出 5 道综合题，覆盖当前概念 + 前置概念
2. 难度适中（不要太难也不要太简单）
3. 题型多样化
4. 评分后给出详细反馈

## 当前上下文
- 领域：{domain_name}
- 验证概念：{concept_name}
- 前置概念：{prerequisites}
- 用户学习时长：{study_minutes} 分钟

## 输出格式
```json
{{
  "questions": [
    {{
      "id": "v1",
      "type": "choice",
      "content": "题目内容",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "answer": "B",
      "explanation": "解析",
      "difficulty": 5
    }}
  ],
  "pass_criteria": {{
    "min_correct": 4,
    "min_accuracy": 0.8
  }}
}}
```
"""

EVALUATE_SYSTEM_PROMPT = """你是一位 {domain_name} 学习效果评估师。请根据用户的验证结果给出评估报告。

## 验证结果
- 总题数：{total}
- 正确数：{correct}
- 正确率：{accuracy}

## 各题详情
{question_details}

## 输出格式
```json
{{
  "passed": true/false,
  "accuracy": 0.8,
  "feedback": "整体评价和鼓励",
  "strengths": ["表现好的方面"],
  "weaknesses": ["需要继续加强的方面"],
  "recommendation": "next_concept/review_more/retry",
  "next_concept_id": "如果通过，下一个概念的ID"
}}
```
"""


async def generate_verification_questions(
    domain_name: str,
    concept_name: str,
    prerequisites: str,
    study_minutes: int,
) -> dict[str, Any]:
    """生成验证题目。"""
    system_prompt = VERIFY_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        concept_name=concept_name,
        prerequisites=prerequisites,
        study_minutes=study_minutes,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请生成 5 道验证题目，检验用户对「{concept_name}」的掌握情况。"},
    ]

    return await chat_completion_json(messages, temperature=0.5, max_tokens=2048)


async def evaluate_verification(
    domain_name: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """评估验证结果。

    Args:
        results: [{"question": {...}, "user_answer": "...", "correct": true/false}, ...]
    """
    total = len(results)
    correct = sum(1 for r in results if r.get("correct"))
    accuracy = correct / total if total > 0 else 0

    question_details = ""
    for i, r in enumerate(results, 1):
        q = r.get("question", {})
        status = "✅" if r.get("correct") else "❌"
        question_details += f"{i}. {status} {q.get('content', '')}\n"
        question_details += f"   用户答案: {r.get('user_answer', '')} | 正确答案: {q.get('answer', '')}\n"

    system_prompt = EVALUATE_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        total=total,
        correct=correct,
        accuracy=f"{accuracy:.0%}",
        question_details=question_details,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "请给出评估报告。"},
    ]

    return await chat_completion_json(messages, temperature=0.3, max_tokens=1024)
