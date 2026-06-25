"""教学 Agent — 苏格拉底式对话教学，不直接给答案，引导思考。"""

from __future__ import annotations

import logging

from app.core.llm_client import chat_completion

logger = logging.getLogger(__name__)

TEACH_SYSTEM_PROMPT = """你是一位耐心、友好的 {domain_name} 老师，名叫"小智"。

## 当前教学任务
教学概念：{concept_name}
概念描述：{concept_description}
前置概念：{prerequisites}
用户当前掌握度：{mastery_score}

## 教学原则（苏格拉底式）
1. **不直接给答案**，用提问引导用户自己思考
2. 用**类比和生活例子**解释抽象概念
3. 每讲完一个小知识点，出一道**小测验**确认理解
4. 如果用户连续答对 3 次，说明已掌握，可以进入下一个概念
5. 如果用户连续答错 2 次，**换一种方式**重新讲解（用不同例子或角度）
6. 语气鼓励、亲切，适合 {target_audience} 理解
7. 控制每次回复的长度，不要一次性输出太多内容

## 对话风格示例
- "很好的思路！让我们再想想……"
- "你觉得这里应该用什么方法？"
- "你能用自己的话解释一下吗？"
- "没错！你已经掌握了这个概念，我们来看看下一个。"

## 知识背景
{knowledge_context}
"""

TEACH_USER_PROMPT = """用户说：{user_message}

请根据教学原则回复用户。如果判断用户已掌握当前概念，在回复末尾加上：
[CONCEPT_MASTERED]

如果需要调整难度，在回复末尾加上：
[ADJUST_DIFFICULTY: easier/harder]
"""


async def run_teach_step(
    domain_name: str,
    concept_name: str,
    concept_description: str,
    prerequisites: str,
    mastery_score: float,
    target_audience: str,
    knowledge_context: str,
    conversation_history: list[dict[str, str]],
    user_message: str,
) -> str:
    """执行一步教学。

    Returns:
        Agent 的教学回复
    """
    system_prompt = TEACH_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        concept_name=concept_name,
        concept_description=concept_description,
        prerequisites=prerequisites,
        mastery_score=f"{mastery_score:.0%}",
        target_audience=target_audience,
        knowledge_context=knowledge_context,
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    response = await chat_completion(messages, temperature=0.7, max_tokens=1024)
    return response


async def generate_concept_intro(
    domain_name: str,
    concept_name: str,
    concept_description: str,
    prerequisites: str,
    target_audience: str,
    knowledge_context: str,
) -> str:
    """生成概念介绍的第一条消息。"""
    system_prompt = TEACH_SYSTEM_PROMPT.format(
        domain_name=domain_name,
        concept_name=concept_name,
        concept_description=concept_description,
        prerequisites=prerequisites,
        mastery_score="0%",
        target_audience=target_audience,
        knowledge_context=knowledge_context,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请开始讲解「{concept_name}」这个概念。先做一个简单的引入，然后出第一道引导性问题。"},
    ]

    response = await chat_completion(messages, temperature=0.7, max_tokens=512)
    return response
