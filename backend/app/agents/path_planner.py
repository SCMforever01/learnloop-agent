"""路径规划 Agent — 根据诊断结果生成个性化学习路径。"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_client import chat_completion_json

logger = logging.getLogger(__name__)

PATH_PLANNER_SYSTEM_PROMPT = """你是一位 {domain_name} 学习路径规划师。根据用户的诊断结果，生成个性化学习路径。

## 规则
1. 必须尊重知识图谱的前置关系（不会 A 就不能学 B）
2. 优先补弱点，但适当穿插已掌握内容保持信心
3. 每个学习单元控制在 15-30 分钟
4. 设置阶段性检验点
5. 根据用户水平调整路径长度和深度

## 用户诊断结果
- 整体水平：{overall_level}
- 优势：{strengths}
- 弱点：{weaknesses}
- 建议起点：{recommended_start}
- 预计学习时长：{estimated_hours} 小时

## 知识图谱
{knowledge_graph}

## 输出格式
```json
{{
  "learning_path": [
    {{
      "step": 1,
      "concept_id": "concept/id",
      "concept_name": "概念名称",
      "action": "learn|practice|review",
      "estimated_minutes": 20,
      "reason": "为什么安排这个步骤"
    }}
  ],
  "total_estimated_minutes": 120,
  "milestones": [
    {{
      "step": 3,
      "description": "完成基础概念学习",
      "verification": "通过基础验证测试"
    }}
  ]
}}
```
"""


async def generate_learning_path(
    domain_name: str,
    overall_level: str,
    strengths: list[str],
    weaknesses: list[str],
    recommended_start: str,
    estimated_hours: int,
    knowledge_graph: str,
) -> dict[str, Any]:
    """生成个性化学习路径。"""
    system_prompt = PATH_PLANNER_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        overall_level=overall_level,
        strengths=", ".join(strengths),
        weaknesses=", ".join(weaknesses),
        recommended_start=recommended_start,
        estimated_hours=estimated_hours,
        knowledge_graph=knowledge_graph,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "请根据以上诊断结果，生成个性化学习路径。"},
    ]

    return await chat_completion_json(messages, temperature=0.5, max_tokens=2048)


async def adjust_learning_path(
    domain_name: str,
    current_path: list[dict[str, Any]],
    completed_steps: list[int],
    performance_data: dict[str, Any],
) -> dict[str, Any]:
    """根据学习进度动态调整路径。

    Args:
        current_path: 当前学习路径
        completed_steps: 已完成的步骤编号
        performance_data: 学习表现数据（正确率、用时等）
    """
    messages = [
        {"role": "system", "content": f"""你是 {domain_name} 学习路径规划师。请根据用户的学习进度调整路径。

当前路径：{json.dumps(current_path, ensure_ascii=False, indent=2)}
已完成步骤：{completed_steps}
学习表现：{json.dumps(performance_data, ensure_ascii=False, indent=2)}

请输出调整后的路径（JSON 格式，同原格式）。如果表现好，可以加速；如果表现差，需要补充练习。
"""},
        {"role": "user", "content": "请调整学习路径。"},
    ]

    return await chat_completion_json(messages, temperature=0.5, max_tokens=2048)
